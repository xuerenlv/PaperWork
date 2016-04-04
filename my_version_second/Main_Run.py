# -*- coding: utf-8 -*-

'''
Created on 2015-08-21

@author: xhj
'''
import datetime
import logging.config
import os
from urllib import quote_plus
from craw_page_parse import crawl_set_time_with_keyword
from utils_no_crwal import uid_is_numbers
from Queue import Queue



# from craw_page_parse import  crawl_set_time_with_only_keyword
if not os.path.exists( 'logs/' ):
    os.mkdir( 'logs' )
if os.path.exists( 'logs/scheduler.log' ):
    open( 'logs/scheduler.log', 'w' ).truncate()

curpath = os.path.normpath( os.path.join( os.getcwd(), os.path.dirname( __file__ ) ) ) 
logging.config.fileConfig( curpath + '/runtime_infor_log.conf' )

if not os.path.exists( 'data/' ):
    os.mkdir( 'data' )
if not os.path.exists( 'cookies/' ):
    os.mkdir( 'cookies' )

###################################################################################### crawl one useer all weibo start

# 一个 uid 抓取一次
def crawl_uses_all_weibo():
    all_thrads_list = []
    
    uid = 'ifengvideo'
    total_num = 38633 / 10 + 1
    how_many_urls_one_thread = total_num / 7;
    
    all_url = [] 
    for index in range( total_num ):
        url = ""
        if uid_is_numbers( uid ):
            url = "http://weibo.cn/u/" + uid + "?page=" + str( index )
        else:
            url = "http://weibo.cn/" + uid + "?page=" + str( index )
        all_url.append( url )
        
    count = 0
    for cut_index in xrange( 0, len( all_url ), how_many_urls_one_thread ):
        this_urls = all_url[cut_index:cut_index + how_many_urls_one_thread]
        url_queue = Queue()
        for one_url in this_urls:
            url_queue.put( one_url )
        count = count + 1
        all_thrads_list.append( crawl_set_time_with_keyword( uid, url_queue , thread_name = str( count ) + "___thread" ) )
        
    
    for thread in all_thrads_list:
        thread.start()
    for thread in all_thrads_list:
        thread.join() 



###################################################################################### crawl one useer all weibo end


if __name__ == '__main__':    
    
    crawl_uses_all_weibo()
    
    pass  
   
   
   
   
   
   
   
   
   
   
   
   
   
   
