#coding:utf-8
"""
Program: 
Description: 
Author: cheng chuan - chengc@nlp.nju.edu.cn
Date: 2014-04-14 04:35:20
Last modified: 2014-04-14 05:28:52
Python release: 2.7.3
"""

import traceback
try:
    import threading
    import time
    from storage_manager import SinaweibosearchKeywords,\
        SinaweiosearchVips,AllKeywords
    from common_conf_manager import KEYWORD_DB_SCAN_INTERVAL
except ImportError as err:
    s = traceback.format_exc()
    print s
    
threadLock = threading.Lock()

class KeywordProcessor(threading.Thread):
    #need to configure
    DEFAUL_PAGE_NUMBER = 1
    
    def __init__(self, thread_name="keywrodprocessor"):
        
        threading.Thread.__init__(self)
        self.name = thread_name
        
        self.real_keyword_dic = {}
        self.hot_keyword_dic = {}
        
        self._access_db_for_real_keywords()
        self._access_db_for_hot_keywords()
        
        self.real_update = True
        self.hot_update = True
        
        self.vip_name_dic = {}
        
        self.vip_name_update = True
        
    def run(self):
        
        while(True):
            
            try:
                self._access_db_for_keywords()
            except:
                pass
            
            time.sleep(KEYWORD_DB_SCAN_INTERVAL)
    
    def get_keywords(self):
        keywords = set()
        
        for k in self.real_keyword_dic.keys():
            keywords.add(k)
            
        return keywords
    
    def get_real_keywords(self):
        keywords = set()
        
        for k in self.real_keyword_dic.keys():
            keywords.add(k)
            
        return keywords
    
    def get_hot_keywords(self):
        keywords = set()
        
        for k in self.hot_keyword_dic.keys():
            keywords.add(k)
            
        return keywords
    
    def set_real_update(self, update):
        global threadLock
        
        threadLock.acquire()
        
        self.real_update = update
        
        threadLock.release()
        
    def set_hot_update(self, update):
        global threadLock
        
        threadLock.acquire()
        
        self.hot_update = update
    
        threadLock.release()
        
    def _access_db_for_keywords(self):
        
        self._access_db_for_real_keywords()
        self._access_db_for_hot_keywords()
        
    def _access_db_for_real_keywords(self):
        
        keywords = AllKeywords.objects  # @UndefinedVariable
         
        new_dict = {}
        for keyword in keywords:
             
            new_dict[keyword.keywords] = keyword.def_page_num
         
        if new_dict != self.real_keyword_dic:
             
            self.real_keyword_dic = new_dict
             
            self.set_real_update(True)
            
    def _access_db_for_hot_keywords(self):
        keywords = AllKeywords.objects  # @UndefinedVariable
        
        new_dict = {}
        for keyword in keywords:
             
            new_dict[keyword.keywords] = keyword.def_page_num
         
        if new_dict != self.hot_keyword_dic:
             
            self.hot_keyword_dic = new_dict
             
            self.set_hot_update(True)
            
    def _access_db_for_vips(self):
        
        vips = SinaweiosearchVips.objects  # @UndefinedVariable
        
        pass 
    
    def add_real_keyword(self, keyword, def_page_num=DEFAUL_PAGE_NUMBER):
    
        self.real_keyword_dic[keyword] = def_page_num
        
    def remove_real_keyword(self, keyword):
    
        self.real_keyword_dic.pop[keyword]
        
    def add_hot_keyword(self, keyword, def_page_num=DEFAUL_PAGE_NUMBER):
    
        self.hot_keyword_dic[keyword] = def_page_num
        
    def remove_hot_keyword(self, keyword):
    
        self.hot_keyword_dic.pop[keyword]

keyword_processor = KeywordProcessor()
        
def get_keyword_processor():
    
    return keyword_processor
