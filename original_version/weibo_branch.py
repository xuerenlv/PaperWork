#encoding=utf8
'''
Created on 2014��6��9��

@author: cc
'''

import datetime
from pymongo import MongoClient
from time import sleep
import threading
import time
from collections import defaultdict

from conf import DBHOST, DBPORT
from common_conf_manager import USERS_INFOR_SCAN_INTERVAL
import traceback
import KeywordsExtraction.ChineseDealing


client = MongoClient(DBHOST, DBPORT)

threadLock = threading.Lock()

class UserKeywordProcessor(threading.Thread):

    def __init__(self, thread_name="user keyword processor"):

        threading.Thread.__init__(self)
        self.name = thread_name


    def run(self):
        global keyword_user_dict

        while(True):

            tmp_keyword_user_dic= keyword_user()

            if threadLock.acquire():
                keyword_user_dict = tmp_keyword_user_dic
                threadLock.release()

            time.sleep(USERS_INFOR_SCAN_INTERVAL)

def keyword_user():
#    users_db = client["users_database"]
#    users_collections = users_db["all_registered_users"]
#    #print users_collections.count()
#
#    user_dict = {user["user_db"]:user["user_keywords"] for user in users_collections.find()}
#    #print user_dict
#
#    keywords_all = []
#    user_keyword_dict = defaultdict(list)
#    for user_db in user_dict:
#        keywords = [item["keywords"] for item in users_db[user_dict[user_db]].find()]
#        user_keyword_dict[user_db]=keywords
#        keywords_all.extend(keywords)
#    keywords_all = list(set(keywords_all))
#
#    keyword_user_dict = defaultdict(list)
#    for keyword in keywords_all:
#        for user_db in user_keyword_dict:
#            if keyword in user_keyword_dict[user_db]:
#                keyword_user_dict[keyword].append(user_db)
#    return keyword_user_dict
    all_users_db = client['all_users_db']
    users_collections = all_users_db['all_users_info']

    all_keywords_collections = all_users_db['all_keywords']
    all_keywords = [keyword_document['keywords'] for keyword_document in all_keywords_collections.find()]

    #print all_keywords
    keyword_user_dict = defaultdict(list)
    for keyword in all_keywords:
        for user in users_collections.find():
            if 'u_mongodb' not in user:
                continue
            user_db = user['u_mongodb']
            if user_db != '':
                user_keywords = [user_keywords_document['keywords'] for user_keywords_document in client[user_db].user_keywords.find() ]
                if keyword in user_keywords:
                    keyword_user_dict[keyword].append(user_db)
    return keyword_user_dict


keyword_user_dict = keyword_user()

def branch_weibo(weibo_2_store):
    weibo = {}
    weibo['mid'] = str(weibo_2_store.mid)
    weibo['uid'] = str(weibo_2_store.uid)
    weibo['typeid'] = int(weibo_2_store.typeid)
    weibo['keyword'] = weibo_2_store.keyword
    weibo['content'] = str(weibo_2_store.content)
    weibo['is_forward'] = bool(weibo_2_store.is_forward)
    weibo['forward_uid'] = str(weibo_2_store.forward_uid)
    weibo['original_ref'] = str(weibo_2_store.original_ref)
    weibo['original _cntnt'] = str(weibo_2_store.original_cntnt)

    date_time = str(weibo_2_store.create_time).split(' ')
    d = date_time[0].split('-')
    t = date_time[1].split(':')
    weibo['create_time'] = datetime.datetime(year=int(d[0]), month=int(d[1]), day=int(d[2]), hour=int(t[0]), minute=int(t[1]))
    weibo['time'] = str(weibo['create_time'])

    weibo['url'] = str(weibo_2_store.url)
    weibo['n_like'] = int(weibo_2_store.n_like)
    weibo['n_forward'] = int(weibo_2_store.n_forward)
    weibo['n_favorite'] = int(weibo_2_store.n_favorite)
    weibo['n_comment'] = int(weibo_2_store.n_comment)
    weibo['source'] = 'weibo'
    weibo['sentiment'] = 0
    weibo['attention'] = 0.0
    try:
        weibo['weibo_keywords'] = KeywordsExtraction.ChineseDealing.extractWeiboTag(weibo['content'])
    except:
        s = traceback.format_exc()
        weibo['weibo_keywords'] = []
        print s

    weibo_keywords = weibo["keyword"]

    if threadLock.acquire():
        all_keywords = keyword_user_dict.keys()
        threadLock.release()

        for weibo_keyword in weibo_keywords:
            if weibo_keyword in all_keywords:
                user_db_list = keyword_user_dict[weibo_keyword]

                for user_db in user_db_list:
                    user_data_db = client[user_db]
                    user_weibo = user_data_db["user_weibo"]

                    if not user_data_db.user_weibo.find_one({"mid":weibo["mid"]}):
                        user_weibo.insert(weibo)

user_keyword_processor = UserKeywordProcessor()

def get_user_keyword_processor():
    global user_keyword_processor

    return user_keyword_processor

if __name__ == "__main__":

    processor = get_user_keyword_processor()

    processor.start()
