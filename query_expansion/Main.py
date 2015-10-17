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





#*********    第一个版本 完全按照《Structured event retrival over microblog archives》  *********************************************************
# 总共632天 每5天作为一个TimeSpan,  242(合并前)->135(合并后)

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
    while smallest_time + timedelta(days=4) <= largest_time:
        key = (smallest_time, smallest_time + timedelta(days=4))
        data_timespan_dic[key] = []
        for i in range(5):
            if data_dic.has_key(smallest_time + timedelta(days=i)):
                data_timespan_dic[key].extend(data_dic[smallest_time + timedelta(days=i)])
        if len(data_timespan_dic[key]) == 0:
            del data_timespan_dic[key]
        smallest_time += timedelta(days=5)
    if smallest_time <= largest_time:   
        key = (smallest_time, largest_time)
        data_timespan_dic[key] = []
        while smallest_time <= largest_time:
            data_timespan_dic[key].extend(data_dic[smallest_time])
            smallest_time += timedelta(days=1)
        if len(data_timespan_dic[key]) == 0:
            del data_timespan_dic[key]
    return data_timespan_dic

# 对于微博个数小于 5 的timespan，把这个timespan与前面一个相融合
def merge_timespan(data_timespan_dic):
    del_key = []
    for key in data_timespan_dic:
        if len(data_timespan_dic[key]) <= 5:
            start, end = key
            new_key = (start - timedelta(days=5), end - timedelta(days=5))
            if data_timespan_dic.has_key(new_key):
                data_timespan_dic[new_key].extend(data_timespan_dic[key])
                del_key.append(key)
    for key in data_timespan_dic:
        if len(data_timespan_dic[key]) <= 5:
            del_key.append(key)
    for key in set(del_key):
        del data_timespan_dic[key]

# 进行分词，使用结巴分词
# 返回的是 touple对象，(start，end)－－》list[list]，里面的list用来存储分词结果
# 返回在这些微博中的所有词
def cut_weibo(data_timespan_dic):
    dic_list = []
    for key in data_timespan_dic:
        list_in = []
        list_in.extend(data_timespan_dic[key])
        cut_list = []
        for one_weibo in list_in:
            cut = jieba.cut(one_weibo)
            cut_list.append(cut)
            dic_list.extend(cut)
        data_timespan_dic[key] = cut_list
    return set(dic_list)


# 计算P（w）
    

#*******************************************************************************************************************************************

if __name__ == '__main__':
    data_dic = read_data_from_db()
    data_timespan_dic = time_span_setting(data_dic)
    merge_timespan(data_timespan_dic)
    dic_list = cut_weibo(data_timespan_dic)
    
#     for word in dic_list:
#         print word
        
#     for datetime in data_dic:
#         print len(data_dic[datetime])
#     print len(data_dic)  # 总共632天
#     for datetime in data_timespan_dic:
#         print len(data_timespan_dic[datetime])
#         pprint.pprint(data_timespan_dic[datetime])
#     print len(data_timespan_dic)
    
    pass
