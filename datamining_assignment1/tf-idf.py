# -*- coding: utf-8 -*-
'''
Created on Sep 24, 2015

@author: xhj
'''

import os
import jieba
import codecs

import sys  
from cmath import log
reload(sys)  
sys.setdefaultencoding('utf8')   

#  读取一个文件，返回 每一行，对应的term,并去除停用词，与空格
def read_one_file(filename, stop_words_list):
    line_seg_list = []
    file_r = open('./lily/' + filename, 'r')
    for line in file_r.readlines():
        raw_list = jieba.cut(line[:-2])
        line_seg_list.append(remove_stop_words_and_space(raw_list, stop_words_list))
    return line_seg_list

# 读取 stop words
def read_stop_words():
    re_list = []
    file_r = codecs.open("Chinese-stop-words.txt", 'r', "utf-8")
    for line in file_r.readlines():
        re_list.append(line[:-2])
    return re_list

# 判断一个word是不是全是空格
def is_only_space(word):
    for i in xrange(0, len(word)):
        if word[i] != ' ':
            return False
    return True

# 判段 list 中是否包含 word
def is_contain(list, word):
    for wo in list:
        if wo == word:
            return True
    return False


# 对与一个 file list 中的所有内容，如果存在于 stop_words_list 中，则删除,(为空也删除)
def remove_stop_words_and_space(line_word_list, stop_words_list):
    re_list = []
    for wo in line_word_list:
        if  not (is_only_space(wo) or is_contain(stop_words_list, wo)):
            re_list.append(wo)
    return re_list



if __name__ == '__main__':
    filelist = os.listdir('./lily')
    all_files_map = {}
    stop_words_list = read_stop_words()
    
    print "第一步，加载文件,并去除停用词"
    for filename in filelist:
        all_files_map[filename[:-4]] = read_one_file(filename, stop_words_list)
    
    print "第二步，生成10个文件的词典"
    dic_10_file_idf_map = {}
    for filename in all_files_map:
        single_file_term_list = []
        for line_list in  all_files_map[filename]:
            single_file_term_list.extend(line_list)
            
        for term in set(single_file_term_list):
            if dic_10_file_idf_map.has_key(term):
                dic_10_file_idf_map[term] += 1
            else:
                dic_10_file_idf_map[term] = 1
    
    print "第三步，对于整个词典，计算idf"
    for term in dic_10_file_idf_map:
        dic_10_file_idf_map[term] = log(10.0 / (1 + float(dic_10_file_idf_map[term])))
        
        
    print "第四步，对于各个file的term list，统计个数"
    all_files_term_count_map = {}
    for filename in all_files_map:
        file_dict = {}
        for line_list in  all_files_map[filename]:
            for term in line_list:
                if file_dict.has_key(term):
                    file_dict[term] += 1
                else:
                    file_dict[term] = 1
        all_files_term_count_map[filename] = file_dict
        
    print "第五步，计算 tf，并进行规范化"
    for filename in all_files_term_count_map:
        file_term_sum = 0
        dic_one_file_term_map = all_files_term_count_map[filename]
        
        # # 计算总term的数量
        for term_key in dic_one_file_term_map:
            file_term_sum += dic_one_file_term_map[term_key]
        
        # # 计算tf，并纪录tf最大值，用于归一化
        max_tf = 0.0
        for term_key in dic_one_file_term_map:
            one_tf = float(dic_one_file_term_map[term_key]) / float(file_term_sum)
            if one_tf > max_tf:
                max_tf = one_tf
            dic_one_file_term_map[term_key] = one_tf
        
        # # 对tf值进行归一化
        for term_key in dic_one_file_term_map:
            one_tf = dic_one_file_term_map[term_key]
            dic_one_file_term_map[term_key] = 0.5 + (0.5 * one_tf) / max_tf
            
            
    print "第六步，计算 tf-idf"
    for filename in all_files_term_count_map:
        dic_one_file_term_map = all_files_term_count_map[filename]
        for term in dic_one_file_term_map:
            dic_one_file_term_map[term] = dic_one_file_term_map[term] * dic_10_file_idf_map[term]
        
    
    
    print "第七步，写入到文件中"
    if not os.path.exists('result/'):
        os.mkdir('result')
    li_10_file_dict_list = dic_10_file_idf_map.keys()  # # 词典list
    for filename in all_files_map:
        file_w = open("./result/" + filename + ".txt", 'a')
        dic_one_file_term_map = all_files_term_count_map[filename]
        for line_list in  all_files_map[filename]:
            line_term_str = ""
            for term in li_10_file_dict_list:
                if is_contain(line_list, term):
                    if len(line_term_str) != 0:
                        if dic_one_file_term_map[term] != 0.0:
                            line_term_str += " " + str(dic_one_file_term_map[term])[1:-4]
                        else:
                            line_term_str += " " + str(0)
                    else:
                        line_term_str = str(dic_one_file_term_map[term])
                else:
                    if len(line_term_str) != 0:
                        line_term_str += " " + str(0)
                    else:
                        line_term_str = str(0)
            line_term_str += '\n'
            file_w.write(line_term_str)
    pass
