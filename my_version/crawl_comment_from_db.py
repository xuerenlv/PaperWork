# -*- coding: utf-8 -*-
'''
Created on Sep 2, 2015

@author: xhj
'''
from store_model import Single_weibo_store, Single_comment, Single_comment_store, \
    UserInfo_store, Single_weibo_with_more_info_store, Weibo_url_to_Comment_url
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
    
    def __init__(self, list_contains_set_weibourl_and_commenturl, thread_name='crawl_comment'):
        threading.Thread.__init__(self)
        self.name = thread_name
        self.list_contains_set_weibourl_and_commenturl = list_contains_set_weibourl_and_commenturl
    
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
    def store_comment_to_db(self, comment_list, weibo_url):
        for comment in comment_list:
            unique_single = Single_comment_store(weibo_id=weibo_url, uid=comment.uid, nickname=comment.nickname, auth=comment.auth, content=comment.content, praise_num=comment.praise_num, creat_time=comment.creat_time)
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
        for weibo_url, comment_url in self.list_contains_set_weibourl_and_commenturl:            
            comment_list = self.crawl(comment_url)
            
            # 如果抓取的 comment 的数目 不为 0 ，则可以从数据库中删除之
            if len(comment_list) > 0:
                WeiboSearchLog().get_scheduler_logger().info("done----" + str(comment_url))
                Weibo_url_to_Comment_url.objects(comment_url=str(comment_url)).delete()
                pass
            
            self.store_comment_to_db(comment_list, weibo_url)
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
