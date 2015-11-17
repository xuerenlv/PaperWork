# -*- coding: utf-8 -*-

'''
Created on 2015-08-21

@author: xhj
'''
from craw_page_parse import crawl_real_time_with_keyword, \
    crawl_set_time_with_keyword, crawl_set_time_with_keyword_and_nickname, \
    crawl_set_time_with_only_keyword
import os
import logging.config
import datetime
from crawl_comment_from_db import read_file_fetch_something, crawl_comment
from itertools import count
from craw_page_parse_2 import crawl_uid_from_nickname, \
    crawl_userinfo_from_uname_or_uid, crawl_userinfo_2_from_uid

if not os.path.exists('logs/'):
    os.mkdir('logs')
curpath = os.path.normpath(os.path.join(os.getcwd(), os.path.dirname(__file__))) 
logging.config.fileConfig(curpath + '/runtime_infor_log.conf')

if not os.path.exists('data/'):
    os.mkdir('data')
if not os.path.exists('cookies/'):
    os.mkdir('cookies')


# 返回创建好的thread
def crawl_real_time_main(key_words_list):
    thrads_list = []
    for i in range(len(key_words_list)):
        thrads_list.append(crawl_real_time_with_keyword(key_words_list[i], 'real_time_' + str(i)))
    return thrads_list

# 按照天数，分别创建开始url  
# 关键词，对应微博很多，按天抓取
def crawl_set_time_main_many(key_word, start_time, end_time,how_many_days_one_thread):
    thrads_list = []
    while start_time + datetime.timedelta(days=how_many_days_one_thread) < end_time:
        end_2 = start_time + datetime.timedelta(days=how_many_days_one_thread)
        thrads_list.append(crawl_set_time_with_keyword(key_word, start_time, end_2, 'crawl_settime_thread' + str(start_time) + " to " + str(end_2)))
        start_time = end_2
    if start_time < end_time:
        thrads_list.append(crawl_set_time_with_keyword(key_word, start_time, end_time, 'crawl_settime_thread' + str(start_time) + " to " + str(end_time)))
    return thrads_list


# 不按天抓取,一次抓取全部
# 给定： 关键词，开始时间，结束时间，用户list
def crawl_set_time_main_little(key_word, start_time, end_time, nickname_list):
    thrads_list = []
    
    for nickname in nickname_list:
        thrads_list.append(crawl_set_time_with_keyword_and_nickname(key_word, start_time, end_time, nickname, nickname + "_thread"))
    
    return thrads_list
    

#  根据给出的微博文件名，爬取评论
#  从本地文件中获取 微博url
def crawl_comment_from_fie(weibo_file_name):
    #  从单独的微博文件中读取信息
    dict_url_id = read_file_fetch_something(weibo_file_name)
    all_thrads_list = []
    
    dict_key_list = []
    start = 0;
    end = 2000;
    # 每2000个创建一个线程
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
        all_thrads_list.append(crawl_comment(dict__one_dict, 'crawl_comment___' + str(count)))
        count += 1
        
    return all_thrads_list
    

# 通过抓取页面，把nickname转换成uid或者在微博的标示
def main_2_just_tran_nickname_to_uidoruname():
    file_r = open("100_atname_file.txt", 'r')
    
    nickname_list = []
    for line in file_r.readlines():
        op_nickname = line[line.find('nickname:'):]
        nickname = op_nickname[op_nickname.find(':') + 1:op_nickname.rfind(']')]
        nickname_list.append(nickname)
    
    all_thrads_list = []
    start = 0
    end = 10
    count = 1
    while end < len(nickname_list):
        all_thrads_list.append(crawl_uid_from_nickname(nickname_list[start:end], "crawl_uid_from_nickname_" + str(count)))
        start += 10
        end += 10
        count += 1
    if(start < len(nickname_list)):
        all_thrads_list.append(crawl_uid_from_nickname(nickname_list[start:len(nickname_list)], "crawl_uid_from_nickname_" + str(count)))
    
    for thread in all_thrads_list:
        thread.start()
    for thread in all_thrads_list:
        thread.join()  
    pass

# 对于一个关键词的抓取
def crawl_one_keyword():
    all_thrads_list = []
    key_word = '腐败'
    start_time = datetime.datetime(2013, 1, 1)
    end_time = datetime.datetime(2015, 11, 1)
    
    all_thrads_list.extend(crawl_set_time_main_many(key_word, start_time, end_time,30))
    
    for thread in all_thrads_list:
        thread.start()
    for thread in all_thrads_list:
        thread.join() 
    pass    

# 对于hashtag的抓取
def crawl_hash_tag():
    all_thrads_list = []
    key_word = '转基因'
    start_time = datetime.datetime(2015, 1, 1)
    end_time = datetime.datetime(2015, 11, 1)
#     all_thrads_list.append((key_word, start_time, end_time,))
    
    how_many_days_one_thread = 15
    while start_time + datetime.timedelta(days=how_many_days_one_thread) < end_time:
        end_2 = start_time + datetime.timedelta(days=how_many_days_one_thread)
        all_thrads_list.append(crawl_set_time_with_only_keyword(key_word, start_time, end_2, 'crawl_settime_thread' + str(start_time) + " to " + str(end_2)))
        start_time = end_2
    if start_time < end_time:
        all_thrads_list.append(crawl_set_time_with_only_keyword(key_word, start_time, end_time, 'crawl_settime_thread' + str(start_time) + " to " + str(end_time)))
   
    
    for thread in all_thrads_list:
        thread.start()
    for thread in all_thrads_list:
        thread.join()    
    pass

# 抓取特定用户下的微博
def crawl_set_user_weibo_about_keyword():
    all_thrads_list = []
    key_word = '扶老人'
    start_time = datetime.datetime(2011, 1, 1)
    end_time = datetime.datetime(2015, 9, 6)
    nickname_list = ["新闻晨报", "南方都市报", "广州日报", "南方日报", "环球时报", "扬子晚报", "新京报", "每日经济新闻", "楚天都市报"]
    all_thrads_list.extend(crawl_set_time_main_little(key_word, start_time, end_time, nickname_list))
    for thread in all_thrads_list:
        thread.start()
    for thread in all_thrads_list:
        thread.join() 
    pass

# 通过用户的uid来抓取用户信息
def chuli_nickname_crawl_userinfo():
    uid_or_uname_list = []
   
    file_r_1 = open("uid_need_to_fetch.txt", 'r')
    for line in file_r_1.readlines():
        uid = line[0:-1]
#        print uid
        uid_or_uname_list.append(uid)
        
    file_r_2 = open("at_nickname_to_(uid_or_uname).txt", 'r')
    for line in file_r_2.readlines():
        op_line = line[2:]
        uid_or_uname = op_line[op_line.find(':') + 1:op_line.find(']')]
        uid_or_uname_list.append(uid_or_uname)
   
    all_thrads_list = []
    start = 0
    end = 10
    count = 1
    while end < len(uid_or_uname_list):
        all_thrads_list.append(crawl_userinfo_from_uname_or_uid(uid_or_uname_list[start:end], "crawl_userinfo_from_uname_or_uid_" + str(count)))
        start += 10
        end += 10
        count += 1
    if(start < len(uid_or_uname_list)):
        all_thrads_list.append(crawl_userinfo_from_uname_or_uid(uid_or_uname_list[start:len(uid_or_uname_list)], "crawl_userinfo_from_uname_or_uid_" + str(count)))
     
    for thread in all_thrads_list:
        thread.start()
    for thread in all_thrads_list:
        thread.join()  


###################################################################################### start 1
# 用query expansion ，抓取相应词语的微博。

# key_word_list : 存放query expansion的keyword
# start_time : datetime对象，开始时间   end_time ： datetime对象，结束时间
def crawl_keywords_list(key_word_list, start_time, end_time):
    all_thrads_list = []
    
    for key_word in key_word_list:
        all_thrads_list.extend(crawl_set_time_main_many(key_word, start_time, end_time,110))
    
    for thread in all_thrads_list:
        thread.start()
    for thread in all_thrads_list:
        thread.join()  

# 读文件，构造keywordslist 
def gen_keywords_list():
    # 已操作文件： 1 
    file_r = open('./query_expansion_three_word/result_three_word_0.txt','r')
    start_time = ""
    end_time  = ""
    count = 1
    key_words_list = []
    for line in file_r.readlines():
        if count == 1:
            line = line[:-1].split(' ')
            start_time = datetime.datetime(int(line[0]),int(line[1]),int(line[2]))
        elif count == 2:
            line = line[:-1].split(' ')
            end_time = datetime.datetime(int(line[0]),int(line[1]),int(line[2]))
        else:
            key_words_list.append(line[:line.find('-')])  
        count+=1
#     print str(start_time),str(end_time)
#     print len(key_words_list)
    return (key_words_list,start_time,end_time)
###################################################################################### end 1

if __name__ == '__main__':
    
#     key_words_list,start_time,end_time=gen_keywords_list()
#     crawl_keywords_list(key_words_list, start_time, end_time)
    
#     crawl_one_keyword()
    
    crawl_hash_tag()
    
#     crawl_set_user_weibo_about_keyword()
    
#     all_thrads_list = []
#         
#     for thread in all_thrads_list:
#         thread.start()
#     for thread in all_thrads_list:
#         thread.join()  
    pass  
   
   
   
   
   
   
   
   
   
   
   
   
   
   
