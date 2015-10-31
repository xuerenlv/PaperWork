# -*- coding: utf-8 -*-

'''
Created on 2015-08-21

@author: xhj
'''
import requests
import StringIO
import gzip
import threading
from loginer import Loginer
import time
from my_log import WeiboSearchLog
import os
import traceback
from bs4 import BeautifulSoup

import sys  
import re
from Queue import Queue
import datetime
from store_model import Single_weibo_store
from mongoengine.errors import NotUniqueError
import random
reload(sys)  
sys.setdefaultencoding('utf8')   


class Crawler_with_proxy:
    
    def __init__(self,url,cookie,proxy):
        self.url = url;
        self.cookie = cookie;
        self.proxy = proxy;
    
    def get_page(self):
        proxies = {"http": self.proxy}
        
        user_agent_list = ["Mozilla/5.0 (Macintosh; Intel Mac OS X 10.10; rv:40.0) Gecko/20100101 Firefox/40.0",\
                           "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/21.0.1180.89 Safari/537.1",\
                           "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.84 Safari/535.11 SE 2.X MetaSr 1.0",\
                           "Mozilla/5.0 (Windows; U; Windows NT 6.1; zh-CN; rv:1.9.2.15) Gecko/20110303 Firefox/3.6.15",\
                           "Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US) AppleWebKit/534.16 (KHTML, like Gecko) Chrome/10.0.648.133 Safari/534.16",\
                           "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11"
                           "Mozilla/5.0 (X11; Linux i686; rv:8.0) Gecko/20100101 Firefox/8.0",\
                           "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; QQDownload 732; .NET4.0C; .NET4.0E)",\
                           "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; .NET4.0E)",\
                           "Mozilla/5.0 (X11; U; Linux x86_64; zh-CN; rv:1.9.2.10) Gecko/20100922 Ubuntu/10.10 (maverick) Firefox/3.6.10",\
                           "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:2.0b13pre) Gecko/20110307 Firefox/4.0b13pre"]
        
        HTTP_HEADERS= {'User-Agent':'Mozilla/5.0 (X11; Linux i686; rv:8.0) Gecko/20100101 Firefox/8.0','Accept-encoding':'gzip'}
        HTTP_HEADERS['User-Agent'] = user_agent_list[int(random.random()*len(user_agent_list))]
        reponse_raw = requests.get(self.url,cookies=self.cookie,proxies=proxies,headers=HTTP_HEADERS)
        if reponse_raw.headers['content-type'] == 'gzip':
            buf = StringIO(reponse_raw.text)
            f = gzip.GzipFile(fileobj=buf)
            page = f.read()
            return page
        else:
            return reponse_raw.text
    
    def get_page_with_form(self,data):
        proxies = {"http": self.proxy}
        HTTP_HEADERS= {'User-Agent':'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.152 Safari/537.36','Accept-encoding':'gzip','Content-Type':'application/x-www-form-urlencoded','Referer':'http://weibo.cn/search/mblog/?keyword=&advanced=mblog&rl=0&f=s'}
#         print '1'
        #,proxies=proxies
        #,cookies=self.cookie,headers=HTTP_HEADERS
        reponse_raw = requests.post(self.url,data,cookies=self.cookie,proxies=proxies)
#         print "2"
        if reponse_raw.headers['content-type'] == 'gzip':
            buf = StringIO(reponse_raw.text)
            f = gzip.GzipFile(fileobj=buf)
            page = f.read()
            return page
        else:
            return reponse_raw.text


# 实时抓取微博，需要关键词
class crawl_real_time_with_keyword(threading.Thread):
    
    def __init__(self,keyword,thread_name='crawl_real_time_with_keyword'):
        threading.Thread.__init__(self)
        self.name = thread_name
        self.keyword = keyword
        self.data = {}
    
    def crawl(self):
        # 实时且原创的微博
        self.data['advancedfilter']= '1'
        self.data['keyword'] =  self.keyword
        self.data['hasori'] =  '1' 
#         self.data['nick'] =  '' 
#         self.data['starttime'] =  '' 
#         self.data['endtime'] =  '' 
        self.data['sort'] =  'time' 
        self.data['smblog'] =  '搜索' 
        url = 'http://weibo.cn/search/'
        
        loginer = Loginer()
        cookie = loginer.get_cookie();
        proxy = loginer.get_proxy();
        craw_object = Crawler_with_proxy(url,cookie,proxy)
        
        weibo_list = []
        try:
            page = craw_object.get_page_with_form(self.data)
            weibo_list = page_parser_from_search(page)
        except :
            print traceback.format_exc()
            loginer.del_proxy()
            WeiboSearchLog().get_scheduler_logger().warning(self.name+" proxy exception , change proxy !")
            time.sleep(int(random.random()*10))
            return self.crawl()
        
        if len(weibo_list) == 0:
            loginer.del_proxy()
            WeiboSearchLog().get_scheduler_logger().warning(self.name+" get nothing, change proxy !")
            time.sleep(int(random.random()*10))
            return self.crawl()
        else:
            return weibo_list
    
    # 第一个版本，将微博存储到文件中
    def store_weibo(self,weibo_list):    
        file_op = open(("./data/real_time_weibo_"+str(self.keyword)+'.txt'),'a')
        file_op.write('\n')
        for weibo in weibo_list:
            file_op.write('\n' + weibo.to_string())
        file_op.flush()
        file_op.close()
    
    def run(self):
        while True:
            WeiboSearchLog().get_scheduler_logger().info(self.name+" start to crawl !")
            weibo_list = self.crawl()
            self.store_weibo(weibo_list)
            WeiboSearchLog().get_scheduler_logger().info(self.name+" crawl success,time to sleep !")
            time.sleep(20)
            

# 抓取在特定时间段的微博
# 20110101 格式，每天抓取100个页面，每个页面10条
# 香港矛盾20130821&endtime=20130821
#  >>> import datetime
#  >>> d1 = datetime.datetime(2005, 2, 16)
#  >>> d2 = datetime.datetime(2004, 12, 31)
class crawl_set_time_with_keyword(threading.Thread):
    del_proxy_lock = threading.Lock()
    
    # start_datetime  end_datetime 为 datetime 类型
    def __init__(self,keyword,start_datetime,end_datetime,thread_name='crawl_set_time_with_keyword'):
        threading.Thread.__init__(self)
        self.name = thread_name
        self.keyword = keyword
        self.start_time = start_datetime
        self.end_time = end_datetime
        self.url_queue = Queue()
    
    # 把每一天的第一个页面URL加入到队列中
    def init_url_queue(self):
        while self.start_time < self.end_time:
            start_time_str = datetime_to_str(self.start_time)
            self.start_time=self.start_time+datetime.timedelta(days=20)
            end_time_str = datetime_to_str(self.start_time)
            url = 'http://weibo.cn/search/mblog?hideSearchFrame=&keyword='+self.keyword+'&advancedfilter=1&hasori=1&starttime='+start_time_str+'&endtime='+end_time_str+"&sort=time&page=1"
            self.url_queue.put(url)
            pass
        pass
    
    # 通过第一天抓的页面，分析出的总条数，填充其后的页面，最多100个页面
    # total_num:共463327821条
    def put_second_and_more_url_queue(self,total_num,first_page_url):
        int_total_num = int(total_num[1:-1])
        
        total_page = 0;
        if int_total_num >= 1000:
            total_page = 100
        else:
            total_page = int_total_num/10
            
        for i in range(total_page):
            if i > 1:
                url = first_page_url[0:-1]+str(i)
                self.url_queue.put(url)
        pass
    
    # 抓取并解析页面
    def crawl(self,url,is_again=True):
        loginer = Loginer()
        cookie = loginer.get_cookie()
        proxy = loginer.get_proxy()
        craw_object = Crawler_with_proxy(url,cookie,proxy)
        
        WeiboSearchLog().get_scheduler_logger().info(self.name+" start to crawl ! "+url)
        
        weibo_list = []
        try:
            page  = craw_object.get_page()
            weibo_list = page_parser_from_search(page)
        except:
            print traceback.format_exc()
            crawl_set_time_with_keyword.del_proxy_lock.acquire()
            if proxy == loginer.get_proxy():
                loginer.del_proxy()
                WeiboSearchLog().get_scheduler_logger().warning(self.name+" proxy exception , change proxy !")
            crawl_set_time_with_keyword.del_proxy_lock.release()
            if is_again:
                return self.crawl(url,is_again=False)
            else:
                return weibo_list
        
        
        if len(weibo_list) == 0:
            if zero_aviable_check_validity(page):
                WeiboSearchLog().get_scheduler_logger().info(self.name +" get nothing, sina does not have ! "+url)
                return weibo_list
            if weibo_guangchang_forbidden(page):
                WeiboSearchLog().get_scheduler_logger().info(self.name +" get nothing, forbidden ! ! "+url)
            crawl_set_time_with_keyword.del_proxy_lock.acquire()
            if proxy == loginer.get_proxy():
                loginer.del_proxy()
                WeiboSearchLog().get_scheduler_logger().warning(self.name+" get nothing, change proxy ! "+url)
            crawl_set_time_with_keyword.del_proxy_lock.release()
            if is_again:
                return self.crawl(url,is_again=False)
            else:
                return weibo_list
            
        else:
            if int(url[url.rfind('=')+1:]) == 1:
                total_num = weibo_list[0].all_weibo_num
                self.put_second_and_more_url_queue(total_num,url)
            WeiboSearchLog().get_scheduler_logger().info(self.name+" crawl success! "+url)
            return weibo_list
    
    # 第一个版本，将微博存储到文件中
    def store_weibo(self,weibo_list):    
        file_op = open(("./data/set_time_weibo_"+str(self.name)+'.txt'),'a')
        file_op.write('\n')
        for weibo in weibo_list:
            file_op.write('\n' + weibo.to_string())
        file_op.flush()
        file_op.close()
        
    # 第二个版本，将微博存储到数据库中
    def store_weibo_to_db(self,weibo_list):
        for weibo in weibo_list:
            unique_single = Single_weibo_store(uid=weibo.uid,nickname=weibo.nickname,is_auth=weibo.is_auth,user_url=weibo.user_url,weibo_url=weibo.weibo_url,content=weibo.content,praise_num=weibo.praise_num,retweet_num=weibo.retweet_num,comment_num=weibo.comment_num,creat_time=weibo.creat_time,all_weibo_num=weibo.all_weibo_num)
            try:
                unique_single.save()
            except NotUniqueError:
                pass
            except:
                WeiboSearchLog().get_scheduler_logger().info(self.name+" insert to database, something wrong !")
                pass
        WeiboSearchLog().get_scheduler_logger().info(self.name+" insert to database, success !")
        pass
    
    def run(self):
        self.init_url_queue()
        while not self.url_queue.empty():
            url = self.url_queue.get()
            weibo_list = self.crawl(url)
#             self.store_weibo(weibo_list)
            self.store_weibo_to_db(weibo_list)
        pass
        

# 抓取一个特定用户的，关于keyword的微博
class crawl_set_time_with_keyword_and_nickname(threading.Thread):
    
    def __init__(self,keyword,start_datetime,end_datetime,nickname,thread_name='crawl_set_time_with_keyword_and_many_nickname'):
        threading.Thread.__init__(self)
        self.name = thread_name
        self.nickname = nickname
        self.keyword = keyword
        self.start_time = start_datetime
        self.end_time = end_datetime

        self.url_queue = Queue()
        self.second_url_queue = Queue() 
        pass
    
    def init_url_queue(self):
        start_time_str = datetime_to_str(self.start_time)
        end_time_str = datetime_to_str(self.end_time)
        url = "http://weibo.cn/search/mblog?hideSearchFrame=&keyword="+self.keyword+"&advancedfilter=1&hasori=1&nick="+self.nickname+"&starttime="+start_time_str+"&endtime="+end_time_str+"&sort=time&hasv=1&page=1"
        self.url_queue.put(url)
        pass
    
    # 通过第一天抓的页面，分析出的总条数，填充其后的页面，最多100个页面
    # total_num:共463327821条
    def put_second_and_more_url_queue(self,total_num,first_page_url):
        int_total_num = int(total_num[1:-1])
        
        total_page = 0;
        if int_total_num >= 1000:
            total_page = 100
        else:
            total_page = int_total_num/10
            
        for i in range(total_page):
            if i > 1:
                url = first_page_url[0:-1]+str(i)
                self.url_queue.put(url)
        pass
    
    # 抓取并解析页面
    def crawl(self,url,is_again=True):
        loginer = Loginer()
        cookie = loginer.get_cookie()
        proxy = loginer.get_proxy()
        craw_object = Crawler_with_proxy(url,cookie,proxy)
        
        WeiboSearchLog().get_scheduler_logger().info(self.name+" start to crawl ! "+url)
        
        weibo_list = []
        try:
            page  = craw_object.get_page()
            weibo_list = page_parser_from_search(page)
        except:
            print traceback.format_exc()
            crawl_set_time_with_keyword.del_proxy_lock.acquire()
            if proxy == loginer.get_proxy():
                loginer.del_proxy()
                WeiboSearchLog().get_scheduler_logger().warning(self.name+" proxy exception , change proxy !")
            crawl_set_time_with_keyword.del_proxy_lock.release()
            if is_again:
                return self.crawl(url,is_again=False)
            else:
                self.second_url_queue.put(url)
                return weibo_list
        
        
        if len(weibo_list) == 0:
            if zero_aviable_check_validity(page):
                WeiboSearchLog().get_scheduler_logger().info(self.name +" get nothing, sina does not have ! "+url)
                return weibo_list
            if weibo_guangchang_forbidden(page):
                WeiboSearchLog().get_scheduler_logger().info(self.name +" get nothing, forbidden ! ! "+url)
                
            crawl_set_time_with_keyword.del_proxy_lock.acquire()
            if proxy == loginer.get_proxy():
                loginer.del_proxy()
                WeiboSearchLog().get_scheduler_logger().warning(self.name+" get nothing, change proxy ! "+url)
            crawl_set_time_with_keyword.del_proxy_lock.release()
            if is_again:
                return self.crawl(url,is_again=False)
            else:
                self.second_url_queue.put(url)
                return weibo_list
            
        else:
            if int(url[url.rfind('=')+1:]) == 1:
                total_num = weibo_list[0].all_weibo_num
                self.put_second_and_more_url_queue(total_num,url)
            WeiboSearchLog().get_scheduler_logger().info(self.name+" crawl success! "+url)
            return weibo_list
    
    # 将微博存储到数据库中
    def store_weibo_to_db(self,weibo_list):
        for weibo in weibo_list:
            unique_single = Single_weibo_store(uid=weibo.uid,nickname=weibo.nickname,is_auth=weibo.is_auth,user_url=weibo.user_url,weibo_url=weibo.weibo_url,content=weibo.content,praise_num=weibo.praise_num,retweet_num=weibo.retweet_num,comment_num=weibo.comment_num,creat_time=weibo.creat_time,all_weibo_num=weibo.all_weibo_num)
            try:
                unique_single.save()
            except NotUniqueError:
                pass
            except:
                WeiboSearchLog().get_scheduler_logger().info(self.name+" insert to database, something wrong !")
                pass
        WeiboSearchLog().get_scheduler_logger().info(self.name+" insert to database, success !")
        pass
    
    def run(self):
        self.init_url_queue()
        while not self.url_queue.empty() or not self.second_url_queue.empty():
            url = ""
            if not self.url_queue.empty():
                url = self.url_queue.get()
            else:
                url = self.second_url_queue.get()
            weibo_list = self.crawl(url)
            self.store_weibo_to_db(weibo_list)
        pass
    

## 抓取所有用户，同一个关键词的
# 这里的keyword是 hashtag
class crawl_set_time_with_only_keyword(threading.Thread):  
    
    def __init__(self,keyword,start_datetime,end_datetime,thread_name='crawl_set_time_with_only_keyword'):
        threading.Thread.__init__(self)
        self.name = thread_name
        self.keyword = keyword
        self.start_time = start_datetime
        self.end_time = end_datetime

        self.url_queue = Queue()
        self.second_url_queue = Queue() 
        pass
    
    def init_url_queue(self):
        start_time_str = datetime_to_str(self.start_time)
        end_time_str = datetime_to_str(self.end_time)
        # %23 hashtag
        url = "http://weibo.cn/search/mblog?hideSearchFrame=&keyword=%23"+self.keyword+"&advancedfilter=1&hasori=1&starttime="+start_time_str+"&endtime="+end_time_str+"&sort=time&page=1"
        self.url_queue.put(url)
        pass
    
    # 通过第一天抓的页面，分析出的总条数，填充其后的页面，最多100个页面
    # total_num:共463327821条
    def put_second_and_more_url_queue(self,total_num,first_page_url):
        int_total_num = int(total_num[1:-1])
        
        total_page = 0;
        if int_total_num >= 1000:
            total_page = 100
        else:
            total_page = int_total_num/10
            
        for i in range(total_page):
            if i > 1:
                url = first_page_url[0:-1]+str(i)
                self.url_queue.put(url)
        pass
    
    # 抓取并解析页面
    def crawl(self,url,is_again=True):
        loginer = Loginer()
        cookie = loginer.get_cookie()
        proxy = loginer.get_proxy()
        craw_object = Crawler_with_proxy(url,cookie,proxy)
        
        WeiboSearchLog().get_scheduler_logger().info(self.name+" start to crawl ! "+url)
        
        weibo_list = []
        try:
            page  = craw_object.get_page()
            weibo_list = page_parser_from_search(page)
        except:
            print traceback.format_exc()
            crawl_set_time_with_keyword.del_proxy_lock.acquire()
            if proxy == loginer.get_proxy():
                loginer.del_proxy()
                WeiboSearchLog().get_scheduler_logger().warning(self.name+" proxy exception , change proxy !")
            crawl_set_time_with_keyword.del_proxy_lock.release()
            if is_again:
                return self.crawl(url,is_again=False)
            else:
                self.second_url_queue.put(url)
                return weibo_list
        
        
        if len(weibo_list) == 0:
            if zero_aviable_check_validity(page):
                WeiboSearchLog().get_scheduler_logger().info(self.name +" get nothing, sina does not have ! "+url)
                return weibo_list
            if weibo_guangchang_forbidden(page):
                WeiboSearchLog().get_scheduler_logger().info(self.name +" get nothing, forbidden ! ! "+url)
                
            crawl_set_time_with_keyword.del_proxy_lock.acquire()
            if proxy == loginer.get_proxy():
                loginer.del_proxy()
                WeiboSearchLog().get_scheduler_logger().warning(self.name+" get nothing, change proxy ! "+url)
            crawl_set_time_with_keyword.del_proxy_lock.release()
            if is_again:
                return self.crawl(url,is_again=False)
            else:
                self.second_url_queue.put(url)
                return weibo_list
            
        else:
            if int(url[url.rfind('=')+1:]) == 1:
                total_num = weibo_list[0].all_weibo_num
                self.put_second_and_more_url_queue(total_num,url)
            WeiboSearchLog().get_scheduler_logger().info(self.name+" crawl success! "+url)
            return weibo_list
    
    # 将微博存储到数据库中
    def store_weibo_to_db(self,weibo_list):
        for weibo in weibo_list:
            unique_single = Single_weibo_store(uid=weibo.uid,nickname=weibo.nickname,is_auth=weibo.is_auth,user_url=weibo.user_url,weibo_url=weibo.weibo_url,content=weibo.content,praise_num=weibo.praise_num,retweet_num=weibo.retweet_num,comment_num=weibo.comment_num,creat_time=weibo.creat_time,all_weibo_num=weibo.all_weibo_num)
            try:
                unique_single.save()
            except NotUniqueError:
                pass
            except:
                WeiboSearchLog().get_scheduler_logger().info(self.name+" insert to database, something wrong !")
                pass
        WeiboSearchLog().get_scheduler_logger().info(self.name+" insert to database, success !")
        pass
    
    def run(self):
        self.init_url_queue()
        while not self.url_queue.empty() or not self.second_url_queue.empty():
            url = ""
            if not self.url_queue.empty():
                url = self.url_queue.get()
            else:
                url = self.second_url_queue.get()
            weibo_list = self.crawl(url)
            self.store_weibo_to_db(weibo_list)
        pass  
    
##########################################################################  工具相关    #########################################################################################################################
# datetime.datetime(2010, 1, 1)  ---> 20100101
def datetime_to_str(start_time):
    year = start_time.year
    month = start_time.month
    day = start_time.day
    
    str_year = str(year)
    str_month = ''
    str_day = ''
    if month<10:
        str_month = '0' + str(month)
    else:
        str_month = str(month)
    if day<10:
        str_day = '0' + str(day)
    else:
        str_day = str(day)
    
    str_re = str_year+str_month+str_day
    return str_re


        
##########################################################################  页面解析相关    #########################################################################################################################

# 检查页面是否为：（抱歉，未找到keyword相关结果。）
def zero_aviable_check_validity(page):
    out_soup = BeautifulSoup(page)
    str_pre = u"抱歉，未找到"
    contain_wrong_div_list = out_soup.findAll('div', attrs={'class':'c'})
    for div_one in contain_wrong_div_list:
        if str_pre in div_one.getText():
            return True
    return False

# 出现“微博广场”，表明被挡
def weibo_guangchang_forbidden(page):
    out_soup = BeautifulSoup(page)
    str_pre = u"微博广场"
    if out_soup.title is None or str_pre in out_soup.title.getText():
        return True
    return False

#处理通过搜索返回的页面，返回一个存放SingleWeibo的list
#uid,nickname,is_auth,url,content,praise_num,retweet_num,comment_num,creat_time
def page_parser_from_search(page):
    weibo_list = []
    
    out_soup = BeautifulSoup(page)
    contain_wrong_div_list = out_soup.findAll('div', attrs={'class':'c'})
    all_weibo_num = ''
    for div_one in contain_wrong_div_list:
        
        # 获取 总条数
        all_weibo_num_span = div_one.find('span', attrs={'class':'cmt'}) 
        if not all_weibo_num_span is None:
            all_weibo_num = all_weibo_num_span.getText()
        
        # 获取单个微博信息
        if 'id' in div_one.attrs and str(div_one.attrs['id']).startswith('M_'):
            from store_model import SingleWeibo
            #获取用户的个人主页URL，uid
            weibo_signal = str(div_one.attrs['id'])[str(div_one.attrs['id']).find('M_')+2:]
            opt_user_url = (div_one.find('a', attrs={'class':'nk'})).attrs['href']
            nickname = div_one.find('a', attrs={'class':'nk'}).getText()
            uid = ''            
            user_url = ''
            if str(opt_user_url).find('/u/') > 0:
                user_url = 'http://weibo.com/u'+opt_user_url[str(opt_user_url).rfind('/'):]
                uid = opt_user_url[str(opt_user_url).rfind('/')+1:]
            else:
                user_url = 'http://weibo.com'+opt_user_url[str(opt_user_url).rfind('/'):]
                comment_url = str((div_one.find('a', attrs={'class':'cc'})).attrs['href'])
                uid = comment_url[comment_url.find('uid=')+4:comment_url.find('&')]
            weibo_url = "http://weibo.com/"+uid+'/'+weibo_signal
            content = (div_one.find('span', attrs={'class':'ctt'}).getText())[1:]
            
            is_auth = ''   
            if div_one.find('img', attrs={'alt':'V'}) is None:
                is_auth = '0'
            else:
                is_auth = '1'
            #  uid nickname is_auth user_url weibo_url content  已获取
            
            praise_num = div_one.find('a',href=re.compile("attitude")).getText()[2:-1]
            retweet_num = div_one.find('a',href=re.compile("repost")).getText()[3:-1]
            comment_num = div_one.find('a',href=re.compile("comment")).getText()[3:-1]
            creat_time = div_one.find('span', attrs={'class':'ct'}).getText()
            # praise_num,retweet_num,comment_num,creat_time 已获取
            
            signal_weibo_object = SingleWeibo(uid,nickname,is_auth,user_url,weibo_url,content,praise_num,retweet_num,comment_num,creat_time,all_weibo_num)
            weibo_list.append(signal_weibo_object)
    
    return weibo_list



