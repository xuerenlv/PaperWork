# -*- coding: utf-8 -*-
'''
Created on Dec 12, 2015

@author: nlp
'''
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt





def read_file():
    file_content = pd.read_csv('train.csv')
#     print file_content.columns  获取列坐标
#     print file_content.index    获取行坐标
#     print list(file_content.tail(1)) 获取最后一行
#     print dict(file_content.loc[1])  #获取第一个对象
#     print dict(file_content.iloc[1]) #获取第一个对象
    
    
    pass


if __name__ == '__main__':
    read_file()
    pass