# -*- coding: utf-8 -*-

'''
Created on Oct 16, 2015

@author: nlp
'''

import sys  
import traceback
from store_model import Single_weibo_store
import datetime
from datetime import timedelta
import pprint
import jieba

reload(sys)  
sys.setdefaultencoding('utf8')   


# 从数据库中读取数据，只要content与create_time
# print entry['uid'],entry['nickname'],entry['is_auth'],entry['creat_time'],entry['content'],entry['praise_num'],entry['retweet_num']
def read_data_from_db():
    data_dic = {}
    for entry in Single_weibo_store.objects:
        datetime_obj = transform_time(entry['creat_time'])
        content = entry['content']
        if not data_dic.has_key(datetime_obj):
            data_dic[datetime_obj] = []
        data_dic[datetime_obj].append(content)
    return data_dic
        
        
# 输入字符串，输出 datetime.datetime 对象
# (2013-01-11 20:34:17)(03月06日)(今天)
def transform_time(ori_time):
    if u'今天' in ori_time:
        return datetime.datetime(2015, 9, 7)
    elif not u'月' in ori_time:
        ori_time = (ori_time[:ori_time.find(' ')]).split('-')
        try:
            return datetime.datetime(int(ori_time[0]), int(ori_time[1]), int(ori_time[2]))
        except:
            for i in range(len(ori_time)):
                print ori_time[i]
            print traceback.format_exc()
    else:
        yue = ori_time[:ori_time.find(u'月')]
        ri = ori_time[len(yue) + 1:ori_time.find(u'日')]
#         print ori_time+"->>>"+ri
        return datetime.datetime(2015, int(yue), int(ri))

# 对微博的content进行预处理
def pre_processing(ori_content):
    pass





#*********    第二个版本 生成长度为2的  *********************************************************

# data_dic 为 time对象－－》list，里面装的是一条条微博
# 返回的是 touple对象，(start，end)－－》list，里面装的是一条条微博
def time_span_setting(data_dic):
    smallest_time = data_dic.keys()[0]
    largest_time = data_dic.keys()[0]
    for key in data_dic:
        if smallest_time > key:
            smallest_time = key
        if largest_time < key:
            largest_time = key
    data_timespan_dic = {}
    while smallest_time + timedelta(days=49) <= largest_time:
        key = (smallest_time, smallest_time + timedelta(days=49))
        data_timespan_dic[key] = []
        for i in range(50):
            if data_dic.has_key(smallest_time + timedelta(days=i)):
                data_timespan_dic[key].extend(data_dic[smallest_time + timedelta(days=i)])
        if len(data_timespan_dic[key]) == 0:
            del data_timespan_dic[key]
        smallest_time += timedelta(days=50)
    if smallest_time < largest_time:   
        key = (smallest_time, largest_time)
        data_timespan_dic[key] = []
        this_time_span = data_timespan_dic[key] 
        while smallest_time <= largest_time:
            if data_dic.has_key(smallest_time):
                this_time_span.extend(data_dic[smallest_time])
            smallest_time += timedelta(days=1)
        if len(this_time_span) == 0:
            del data_timespan_dic[key]
    return data_timespan_dic

# 对于微博个数小于 50 的timespan，把这个timespan与前面一个相融合
def merge_timespan(data_timespan_dic):
    del_key = []
    for key in data_timespan_dic:
        if len(data_timespan_dic[key]) <= 50:
            del_key.append(key)
    for key in set(del_key):
        del data_timespan_dic[key]

# 进行分词，使用结巴分词
# 返回的是 touple对象，(start，end)－－》list[list]，里面的list用来存储分词结果
# 返回在这些微博中的所有词
def cut_weibo(data_timespan_dic):
    dic_list = []
    data_timespan_dic_cutted = {}
    for key in data_timespan_dic:
        data_timespan_dic_cutted[key] = []
        re_list = data_timespan_dic_cutted[key]
        for one_weibo in data_timespan_dic[key]:
            cut = [word for word in jieba.cut(one_weibo)]
            re_list.append(cut)
            dic_list.extend(cut)
    return (data_timespan_dic_cutted, set(dic_list), dic_list)


# 计算P(w)
def calculate_p_w(dic_set, dic_list):
    p_w_dic = {}
    w_map_count = {}
    K = 10
    V = 250000
    total_term_in_microarchive = len(dic_set)
    for word in dic_set:
        count = 0 
        for in_word in dic_list:
            if in_word == word:
                count += 1
        w_map_count[word] = count
        p_w_dic[word] = float(count + K) / float(total_term_in_microarchive + K * V)
#         print word,p_w_dic[word],"calculate_p_w"
    return (p_w_dic, w_map_count, total_term_in_microarchive)

# 计算P(w|TS)
def calculate_p_w_ts(data_timespan_dic_cutted, w_map_count, total_term_in_microarchive):
    u = 500
    N = total_term_in_microarchive
    
    data_timespan_dic_p_w_ts = {}
    for time_span in data_timespan_dic_cutted:
        all_term_list = []
        for one_weibo_cutted in data_timespan_dic_cutted[time_span]:
            all_term_list.extend(one_weibo_cutted)
        all_term_set = set(all_term_list)
        ts_len = len(all_term_list)
            
        data_timespan_dic_p_w_ts[time_span] = {}
        re_map = data_timespan_dic_p_w_ts[time_span]
        for word in all_term_set:
            count = 0
            for term in all_term_list:
                if word == term:
                    count += 1
            re_map[word] = float(count + u * float(w_map_count[word] / N)) / float(ts_len + u)
#             print word,re_map[word],"calculate_p_w_ts"
    return data_timespan_dic_p_w_ts
        
# 计算 burstiness score
def calculate_burstiness_score(p_w_dic, data_timespan_dic_p_w_ts):
    result_map = {}
    for time_span in data_timespan_dic_p_w_ts:
        result_map[time_span]={}
        op = result_map[time_span]
        re_map = data_timespan_dic_p_w_ts[time_span]
        for word in re_map:
            re_map[word] = re_map[word] / p_w_dic[word]
            op[word] = re_map[word]
    return result_map
# 输出
def print_result(result_map):
    for time_span in result_map:
        re_map = result_map[time_span]
        keys = re_map.keys()
        keys.sort(lambda x, y:cmp(re_map[y], re_map[x]))
        print "*********************start************************************************"
        for i in range(10):
            print keys[i], re_map[keys[i]]
        print "*********************end************************************************"
    pass
    
#*******************************************************************************************************************************************

if __name__ == '__main__':
    data_dic = read_data_from_db()
    data_timespan_dic = time_span_setting(data_dic)
    merge_timespan(data_timespan_dic)
    data_timespan_dic_cutted, dic_set, dic_list = cut_weibo(data_timespan_dic)
    
    
    p_w_dic, w_map_count , total_term_in_microarchive = calculate_p_w(dic_set, dic_list)
    data_timespan_dic_p_w_ts = calculate_p_w_ts(data_timespan_dic_cutted, w_map_count, total_term_in_microarchive)
     
    result_map = calculate_burstiness_score(p_w_dic, data_timespan_dic_p_w_ts)
      
      
    print_result(result_map)    
    
    pass
