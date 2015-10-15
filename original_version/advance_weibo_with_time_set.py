#encoding=utf8
'''
Created on 2014��5��5��

@author: cc
'''

import sys
from advance_weibo_frame import COMMENT_PER_PAGE_NUMBER,RETWEET_PER_PAGE_NUMBER
from common_conf_manager import MAX_CRAWL_COMMENT_PAGE_NUMBER,MAX_CRAWL_RETWEET_PAGE_NUMBER
from storage_manager import SingleWeibo

reload(sys)
sys.setdefaultencoding('utf8')  # @UndefinedVariable

import os
import traceback
import random
import time
import  datetime
try:
    import logging.config
    
    from storage_manager import connect_db
    from loginer import get_loginer
    from get_valid_ip import proxy_ip_manager
    
    from advance_keyword_real_weibo import get_url_wrapper_generator as real_generator,\
        AdvKeywordRealWeiboURLWrapper,\
        AdvKeywordRealWeiboCommentURLWrapper,\
        AdvKeywordRealWeiboParser,\
        AdvKeywordRealWeiboCommentParser,\
        AdvKeywordRealWeiboCrawler,\
        AdvKeywordRealWeiboCommentCrawler,\
        AdvKeywordRealWeiboRetweetURLWrapper,\
        AdvKeywordRealWeiboRetweetParser,\
        AdvKeywordRealWeiboRetweetCrawler
        
    from advance_keyword_hot_weibo import get_url_wrapper_generator as hot_generator,\
        AdvKeywordHotWeiboURLWrapper,\
        AdvKeywordHotWeiboCommentURLWrapper,\
        AdvKeywordHotWeiboParser,\
        AdvKeywordHotWeiboCommentParser,\
        AdvKeywordHotWeiboCrawler,\
        AdvKeywordHotWeiboCommentCrawler
        
    from common_conf_manager import MAX_RELOGIN_TRIAL_NUMBER,\
        GET_INTERVAL_SECONDS,\
        PROXY_GET_INTERVAL_SECONDS,\
        USER_INFOR_MANAGER,\
        SLEEP_SECONDS_WHEN_GET_PROXY_IP_FAILED,\
        TOTAL_USER_COUNT,\
        NORMAL_USER_COUNT, \
        OPEN_PROXY_CRAWL,\
        OPEN_NORMAL_CRAWL,\
        COOKIE_FILE_NAME
    
except:
    
    s = traceback.format_exc()
    
    print s

loginer = get_loginer()
if not os.path.exists('logs/'):
    os.mkdir('logs')
if not os.path.exists('Cookies/'):
    os.mkdir('Cookies')
curpath=os.path.normpath( os.path.join( os.getcwd(), os.path.dirname(__file__) ) ) 
logging.config.fileConfig(curpath+'/runtime_infor_log.conf')
scheduler_logger = logging.getLogger("schedulerLog")



try:
    from Queue import Queue
    import threading
except:
    s = traceback.format_exc()
    print s 

normal_cookie_queue = Queue()
class NormalCookieManager(threading.Thread):
    cookie_index = 0
    
    def __init__(self, thread_name="normal cookie manager"):
        
        threading.Thread.__init__(self)
        
        self.name = thread_name
        self.stop_me = False
    
    def run(self):
        global normal_cookie_queue
        
        while not self.stop_me:
            if normal_cookie_queue.qsize() < TOTAL_USER_COUNT:
                NormalCookieManager.cookie_index = (NormalCookieManager.cookie_index + 1) % NORMAL_USER_COUNT
                
                cur_index = NormalCookieManager.cookie_index
                new_username = USER_INFOR_MANAGER[cur_index]['username']
                new_password = USER_INFOR_MANAGER[cur_index]['password']
                new_cookie_file = COOKIE_FILE_NAME + str(cur_index + 1)
                
                normal_cookie_queue.put([str(new_username), str(new_password), str(new_cookie_file)])
            
            sleep_seconds = random.uniform(GET_INTERVAL_SECONDS - 10, GET_INTERVAL_SECONDS)
            time.sleep(sleep_seconds)
    
    def stop_me(self):
        self.stop_me = True
        
PROXY_USER_COUNT = TOTAL_USER_COUNT - NORMAL_USER_COUNT
proxy_cookie_queue = Queue()
class ProxyCookieManager(threading.Thread):
    cookie_index = 0
    
    def __init__(self, thread_name="proxy cookie manager"):
        
        threading.Thread.__init__(self)
        
        self.name = thread_name
        self.stop_me = False
        
    def run(self):
        global proxy_cookie_queue
        
        while not self.stop_me:
            proxy_ip = proxy_ip_manager.get_ip()
            
            if proxy_ip == "":
                time.sleep(SLEEP_SECONDS_WHEN_GET_PROXY_IP_FAILED)
                continue
            
            scheduler_logger.debug("before set pcq's size: " + str(proxy_cookie_queue.qsize()))
            if proxy_ip_manager.has_enough_ips() and proxy_cookie_queue.qsize() < PROXY_USER_COUNT:
                ProxyCookieManager.cookie_index = (ProxyCookieManager.cookie_index + 1) % PROXY_USER_COUNT
                
                cur_index = ProxyCookieManager.cookie_index + NORMAL_USER_COUNT
                new_username = USER_INFOR_MANAGER[cur_index]['username']
                new_password = USER_INFOR_MANAGER[cur_index]['password']
                new_cookie_file = COOKIE_FILE_NAME + str(cur_index + 1)
                
                proxy_cookie_queue.put([str(new_username), str(new_password), str(new_cookie_file), str(proxy_ip)])
                scheduler_logger.debug("after set pcq's size: " + str(proxy_cookie_queue.qsize()))
            
#             interval = 0
#             if proxy_ip_manager.get_ip_number() == 0 or PROXY_USER_COUNT == 0:
#                 interval = SLEEP_SECONDS_WHEN_GET_PROXY_IP_FAILED
#             elif proxy_ip_manager.get_ip_number() < PROXY_USER_COUNT:
#                 interval = GET_INTERVAL_SECONDS / ((float)(proxy_ip_manager.get_ip_number()))
#             else:
#                 interval =  GET_INTERVAL_SECONDS / ((float)(PROXY_USER_COUNT))
            
            sleep_seconds = random.uniform(PROXY_GET_INTERVAL_SECONDS-1, PROXY_GET_INTERVAL_SECONDS)
            time.sleep(sleep_seconds)
    
    def stop_me(self):
        self.stop_me = True
        
#########################################################################################################################
#####################The following are involving with normal and proxy cookie get and execute crawling###################
loginer = get_loginer()
class NormalCrawlExecuter(threading.Thread):
    
    def __init__(self, url_wrapper_list_manager, thread_name='normal crawl executer'):
        
        threading.Thread.__init__(self)
        self.name = thread_name
        self.url_wrapper_list_manager = url_wrapper_list_manager
        
    def run(self):
        url_wrapper_list_manager = self.url_wrapper_list_manager
        global normal_cookie_queue
        
        while True:
            [cur_username, cur_password, cur_cookie_file] = normal_cookie_queue.get()
            
            if url_wrapper_list_manager.is_empty():
                break
            
            new_url_wrapper = url_wrapper_list_manager.get_next_priority_url_wrapper()
                
            scheduler_logger.info("In normal crawling: {time: \"%s\", cur_url_size: \"%s\", cur_url: \"%s\", url: \"%s\"}" % (str(datetime.datetime.now()),\
                                                                                        str(len(url_wrapper_list_manager.url_wrapper_list)),\
                                                                                        new_url_wrapper.url_wrapper.tostring(),\
                                                                                        new_url_wrapper.url_wrapper.to_url()))
            scheduler_logger.info("url_wrapper_list's url_index is: " + str(url_wrapper_list_manager.url_index) + " size: " + str(len(url_wrapper_list_manager.url_wrapper_list)))
            
            new_crawler = get_crawler_by_url_wrapper(new_url_wrapper.url_wrapper)
            scheduler_logger.debug("username: " + cur_username + " password: " + cur_password + " cookie_file: " + cur_cookie_file)
            try:
                scheduler_logger.debug("before execute_crawl")
                [crawl_feed_count, new_feed_count,increment] = self.execute_crawl(new_crawler, cur_username, cur_password, cur_cookie_file)
                scheduler_logger.debug("after execute_crawl")
                
                #modify the url_wrapper's priority according to the actual crawling result
#                 new_url_wrapper.modify_counter(crawl_feed_count, new_feed_count, increment)
#                if crawl_feed_count == 0 and not page_is_validity:
#                    url_wrapper_list_manager.add_priority_url_wrapper(new_url_wrapper)
                scheduler_logger.info("{crawl_feed_count: " + str(crawl_feed_count) +", new_feed_count: " + str(new_feed_count) + ", increment:" +str(increment)+ "}")
            except:
                s = traceback.format_exc()
                print s
                pass
            
        scheduler_logger.info("normal executor main recycle terminates!")
        
    def execute_crawl(self, crawler, cur_username, cur_password, cur_cookie_file):

        crawl_feed_count = 0
        new_feed_count = 0
        increment = 0
        
        if loginer.login(str(cur_username), str(cur_password), str(cur_cookie_file)):
            scheduler_logger.info("normal login succeed and cookie file is: " + cur_cookie_file)
            [page_is_validity, new_url_list, crawl_feed_count, new_feed_count,increment ] = crawler.crawl()

            print 'page_is_validity',page_is_validity
                
            #for re-get page
            if not page_is_validity:
                    
                relogin_num = MAX_RELOGIN_TRIAL_NUMBER
                    
                while relogin_num > 0:
                        
                    sleep_when_relogin(GET_INTERVAL_SECONDS - 5)

                    if loginer.relogin(str(cur_username), str(cur_password), str(cur_cookie_file)):
                        [page_is_validity, new_url_list, crawl_feed_count, new_feed_count,increment ] = crawler.crawl()
                        print 'page_is_validity',page_is_validity
                        
                        break
                        
                    relogin_num -= 1
                
            #doubt
            if not page_is_validity:
                    
                return [crawl_feed_count, new_feed_count,increment ]
                
            for new_url in new_url_list:
                    
                self.url_wrapper_list_manager.add_url_wrapper(new_url)
            
        return [crawl_feed_count, new_feed_count,increment ]

 
class ProxyCrawlExecuter(threading.Thread):
    
    def __init__(self, url_wrapper_list_manager, thread_name='proxy crawl executer'):
        threading.Thread.__init__(self)
        self.name = thread_name
        self.url_wrapper_list_manager = url_wrapper_list_manager
        
    def run(self):
        url_wrapper_list_manager = self.url_wrapper_list_manager
        global proxy_cookie_queue
        
        while True:
            
            scheduler_logger.debug("before get pcq's size: " + str(proxy_cookie_queue.qsize()))
                    
            [cur_username, cur_password, cur_cookie_file, proxy_IP] = proxy_cookie_queue.get()
                
            scheduler_logger.debug("current proxy_IP is: " + proxy_IP)
            
            scheduler_logger.debug("after get pcq's size: " + str(proxy_cookie_queue.qsize()))
            
            if url_wrapper_list_manager.is_empty():
                break 
            
            new_url_wrapper = url_wrapper_list_manager.get_next_priority_url_wrapper()
        
            scheduler_logger.info("In proxy crawling: {time: \"%s\", cur_url_size: \"%s\", cur_url: \"%s\", url: \"%s\"}" % (str(datetime.datetime.now()),\
                                                                                        str(len(url_wrapper_list_manager.url_wrapper_list)),\
                                                                                        new_url_wrapper.url_wrapper.tostring(),\
                                                                                        new_url_wrapper.url_wrapper.to_url()))
            scheduler_logger.info("url_wrapper_list's url_index is: " + str(url_wrapper_list_manager.url_index) + " size: " + str(len(url_wrapper_list_manager.url_wrapper_list)))
                    
            new_crawler = get_crawler_by_url_wrapper(new_url_wrapper.url_wrapper, proxy_IP, True, cur_cookie_file)
            scheduler_logger.debug("username: " + cur_username + " password: " + cur_password + " cookie_file: " + cur_cookie_file)
            try:
                scheduler_logger.debug("before execute_crawl")
                [crawl_feed_count, new_feed_count, increment] = self.execute_crawl(new_crawler, cur_username, cur_password, cur_cookie_file)
                scheduler_logger.debug("after execute_crawl")
                    
#                 new_url_wrapper.modify_counter(crawl_feed_count, new_feed_count, increment)
#                if crawl_feed_count == 0 and not page_is_validity:
#                    url_wrapper_list_manager.add_priority_url_wrapper(new_url_wrapper)
                    
                scheduler_logger.info("{crawl_feed_count: " + str(crawl_feed_count) +", new_feed_count: " + str(new_feed_count) +", increment: "+str(increment)+"}")
            except:
                s = traceback.format_exc()
                    
                scheduler_logger.info(s)
                pass
        scheduler_logger.info("Proxy executor main recycle terminates!")
                    
    def execute_crawl(self, crawler, cur_username, cur_password, cur_cookie_file):
        
        crawl_feed_count = 0
        new_feed_count = 0
        increment = 0
        new_url_list = []
        
        if loginer.proxy_login(cur_username, cur_password, cur_cookie_file):
            scheduler_logger.info("proxy login succeed and cookie file is: " + cur_cookie_file)
            
            [page_is_validity, new_url_list, crawl_feed_count, new_feed_count, increment ] = crawler.crawl()
            
            scheduler_logger.info("after first crawl")
            #for re-get page
            print 'page_is_validity:' , page_is_validity

            if not page_is_validity:
                    
                relogin_num = MAX_RELOGIN_TRIAL_NUMBER
                    
                while relogin_num > 0:
                        
                    sleep_when_relogin(PROXY_GET_INTERVAL_SECONDS)

                    if loginer.relogin(cur_username, cur_password, cur_cookie_file):
                        
                        scheduler_logger.debug("before recrawl")
                        [page_is_validity, new_url_list, crawl_feed_count, new_feed_count, increment ] = crawler.crawl()
                        
                        print 'page_is_validity:' , page_is_validity
                        scheduler_logger.debug("after recrawl")
                        
                        break
                        
                    relogin_num -= 1
                
            if not page_is_validity:
                    
                return [crawl_feed_count, new_feed_count,increment ]
                
            for new_url in new_url_list:
                    
                self.url_wrapper_list_manager.add_url_wrapper(new_url)
            
        return [crawl_feed_count, new_feed_count,increment]
#########################################################################################################################
##########################The following are involving with url wrapper list management###################################
class PriorityUrlWrapper:
    _DEFAULT_PRIORITY = 1
    
    def __init__(self, url_wrapper):
        self.url_wrapper = url_wrapper
        self.cur_priority = PriorityUrlWrapper._DEFAULT_PRIORITY
        self.counter = self.cur_priority
    
#     def modify_counter(self, crawl_feed_count, new_feed_count, increment):
#         
# #         print "old cur_priority is: " + str(self.cur_priority) + " counter is: " + str(self.counter)
# #         print "modifying: crawl_feed_count is " + str(crawl_feed_count) + " and new_feed_count is " + str(new_feed_count)
#         if crawl_feed_count == 0:
#             self.counter = 1
#             return 
#         
#         if increment == crawl_feed_count:
#             self.cur_priority = PriorityUrlWrapper._DEFAULT_PRIORITY
#             self.counter = self.cur_priority
#             
#         elif increment < (crawl_feed_count)/2:
#             self.cur_priority += 1
#             self.counter = self.cur_priority
#         else:
#             if self.cur_priority <= PriorityUrlWrapper._DEFAULT_PRIORITY:
#                 self.cur_priority = PriorityUrlWrapper._DEFAULT_PRIORITY
#                 self.counter = self.cur_priority
#             else:
#                 self.cur_priority -= 1
#                 self.counter = self.cur_priority
wrapper_list_mutex = threading.Lock()
class UrlWrapperListManager(threading.Thread):
    url_wrapper_list = []
    real_url_wrapper_generator = real_generator()
    hot_url_wrapper_generator = hot_generator()
    url_index = 0
    
    def __init__(self, thread_name="url wrapper list manager"):
        threading.Thread.__init__(self)
        self.name = thread_name
    
    def add_url_wrapper(self, url_wrapper):
        global wrapper_list_mutex
        
        if wrapper_list_mutex.acquire():
            UrlWrapperListManager.url_wrapper_list.append(PriorityUrlWrapper(url_wrapper))
            wrapper_list_mutex.release()
            
    def add_priority_url_wrapper(self, url_wrapper):
        global wrapper_list_mutex
        
        if wrapper_list_mutex.acquire():
            UrlWrapperListManager.url_wrapper_list.append(url_wrapper)
            wrapper_list_mutex.release()
            
    def get_next_priority_url_wrapper(self):
        global wrapper_list_mutex
        
        url_wrapper = None
        
        if not UrlWrapperListManager.url_wrapper_list:
            return url_wrapper
        else:
            if wrapper_list_mutex.acquire():
                url_wrapper = UrlWrapperListManager.url_wrapper_list[0]
                UrlWrapperListManager.url_wrapper_list = UrlWrapperListManager.url_wrapper_list[1:]
                wrapper_list_mutex.release()
        
        return url_wrapper
    
    def is_empty(self):
        global wrapper_list_mutex
        
        result = False
        if wrapper_list_mutex.acquire():
            if len(UrlWrapperListManager.url_wrapper_list) == 0:
                result = True
            wrapper_list_mutex.release()
        
        return result
                 
def get_crawler_by_url_wrapper(url_wrapper, proxy_IP="", proxy_used=False, proxy_cookie_file=""):
    new_weibo_parser = None
    new_crawler = None
         
    if isinstance(url_wrapper, AdvKeywordRealWeiboURLWrapper):
        new_weibo_parser = AdvKeywordRealWeiboParser(url_wrapper)
        new_crawler = AdvKeywordRealWeiboCrawler(url_wrapper, new_weibo_parser, proxy_IP, proxy_used, proxy_cookie_file)
    elif isinstance(url_wrapper, AdvKeywordRealWeiboCommentURLWrapper):
        new_comment_parser = AdvKeywordRealWeiboCommentParser(url_wrapper)
        new_crawler = AdvKeywordRealWeiboCommentCrawler(url_wrapper, new_comment_parser, proxy_IP, proxy_used, proxy_cookie_file)
    elif isinstance(url_wrapper, AdvKeywordHotWeiboURLWrapper):
        new_weibo_parser = AdvKeywordHotWeiboParser(url_wrapper)
        new_crawler = AdvKeywordHotWeiboCrawler(url_wrapper, new_weibo_parser, proxy_IP, proxy_used, proxy_cookie_file)
    elif isinstance(url_wrapper, AdvKeywordHotWeiboCommentURLWrapper):
        new_comment_parser = AdvKeywordHotWeiboCommentParser(url_wrapper)
        new_crawler = AdvKeywordHotWeiboCommentCrawler(url_wrapper, new_comment_parser, proxy_IP, proxy_used, proxy_cookie_file)
    elif isinstance(url_wrapper,AdvKeywordRealWeiboRetweetURLWrapper):
        new_retweet_parser = AdvKeywordRealWeiboRetweetParser(url_wrapper)
        new_crawler = AdvKeywordRealWeiboRetweetCrawler(url_wrapper, new_retweet_parser, proxy_IP, proxy_used, proxy_cookie_file)
            
    return new_crawler

def sleep_when_relogin(sleep_seconds=3):
    scheduler_logger.info('--------------------------')
    scheduler_logger.info('relogin sleep time: ' + str(sleep_seconds))
    scheduler_logger.info('--------------------------')
    time.sleep(sleep_seconds)

    return sleep_seconds

#############################################################################################################################
def search_comments_by_weibos():
    threads = {}
    
    url_wrapper_list_manager = UrlWrapperListManager()
    
    weibo_count = 0
    for single_weibo in SingleWeibo.objects:  # @UndefinedVariable
        weibo_count += 1
        keyword = single_weibo.keyword[0]
        mid = single_weibo.mid
        n_comment = int(single_weibo.n_comment)
        uid = single_weibo.uid
        nickname = single_weibo.nickname
                    
        if int(n_comment) is not 0:
                        
            max_page_number = (int(n_comment / COMMENT_PER_PAGE_NUMBER))
                        
            if (n_comment % COMMENT_PER_PAGE_NUMBER) is not 0:
                max_page_number += 1
                            
            if MAX_CRAWL_COMMENT_PAGE_NUMBER < max_page_number:
                max_page_number = MAX_CRAWL_COMMENT_PAGE_NUMBER
                        
            for pagenum in range(1, max_page_number + 1):
                            
                new_wrapper = AdvKeywordRealWeiboCommentURLWrapper(keyword=keyword, mid=mid, page_num=str(pagenum), uid=uid, nickname=nickname)
                url_wrapper_list_manager.add_url_wrapper(new_wrapper)
    
    print "In searching comments by weibos and total weibo count is: " + str(weibo_count)
    
    threads['list'] = url_wrapper_list_manager
    if OPEN_NORMAL_CRAWL:
        threads['normal cookie manager'] = NormalCookieManager()
        threads['normal crawl executer'] = NormalCrawlExecuter(url_wrapper_list_manager=url_wrapper_list_manager)
    if OPEN_PROXY_CRAWL:
        threads['proxy ip manager'] = proxy_ip_manager
        threads['proxy cookie manager'] = ProxyCookieManager()
        threads['proxy crawl executer'] = ProxyCrawlExecuter(url_wrapper_list_manager=url_wrapper_list_manager)
     
    for thread in threads.values():
        scheduler_logger.info("thread " + thread.name + " start!")
#         print "thread " + thread.name + " start!"
        thread.start()


def search_retweets_by_weibos():
    threads = {}

    url_wrapper_list_manager = UrlWrapperListManager()
    
    weibo_count = 0
    for single_weibo in SingleWeibo.objects:
        weibo_count += 1
        keyword = single_weibo.keyword[0]
        mid = single_weibo.mid
        n_forward = single_weibo.n_forward
        uid = single_weibo.uid
        nickname = single_weibo.nickname
        
        if n_forward != 0:
            max_page_number = n_forward / RETWEET_PER_PAGE_NUMBER
            if n_forward%RETWEET_PER_PAGE_NUMBER != 0:
                max_page_number += 1
            if MAX_CRAWL_RETWEET_PAGE_NUMBER < max_page_number:
                max_page_number = MAX_CRAWL_RETWEET_PAGE_NUMBER
            
            for page_num in range(1, max_page_number+1):
                new_wrapper = AdvKeywordRealWeiboRetweetURLWrapper(keyword=keyword, mid=mid, page_num=str(page_num), uid=uid, nickname=nickname) 
#                print new_wrapper.to_url()
                url_wrapper_list_manager.add_url_wrapper(new_wrapper)

    threads['list'] = url_wrapper_list_manager
    if OPEN_NORMAL_CRAWL:
        threads['normal cookie manager'] = NormalCookieManager()
        threads['normal crawl executer'] = NormalCrawlExecuter(url_wrapper_list_manager=url_wrapper_list_manager)
    if OPEN_PROXY_CRAWL:
        threads['proxy ip manager'] = proxy_ip_manager
        threads['proxy cookie manager'] = ProxyCookieManager()
        threads['proxy crawl executer'] = ProxyCrawlExecuter(url_wrapper_list_manager=url_wrapper_list_manager)
    
    for thread in threads.values():
        scheduler_logger.info("thread " + thread.name + " start!")
        thread.start()


def search_single_keyword(keyword,crawl_time_range_list):
    threads = {}
    
    url_wrapper_list_manager = UrlWrapperListManager()
   
    for start,end in crawl_time_range_list:
        start_time = datetime.datetime.strptime(start,"%Y-%m-%d-%H") 
        end_time = datetime.datetime.strptime(end,"%Y-%m-%d-%H") 

        delta_days = (end_time - start_time).days
        delta_seconds = (end_time - start_time).seconds
        delta_hours = delta_days*24 + delta_seconds/3600

        for i in range(delta_hours):
            begin_hour,end_hour = get_time(start_time,i)

            first_page = AdvKeywordRealWeiboURLWrapper(keyword=keyword, start_time=begin_hour, end_time=end_hour, page_num=str(1), max_page_num=str(50))
            url_wrapper_list_manager.add_url_wrapper(first_page)
            print first_page.to_url()

    
    threads['list'] = url_wrapper_list_manager
    if OPEN_NORMAL_CRAWL:
        threads['normal cookie manager'] = NormalCookieManager()
        threads['normal crawl executer'] = NormalCrawlExecuter(url_wrapper_list_manager=url_wrapper_list_manager)
    if OPEN_PROXY_CRAWL:
        threads['proxy ip manager'] = proxy_ip_manager
        threads['proxy cookie manager'] = ProxyCookieManager()
        threads['proxy crawl executer'] = ProxyCrawlExecuter(url_wrapper_list_manager=url_wrapper_list_manager)
    
    for thread in threads.values():
        scheduler_logger.info("thread " + thread.name + " start!")
        thread.start()
    
#     while True:
#         time.sleep(4)
#         if not threads['normal crawl executer'].isAlive():
#             threads['normal cookie manager'].stop_me()
#             
#         if not threads['proxy crawl executer'].isAlive():
#             threads['proxy ip manager'].stop_me()
#             threads['proxy cookie manager'].stop_me()
#             
#         for thread in threads.values():
#             if thread.isAlive():
#                 continue
#         break


def get_time(start,i):
    begin_hour = (start+datetime.timedelta(0,i*3600)).strftime("%Y-%m-%d-%H")
    end_hour = (start+datetime.timedelta(0,i*3600+3600)).strftime("%Y-%m-%d-%H")

    return begin_hour,end_hour


def main():
#     search_single_keyword("郁彬", 50, '2014-4-27-0', '2014-5-5-24')
#     search_single_keyword("Yu Bin", 50, '2014-4-27-0', '2014-5-5-24')
    crawl_time_range_list = []
    crawl_time_range_list.append(("2015-07-01-0","2015-07-16-0"))   # 2014-8-8-24 should be transformed to 2014-8-9-0

    search_single_keyword("食品安全",crawl_time_range_list)
#    search_comments_by_weibos()
#    search_retweets_by_weibos()

if __name__ == '__main__':
    main()
