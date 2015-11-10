# -*- coding: utf-8 -*-


'''
Created on Nov 9, 2015

@author: nlp
'''
import os
import codecs
import jieba
import pprint


# 判断这个词是不是无意义的
def prun(word):
    
    if word == u' ' or word == u'\t' or word == u'\r\n' or word == u'\r'or word == u'\n':
        return False
    
    if word == u'.' or word == u',' or word == u'，' or word == u'。' or word == u'[' or word == u']':
        return False
    
    if word == u'（' or word == u'）' or word == u'：' or word == u'；' or word == u'“' or word == u'”':
        return False
    
    if word == u'／' or word == u'》' or word == u'《' or word == u'‘' or word == u'’':
        return False
    
    return True

if __name__ == '__main__':
    filelist = os.listdir('./test2')
    file_write = codecs.open('merged_test2.txt', 'a', 'utf-8')
    
    count = 0
    for file_name in filelist:
        file_r = codecs.open('./test2/' + file_name, 'r', 'GBK')
        all_str = ""
        try:
            for line in file_r.readlines():
                all_str += line
            cut_words = [w for w in jieba.cut(all_str)  if prun(w)]
            file_write.write('[' + str(file_name) + "][" + ' '.join(cut_words) + ']\n')
        except:
            print file_name
    pass
