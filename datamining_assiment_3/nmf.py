# -*- coding: utf-8 -*-
'''
Created on Oct 27, 2015

@author: nlp
'''
import numpy as np
import math

# nmf 聚类主体
def nmf(file_list, k):
    X = np.array(file_list).transpose()
    m_x, n_x = X.shape
    
    # 随机生成初始矩阵
    U = np.random.rand(m_x, k) 
    V = np.random.rand(n_x, k)
    is_convergence = False
    count = 0
    while not is_convergence:
        count+=1
        U_old = U.copy()
        V_old = V.copy()
        
        X_V = np.dot(X, V)
        U_VT_V = np.dot(U, np.dot(V.transpose(), V))
        U = U * X_V / U_VT_V

        XT_U = np.dot(X.transpose(), U)
        V_UT_U = np.dot(V, np.dot(U.transpose(), U))
        V = V * XT_U / V_UT_U
        
        if abs((U - U_old).sum()) < 0.01 and abs((V - V_old).sum()) < 0.01:
            is_convergence = True
    
    # normalize U and V
    u_pow_2 = (U ** 2).sum(axis=0) 
    u_sqrt_pow_2 = [math.sqrt(w) for w in u_pow_2]
    for i in range(m_x):
            for j in range(k):
                U[i, j] = U[i, j] / u_sqrt_pow_2[j] 
    for i in range(n_x):
            for j in range(k):
                V[i, j] *= u_sqrt_pow_2[j] 
                
    # restlt_example_map_cluster
    restlt_example_map_cluster = {}
    for i in range(n_x):
        max_val = 0
        for j in range(k):
            if V[i][j] > max_val:
                max_val = V[i][j]
                restlt_example_map_cluster[i] = j

    return restlt_example_map_cluster

# 读文件 生成list［list［］］，里面的list代表文件的一行; list[] 代表第i行所属的类。
def read_file(file_name):
    file_list = []
    lable_list = []
    for line in open(file_name).readlines():
        arr_line = list(line.split(','));
        lable_list.append(arr_line[-1][:-1]);
        del arr_line[-1];
        file_list.append([float(one) if not one=='0' else 0.000001  for one in arr_line])
    return (file_list, lable_list)


#*****************         评价标准          **********************************
# purity
def gen_purity(file_list, lable_list, restlt_example_map_cluster, cluster_num):
    # 初始化 m（i，j）二维数组
    gen_matrix = [[0 for j in range(cluster_num)] for i in range(cluster_num)]
    
    for index in xrange(len(file_list)):
        lable = int(lable_list[index])  if int(lable_list[index]) > 0 else 0
        gen_matrix[lable][restlt_example_map_cluster[index]] += 1
    
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
def gen_gini(file_list, lable_list, restlt_example_map_cluster, cluster_num):
    # 初始化 m（i，j）二维数组
    gen_matrix = np.array([[0 for j in range(cluster_num)] for i in range(cluster_num)])
    
    for index in xrange(len(file_list)):
        lable = int(lable_list[index])  if int(lable_list[index]) > 0 else 0
        gen_matrix[lable][restlt_example_map_cluster[index]] += 1
    
    M_j = gen_matrix.sum(axis=0)
    g_j = [0 for i in range(cluster_num)]
    for j in range(cluster_num):
        for i in range(cluster_num):
            g_j[j] += (float(gen_matrix[i][j]) / float(M_j[j])) ** 2
        g_j[j] = 1 - g_j[j]
    
    fenzi_sum = 0.0
    for j in range(cluster_num):
        fenzi_sum += g_j[j] * M_j[j]
    return float(fenzi_sum) / float(len(file_list))

#****************************************************************************

def nmf_main(file_name,cluster_nums):
    file_list, lable_list = read_file(file_name)
    restlt_example_map_cluster = nmf(file_list, cluster_nums)
    purity = gen_purity(file_list, lable_list, restlt_example_map_cluster, cluster_nums)
    gini = gen_gini(file_list, lable_list, restlt_example_map_cluster, cluster_nums)
       
    print file_name,'purity:',purity, "gini:",gini

if __name__ == '__main__':
    nmf_main("german.txt", 2)
    
    nmf_main("mnist.txt", 10)
    pass
