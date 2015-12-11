# -*- coding: utf-8 -*-
'''
Created on Dec 5, 2015

@author: xhj
'''
import csv


# 读取训练集
def read_train_file():
    csvfile = file('train.csv', 'rb')
    data_list = [] 
    lable_list = []
    feature_list = []
    reader = csv.reader(csvfile)
    count = 0
    for line in reader:
        if count == 0:
            feature_list.extend(line)
            count += 1
            continue
        data_list.append(line[:-1])
        lable_list.append(line[-1])
    csvfile.close() 
    return (data_list, lable_list, feature_list)

# 读取测试集
def read_test_file():
    csvfile = file('test.csv', 'rb')
    data_list = [] 
    reader = csv.reader(csvfile)
    count = 0
    for line in reader:
        if count == 0:
            count += 1
            continue
        data_list.append(line)
    csvfile.close() 
    return data_list

if __name__ == '__main__':
    data_list, lable_list, feature_list = read_train_file()
    print len(data_list), len(lable_list),len(feature_list)
    test_data_list = read_test_file()
    print len(test_data_list)
    pass
