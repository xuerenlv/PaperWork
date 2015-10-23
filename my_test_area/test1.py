# -*- coding: utf-8 -*-

'''
Created on Oct 16, 2015

@author: nlp
'''

import sys  
import traceback
from store_model import Single_weibo_store
import datetime
from datetime import timedelta
import pprint
import jieba

reload(sys)  
sys.setdefaultencoding('utf8')   


def is_all_chinese(word):
    for uchar in word:
        if uchar >= u'\u4e00' and uchar<=u'\u9fa5':
            pass
        else:
            return False
    return True


def is_all_alpha(word):
    for one in word:
        if (one >= 'a' and one <= u'z') or (one >= 'A' and one <= u'Z'):
            pass
        else:
            return False
    return True

if __name__ == '__main__':
    x = '[timedelta'
    y = u'薛薛啊结构'
    print is_all_chinese(x)
    print is_all_chinese(y)
    pass
