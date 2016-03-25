# -*- coding: utf-8 -*-


'''
Created on 2015-08-21

@author: xhj
'''
from mongoengine.connection import connect
from config_operation import DB_HOST, DB_PORT, DBNAME
from mongoengine.document import Document
from mongoengine.fields import StringField


import sys  
reload(sys)  
sys.setdefaultencoding('utf8')   


class SingleWeibo():
    
    def __init__(self, uid, nickname, is_auth, user_url, weibo_url, content, praise_num, retweet_num, comment_num, creat_time, all_weibo_num):
        self.uid = uid
        self.nickname = nickname
        self.is_auth = is_auth
        self.user_url = user_url
        self.weibo_url = weibo_url
        self.content = content
        
        self.praise_num = praise_num
        self.retweet_num = retweet_num
        self.comment_num = comment_num
        
        self.creat_time = creat_time
        self.all_weibo_num = all_weibo_num
        
    def to_string(self):
        return self.uid + '\t' + self.nickname + '\t' + self.is_auth + '\t' + self.weibo_url + '\t' + self.user_url + '\t' + \
            self.content + '\t' + self.praise_num + '\t' + self.retweet_num + '\t' + self.comment_num + '\t' + self.creat_time + '\t' + self.all_weibo_num

# 单独的一条微博，有转发信息，@信息，＃信息            
class SingleWeibo_with_more_info():
    
    def __init__(self, uid, nickname, is_auth, user_url, weibo_url, content, praise_num, retweet_num, comment_num, creat_time, all_weibo_num, come_from_user_id,come_from_nickname, come_from_url, come_from_user_is_V, at_info, hash_info, original_retweet_num, original_praise_num, original_comment_num, retweet_reason,retweet_reason_hash_tag,retweet_reason_at_info):
        self.uid = uid
        self.nickname = nickname
        self.is_auth = is_auth
        self.user_url = user_url
        self.weibo_url = weibo_url
        self.content = content
        
        self.praise_num = praise_num
        self.retweet_num = retweet_num
        self.comment_num = comment_num
        
        self.creat_time = creat_time
        self.all_weibo_num = all_weibo_num
        
        self.come_from_user_id = come_from_user_id
        self.come_from_nickname = come_from_nickname
        self.come_from_url = come_from_url
        self.come_from_user_is_V = come_from_user_is_V
        
        self.at_info = at_info
        self.hash_info = hash_info
        
        self.original_retweet_num = original_retweet_num
        self.original_praise_num = original_praise_num
        self.original_comment_num = original_comment_num
        self.retweet_reason = retweet_reason
        
        self.retweet_reason_hash_tag = retweet_reason_hash_tag
        self.retweet_reason_at_info = retweet_reason_at_info
        
    def to_string(self):
        return self.uid + '\t' + self.nickname + '\t' + self.is_auth + '\t' + self.weibo_url + '\t' + self.user_url + '\t' + \
            self.content + '\t' + self.praise_num + '\t' + self.retweet_num + '\t' + self.comment_num + '\t' + self.creat_time + '\t' + \
            self.all_weibo_num + '\t' + self.come_from + '\t' + self.at_info + '\t' + self.hash_info



class Single_comment():
    
    def __init__(self, uid, nickname, auth, content, praise_num, creat_time):
        self.uid = uid
        self.nickname = nickname
        self.auth = auth
        self.content = content
        self.praise_num = praise_num
        self.creat_time = creat_time
    
    def to_string(self):
        return self.uid + '\t' + self.nickname + '\t' + self.auth + '\t' + self.content + '\t' + self.praise_num + '\t' + self.creat_time

class UserInfo():
        
    def __init__(self, uid_or_uname, nickname, is_persion, check_or_not, fensi,sex,location,check_info,weibo_all_nums,guan_zhu_nums):
        self.uid_or_uname = uid_or_uname
        self.nickname = nickname
        self.is_persion = is_persion
        self.check_or_not = check_or_not
        self.fensi = fensi
        self.sex = sex
        self.location = location
        self.check_info = check_info
        self.weibo_all_nums = weibo_all_nums
        self.guan_zhu_nums = guan_zhu_nums

    def to_string(self):
        return self.uid_or_uname + '\t' + self.nickname + '\t' + self.is_persion + '\t' + self.check_or_not + '\t' + self.fensi


class UserInfo_loc():
    
    def __init__(self, uid, nickname, location, sex, birth, intro, check_or_not, check_info):
        self.uid = uid
        self.nickname = nickname
        self.location = location
        self.sex = sex
        self.birth = birth
        self.intro = intro
        self.check_or_not = check_or_not
        self.check_info = check_info
        pass
    
    def print_self(self):
        print    "info:" + self.nickname
        print    "info:" + self.location 
        print    "info:" + self.sex 
        print    "info:" + self.birth 
        print    "info:" + self.intro 
        print "[是否验证：" + self.check_or_not + "]"


    def to_string(self):
        return "[昵称：" + self.nickname + "]" + "[所在地：" + self.location + "]" + "[性别：" + self.sex + "]" + "[是否验证：" + self.check_or_not + "]" + "[" + self.check_info + "]" + "[生日：" + self.birth + "]" + "[简介：" + self.intro + "]"





connect(DBNAME, host=DB_HOST, port=int(DB_PORT))
#############################   存到mongodb   #############################################
class UserInfo_loc_store(Document):
    uid = StringField()
    nickname = StringField()
    location = StringField()
    sex = StringField()
    birth = StringField()
    intro = StringField()
    check_or_not = StringField()
    check_info = StringField()

class UserInfo_store(Document):
    meta = {'collection': 'user_info_all_store'}
    uid_or_uname = StringField(unique=True)
    nickname = StringField()
    is_persion = StringField()
    check_or_not = StringField()
    fensi = StringField()
    
    sex= StringField()
    location= StringField()
    check_info= StringField()
    weibo_all_nums= StringField()
    guan_zhu_nums= StringField()

class Single_comment_store(Document):
    weibo_id = StringField()
    uid = StringField()
    nickname = StringField()
    auth = StringField()
    content = StringField()
    praise_num = StringField()
    creat_time = StringField()
        

class Single_weibo_store(Document):
    meta = {'collection': 'single_weibo_store_three_0'}
    uid = StringField()
    nickname = StringField()
    is_auth = StringField()
    user_url = StringField()
    weibo_url = StringField(unique=True)
    content = StringField(unique=True)
        
    praise_num = StringField()
    retweet_num = StringField()
    comment_num = StringField()
        
    creat_time = StringField()
    all_weibo_num = StringField()
    
class Single_weibo_with_more_info_store(Document):
    meta = {'collection': 'zhuanjiyin_2012_01_01_to_2012_06_01_f_1'}
    uid = StringField()
    nickname = StringField()
    is_auth = StringField()
    user_url = StringField()
    weibo_url = StringField()
    content = StringField()
        
    praise_num = StringField()
    retweet_num = StringField()
    comment_num = StringField()
        
    creat_time = StringField()
    all_weibo_num = StringField()

    come_from_user_id = StringField()
    come_from_nickname = StringField()
    come_from_url = StringField()
    come_from_user_is_V = StringField()
        
    at_info = StringField()
    hash_info = StringField()
        
    original_retweet_num = StringField()
    original_praise_num = StringField()
    original_comment_num = StringField()
    retweet_reason = StringField()
    retweet_reason_hash_tag = StringField()
    retweet_reason_at_info = StringField()