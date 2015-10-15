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
    
    def __init__(self,uid,nickname,is_auth,user_url,weibo_url,content,praise_num,retweet_num,comment_num,creat_time,all_weibo_num):
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
        return self.uid+'\t'+self.nickname+'\t'+self.is_auth+'\t'+self.weibo_url+'\t'+self.user_url+'\t'+\
            self.content+'\t'+self.praise_num+'\t'+self.retweet_num+'\t'+self.comment_num+'\t'+self.creat_time+'\t'+self.all_weibo_num
            

class Single_comment():
    
    def __init__(self,uid,nickname,auth,content,praise_num,creat_time):
        self.uid = uid
        self.nickname = nickname
        self.auth = auth
        self.content = content
        self.praise_num = praise_num
        self.creat_time = creat_time
    
    def to_string(self):
        return self.uid+'\t'+self.nickname+'\t'+self.auth+'\t'+self.content+'\t'+self.praise_num+'\t'+self.creat_time

class UserInfo():
        
    def __init__(self,uid_or_uname,nickname,is_persion,check_or_not,fensi):
        self.uid_or_uname = uid_or_uname
        self.nickname = nickname
        self.is_persion = is_persion
        self.check_or_not = check_or_not
        self.fensi = fensi

    def to_string(self):
        return self.uid_or_uname+'\t'+self.nickname+'\t'+self.is_persion+'\t'+self.check_or_not+'\t'+self.fensi


class UserInfo_loc():
    
    def __init__(self,uid,nickname,location,sex,birth,intro,check_or_not,check_info):
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
        print    "info:"+self.nickname
        print    "info:"+self.location 
        print    "info:"+self.sex 
        print    "info:"+self.birth 
        print    "info:"+self.intro 
        print "[是否验证：" + self.check_or_not+"]"


    def to_string(self):
        return "[昵称：" + self.nickname + "]" + "[所在地：" + self.location + "]" + "[性别：" + self.sex + "]"+ "[是否验证：" + self.check_or_not + "]"+ "[" + self.check_info + "]"+"[生日：" + self.birth + "]"+"[简介：" + self.intro + "]"





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
    uid_or_uname = StringField(unique=True)
    nickname = StringField()
    is_persion = StringField()
    check_or_not = StringField()
    fensi = StringField()

class Single_comment_store(Document):
    weibo_id = StringField()
    uid = StringField()
    nickname = StringField()
    auth = StringField()
    content = StringField()
    praise_num = StringField()
    creat_time= StringField()
        

class Single_weibo_store(Document):
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