#encoding=utf8
'''
Created on 2014.5.5

@author: cc
'''

import traceback
try:
    from conf import LOGIN_USER_INFOR,\
        COOKIE_FILE
        
except ImportError as err:
    s = traceback.format_exc()
    
    print s


#the keywordprocess module's scan keyword databases interval
KEYWORD_DB_SCAN_INTERVAL = 29

#the weibo_branch module's scan users_database interval
USERS_INFOR_SCAN_INTERVAL = 10 

#whether open the proxy ip crawling
SCAN_FREE_DAILI = False
OPEN_PROXY_CRAWL = True

OPEN_NORMAL_CRAWL = True

#need to configure
GET_INTERVAL_SECONDS = 30
MAX_RELOGIN_TRIAL_NUMBER = 1
#Max crawl page number when crawling weibo comments
MAX_CRAWL_COMMENT_PAGE_NUMBER = 5000
#Max crawl page number when crawling weibo retweets
MAX_CRAWL_RETWEET_PAGE_NUMBER = 5000
#the update interval time when processing proxy IP 
PROXY_IP_UPDATE_INTERVAL = 1800#3600
#when test whether a proxy ip is well enough to be used
GOOD_PROXY_IP_THRESHOLD = 15
#threads number ot verify whether a proxy ip is good
VERIFY_PROXY_IP_NUMBER = 40
#two proxy ip''s gotten interval
PROXY_GET_INTERVAL_SECONDS = 4
SLEEP_SECONDS_WHEN_GET_PROXY_IP_FAILED = 30

SLEEP_SECONDS_WHEN_GET_URL_FAILED = 10
UPDATE_URL_WRAPPER_LIST_INTERVAL = 30

#data bases name(for mongoDB)
DATABASE_SUFFIX = "_keyword_adv_time"

GET_PAGE_TIMEOUT = 24
#whether open the corresponding log
OPEN_WRITE_NOTUNIQUE_LOG = 0
USER_INFOR_MANAGER = LOGIN_USER_INFOR

COOKIE_FILE_NAME = COOKIE_FILE

TOTAL_USER_COUNT = len(USER_INFOR_MANAGER)
NORMAL_USER_COUNT = 4

