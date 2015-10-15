#-*- coding: utf-8 -*-

'''
Created on 2015-08-21

@author: xhj
'''
from craw_page_parse import crawl_real_time_with_keyword,\
    crawl_set_time_with_keyword,crawl_set_time_with_keyword_and_nickname,\
    crawl_set_time_with_only_keyword
import os
import logging.config
import datetime
from crawl_comment_from_db import read_file_fetch_something, crawl_comment
from itertools import count
from craw_page_parse_2 import crawl_uid_from_nickname,\
    crawl_userinfo_from_uname_or_uid, crawl_userinfo_2_from_uid

if not os.path.exists('logs/'):
    os.mkdir('logs')
curpath=os.path.normpath( os.path.join( os.getcwd(), os.path.dirname(__file__) ) ) 
logging.config.fileConfig(curpath+'/runtime_infor_log.conf')

if not os.path.exists('data/'):
    os.mkdir('data')
if not os.path.exists('cookies/'):
    os.mkdir('cookies')


# 返回创建好的thread
def crawl_real_time_main(key_words_list):
    thrads_list = []
    for i in range(len(key_words_list)):
        thrads_list.append(crawl_real_time_with_keyword(key_words_list[i],'real_time_'+str(i)))
    return thrads_list

# 按照天数，分别创建开始url   关键词，对应微博很多，按天抓取
def crawl_set_time_main_many(key_word,start_time,end_time):
    thrads_list = []
    while start_time+datetime.timedelta(days=90) < end_time:
        end_2 = start_time+datetime.timedelta(days=90)
        thrads_list.append(crawl_set_time_with_keyword(key_word,start_time,end_2,'crawl_settime_thread'+str(start_time)+" to "+str(end_2)))
        start_time = end_2
    if start_time < end_time:
        thrads_list.append(crawl_set_time_with_keyword(key_word,start_time,end_time,'crawl_settime_thread'+str(start_time)+" to "+str(end_time)))
    return thrads_list

# 不按天抓取,一次抓取全部
def crawl_set_time_main_little(key_word, start_time, end_time,nickname_list):
    thrads_list = []
    
    for nickname in nickname_list:
        thrads_list.append(crawl_set_time_with_keyword_and_nickname(key_word,start_time,end_time,nickname,nickname+"_thread"))
    
    return thrads_list
    

#  根据给出的微博文件名，爬取评论
def crawl_comment_from_fie(weibo_file_name):
    dict_url_id = read_file_fetch_something(weibo_file_name)
    all_thrads_list = []
    
    dict_key_list = []
    start = 0;
    end = 2000;
    while end < len(dict_url_id.keys()):
        dict_key_list.append(dict_url_id.keys()[start:end])
        start += 2000
        end += 2000;
    if start <= len(dict_url_id.keys()):
        dict_key_list.append(dict_url_id.keys()[start:])
    
    count = 1
    for dict_key_list_one in dict_key_list:
        dict__one_dict = {}
        for key in dict_key_list_one:
            dict__one_dict[key] = dict_url_id[key]
        all_thrads_list.append(crawl_comment(dict__one_dict,'crawl_comment___'+str(count)))
        count += 1
        
    return all_thrads_list
    

def main_2_just_tran_nickname_to_uidoruname():
    file_r = open("100_atname_file.txt",'r')
    
    nickname_list = []
    for line in file_r.readlines():
        op_nickname = line[line.find('nickname:'):]
        nickname = op_nickname[op_nickname.find(':')+1:op_nickname.rfind(']')]
        nickname_list.append(nickname)
    
    all_thrads_list = []
    start = 0
    end = 10
    count = 1
    while end < len(nickname_list):
        all_thrads_list.append(crawl_uid_from_nickname(nickname_list[start:end],"crawl_uid_from_nickname_"+str(count)))
        start += 10
        end += 10
        count +=1
    if(start < len(nickname_list)):
        all_thrads_list.append(crawl_uid_from_nickname(nickname_list[start:len(nickname_list)],"crawl_uid_from_nickname_"+str(count)))
    
    for thread in all_thrads_list:
        thread.start()
    for thread in all_thrads_list:
        thread.join()  
    pass
    
def main_1_remember():
    all_thrads_list = []
    
#     key_words_list = ['滨海','香港','上海']
#     all_thrads_list.extend(crawl_real_time_main(key_words_list))
      
#     nickname_list = ["新闻晨报","南方都市报","广州日报","南方日报","环球时报","扬子晚报","新京报","每日经济新闻","楚天都市报"]
     
#     key_word = '中港矛盾'
    key_word = '港中矛盾'
    start_time = datetime.datetime(2015, 1, 1)
    end_time = datetime.datetime(2015, 9, 6)
     
    all_thrads_list.extend(crawl_set_time_main_many(key_word, start_time, end_time))
#     all_thrads_list.extend(crawl_set_time_main_little(key_word, start_time, end_time,nickname_list))
#     key_word = "港中矛盾"
    all_thrads_list.append(crawl_set_time_with_only_keyword(key_word,start_time,end_time,))
    
    for thread in all_thrads_list:
        thread.start()
    for thread in all_thrads_list:
        thread.join()    



def chuli_nickname_crawl_userinfo():
    uid_or_uname_list = []
   
    file_r_1 = open("uid_need_to_fetch.txt",'r')
    for line in file_r_1.readlines():
        uid = line[0:-1]
#        print uid
        uid_or_uname_list.append(uid)
        
    file_r_2 = open("at_nickname_to_(uid_or_uname).txt",'r')
    for line in file_r_2.readlines():
        op_line = line[2:]
        uid_or_uname = op_line[op_line.find(':')+1:op_line.find(']')]
        uid_or_uname_list.append(uid_or_uname)
   
#     for con in uid_or_uname_list:
#         print con
#     print len(uid_or_uname_list)
    all_thrads_list = []
    start = 0
    end = 10
    count = 1
    while end < len(uid_or_uname_list):
        all_thrads_list.append(crawl_userinfo_from_uname_or_uid(uid_or_uname_list[start:end],"crawl_userinfo_from_uname_or_uid_"+str(count)))
        start += 10
        end += 10
        count +=1
    if(start < len(uid_or_uname_list)):
        all_thrads_list.append(crawl_userinfo_from_uname_or_uid(uid_or_uname_list[start:len(uid_or_uname_list)],"crawl_userinfo_from_uname_or_uid_"+str(count)))
     
    for thread in all_thrads_list:
        thread.start()
    for thread in all_thrads_list:
        thread.join()  


if __name__ == '__main__':
   
        
#     for con in uid_or_uname_list:
#         print con
#     print len(uid_or_uname_list)
    all_thrads_list = []
    
    
#     key_word = '苹果 手机'
#     start_time = datetime.datetime(2013, 1, 1)
#     end_time = datetime.datetime(2015, 9, 20)
#        
#     all_thrads_list.extend(crawl_set_time_main_many(key_word, start_time, end_time))
    
    all_thrads_list.extend(crawl_comment_from_fie("apple_phone_single_weibo.txt"))
    
#     uid_list = []
# 
#     file_r = open("uid_all_data_unique.txt",'r')
#     for line in file_r.readlines():
#         uid = line[0:-1]
#         uid_list.append(uid)
# 
#     start = 0
#     end = 100
#     count = 1
#     while end < len(uid_list):
#         all_thrads_list.append(crawl_userinfo_2_from_uid(uid_list[start:end],"crawl_userinfo_2_from_uid"+str(count)))
#         start += 100
#         end += 100
#         count +=1
#     if(start < len(uid_list)):
#         all_thrads_list.append(crawl_userinfo_2_from_uid(uid_list[start:len(uid_list)],"crawl_userinfo_2_from_uid"+str(count)))
        
    for thread in all_thrads_list:
        thread.start()
    for thread in all_thrads_list:
        thread.join()  
    pass  
   
   
   
   
   
   
   
   
   
   
   
   
   
   