#coding:utf-8
"""
Program: 
Description: 
Author: cheng chuan - chengc@nlp.nju.edu.cn
Date: 2014-04-14 02:21:03
Last modified: 2014-04-21 18:02:53
Python release: 2.7.3
"""
'''
Created on 2014��4��3��

@author: cc
'''

import traceback
try:
    import random
    import time
    import datetime
    import threading
    import logging
    
    from loginer import get_loginer

    from keyword_processor import get_keyword_processor
    from get_valid_ip import proxy_ip_manager
    from common_conf_manager import MAX_RELOGIN_TRIAL_NUMBER,\
        GET_INTERVAL_SECONDS,\
        PROXY_GET_INTERVAL_SECONDS,\
        USER_INFOR_MANAGER,\
        UPDATE_URL_WRAPPER_LIST_INTERVAL,\
        SLEEP_SECONDS_WHEN_GET_PROXY_IP_FAILED,\
        SLEEP_SECONDS_WHEN_GET_URL_FAILED,\
        TOTAL_USER_COUNT,\
        NORMAL_USER_COUNT, \
        OPEN_PROXY_CRAWL,\
        OPEN_NORMAL_CRAWL,\
        COOKIE_FILE_NAME
    
    from advance_keyword_real_weibo import get_url_wrapper_generator as real_generator,\
        AdvKeywordRealWeiboURLWrapper,\
        AdvKeywordRealWeiboCommentURLWrapper,\
        AdvKeywordRealWeiboParser,\
        AdvKeywordRealWeiboCommentParser,\
        AdvKeywordRealWeiboCrawler,\
        AdvKeywordRealWeiboCommentCrawler
        
    from advance_keyword_hot_weibo import get_url_wrapper_generator as hot_generator,\
        AdvKeywordHotWeiboURLWrapper,\
        AdvKeywordHotWeiboCommentURLWrapper,\
        AdvKeywordHotWeiboParser,\
        AdvKeywordHotWeiboCommentParser,\
        AdvKeywordHotWeiboCrawler,\
        AdvKeywordHotWeiboCommentCrawler
    from storage_manager import SinaweibosearchCurrentUrl
    
    from my_log import get_log
#     from storage_manager import connect_db
    
except ImportError as err:
    s = traceback.format_exc()
    
    print s

my_log = get_log()
scheduler_logger = logging.getLogger("schedulerLog")
###################################The following are involving with normal and proxy cookie management###################
try:
    from Queue import Queue
except:
    s = traceback.format_exc()
    print s 

normal_cookie_queue = Queue()
class NormalCookieManager(threading.Thread):
    cookie_index = 0
    
    def __init__(self, thread_name="normal cookie manager"):
        
        threading.Thread.__init__(self)
        
        self.name = thread_name
    
    def run(self):
        global normal_cookie_queue
        
        while True:
            
            if normal_cookie_queue.qsize() < TOTAL_USER_COUNT:
                NormalCookieManager.cookie_index = (NormalCookieManager.cookie_index + 1) % NORMAL_USER_COUNT
                
                cur_index = NormalCookieManager.cookie_index
                new_username = USER_INFOR_MANAGER[cur_index]['username']
                new_password = USER_INFOR_MANAGER[cur_index]['password']
                new_cookie_file = COOKIE_FILE_NAME + str(cur_index + 1)
                
                normal_cookie_queue.put([str(new_username), str(new_password), str(new_cookie_file)])
            
            sleep_seconds = random.uniform(GET_INTERVAL_SECONDS - 10, GET_INTERVAL_SECONDS)
            time.sleep(sleep_seconds)
        
PROXY_USER_COUNT = TOTAL_USER_COUNT - NORMAL_USER_COUNT
proxy_cookie_queue = Queue()
class ProxyCookieManager(threading.Thread):
    cookie_index = 0
    
    def __init__(self, thread_name="proxy cookie manager"):
        
        threading.Thread.__init__(self)
        
        self.name = thread_name
    
    def run(self):
        global proxy_cookie_queue
        
        while True:
            proxy_ip = proxy_ip_manager.get_ip()
            
            if proxy_ip == "":
                time.sleep(SLEEP_SECONDS_WHEN_GET_PROXY_IP_FAILED)
                continue
            
#             scheduler_logger.debug("before set pcq's size: " + str(proxy_cookie_queue.qsize()))
            if proxy_ip_manager.has_enough_ips() and proxy_cookie_queue.qsize() < PROXY_USER_COUNT:
                ProxyCookieManager.cookie_index = (ProxyCookieManager.cookie_index + 1) % PROXY_USER_COUNT
                
                cur_index = ProxyCookieManager.cookie_index + NORMAL_USER_COUNT
                new_username = USER_INFOR_MANAGER[cur_index]['username']
                new_password = USER_INFOR_MANAGER[cur_index]['password']
                new_cookie_file = COOKIE_FILE_NAME + str(cur_index + 1)
                
                proxy_cookie_queue.put([str(new_username), str(new_password), str(new_cookie_file), str(proxy_ip)])
#                 scheduler_logger.debug("after set pcq's size: " + str(proxy_cookie_queue.qsize()))
            
            interval = 0
            if proxy_ip_manager.get_ip_number() == 0 or PROXY_USER_COUNT == 0:
                interval = SLEEP_SECONDS_WHEN_GET_PROXY_IP_FAILED
            elif proxy_ip_manager.get_ip_number() < PROXY_USER_COUNT:
                interval = GET_INTERVAL_SECONDS / ((float)(proxy_ip_manager.get_ip_number()))
            else:
                interval =  GET_INTERVAL_SECONDS / ((float)(PROXY_USER_COUNT))
            
            now_time = datetime.datetime.now()
            sleep_seconds = random.uniform(PROXY_GET_INTERVAL_SECONDS-1, PROXY_GET_INTERVAL_SECONDS)
            if now_time.hour < 7:
                sleep_seconds = random.uniform(26 - 1, 26)
                
            time.sleep(sleep_seconds)
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
            new_url_wrapper = url_wrapper_list_manager.get_next_priority_url_wrapper()
        
            if not new_url_wrapper:
            
                time.sleep(SLEEP_SECONDS_WHEN_GET_URL_FAILED)
                continue
                
            scheduler_logger.info("In normal crawling: {time: \"%s\", cur_url_size: \"%s\", cur_url: \"%s\"}" % (str(datetime.datetime.now()),\
                                                                                        str(len(url_wrapper_list_manager.url_wrapper_list)),\
                                                                                        new_url_wrapper.url_wrapper.tostring()))
            scheduler_logger.info("url_wrapper_list's url_index is: " + str(url_wrapper_list_manager.url_index) + " size: " + str(len(url_wrapper_list_manager.url_wrapper_list)))
            
            new_crawler = get_crawler_by_url_wrapper(new_url_wrapper.url_wrapper)
            scheduler_logger.debug("username: " + cur_username + " password: " + cur_password + " cookie_file: " + cur_cookie_file)
            try:
                scheduler_logger.debug("before execute_crawl")
                [crawl_feed_count, new_feed_count,increment] = self.execute_crawl(new_crawler, cur_username, cur_password, cur_cookie_file)
                scheduler_logger.debug("after execute_crawl")
                
                #modify the url_wrapper's priority according to the actual crawling result
                new_url_wrapper.modify_counter(crawl_feed_count, new_feed_count, increment)
                scheduler_logger.info("keyword:"+new_url_wrapper.url_wrapper.keyword)
                scheduler_logger.info("{crawl_feed_count: " + str(crawl_feed_count) +", new_feed_count: " + str(new_feed_count) + ", increment: " +str(increment)+ "}")
            except:
                s = traceback.format_exc()
                print s
                pass

    def execute_crawl(self, crawler, cur_username, cur_password, cur_cookie_file):

        crawl_feed_count = 0
        new_feed_count = 0
        increment = 0
        
        if loginer.login(str(cur_username), str(cur_password), str(cur_cookie_file)):
            scheduler_logger.info("normal login succeed and cookie file is: " + cur_cookie_file)
            [page_is_validity, new_url_list, crawl_feed_count, new_feed_count,increment ] = crawler.crawl()
                
            #for re-get page
            if not page_is_validity:
                    
                relogin_num = MAX_RELOGIN_TRIAL_NUMBER
                    
                while relogin_num > 0:
		    slt = (int)(random.uniform(15, 85))
                        
                    sleep_when_relogin(crawler,slt)

                    if loginer.relogin(str(cur_username), str(cur_password), str(cur_cookie_file)):
                        [page_is_validity, new_url_list, crawl_feed_count, new_feed_count,increment ] = crawler.crawl()
                        
                        break
                        
                    relogin_num -= 1
                
            if not page_is_validity:
                    
                return [crawl_feed_count, new_feed_count, increment ]
                
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
                
            new_url_wrapper = url_wrapper_list_manager.get_next_priority_url_wrapper()
        
            if not new_url_wrapper:
                
                time.sleep(SLEEP_SECONDS_WHEN_GET_URL_FAILED)
                continue
                    
            scheduler_logger.info("In proxy crawling: {time: \"%s\", cur_url_size: \"%s\", cur_url: \"%s\"}" % (str(datetime.datetime.now()),\
                                                                                        str(len(url_wrapper_list_manager.url_wrapper_list)),\
                                                                                        new_url_wrapper.url_wrapper.tostring()))
            scheduler_logger.info("url_wrapper_list's url_index is: " + str(url_wrapper_list_manager.url_index) + " size: " + str(len(url_wrapper_list_manager.url_wrapper_list)))
                    
            new_crawler = get_crawler_by_url_wrapper(new_url_wrapper.url_wrapper, proxy_IP, True, cur_cookie_file)
            scheduler_logger.debug("username: " + cur_username + " password: " + cur_password + " cookie_file: " + cur_cookie_file)
            try:
                scheduler_logger.debug("before execute_crawl")
                [crawl_feed_count, new_feed_count, increment] = self.execute_crawl(new_crawler, cur_username, cur_password, cur_cookie_file)
                scheduler_logger.debug("after execute_crawl")
                    
                new_url_wrapper.modify_counter(crawl_feed_count, new_feed_count, increment)
                scheduler_logger.info("keyword:"+new_url_wrapper.url_wrapper.keyword)
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
            
            [page_is_validity, new_url_list, crawl_feed_count, new_feed_count,increment ] = crawler.crawl()
            
            scheduler_logger.info("after first crawl")
            #for re-get page
            if not page_is_validity:
                relogin_num = MAX_RELOGIN_TRIAL_NUMBER
                while relogin_num > 0:
                    slt = (int)(random.uniform(10,90))  
                    sleep_when_relogin(crawler,slt)

                    if loginer.relogin(cur_username, cur_password, cur_cookie_file):
                        scheduler_logger.debug("before recrawl")
                        [page_is_validity, new_url_list, crawl_feed_count, new_feed_count,increment ] = crawler.crawl()
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
    
    def modify_counter(self, crawl_feed_count, new_feed_count, increment):
        
#         print "old cur_priority is: " + str(self.cur_priority) + " counter is: " + str(self.counter)
#         print "modifying: crawl_feed_count is " + str(crawl_feed_count) + " and new_feed_count is " + str(new_feed_count)
        if crawl_feed_count == 0:
            self.counter = 1
            return 
        
        if increment == crawl_feed_count:
            self.cur_priority = PriorityUrlWrapper._DEFAULT_PRIORITY
            self.counter = self.cur_priority
            
        elif increment < (crawl_feed_count)/2:
            self.cur_priority += 1
            self.counter = self.cur_priority
        else:
            if self.cur_priority <= PriorityUrlWrapper._DEFAULT_PRIORITY:
                self.cur_priority = PriorityUrlWrapper._DEFAULT_PRIORITY
                self.counter = self.cur_priority
            else:
                self.cur_priority -= 1
                self.counter = self.cur_priority
#         print "new cur_priority is: " + str(self.cur_priority) + " counter is: " + str(self.counter)

wrapper_list_mutex = threading.Lock()
class UrlWrapperListManager(threading.Thread):
    url_wrapper_list = []
    keyword_processor = get_keyword_processor()
    real_url_wrapper_generator = real_generator()
    hot_url_wrapper_generator = hot_generator()
    url_index = 0
    
    def __init__(self, thread_name="url wrapper list manager"):
        threading.Thread.__init__(self)
        self.name = thread_name
    
    def run(self):
        while True:
            self._update_url_wrapper_list()
            try:
                SinaweibosearchCurrentUrl.drop_collection()
            except:
                scheduler_logger.info("drop current url table failed!")
            
            if wrapper_list_mutex.acquire():
                for url in UrlWrapperListManager.url_wrapper_list:
                    try: 
                        SinaweibosearchCurrentUrl(keyword=url.url_wrapper.keyword, url=url.url_wrapper.to_url(), cur_priority=url.cur_priority, counter=url.counter).save()
                    except:
                        scheduler_logger.info("store current url failed!")
                
                wrapper_list_mutex.release()
            
            time.sleep(UPDATE_URL_WRAPPER_LIST_INTERVAL)
            
    
    def _update_url_wrapper_list(self):
        
        if (not UrlWrapperListManager.keyword_processor.real_update) and (not UrlWrapperListManager.keyword_processor.hot_update):
            
            return False
        
        tmp_url_wrapper_list = []
        old_original_set = dict()
        for url_wrapper in UrlWrapperListManager.url_wrapper_list:
            old_original_set[url_wrapper.url_wrapper.keyword] = url_wrapper.url_wrapper.max_page_num 
        
        new_keyword_set = set()
        updated_keyword_set = set()
        if UrlWrapperListManager.keyword_processor.real_update is True:

            for (keyword, max_page_num) in UrlWrapperListManager.keyword_processor.real_keyword_dic.items():
                #be careful when processing real and hot seperately
                new_keyword_set.add(keyword)
                if not old_original_set.has_key(keyword):
                    tmp_url_wrapper_list.append(UrlWrapperListManager.real_url_wrapper_generator.generate_first_page_url_adv_keyword_real(keyword, max_page_num))
                elif int(old_original_set[keyword]) != int(max_page_num):
                    updated_keyword_set.add(keyword)
                    tmp_url_wrapper_list.append(UrlWrapperListManager.real_url_wrapper_generator.generate_first_page_url_adv_keyword_real(keyword, max_page_num))

            UrlWrapperListManager.keyword_processor.set_real_update(False)
             
        if UrlWrapperListManager.keyword_processor.hot_update is True:
            
            for (keyword, max_page_num) in UrlWrapperListManager.keyword_processor.hot_keyword_dic.items():
                #be careful when processing real and hot seperately
                new_keyword_set.add(keyword)
                if not old_original_set.has_key(keyword):
                    tmp_url_wrapper_list.append(UrlWrapperListManager.hot_url_wrapper_generator.generate_first_page_url_adv_keyword_hot(keyword, max_page_num))
                elif int(old_original_set[keyword]) != int(max_page_num):
                    updated_keyword_set.add(keyword)
                    tmp_url_wrapper_list.append(UrlWrapperListManager.hot_url_wrapper_generator.generate_first_page_url_adv_keyword_hot(keyword, max_page_num))
 
            UrlWrapperListManager.keyword_processor.set_hot_update(False)
        
        tmp_priority_wrapper_list = []
        for url_wrapper in tmp_url_wrapper_list:
            tmp_priority_wrapper_list.append(PriorityUrlWrapper(url_wrapper))
        
        old_count = 0
        for priority_wrapper in UrlWrapperListManager.url_wrapper_list:
            if priority_wrapper.url_wrapper.keyword in new_keyword_set and not (priority_wrapper.url_wrapper.keyword in updated_keyword_set):
                tmp_priority_wrapper_list.append(priority_wrapper)
                old_count += 1
        
        global wrapper_list_mutex
        if wrapper_list_mutex.acquire():
            UrlWrapperListManager.url_wrapper_list = tmp_priority_wrapper_list
            wrapper_list_mutex.release()
        
        return True
    
    def add_url_wrapper(self, url_wrapper):
        global wrapper_list_mutex
        
        if wrapper_list_mutex.acquire():
            UrlWrapperListManager.url_wrapper_list.append(PriorityUrlWrapper(url_wrapper))
            wrapper_list_mutex.release()
            
    def get_next_priority_url_wrapper(self):
        global wrapper_list_mutex
        
        url_wrapper = None
        
        if not UrlWrapperListManager.url_wrapper_list:
            return url_wrapper
        
        if wrapper_list_mutex.acquire():
            try:
                old_index = UrlWrapperListManager.url_index
                index = old_index
                while True:
                    url_wrapper = UrlWrapperListManager.url_wrapper_list[index]
                    url_wrapper.counter -= 1
                    
                    if url_wrapper.counter <= 0:
                        url_wrapper.counter = url_wrapper.cur_priority
                        UrlWrapperListManager.url_index = (index + 1) % len(UrlWrapperListManager.url_wrapper_list)
                        break
                    
                    index = (index + 1) % len(UrlWrapperListManager.url_wrapper_list)
                    
                    if old_index == index:
                        UrlWrapperListManager.url_index = (index + 1) % len(UrlWrapperListManager.url_wrapper_list)
                        break
            except:
                url_wrapper = None
                pass
            finally:
                wrapper_list_mutex.release()
        
        return url_wrapper 
#########################################################################################################################
###########################The following involving with get crawler according to url_wrapper type########################

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
            
    return new_crawler

def sleep_when_relogin(crawler,sleep_seconds=3):
    keyword = crawler.url_wrapper.keyword
    scheduler_logger.info('--------------------------')
    scheduler_logger.info('keyword————'+keyword)
    scheduler_logger.info('relogin sleep time: ' + str(sleep_seconds))
    scheduler_logger.info('--------------------------')
    time.sleep(sleep_seconds)

    return sleep_seconds
#########################################################################################################################            
                
class WeiboScheduler(threading.Thread):
    '''
    Responsible for scheduling
    '''
    
    def __init__(self, thread_name="weiboscheduler"):
        threading.Thread.__init__(self)
        
        self.name = thread_name
        
    def run(self):
        sub_threads = []
        
        url_wrapper_list_manager = UrlWrapperListManager()
        sub_threads.append(url_wrapper_list_manager)
        if OPEN_NORMAL_CRAWL:
            sub_threads.append(NormalCookieManager())
            sub_threads.append(NormalCrawlExecuter(url_wrapper_list_manager=url_wrapper_list_manager))
        if OPEN_PROXY_CRAWL:
            sub_threads.append(ProxyCookieManager())
            sub_threads.append(ProxyCrawlExecuter(url_wrapper_list_manager=url_wrapper_list_manager))
#         
        try:
            for t in sub_threads:
                t.start()
                scheduler_logger.info("thread " + (t.name) + " start!")
        except:
            s = traceback.format_exc()
            print s
            
#         for thread in sub_threads:
#             thread.join()
            
weibo_scheduler = WeiboScheduler()

def get_weibo_scheduler():
    
    return weibo_scheduler

##############################################################################################################################
