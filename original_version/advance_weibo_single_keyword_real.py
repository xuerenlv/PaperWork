#encoding=utf8
'''
Created on 2014年7月23日

@author: cc
'''
import sys
from advance_weibo_frame import COMMENT_PER_PAGE_NUMBER
from common_conf_manager import MAX_CRAWL_COMMENT_PAGE_NUMBER
from storage_manager import SingleWeibo

reload(sys)
sys.setdefaultencoding('utf8')  # @UndefinedVariable

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
        AdvKeywordRealWeiboCommentCrawler
        
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

scheduler_logger = logging.getLogger("schedulerLog")
loginer = get_loginer()

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

def sleep_when_relogin(sleep_seconds=3):
    scheduler_logger.info('--------------------------')
    scheduler_logger.info('relogin sleep time: ' + str(sleep_seconds))
    scheduler_logger.info('--------------------------')
    time.sleep(sleep_seconds)

    return sleep_seconds