# -*- coding: utf-8 -*-
'''
Created on Oct 16, 2015

@author: nlp
'''
import os
from store_model import Single_weibo_store

import sys  
import traceback
reload(sys)  
sys.setdefaultencoding('utf8')   




if __name__ == '__main__':
    filelist = os.listdir('./china_hongkong_conflict_files')
    
    count = 0
    for file_name in filelist:
        for line in open('./china_hongkong_conflict_files/' + file_name, 'r').readlines():
            count+=1
            line_change = line.split(']')
            uid = ''
            nickname = ''
            is_auth = ''
            weibo_url = ''
            content = ''
        
            praise_num = ''
            retweet_num = ''
            comment_num = ''
        
            creat_time = ''
            
            for one in line_change:
                if 'uid:' in one:
                    uid = one[one.find(':') + 1:]
                if 'nickname:' in one:
                    nickname = one[one.find(':') + 1:]
                if 'is_auth:' in one:
                    is_auth = one[one.find(':') + 1:]
                if 'weibo_url:' in one:
                    weibo_url = one[one.find(':') + 1:]
                if 'content:' in one:
                    content = one[one.find(':') + 1:]
                    
                if 'praise_num:' in one:
                    praise_num = one[one.find(':') + 1:]
                if 'retweet_num:' in one:
                    retweet_num = one[one.find(':') + 1:]
                if 'comment_num:' in one:
                    comment_num = one[one.find(':') + 1:]
                    
                if 'creat_time:' in one:
                    creat_time = one[one.find(':') + 1:]
            print uid,nickname,is_auth
            print weibo_url
            print content
            print praise_num,retweet_num,comment_num
            print creat_time
            
            try:
                single_weibo = Single_weibo_store(uid, nickname, is_auth , weibo_url , content, praise_num , retweet_num, comment_num , creat_time)
                single_weibo.save()
            except:
                print traceback.format_exc()
    print count
    pass
