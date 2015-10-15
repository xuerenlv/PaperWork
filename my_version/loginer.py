# -*- coding: utf-8 -*-

'''
Created on 2015-08-20

@author: xhj
'''

import traceback
from my_log import WeiboSearchLog
from Queue import Queue
import threading
import sys
import time
from _random import Random
import random
try:
    import os, errno
    from login import login
    import cookielib
    import urllib2
    
    from login import do_login
except:
    s = traceback.format_exc()
    print s
    

class Loginer:
    cookies_list = []
    cookies_list_mutex = threading.Lock()
    
    proxy_list = []
    proxy_list_mutex = threading.Lock()
        
    per_proxy_used_most = 0
        
    def __init__(self):
        pass
    
    def get_cookie_from_file(self, cookie_file):
        cookie = {}
        with open(cookie_file) as f:
            lines = f.readlines()
        for line in lines[1:]:
            line = line.strip()
            space_index = line.find(' ')
            pair = line.split(';')[0][space_index:]
            pair = pair.replace('\"', '')
            equal_index = pair.find('=')
            key = pair[:equal_index]
            value = pair[equal_index + 1:]
            cookie[key] = value
        return cookie

    def fill_cookies_list(self):
        from config_operation import LOGIN_USER_INFOR as user_info_list
        for login_info in user_info_list:
            username = login_info['username']
            password = login_info['password']
            cookie_file = 'cookies/weibo_login_cookies_' + login_info['username'] + '.dat'
            if do_login(username, password, cookie_file) == 1:
                WeiboSearchLog().get_scheduler_logger().info(username + "--login success !")
                Loginer.cookies_list.append(self.get_cookie_from_file(cookie_file))
            else:
                WeiboSearchLog().get_scheduler_logger().warning(username + "--login failed !")
        pass
    
    def fill_proxy_list(self):
        from config_operation import PROXIES as proxy_info_list
        for proxy in proxy_info_list:
            Loginer.proxy_list.append(proxy)
    
    def del_cookie(self):
        if len(Loginer.cookies_list) > 0:
            Loginer.cookies_list_mutex.acquire()
            del Loginer.cookies_list[-1]
            WeiboSearchLog().get_scheduler_logger().warning("  --change cookie ! cookie size: "+str(len(Loginer.cookies_list)))
            time.sleep(int(60))
            Loginer.cookies_list_mutex.release()
    
    # 抓取失败时，先换proxy，当所有的proxy换完时，换账号
    def del_proxy(self):
        Loginer.proxy_list_mutex.acquire()
        Loginer.per_proxy_used_most = 0
        if len(Loginer.proxy_list) > 0:
            del Loginer.proxy_list[-1]
            WeiboSearchLog().get_scheduler_logger().warning("  --change proxy ! proxy size: "+str(len(Loginer.proxy_list)))
            time.sleep(int(60))
        if len(Loginer.proxy_list) == 0:
            self.del_cookie()
            time.sleep(int(60))
        Loginer.proxy_list_mutex.release()
            

    def get_cookie(self):
        Loginer.cookies_list_mutex.acquire()
        if len(Loginer.cookies_list) > 0:
            Loginer.cookies_list_mutex.release()
            return Loginer.cookies_list[-1]
        else:
            self.fill_cookies_list()
            if len(Loginer.cookies_list) > 0:
                re = Loginer.cookies_list[-1]
                Loginer.cookies_list_mutex.release()
                return re
            else:
                WeiboSearchLog().get_scheduler_logger().error("ALL user login failed,the ip .....")
                sys.exit(1)
    
    def get_proxy(self):
        Loginer.proxy_list_mutex.acquire()
        Loginer.per_proxy_used_most += 1
        re = ""
        if len(Loginer.proxy_list) > 0:
            re = Loginer.proxy_list[-1]
        else:
            self.fill_proxy_list()
            Loginer.per_proxy_used_most = 0
            re = Loginer.proxy_list[-1]
        Loginer.proxy_list_mutex.release()
        
        if Loginer.per_proxy_used_most > 100:
            self.del_proxy()
            
        return re
            
if __name__ == '__main__':
    loginer = Loginer()
    print loginer.get_proxy()
    print loginer.get_cookie()
