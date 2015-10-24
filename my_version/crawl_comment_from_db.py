# -*- coding: utf-8 -*-
'''
Created on Sep 2, 2015

@author: xhj
'''
from store_model import Single_weibo_store, Single_comment, Single_comment_store, \
    UserInfo_store
import sys
import threading
import Queue
from loginer import Loginer
from craw_page_parse import Crawler_with_proxy
from my_log import WeiboSearchLog
from bs4 import BeautifulSoup
import traceback
from mongoengine.errors import NotUniqueError
reload(sys)  
sys.setdefaultencoding('utf8')   





class crawl_comment(threading.Thread):
    del_proxy_lock = threading.Lock()
    
    def __init__(self, dict_url_id, thread_name='crawl_comment'):
        threading.Thread.__init__(self)
        self.name = thread_name
        self.dict_url_id = dict_url_id
    
    # 抓取并解析页面
    def crawl(self, url, is_again=True, two_again=True):
        loginer = Loginer()
        cookie = loginer.get_cookie()
        proxy = loginer.get_proxy()
        craw_object = Crawler_with_proxy(url, cookie, proxy)
        
        WeiboSearchLog().get_scheduler_logger().info(self.name + " start to crawl ! " + url)
        
        comment_list = []
        page = ""
        try:
            page = craw_object.get_page()
            comment_list = page_parser_from_search_for_comment(page)
        except:
            print traceback.format_exc()
            crawl_comment.del_proxy_lock.acquire()
            if proxy == loginer.get_proxy():
                loginer.del_proxy()
                WeiboSearchLog().get_scheduler_logger().warning(self.name + " proxy exception , change proxy !")
            crawl_comment.del_proxy_lock.release()
            if is_again :
                return self.crawl(url, is_again=False)
            else:
                if two_again:
                    return self.crawl(url, is_again=False, two_again=False)
                return comment_list
        
        
        if len(comment_list) == 0:
            # ## 还没有人针对这条微博发表评论!
            if no_one_commented(page):
                WeiboSearchLog().get_scheduler_logger().info(self.name + " nobody commented !")
                return comment_list;
            
            crawl_comment.del_proxy_lock.acquire()
            if proxy == loginer.get_proxy():
                loginer.del_proxy()
                WeiboSearchLog().get_scheduler_logger().warning(self.name + " comment_list is 0 , change proxy !")
            crawl_comment.del_proxy_lock.release()
            if is_again:
                return self.crawl(url, is_again=False)
            else:
                if two_again:
                    return self.crawl(url, is_again=False, two_again=False)
                return comment_list
        else:
            return comment_list

    # 将微博存储到数据库中
    def store_comment_to_db(self, comment_list, weibo_id):
        for comment in comment_list:
            unique_single = Single_comment_store(weibo_id=weibo_id, uid=comment.uid, nickname=comment.nickname, auth=comment.auth, content=comment.content, praise_num=comment.praise_num, creat_time=comment.creat_time)
            try:
                unique_single.save()
            except NotUniqueError:
                pass
            except:
                WeiboSearchLog().get_scheduler_logger().info(self.name + " insert to database, something wrong !")
                pass
        WeiboSearchLog().get_scheduler_logger().info(self.name + " insert to database, success !")
        pass
    
    def run(self):
        for url_key in self.dict_url_id:
            weibo_id = self.dict_url_id[url_key]
            comment_list = self.crawl(url_key)
            self.store_comment_to_db(comment_list, weibo_id)
        pass


####################################################### 解析模块 #######################################################################
# 解析 微博页面，返回： comment_list 一个页面里的所有comment
def page_parser_from_search_for_comment(page):
    comment_list = []
    out_soup = BeautifulSoup(page)
    
    div_c = out_soup.findAll('div', attrs={"class":"c"})
    for div_one in div_c:
        if 'id' in div_one.attrs and str(div_one.attrs['id']).startswith('C_'):
            from store_model import Single_comment
            
            uid = ''
            nickname = ''
            a_all = div_one.findAll('a')
            for a_one  in a_all:
                if 'href' in a_one.attrs and str(a_one.attrs['href']).startswith('/u/'):
                    uid = str(a_one.attrs['href'])[3:]
                    nickname = a_one.getText()
            
            auth = ''
            imag_all = div_one.findAll('img')
            for imag_one in imag_all:
                if 'alt' in imag_one.attrs and str(imag_one.attrs['alt']).startswith('V'):
                    auth = 'V' 
                if 'alt' in imag_one.attrs and str(imag_one.attrs['alt']).startswith(u'达人'):
                    auth = u'达人'
            
            content = ''
            span_ctt = div_one.find('span', attrs={"class":"ctt"})
            content = span_ctt.getText()
            
            praise_num = ''
            span_cc_all = div_one.findAll('span', attrs={"class":"cc"})
            for span_cc_one in span_cc_all:
                span_cc_one_text = str(span_cc_one.getText())
                if u'赞' in span_cc_one_text:
                    praise_num = span_cc_one_text[span_cc_one_text.find('['):]
            
            creat_time = ''
            span_ct = div_one.find('span', attrs={"class":"ct"})
            creat_time = span_ct.getText()
            
            single_comment_object = Single_comment(uid, nickname, auth, content, praise_num, creat_time)
            comment_list.append(single_comment_object)
    return comment_list   

# 判断是否：还没有人针对这条微博发表评论!
def no_one_commented(page):
    out_soup = BeautifulSoup(page)
    div_c_all = out_soup.findAll('div', attrs={"class":"c"})
    for div_c_one in div_c_all:
        if u"没有人针对这条微博" in div_c_one.getText():
            return True
    return False

##############################################################################################################################

# [http://weibo.cn/comment/CsfPu1hds?rl=1#cmtfrm][10]  "&page="+str(page_num)
# ## 读取文件，从文件中获取，微博id，weibo_url，评论数目
def read_file_fetch_something(weibo_file_name):
#     file_r = open("single_weibo_from_10_media.txt",'r')
    file_r = open(weibo_file_name, 'r')
    dict_url_id = {}
    
    for line in file_r.readlines():
        num_line = line
        weibo_id = line[line.find(':') + 1:line.find(']')]

        line = line[line.find('weibo_url'):]
        line = line[line.find(':') + 1:line.find(']')]
        weibo_loc = line[line.rfind('/') + 1:]
        str_first_part = "http://weibo.cn/comment/" + weibo_loc + "?rl=1&page="
        
        num_line = num_line[num_line.find('comment_num'):]
        comment_num = num_line[num_line.find(':') + 1:num_line.find(']')]
        
        comment_num_candidate = int(comment_num)
        if comment_num_candidate > 4000:
            comment_num = 4000
        else:
            comment_num = comment_num_candidate
        if comment_num < 5:
            continue
        yemian_num = comment_num / 10 if comment_num % 10 == 0 else comment_num / 10 + 1 
        
        for ye in xrange(1, yemian_num + 1):
            dict_url_id[str_first_part + str(ye)] = weibo_id
            
    return dict_url_id

# 从数据库中提取已抓取到的微博,并写入文件
def main_getobjects_from_db(filename):
    file_w = open(filename, 'a')
    count = 1
    for entry_s in Single_weibo_store.objects:
        str_s = '[' + "id:" + str(count) + ']'
        str_s += '[' + "uid:" + entry_s['uid'] + ']'
        str_s += '[' + "nickname:" + entry_s['nickname'] + ']'
        str_s += '[' + "content:" + entry_s['content'] + ']'
        str_s += '[' + "weibo_url:" + entry_s['weibo_url'] + ']'
        str_s += '[' + "praise_num:" + entry_s['praise_num'] + ']'
        str_s += '[' + "retweet_num:" + entry_s['retweet_num'] + ']'
        str_s += '[' + "comment_num:" + entry_s['comment_num'] + ']'
        str_s += '[' + "creat_time:" + entry_s['creat_time'] + ']'
        file_w.write(str_s + '\n')
        count += 1
    file_w.flush()
    file_w.close()

# 从数据库中提取已抓取到的微博评论,并写入文件
def main_get_comment_from_db():
    file_w = open("apple_phone_single_weibo_comment.txt", 'a')
    for i in xrange(12049, 30967):
        for entry_s in Single_comment_store.objects(weibo_id=str(i)):
            strs = '[' + "weibo_id:" + entry_s['weibo_id'] + ']'
            strs += '[' + "uid:" + entry_s['uid'] + ']'
            strs += '[' + "nickname:" + entry_s['nickname'] + ']'
            strs += '[' + "auth:" + entry_s['auth'] + ']'
            strs += '[' + "content:" + entry_s['content'] + ']'
            strs += '[' + "praise_num:" + entry_s['praise_num'] + ']'
            strs += '[' + "creat_time:" + entry_s['creat_time'] + ']'
            file_w.write(strs + '\n')
    file_w.flush()
    file_w.close()

# 从数据库中提取已抓取到的用户信息,并写入文件    
def main_get_userinfo_from_db():
    file_w = open("user_info_just_this_time.txt", 'a')
    for entry_s in UserInfo_store.objects:
        strs = '[uid_or_uname:' + entry_s['uid_or_uname'] + ']'
        
        nickname_can = entry_s['nickname']
        nickname = nickname_can
        if nickname_can.find(u"男") != -1:
            nickname = nickname_can[:nickname_can.find(u"男") - 1]
        if nickname_can.find(u"女") != -1:
            nickname = nickname_can[:nickname_can.find(u"女") - 1]
        
        strs += '[nickname:' + nickname + ']'
        strs += '[is_persion:' + entry_s['is_persion'] + ']'
        strs += '[verfied_or_not:' + entry_s['check_or_not'] + ']'    
        strs += '[fensi:' + entry_s['fensi'] + ']'  
        file_w.write(strs + '\n')  
    file_w.flush()
    file_w.close()
    
if __name__ == '__main__':
#     first = "single_weibo_from_10_media.txt"
#     main_get_comment_from_db()
#     second_name = "4_keyword_2015_1_1_to_2015_9_6.txt"
#     main_getobjects_from_db(second_name)

#     main_get_userinfo_from_db()
#     main_getobjects_from_db("apple_phone_single_weibo.txt")

    main_getobjects_from_db("一带一路.txt")
    
#     main_get_comment_from_db()

    pass
    
