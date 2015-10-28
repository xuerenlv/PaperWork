# -*- coding: utf-8 -*-
'''
Created on Oct 26, 2015

@author: nlp
'''

import random
import sys
import numpy as np

# 使 objective function 最小化
def minmize_objective_function(file_name, loop_time, k):
    file_list, lable_list = read_file(file_name)
    result_k_central = []
    result_central_map_example = {}
    obj_func = sys.maxint 
    for i in range(loop_time):
        this_dist = 0.0
        k_central, central_map_example = k_means_second_version(file_list, k)
        for j in range(k):
            for one_example in central_map_example[j]:
                this_dist += dist_len(one_example, k_central[j])
        if this_dist < obj_func:
            obj_func = this_dist
            result_k_central = k_central
            result_central_map_example = central_map_example
    return (file_list, lable_list, result_k_central, result_central_map_example, obj_func)

# k-means 算法主体   第二个版本：最多迭代20次
def k_means_second_version(file_list, k):
    k_central = []  # 选取k个中心
    central_map_example = {}  # 所属k个中心的example
    # 随机选择 k 个初始 example
    while len(k_central) < k:
        ran = int(random.random() * len(file_list))
        k_central.append(file_list[ran])
    
    un_changled = False
    count = 0
    while not un_changled and count < 20:
        count += 1
        print count, k_central[0]
        central_map_example.clear()
        # 对于每一个example，计算其所属的类
        for one_example in file_list:
            index_cen = get_min_central(one_example, k_central)
            if not central_map_example.has_key(index_cen):
                central_map_example[index_cen] = []
            central_map_example[index_cen].append(one_example)
        # 生成新的聚类中心
        for i in xrange(k):
            orgin_central = k_central[i]
            belong_examples = central_map_example[i]
            new_central = gen_new_central(belong_examples)
            if is_equals(new_central, orgin_central):
                un_changled = True
            else:
                un_changled = False
            k_central[i] = new_central
    return k_central, central_map_example


# k-means 算法主体   第一个版本：迭代直到聚类中心不再变化
def k_means(file_list, k):
    k_central = []  # 选取k个中心
    central_map_example = {}  # 所属k个中心的example
    # 随机选择 k 个初始 example
    while len(k_central) < k:
        ran = int(random.random() * len(file_list))
        k_central.append(file_list[ran])
    
    un_changled = False
    while not un_changled:
#         print len(k_central)
        print k_central[0]
        central_map_example.clear()
        # 对于每一个example，计算其所属的类
        for one_example in file_list:
            index_cen = get_min_central(one_example, k_central)
            if not central_map_example.has_key(index_cen):
                central_map_example[index_cen] = []
            central_map_example[index_cen].append(one_example)
        # 生成新的聚类中心
        for i in xrange(k):
            orgin_central = k_central[i]
            belong_examples = central_map_example[i]
            new_central = gen_new_central(belong_examples)
            if is_equals(new_central, orgin_central):
                un_changled = True
            else:
                un_changled = False
            k_central[i] = new_central
    return k_central, central_map_example

# 判断两个聚类中心是否相同
def is_equals(new_central, orgin_central):
    for i in xrange(len(new_central)):
        if not new_central[i] == orgin_central[i]:
            return False
    return True

# 根据所属的examples，生成新的聚类中心
def gen_new_central(belong_examples):
    new_centrals = []
    N = len(belong_examples)
    for i in xrange(len(belong_examples[0])):
        new_centrals.append(float(0))
        for one in belong_examples:
            new_centrals[i] += float(one[i])
    for i in xrange(len(new_centrals)):
        new_centrals[i] /= float(N)
    return new_centrals

# 返回 one_example 与 k_central 中的哪一个中心点的 dist 最小
def get_min_central(one_example, k_central):
    dist = {}
    for i in xrange(len(k_central)):
        dist[i] = dist_len(one_example, k_central[i])
    keys = dist.keys()
    keys.sort(lambda x, y:cmp(dist[x], dist[y]))
    return keys[0]

# 返回 两个example的欧式距离
def dist_len(one_example, another_example):
    dist_l = 0.0
    for i in xrange(len(one_example)):
        dist_l += (one_example[i] - another_example[i]) ** 2
    return dist_l

# 读文件 生成list［list［］］，里面的list代表文件的一行; list[] 代表第i行所属的类。
def read_file(file_name):
    file_list = []
    lable_list = []
    for line in open(file_name).readlines():
        arr_line = list(line.split(','));
        lable_list.append(arr_line[-1][:-1]);
        del arr_line[-1];
        file_list.append([float(one) for one in arr_line])
    return (file_list, lable_list)




#*****************         评价标准          **********************************

# confussion matrix
def gen_confusion_matrix(file_list, lable_list, result_central_map_example, cluster_num):
    # 初始化 m（i，j）二维数组
    gen_matrix = np.array([[0 for j in range(cluster_num)] for i in range(cluster_num)])
    
    for index in xrange(len(file_list)):
        lable = int(lable_list[index])  if int(lable_list[index]) > 0 else 0
        one_example = file_list[index]  
        for j_index in range(len(result_central_map_example)):
            if one_example in result_central_map_example[j_index]:
                gen_matrix[lable][j_index] += 1
    
    return gen_matrix
    

# purity
def gen_purity(file_list, lable_list, result_central_map_example, cluster_num, gen_matrix):
    p_j = [0 for i in range(cluster_num)]
    for j in range(cluster_num):
        max_m_i_j = 0
        for i in range(cluster_num):
            if gen_matrix[i][j] > max_m_i_j:
                max_m_i_j = gen_matrix[i][j]
        p_j[j] = max_m_i_j
    sum_val = 0
    for  x in p_j:
        sum_val += x
    return float(sum_val) / float(len(file_list))

# Gini
def gen_gini(file_list, lable_list, result_central_map_example, cluster_num, gen_matrix):
    g_j = [0 for i in range(cluster_num)]
    M_j = gen_matrix.sum(axis=0)
    for j in range(cluster_num):
        for i in range(cluster_num):
            g_j[j] += (float(gen_matrix[i][j]) / float(M_j[j])) ** 2
        g_j[j] = 1 - g_j[j]
    
    fenzi_sum = 0.0
    for j in range(cluster_num):
        M_j = len(result_central_map_example[j])
        fenzi_sum += g_j[j] * M_j
    return float(fenzi_sum) / float(len(file_list))

#****************************************************************************

if __name__ == '__main__':
    file_list, lable_list, result_k_central, result_central_map_example, obj_func = minmize_objective_function("german.txt", 10, 2)
    gen_matrix = gen_confusion_matrix(file_list, lable_list, result_central_map_example, 2)
    print obj_func
    purity = gen_purity(file_list, lable_list, result_central_map_example, 2, gen_matrix)
    gini = gen_gini(file_list, lable_list, result_central_map_example, 2, gen_matrix)
    print purity, gini
     
     
    file_list, lable_list, result_k_central, result_central_map_example, obj_func = minmize_objective_function("mnist.txt", 10, 10)
    gen_matrix = gen_confusion_matrix(file_list, lable_list, result_central_map_example, 10)
    print obj_func
    purity = gen_purity(file_list, lable_list, result_central_map_example, 10, gen_matrix)
    gini = gen_gini(file_list, lable_list, result_central_map_example, 10, gen_matrix)
    print purity, gini
    pass
