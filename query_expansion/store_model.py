'''
Created on Oct 16, 2015

@author: nlp
'''
from mongoengine.fields import StringField
from mongoengine.document import Document
from mongoengine.connection import connect




#weibo_xhj_fubai_11_07
#weibo_xhj_zhonggangmaodun
connect("weibo_xhj_fubai_11_07", host="114.212.191.119", port=27017)





class Single_weibo_store(Document):
    uid = StringField()
    nickname = StringField()
    is_auth = StringField()

    weibo_url = StringField()
    content = StringField()
        
    praise_num = StringField()
    retweet_num = StringField()
    comment_num = StringField()
        
    creat_time = StringField()
