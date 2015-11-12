# -*- coding: utf-8 -*-

'''
Created on Nov 12, 2015

@author: nlp
'''
import numpy as np
import random

def Pegasos_algorithm(file_list, lable_list, lamda):
    m = len(file_list)
    T = 5 * m
    w = np.array([0.0 for i in range(len(file_list[0]))])
    for ieration in xrange(1, T + 1):
        it = int(random.uniform(0, m))
        Xit = np.array(file_list[it])
        nt = 1.0 / float(lamda * ieration)
        if lable_list[it] * np.dot(Xit.transpose(), w) < 1:
            w = (1 - nt * lamda) * w + nt * lable_list[it] * Xit
        else:
            w = (1 - nt * lamda) * w
    return w




def predict(file_list, lable_list, w):
    count_right = 0
    for index in xrange(len(file_list)):
        one_line = np.array(file_list[index])
        
        if np.dot(one_line.transpose(), w) > 0 and lable_list[index] > 0:
            count_right += 1
        if np.dot(one_line.transpose(), w) < 0 and lable_list[index] < 0:
            count_right += 1
        
    print float(count_right) / len(file_list)
    pass


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
    
    w = Pegasos_algorithm(a8a_training_file_list, a8a_training_lable_list, 0.0001)
    predict(a8a_testing_file_list, a8a_testing_lable_list, w)
    
    ## *******************************************************************************************
    a9a_training_file_list, a9a_training_lable_list = read_file("dataset1-a9a-training.txt")
    a9a_testing_file_list, a9a_testing_lable_list = read_file("dataset1-a9a-testing.txt")
    
    w = Pegasos_algorithm(a9a_training_file_list, a9a_training_lable_list, 0.00005)
    predict(a9a_testing_file_list, a9a_testing_lable_list, w)
    
    
    pass
