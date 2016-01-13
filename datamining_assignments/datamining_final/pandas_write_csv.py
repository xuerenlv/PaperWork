# -*- coding: utf-8 -*-
'''
Created on Dec 20, 2015

@author: nlp
'''
import pandas as pd
from sklearn.feature_extraction import DictVectorizer
from sklearn.cross_validation import train_test_split
from sklearn import cross_validation
from sklearn.naive_bayes import GaussianNB
from sklearn import tree
from sklearn.ensemble import RandomForestClassifier
from sklearn import svm
import datetime
import numpy as np
import matplotlib.pyplot as plt


if __name__ == '__main__':
    a_dic = {}
    a_dic['A'] = [23, 543, 6545]
    a_dic['B'] = [1223, 324, 4353]
    data_fra = pd.DataFrame(a_dic)
    print data_fra
    data_fra.to_csv('te.csv', index=False)
    pass
