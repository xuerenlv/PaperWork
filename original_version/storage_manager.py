#!/usr/bin/env python
# coding=utf-8

import traceback
import datetime
#############################################################################################################################################
#####################The following are codes about crawl log which are stored in the MySQL Database##########################################
try:

    import MySQLdb as mdb

    from DBUtils.PooledDB import PooledDB

   #the following modules come from my own
    from conf import LOGDB, LOGHOST, LOGUSER, LOGPW, CHARSET, MINCACHED,MAXCACHED,MAXCONNECTIONS, BLOCKING, MAXUSAGE, SETSESSION, RESET

    from common_conf_manager import DATABASE_SUFFIX
    #connect database named weibo in mysql server

except ImportError:
    
    s = traceback.format_exc()

    print s

my_db_pool = PooledDB(creator=mdb, 
                   mincached=MINCACHED,
                   maxcached=MAXCACHED,
                   maxconnections=MAXCONNECTIONS,
                   blocking=BLOCKING,
                   maxusage=MAXUSAGE,
                   setsession=SETSESSION,
                   reset=RESET,
                   host=LOGHOST, 
                   user=LOGUSER, 
                   passwd=LOGPW, 
                   db=LOGDB,
                   charset=CHARSET)

SINAWEIBOSEARCH_LOG_TABLE_NAME = '''sinaweibosearch_log'''
SINAWEIBOSEARCH_NOTUNIQUE_LOG_TABLE_NAME = '''sinaweibosearch_notunique_log'''

CREATE_LOG_TABLE_SQL = '''CREATE TABLE IF NOT EXISTS ''' + SINAWEIBOSEARCH_LOG_TABLE_NAME + '''(\
        log_id BIGINT PRIMARY KEY NOT NULL AUTO_INCREMENT,\
        type INT NOT NULL,\
        status INT NOT NULL,\
        crawl_feed_count INT NOT NULL DEFAULT 0,\
        new_feed_count INT NOT NULL DEFAULT 0,
        fail_code INT DEFAULT 1,\
        err_msg VARCHAR(256) DEFAULT '',\
        write_time TIMESTAMP NOT NULL,\
        run_time INT NOT NULL DEFAULT 0\
        )'''
        
CREATE_NOTUNIQUE_LOG_TABLE_SQL = '''CREATE TABLE IF NOT EXISTS ''' + SINAWEIBOSEARCH_NOTUNIQUE_LOG_TABLE_NAME + '''(\
        log_id BIGINT PRIMARY KEY NOT NULL AUTO_INCREMENT,\
        id VARCHAR(20) NOT NULL,\
        type INT NOT NULL,\
        keyword VARCHAR(40) NOT NULL, \
        fail_code INT NOT NULL, \
        page_num INT NOT NULL, \
        write_time TIMESTAMP NOT NULL
        )''' 
        
con = my_db_pool.connection()
cur = con.cursor()

try:
    cur.execute(CREATE_LOG_TABLE_SQL)
    cur.execute(CREATE_NOTUNIQUE_LOG_TABLE_SQL)
except:
    s = traceback.format_exc()
    print s
finally:
    cur.close()
    con.close()
    
#db_pool = PooledDB(mdb, mincached=MINCACHED, maxcached=MAXCACHED,  maxconnections=MAXCONNECTIONS, blocking=BLOCKING, maxusage=MAXUSAGE, setsession=SETSESSION, reset=RESET, host=LOGHOST, user=LOGUSER, passwd=LOGPW, db=LOGDB, charset=CHARSET)


#####################Codes about crawl log which are stored in the MySQL Database end########################################################
#############################################################################################################################################

#############################################################################################################################################
#####################The following are codes about advanced keyword weibo and comment which are stored in the mongodb########################
try:
    from mongoengine import connect, EmbeddedDocument, Document, FloatField, StringField, IntField, \
                BooleanField, DateTimeField, EmbeddedDocumentField, ListField

    from conf import DBNAME, DBHOST, DBPORT

except ImportError:

    s = traceback.format_exc()

    print s
####################The following are classes corresponding to advanced weibo searching's documents in mongo DB##########################
class Geo(EmbeddedDocument):
    longitude = FloatField()
    latitude = FloatField()
    location = StringField()

class SrcWeibo(EmbeddedDocument):
    uid = StringField()
    mid = StringField()
    content = StringField()

# class SingleWeiboAdvReal(Document):
#     mid = StringField(required=True,unique=True)
#     uid = StringField(required=True)
#     
#     typeid = IntField()
#     
#     keyword = StringField()
#     content = StringField()
# 
#     is_forward = BooleanField()
#     forward_uid = StringField()
#     original_ref = StringField()
#     original_cntnt = StringField()
# 
#     create_time = DateTimeField()
#     url = StringField()
#     geo = EmbeddedDocumentField(Geo)
# 
# #     search_url = StringField()
#     
#     n_like = IntField()
#     n_forward = IntField()
#     n_favorite = IntField()
#     n_comment = IntField()
# 
# 
# class CommentAdvReal(Document):
#     cid = StringField(required=True, unique=True)
#     attached_mid = StringField(required=True)
#     
#     content = StringField()
#     
#     create_time = StringField()
    
class SingleWeibo(Document):
    mid = StringField(required=True,unique=True)
    uid = StringField(required=True)
    nickname = StringField()
    typeid = IntField()
    keyword = ListField()
    content = StringField()
    is_forward = BooleanField()
    forward_uid = StringField()
    original_ref = StringField()
    original_cntnt = StringField()
    create_time = DateTimeField()
    url = StringField()
    geo = EmbeddedDocumentField(Geo)
#     search_url = StringField()
    n_like = IntField()
    n_forward = IntField()
    n_favorite = IntField()
    n_comment = IntField()


class CommentAdv(Document):
    cid = StringField(required=True, unique=True)
    attached_mid = StringField(required=True)
    uid = StringField()
    nickname = StringField()
    content = StringField()
    create_time = StringField()
    ori_uid = StringField()
    ori_nickname = StringField()
    
class RetweetAdv(Document):
    rid = StringField(required=True, unique=True)
    attached_mid = StringField(required=True)
    uid = StringField()
    nickname = StringField()
    content = StringField()
    create_time = StringField()
    ori_uid = StringField()
    ori_nickname = StringField()

# class SingleWeiboAdvHot(Document):
#     mid = StringField(required=True,unique=True)
#     uid = StringField(required=True)
#     
#     typeid = IntField()
#     
#     keyword = StringField()
#     content = StringField()
# 
#     is_forward = BooleanField()
#     forward_uid = StringField()
#     original_ref = StringField()
#     original_cntnt = StringField()
# 
#     create_time = DateTimeField()
#     url = StringField()
#     geo = EmbeddedDocumentField(Geo)
# 
# #     search_url = StringField()
#     
#     n_like = IntField()
#     n_forward = IntField()
#     n_favorite = IntField()
#     n_comment = IntField()
# 
# 
# class CommentAdvHot(Document):
#     cid = StringField(required=True, unique=True)
#     attached_mid = StringField(required=True)
#     
#     content = StringField()
#     
#     create_time = StringField()
    
class Log(Document):
    
    create_time = DateTimeField()
    
    is_successful = BooleanField()
    
    content = StringField()
    
class SinaweibosearchKeywords(Document):
    
    keywords = StringField(required=True,unique=True)
    
    def_page_num = IntField(required=True)
    
class AllKeywords(Document):
    keywords = StringField(required=True,unique=True)
    def_page_num = IntField(required=True)

class SinaweibosearchKeywordReal(Document):
    
    keywords = StringField(required=True,unique=True)
    
    def_page_num = IntField(required=True)
    
class SinaweibosearchKeywordHot(Document):
    
    keywords = StringField(required=True,unique=True)
    
    def_page_num = IntField(required=True)
    
class SinaweibosearchCurrentUrl(Document):
    
    keyword = StringField()
    
    url = StringField()
    
    cur_priority = IntField()
    
    counter = IntField()
    
class SinaweiosearchVips(Document):
    
    username = StringField()
    
    uid = StringField()
    
#######################################################################################################
###########################The following classes are about hot topic###################################
class HotTopic(Document):
    rank = IntField(required=True)
    topic = StringField(required=True)
    url = StringField(required=True)
    num_infor = IntField(required=True)
    host = StringField()


class ProxyIp(Document):
    ip = StringField(required=True, unique=True)

#######################################################################################################

def connect_db(dbsuffix=''):
    dbname = DBNAME + dbsuffix
    print 'dbname :',dbname
    try:
        connect(dbname, host=DBHOST, port=DBPORT)
    except:
        print 'Error connecting mongodb'
    return

# connect_db(DATABASE_SUFFIX)
connect_db()
#####################advanced keyword weibo and comment which are stored in the mongodb end##################################################
#############################################################################################################################################

if __name__ == '__main__':

    counter = 1    
    for weibo in SingleWeibo.objects():
        if counter > 10: 
            break
        
        counter += 1
        
        tags = []
        for keyword in weibo.keyword:
            tags.append(keyword)
            
        print " ".join(tags)
