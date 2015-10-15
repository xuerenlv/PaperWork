#coding:utf-8
"""
Program: 
Description: 
Author: cheng chuan - chengc@nlp.nju.edu.cn
Date: 2014-04-13 18:44:39
Last modified: 2014-04-14 06:28:29
Python release: 2.7.3
"""
'''
Created on 2014��4��5��

@author: cc
'''

import traceback

try:
    import logging
    from storage_manager import SINAWEIBOSEARCH_LOG_TABLE_NAME as sltn, \
            my_db_pool as mdp,\
            SINAWEIBOSEARCH_NOTUNIQUE_LOG_TABLE_NAME as snltn
            
except ImportError:
    s = traceback.format_exc()
    print s

scheduler_logger = logging.getLogger("schedulerLog")

class WeiboSearchLog:

    INSERT_LOG_SQL  = '''INSERT INTO ''' + sltn + '''(type, status, crawl_feed_count, new_feed_count, fail_code, err_msg, run_time) VALUES(%s, %s, %s, %s, %s, %s, %s)'''
    INSERT_NOTUNIQUE_LOG_SQL = '''INSERT INTO ''' + snltn + '''(id, type, fail_code, keyword, page_num) VALUES(%s, %s, %s, %s, %s)'''
    
    def __init__(self):

        pass

    def write_log(self, log_type, operation_status, fail_code, err_msg, crawl_feed_count=0, new_feed_count=0, run_time=0):

        con = mdp.connection()

        cur = con.cursor()

        try:
            cur.execute(WeiboSearchLog.INSERT_LOG_SQL, (log_type, operation_status, crawl_feed_count, new_feed_count, fail_code, err_msg, run_time, ))
        
            #need to faster
            con.commit()
            
        except:
            s = traceback.format_exc()
            
            scheduler_logger.warn(s)
            pass
        finally:    

            cur.close()
            con.close()
            
    def write_notunique_log(self, log_id, log_type, fail_code, keyword, page_num):
        
        con = mdp.connection()

        cur = con.cursor()

        try:
            cur.execute(WeiboSearchLog.INSERT_NOTUNIQUE_LOG_SQL, (log_id, log_type, fail_code, keyword, page_num, ))
        
            #need to faster
            con.commit()
        
        except:
            
            s = traceback.format_exc()
            
            scheduler_logger.warn(s)
            pass

        finally:    

            cur.close()
            con.close()
        

loger = WeiboSearchLog()

def get_log():
    global loger
    return loger
########################################################################################################################
########################################################################################################################

########################################################################################################################

if __name__ == "__main__":
#     logging.debug("for debug")
    pass