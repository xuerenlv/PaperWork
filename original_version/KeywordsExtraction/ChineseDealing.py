# -*- coding: utf-8 -*- 
'''
Created on 2014年8月14日

@author: GreatShang
@environment: win7 sp1 64, eclipse 4.4, Pydev 3.6, Python 3.4
'''
import jieba
import codecs
import os
#idf.txt contains idf-score of Chinese words from jieba
#filePath =r'D:\My Data\SNAS\KeywordsExtraction'
#chinese_idf_content = open(r".\idf.txt",'rb').read().decode('utf-8')

curpath=os.path.normpath( os.path.join( os.getcwd(), os.path.dirname(__file__) ) ) 
chinese_idf_content = codecs.open(curpath+r"/idf.txt",'rb','utf-8')
lines = chinese_idf_content.readlines()

idf_freq = {}
for line in lines:
    word,freq = line.split(' ')
    idf_freq[word] = float(freq)

median_idf = sorted(idf_freq.values())[int(len(idf_freq)/2)]

#prepare Chinese stopwords list from chinesestopwords.txt
#chinese_stopwords_file = open(r'.\chinesestopwords.txt',encoding= 'utf8')
chinese_stopwords_file = codecs.open(curpath+r'/chinesestopwords.txt','r','utf8')
chinese_lines = chinese_stopwords_file.readlines()
chinese_stopwords_list = []
for eachline in chinese_lines:
    chinese_stopwords_list.append(eachline[:-1])  #the last sign is the change line
'''
#prepare English stopwords list from englishstopwords.txt if necessary
englist_stopwords_file = open('englishstopwords.txt')
englist_stopwords_list = []
for eachline in chinese_stopwords_file:
    englist_stopwords_list.append(eachline[:-1])
'''
def extract_tags(sentence,topK=10):
    words = jieba.cut(sentence)
    freq = {}
    for w in words:
        if len(w.strip())<2: continue
        if w.lower() in chinese_stopwords_list: continue
        if w.isdigit():continue
        freq[w]=freq.get(w,0.0)+1.0
    total = sum(freq.values())
    freq = [(k,v/total) for k,v in freq.items()]

    tf_idf_list = [(v * idf_freq.get(k,median_idf),k) for k,v in freq]
    st_list = sorted(tf_idf_list,reverse=True)

    top_tuples= st_list[:topK]
    tags = [a[1] for a in top_tuples]
    return tags

def extractWeiboTag(weiboContent):
    return extract_tags(weiboContent,3)

def extractForumTag(forumContent):
    if len(forumContent)<=200:
        return extract_tags(forumContent,3)
    else:
        return extract_tags(forumContent,5)

def extractNewsTag(newsContent):
    return extract_tags(newsContent,5)

