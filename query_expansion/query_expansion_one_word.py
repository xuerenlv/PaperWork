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
# data_dic 的键是： datetime对象，值是：在这一天之中发生的微博
def read_data_from_db():
    data_dic = {}
    for entry in Single_weibo_store.objects:
        datetime_obj = transform_time(entry['creat_time'])
        content = entry['content']
        if not data_dic.has_key(datetime_obj):
            data_dic[datetime_obj] = []
        data_dic[datetime_obj].append(pre_processing_content(content))
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
            # 转换出错，打印出原因
            for i in range(len(ori_time)):
                print ori_time[i]
            print traceback.format_exc()
    else:
        yue = ori_time[:ori_time.find(u'月')]
        ri = ori_time[len(yue) + 1:ori_time.find(u'日')]
        return datetime.datetime(2015, int(yue), int(ri))



# 对微博的content进行预处理
# 这里没做处理，当要进行处理时，直接添加代码即可
def pre_processing_content(ori_content):
    return ori_content




#*********    第一个版本 完全按照《Structured event retrival over microblog archives》  *********************************************************
# 总共632天 每5天作为一个TimeSpan,  242(合并前)->135(合并后)

# data_dic 为 time对象－－》list，里面装的是一条条微博
# 返回的是 touple对象，(start，end)－－》list，里面装的是一条条微博
def merge_data_dic(data_dic, n_days):
    # 获取开始时间与结束时间
    smallest_time = data_dic.keys()[0]
    largest_time = data_dic.keys()[0]
    for key in data_dic:
        if smallest_time > key:
            smallest_time = key
        if largest_time < key:
            largest_time = key
    
    # 对data_dic进行合并
    data_timespan_dic = {}
    while smallest_time + timedelta(days=n_days) <= largest_time:
        key = (smallest_time, smallest_time + timedelta(days=n_days))
        data_timespan_dic[key] = []
        for i in range(n_days + 1):
            if data_dic.has_key(smallest_time + timedelta(days=i)):
                data_timespan_dic[key].extend(data_dic[smallest_time + timedelta(days=i)])
        if len(data_timespan_dic[key]) == 0:
            del data_timespan_dic[key]
        smallest_time += timedelta(days=n_days + 1)
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
    
    print "******  merge timespan result ****"
    print "合并后，timespan个数：", len(data_timespan_dic)
    len_str = ""
    for key in data_timespan_dic:
        len_str += " , " + str(len(data_timespan_dic[key]))
    print len_str
    print "*********************************"
    
    return data_timespan_dic

# 对于微博个数小于 50 的timespan，把这个timespan删除掉
# 小数据，不具有影响力
def merge_timespan(data_timespan_dic):
    del_key = []
    for key in data_timespan_dic:
        if len(data_timespan_dic[key]) <= 50:
            del_key.append(key)
    for key in del_key:
        del data_timespan_dic[key]


# 进行分词，使用结巴分词
# 返回的是 touple对象，(start，end)－－》list[list]，里面的list用来存储分词结果
# dic_list ： 包含所有词的列表
# data_timespan_dic_cutted : 分词结果
def cut_weibo(data_timespan_dic):
    dic_list = []
    data_timespan_dic_cutted = {}
    for key in data_timespan_dic:
        data_timespan_dic_cutted[key] = []
        re_list = data_timespan_dic_cutted[key]
        for one_weibo in data_timespan_dic[key]:
            cut = [word for word in cut_filter(jieba.cut(one_weibo))]
            re_list.append(cut)
            dic_list.extend(cut)
    return (data_timespan_dic_cutted, set(dic_list), dic_list)

# 对结巴分词结果进行过滤
# 只有全是汉字的才返回
def cut_filter(cut):
    new_cut = []
    for word in cut:
        if is_all_chinese(word):
            new_cut.append(word)
    return new_cut

# 判断是不是全部为汉字
def is_all_chinese(word):
    for uchar in word:
        if uchar >= u'\u4e00' and uchar <= u'\u9fa5':
            pass
        else:
            return False
    return True

# 判断是不是全部为字母
def is_all_alpha(word):
    for one in word:
        if (one >= 'a' and one <= u'z') or (one >= 'A' and one <= u'Z'):
            pass
        else:
            return False
    return True

# 计算P(w)
# w_map_count ： 每一个 word 在微博分词结果中出现的次数
def calculate_p_w(dic_set, dic_list):
    p_w_dic = {}
    w_map_count = {}
    K = 10
    V = 25000
    N = len(dic_set)
    for word in dic_set:
        count = 0 
        for in_word in dic_list:
            if in_word == word:
                count += 1
        w_map_count[word] = count
        p_w_dic[word] = float(count + K) / float(N + K * V)
    return (p_w_dic, w_map_count, N)


# 计算P(w|TS i)
# data_timespan_dic_p_w_ts 的 key 是 time_span，值是一个map
# 里面的map，key是一个 word，值是 P(w|TS i)
def calculate_p_w_ts(data_timespan_dic_cutted, w_map_count, N):
    u = 500
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
    return data_timespan_dic_p_w_ts
        
        
# 计算 burstiness score
def calculate_burstiness_score(p_w_dic, data_timespan_dic_p_w_ts):
    result_map = {}
    for time_span in data_timespan_dic_p_w_ts:
        result_map[time_span] = {}
        op = result_map[time_span]
        re_map = data_timespan_dic_p_w_ts[time_span]
        for word in re_map:
            op[word] = re_map[word] / p_w_dic[word]
    return result_map


# 输出
def print_result(result_map):
    for time_span in result_map:
        re_map = result_map[time_span]
        keys = re_map.keys()
        keys.sort(lambda x, y:cmp(re_map[y], re_map[x]))
        print "*********************start************************************************"
        for i in range(50):
            print keys[i], re_map[keys[i]]
        print "*********************end************************************************"
    pass

# 输出到文件中
def print_result_to_file(result_map):
    file_w = open('result_one_word.txt', 'a')
    for time_span in result_map:
        re_map = result_map[time_span]
        keys = re_map.keys()
        keys.sort(lambda x, y:cmp(re_map[y], re_map[x]))
        file_w.write("*********************start************************************************" + '\n')
        for i in range(50):
            file_w.write(str(keys[i]) + "\t" + str(re_map[keys[i]]) + '\n')
        file_w.write("*********************end************************************************" + '\n')
    pass
    
#*******************************************************************************************************************************************

if __name__ == '__main__':
    data_dic = read_data_from_db()
    data_timespan_dic = merge_data_dic(data_dic,99)
    merge_timespan(data_timespan_dic)
    data_timespan_dic_cutted, dic_set, dic_list = cut_weibo(data_timespan_dic)
    
    p_w_dic, w_map_count , total_term_in_microarchive = calculate_p_w(dic_set, dic_list)
    data_timespan_dic_p_w_ts = calculate_p_w_ts(data_timespan_dic_cutted, w_map_count, total_term_in_microarchive)
     
    result_map = calculate_burstiness_score(p_w_dic, data_timespan_dic_p_w_ts)
      
      
    print_result(result_map)
    print_result_to_file(result_map)
    
    
    pass
