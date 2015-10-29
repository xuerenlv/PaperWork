# -*- coding: utf-8 -*-
'''
Created on Oct 28, 2015

@author: nlp
'''

import numpy as np
import random
import sys


# 谱聚类算法主体
def spectral_clustering(W, num_examples, k):
    # 计算 Laplacian 矩阵
    D = W.sum(axis=0)
    L = np.zeros((num_examples, num_examples))
    for i in range(num_examples):
        L[i][i] = D[i]
    L = L - W
    print "aaaaaaaaaaaaaaaaaa"
    eigenvalue, eigenvector = np.linalg.eig(L)
    
    print eigenvalue
    print eigenvector
    
    # 选择 k 个最小的特征值，对应的特征向量
    K_smallest_eigenvector = []
    eigenvalue_argsort = eigenvalue.argsort()
    for i in range(len(eigenvalue_argsort)):
        if eigenvalue_argsort[i] < k:
            K_smallest_eigenvector.append(eigenvector[i])

    # 生成新的 邻接矩阵    
    W_new = np.array(K_smallest_eigenvector).transpose()
    return k_means_second_version(W_new, k)
    

#****************************        k-means        **********************************
# k-means 算法主体   第二个版本：最多迭代20次
def k_means_second_version(file_list, k):
    k_central = []  # 选取k个中心
    central_map_example = {}  # 所属k个中心的example
    # 随机选择 k 个初始 example
    while len(k_central) < k:
        k_central.append(file_list[int(random.random() * len(file_list))])
    
    un_changled = False
    count = 0
    while not un_changled and count < 20:
        count += 1
        print count
        central_map_example = {}
        # 对于每一个example，计算其所属的类
        for index  in range(len(file_list)):
            one_example = file_list[index]
            index_cen = get_min_central(one_example, k_central)
            if not central_map_example.has_key(index_cen):
                central_map_example[index_cen] = []
            central_map_example[index_cen].append(index)
        # 生成新的聚类中心
        for i in xrange(k):
            orgin_central = k_central[i]
            new_central = gen_new_central(file_list, central_map_example[i])
            un_changled = True if list(new_central) == list(orgin_central) else False
            k_central[i] = new_central
    return central_map_example

# 根据所属的examples，生成新的聚类中心
def gen_new_central(file_list, central_map_example_index):
    belong_examples = []
    for i in central_map_example_index:
        belong_examples.append(file_list[i])
    belong_examples = np.array(belong_examples)
    M, N = belong_examples.shape
    new_centrals = belong_examples.sum(axis=0) / float(M)
    return list(new_centrals)

# 返回 one_example 与 k_central 中的哪一个中心点的 dist 最小
def get_min_central(one_example, k_central):
    min_dist = sys.maxint
    min_index = 0
    for i in xrange(len(k_central)):
        dist = dist_len(one_example, k_central[i]) 
        if dist < min_dist:
            min_dist = dist
            min_index = i
    return min_index
#*******************************************************************************************
#*****************         评价标准          **********************************

# confussion matrix
def gen_confusion_matrix(lable_list, result_central_map_example, cluster_num):
    # 初始化 m（i，j）二维数组
    gen_matrix = np.array([[0 for j in range(cluster_num)] for i in range(cluster_num)])
    
    for index in xrange(len(lable_list)):
        lable = int(lable_list[index])  if int(lable_list[index]) > 0 else 0

        for j_index in range(len(result_central_map_example)):
            if index in result_central_map_example[j_index]:
                gen_matrix[lable][j_index] += 1
    
    return gen_matrix
    

# purity
def gen_purity(lable_list, result_central_map_example, cluster_num, gen_matrix):
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
    return float(sum_val) / float(len(lable_list))

# Gini
def gen_gini(lable_list, result_central_map_example, cluster_num, gen_matrix):
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
    return float(fenzi_sum) / float(len(lable_list))

#****************************************************************************

# 生成邻接矩阵 W
def gen_weighted_matrix(file_list, n):
    num_examples = len(file_list)
    file_list = np.array(file_list)
    W = np.zeros((num_examples, num_examples))
    
    for i in range(num_examples - 1):
        for j in range(i + 1, num_examples):
            dist = dist_len(file_list[i], file_list[j])
            W[i][j] = dist
            W[j][i] = dist
    
    # n nearest neighbors
    # let W symmetric
    for i in range(num_examples):
        argsort = W[i].argsort()
        for j in range(num_examples):
            if argsort[j] <= n:
                W[i][j] = 1.0
                W[j][i] = 1.0
            elif  not W[i][j] == 1.0:
                W[i][j] = 0.0
    return W

# 返回 两个example的欧式距离
def dist_len(one_example, another_example):
    one_example = np.array(one_example)
    another_example = np.array(another_example)
    return ((one_example - another_example) ** 2).sum()

# 读文件 生成list［list［］］，里面的list代表文件的一行; list[] 代表第i行所属的类。
def read_file(file_name):
    file_list = []
    lable_list = []
    for line in open(file_name).readlines():
        arr_line = list(line.split(','));
        lable_list.append(arr_line[-1][:-1]);
        del arr_line[-1];
        file_list.append([float(one) if not one == '0' else 0.000001  for one in arr_line])
    return (file_list, lable_list)



if __name__ == '__main__':
    file_list, lable_list = read_file("german.txt")
    W = gen_weighted_matrix(file_list, 3)
    central_map_example = spectral_clustering(W, len(file_list), 2)
    gen_matrix = gen_confusion_matrix(lable_list, central_map_example, 2)
    purity = gen_purity(lable_list, central_map_example, 2, gen_matrix)
    gini = gen_gini(lable_list, central_map_example, 2, gen_matrix)
    print purity,gini
    
#     
#     print "1a"
#     file_list, lable_list = read_file("mnist.txt")
#     print "2a"
#     W = gen_weighted_matrix(file_list, 9)
#     print "3a"
#     central_map_example = spectral_clustering(W, len(file_list), 10)
#     print "4a"
#     gen_matrix = gen_confusion_matrix(lable_list, central_map_example, 10)
#     purity = gen_purity(lable_list, central_map_example, 10, gen_matrix)
#     gini = gen_gini(lable_list, central_map_example, 10, gen_matrix)
#     print purity, gini
    pass
