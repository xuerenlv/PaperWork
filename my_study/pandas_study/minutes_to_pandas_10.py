# -*- coding: utf-8 -*-
'''
Created on Dec 11, 2015

@author: nlp
'''

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt



def plot_1():
    ts = pd.Series(np.random.randn(1000), index=pd.date_range('1/1/2000', periods=1000))
    ts = ts.cumsum()
    ts.plot()
    pass


def test1():
    dates = pd.date_range('20130101', periods=6)
    print dates
    
    df = pd.DataFrame(np.random.randn(6,4), index=dates, columns=list('ABCD'))
    print df
    
    df2 = pd.DataFrame({ 'A' : 1.,
                        'B' : pd.Timestamp('20130102'),
                        'C' : pd.Series(1,index=list(range(4)),dtype='float32'),
                        'D' : np.array([3] * 4,dtype='int32'),
                        'E' : pd.Categorical(["test","train","test","train"]),
                        'F' : 'foo' })
    print df2
    
    print df.describe()
    
if __name__ == '__main__':
#     test1()
    plot_1()
    pass