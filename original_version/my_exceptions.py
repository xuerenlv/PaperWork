# -*- coding: utf-8 -*-
'''
Created on 2014年3月22日

@author: cc
'''

class MyException(Exception):

    def __init__(self, error_code):
        
        self.error_code = error_code

    def get_error_code(self):

        pass

###################################################################################################################
class AdvKeywordWeiboPageParseException(MyException):
    ERROR_CODE_DICT = {
                       "total tree construct" : 1, 
                       "script find failed" : 2,
                       "content inside script find failed" : 3,
                       "weibo trees construct" : 4,
                       "get mid element failed" : 5,
                       "get mid attribute failed" : 6,
                       "get uid element failed" : 7,
                       "get uid attribute failed" : 8,
                       "get content element failed" : 9,
                       "get nickname failed" : 50,
                       "get is forward element failed" : 10,
                       "get forward uid element failed" : 11,
                       "get forward uid attribute failed" : 12,
                       "get howmannypgs failed" : 13
                       }    
    ERROR_CODE_2_DETAIL_DICT = {v:k for k,v in ERROR_CODE_DICT.items()}
    
    def __init__(self, error_code):
        
       MyException.__init__(self, error_code)

    def get_error_code(self):

        return self.error_code
class AdvKeywordPageGetException(MyException):
    ERROR_CODE_DICT = {
                       "urllib2 open failed" : 14,
                       "verification error" : 15,
                       "cookie outofdate error" : 16,
                       "pass certificate error" : 17,
                       "page not exist" : 18,
                       "connect to proxy failed" : 44
                       }
    ERROR_CODE_2_DETAIL_DICT = {v:k for k,v in ERROR_CODE_DICT.items()}
    
    def __init__(self, error_code, url = ""):
       
        MyException.__init__(self, error_code)

        self.url = url
    
    def get_error_code(self):

        return self.error_code

class AdvKeywordWeiboCommentPageParseException(MyException):
    ERROR_CODE_DICT = {
                       "total tree construct" : 19, 
                       "script find failed" : 20,
                       "content inside script find failed" : 21,
                       "comment trees construct" : 22,
                       "get cid element failed" : 23,
                       "get cid attribute failed" : 24,
                       "get attached mid element failed" : 25,
                       "get attached mid attribute failed" : 26,
                       "get content element failed" : 27,
                       "extract cid failed" : 28,
                       "get forward uid element failed" : 29,
                       "get forward uid attribute failed" : 30,
                       "get howmannypgs failed" : 31,
                       "JSON decoded failed" : 47,
                       "extract uid failed" : 48,
                       "extract nickname failed" : 49
                       }    
    ERROR_CODE_2_DETAIL_DICT = { v:k for k,v in ERROR_CODE_DICT.items() }
    
    def __init__(self, error_code):
        
        MyException.__init__(self, error_code) 

    def get_error_code(self):
    
        return self.error_code

class HotTopicPageParseException(MyException):
    ERROR_CODE_DICT = {
                       "XXX" : 45
                       }
    
    def __init__(self, error_code):
        super.__init__(self, error_code)
        
    def get_error_code(self):
        
        return self.error_code
###################################################################################################################
class ImportantPersonException(MyException):
    ERROR_CODE_DICT = {
                       "XXX" : 46
                       }
    
    def __init__(self, error_code):
        super.__init__(self, error_code)
        
    def get_error_code(self):
        
        return self.error_code
###################################################################################################################
###################################################################################################################
class OtherException(MyException):
    ERROR_CODE_DICT = {
                       "weibo store NotUniqueError" : 32,
                       "weibo store ValidationError" : 33,
                       "weibo store OperationError" : 34,
                       "weibo store OtherError" : 35,
                       "weibo comment store NotUniqueError" : 36,
                       "weibo comment store ValidationErron" : 37,
                       "weibo comment store OperationError" : 38,
                       "weibo comment store OtherError" : 39,
                       "weibo hot topic NotUniqueError" : 40,
                       "weibo hot topic ValidationError" : 41,
                       "weibo hot topic OperationError" : 42, 
                       "weibo hot topic OtherError" : 43
                        }

    def __init__(self, error_code):

        MyException.__init__(self, error_code)

    def get_error_code(self):

        return self.error_code
###################################################################################################################
