# -*- coding: utf-8 -*-

'''
Created on Nov 12, 2015

@author: nlp
'''
import numpy as np
import random
import matplotlib.pyplot as plt

# Pegasos algorithm 按照要求，训练出10个 w
def Pegasos_algorithm(file_list, lable_list, lamda):
    m = len(file_list)
    T = 5 * m
    w = np.array([0.0 for i in range(len(file_list[0]))])
    w_list = []
    w_t_index = [int(i / 10.0 * T) for i in range(1, 11)]
    for iteration in xrange(1, T + 1):
        it = int(random.uniform(0, m))
        Xit = np.array(file_list[it])
        nt = 1.0 / float(lamda * iteration)
        if lable_list[it] * np.dot(Xit.transpose(), w) < 1:
            w = (1 - nt * lamda) * w + nt * lable_list[it] * Xit
        else:
            w = (1 - nt * lamda) * w
        if int(iteration) in w_t_index:
            w_list.append(w)
            
    return (w_list, w_t_index)




def predict(file_list, lable_list, w_list):
    right_rate_list = []
    for w in w_list:
        count_right = 0
        for index in xrange(len(file_list)):
            one_line = np.array(file_list[index])
            if np.dot(one_line.transpose(), w) > 0 and lable_list[index] > 0:
                count_right += 1
            if np.dot(one_line.transpose(), w) < 0 and lable_list[index] < 0:
                count_right += 1
        right_rate_list.append(1.0 - (float(count_right) / len(file_list)))
    return right_rate_list


# 读文件，返回 file_list 与 lable_list
def read_file(file_name):
    file_list = []
    lable_list = []
    for one_line in open(file_name).readlines():
        line_op = one_line[:-1].split(",")
        lable_list.append(int(line_op[-1]))
        del line_op[-1]
        file_list.append([int(one) for one in line_op])
    return (file_list, lable_list)


if __name__ == '__main__':
    a8a_training_file_list, a8a_training_lable_list = read_file("dataset1-a8a-training.txt")
    a8a_testing_file_list, a8a_testing_lable_list = read_file("dataset1-a8a-testing.txt")
    w_list, w_t_index = Pegasos_algorithm(a8a_training_file_list, a8a_training_lable_list, 0.0001)
    right_rate_list = predict(a8a_testing_file_list, a8a_testing_lable_list, w_list)
    
    print w_t_index
    print right_rate_list
    
    plt.figure(num='Hinge Loss Result',figsize=(20,8))
    plt.subplot(1, 2, 1)
    plt.plot(w_t_index, right_rate_list, 'r', linewidth=2.5, linestyle="-", label="dataset1-a8a")
    
    plt.xlim(min(w_t_index) * 0.9, max(w_t_index) * 1.1)
    plt.ylim(min(right_rate_list) * 0.9, max(right_rate_list) * 1.1)
    
    plt.title("dataset1-a8a predict result")
    plt.xlabel("number of iterations t")
    plt.ylabel("test error")
    plt.legend(loc='upper right', frameon=False)
    
    
#     plt.show()
    
    
    ## *******************************************************************************************
    a9a_training_file_list, a9a_training_lable_list = read_file("dataset1-a9a-training.txt")
    a9a_testing_file_list, a9a_testing_lable_list = read_file("dataset1-a9a-testing.txt")
    w_list, w_t_index = Pegasos_algorithm(a9a_training_file_list, a9a_training_lable_list, 0.00005)
    right_rate_list = predict(a9a_testing_file_list, a9a_testing_lable_list, w_list)
     
    print w_t_index
    print right_rate_list
    plt.subplot(1, 2, 2)
    plt.plot(w_t_index, right_rate_list, 'b', linewidth=2.5, linestyle="-", label="dataset2-a9a")
    
    plt.xlim(min(w_t_index) * 0.9, max(w_t_index) * 1.1)
    plt.ylim(min(right_rate_list) * 0.9, max(right_rate_list) * 1.1)
    
    plt.title("dataset2-a9a predict result")
    plt.xlabel("number of iterations t")
    plt.ylabel("test error")
    plt.legend(loc='upper right', frameon=False)
    
    
    plt.show()
#     
    pass
