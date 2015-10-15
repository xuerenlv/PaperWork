#encoding=utf8
'''
Created on 2014年4月23日

@author: cc
'''

import traceback

####################################URLWrapper Related#########################################
try:
    from advance_weibo_frame import URLWrapper
except:
    s = traceback.format_exc()
    
    print s
    
class HotTopicURLWrapper(URLWrapper):
    
    def __init__(self, keyword="", page_num=1):
        
        URLWrapper.__init__(self, URLWrapper.HOT_TOPIC_WEIBO)
        self.keyword = keyword
        self.page_num = page_num
        
    def tostring(self):
        
        pass
    
    def to_url(self):
        
        url = "http://huati.weibo.com/?refer=index_hot_new"
        
        url = "http://huati.weibo.com/?ctg1=99&ctg2=0&prov=0&sort=time&p=1&t=1"
        
#         url = "http://huati.weibo.com/aj_topiclist/big?ctg1=99&ctg2=0&prov=0&sort=time&p=1&t=1&_t=0&__rnd=1398256827879"#+str(int(time.time()*1000))
        
        return url
    
    def get_url_type(self):
        
        return self.url_type
    
###############################################################################################

####################################URLParser Related##########################################
try:
    import time
    
    from advance_weibo_frame import DOM_TREE_CONSTRUCT_ENCODE,\
        my_log,\
        PageParser
        
    from my_test import print_to_file
    
    from common_conf_manager import OPEN_WRITE_NOTUNIQUE_LOG
except:
    s = traceback.format_exc()
    
    print s

HOT_TOPIC_CONSTANT_DIC = {
                          u"":u""
                          }

class HotTopicXMLTreeParser:

    def __init__(self, topic):
        
        self.topic = topic
        
    def get_infors(self):
        rank = 0
        topic = ""
        url = ""
        num_infor = 0
        host = ""
        
        return [rank, topic, url, num_infor, host]

def find_inside_topic_trees(page):
    pass

def page_2_topic_trees(searchpage):
    
    return find_inside_topic_trees(searchpage)

class HotTopicPageParser(PageParser):
    
    def __init__(self, keyword=""):
        PageParser.__init__(self)
        
        self.keyword = keyword
    
    def parse(self, page, url_wrapper):
        
        search_url = url_wrapper.to_url()
        weibo_type = url_wrapper.get_url_type() 
        page_num = url_wrapper.page_num
        
        comment_trees = []
        crawl_feed_count = 0
        new_feed_count = 0   
        
        
        
        return [crawl_feed_count, new_feed_count]
    
###############################################################################################
####################################WeiboCrawler Related#######################################
try:
    from advance_weibo_frame import WeiboCrawler
    from my_exceptions import AdvKeywordPageGetException, HotTopicPageParseException
except:
    s = traceback.format_exc()
    
    print s
    
class HotTopicCrawler(WeiboCrawler):
    
    def __init__(self, url_wrapper, page_parser):
        
        WeiboCrawler.__init__(self, url_wrapper, page_parser)
    
    def crawl(self, wait_time):
        start_time = time.clock()
        
        crawl_feed_count = 0
        new_feed_count = 0
        
        try:
            page = self._get_page()
        except:
            end_time = time.clock()
            run_time = (int)((end_time + wait_time - start_time) * 1000)
            
        
            #need to log
            my_log.write_log(
                        log_type=self.url_wrapper.get_url_type(),
                        operation_status=0,
                        fail_code=AdvKeywordPageGetException.ERROR_CODE_DICT['urllib2 open failed'],
                        err_msg=self.url_wrapper.to_url(),
                        run_time=run_time
                        )
            
            return [ False, [] ]
        
        print_to_file("first hot topic.html", page)
        
        self.url_wrapper.url = "http://huati.weibo.com/?ctg1=3&ctg2=0&prov=0&sort=day&p=1"#&_t=0&__rnd=" + str(int(time.time()*1000))
        
        page = self._get_new_page()
        print_to_file("second hot topic.html", page)
        
        [ validity_check, error_code ]= self.page_validity_checker.check(page, self.url_wrapper.to_url())
    
        if not validity_check:
            end_time = time.clock()
            run_time = (int)((end_time + wait_time - start_time) * 1000)
             
            #need to log
            my_log.write_log(
                        log_type=self.url_wrapper.get_url_type(),
                        operation_status=0,
                        fail_code=error_code,
                        err_msg=self.url_wrapper.to_url(),
                        run_time=run_time
                        )
            
            return [ False, [] ]
        try:
            [crawl_feed_count, new_feed_count] = self.page_parser.parse(page, self.url_wrapper)
        except HotTopicPageParseException as err:
            end_time = time.clock()
            run_time = (int)((end_time + wait_time - start_time) * 1000)
            
            my_log.write_log(
                        log_type=self.url_wrapper.get_url_type(),
                        operation_status=0,
                        fail_code=err.get_error_code(),
                        err_msg=self.url_wrapper.to_url(),
                        run_time=run_time
                        )
            return [ True, [] ]
        
        end_time = time.clock()
        run_time = (int)((end_time + wait_time - start_time) * 1000)
        #need to log
#         my_log.write_log(
#                         log_type=self.url_wrapper.get_url_type(),
#                         operation_status=1,
#                         fail_code=0,
#                         err_msg=self.url_wrapper.to_url(),
#                         crawl_feed_count=crawl_feed_count,
#                         new_feed_count=new_feed_count,
#                         run_time=run_time
#                         )
        print "parse succeed"
        
        return [ True, [] ]
    
    def _get_new_page(self):
        import urllib2
        HTTP_HEADERS= {'User-Agent':'Mozilla/5.0 (X11; Linux i686; rv:8.0) Gecko/20100101 Firefox/8.0'}
        
        search_url = self.url_wrapper.to_url()
        
        searchreq = urllib2.Request(url = search_url, headers = HTTP_HEADERS)
#         searchreq.add_header('Accept-encoding','gzip')
        searchreq.add_header('Host','huati.weibo.com')
        searchreq.add_header('Connection','Keep-alive')
        searchreq.add_header('X-Requested-With','XMLHttpRequest')
        searchreq.add_header('Content-Type','application/x-www-form-urlencoded')
        
        try:
            webpage = urllib2.urlopen(searchreq)
            
        #for exception handle
        except :
            raise AdvKeywordPageGetException(AdvKeywordPageGetException.ERROR_CODE_DICT['urllib2 open failed'], search_url)
        
        import StringIO
        import gzip
        #decode gziped result 
        if webpage.info().get('Content-Encoding') == 'gzip':
            buf = StringIO(webpage.read())
            f = gzip.GzipFile(fileobj = buf)
            searchpage = f.read()
        else:
            #print 'webpage.info encoding : ',webpage.info().get('Content-Encoding')
            
            searchpage = webpage.read()

        return searchpage 
###############################################################################################
####################################DataStorer Related#########################################
try:
    from advance_weibo_frame import DataStorer
    from storage_manager import HotTopic as MongoHotTopic
    from mongoengine.errors import NotUniqueError, ValidationError, OperationError
    from my_exceptions import OtherException
except:
    s = traceback.format_exc()
    
    print s
    
class HotTopic:
    
    def __init__(self, rank, topic,  url, num_infor, host, page_num=1):
        
        self.rank = rank
        self.topic = topic
        self.url = url
        self.num_infor = num_infor
        self.host = host
        self.typeid = URLWrapper.HOT_TOPIC_WEIBO
    
class HotTopicStorer(DataStorer):
    
    def __init__(self, hot_topic):
        
        super.__init__(self)
        
        self.data = hot_topic
        
    def store(self):
        
        topic_2_store = MongoHotTopic()
        
        topic_2_store.rank = self.data.rank
        topic_2_store.topic = self.data.topic
        topic_2_store.url = self.data.url
        topic_2_store.num_infor = self.data.num_infor
        topic_2_store.host = self.data.host
        
        old_topic_in_store = MongoHotTopic.objects(topic=topic_2_store.topic)  # @UndefinedVariable
        
        if len(old_topic_in_store) is 0:
            try:
                topic_2_store.save()
                
                return True
             #need to log
            except NotUniqueError as err:
                if OPEN_WRITE_NOTUNIQUE_LOG:
                    my_log.write_notunique_log(
                                     log_id=self.data.topic,
                                     log_type=self.data.typeid,
                                     fail_code=OtherException.ERROR_CODE_DICT["weibo hot topic NotUniqueError"],
                                     keyword="",
                                     page_num=self.data.page_num
                                    )
                return False
            except ValidationError as err:
                if OPEN_WRITE_NOTUNIQUE_LOG:
                    my_log.write_notunique_log(
                                     log_id=self.data.topic,
                                     log_type=self.data.typeid,
                                     fail_code=OtherException.ERROR_CODE_DICT["weibo hot topic ValidationError"],
                                     keyword="",
                                     page_num=self.data.page_num
                                    )
                return False
            except OperationError as err:
                if OPEN_WRITE_NOTUNIQUE_LOG:
                    my_log.write_notunique_log(
                                     log_id=self.data.topic,
                                     log_type=self.data.typeid,
                                     fail_code=OtherException.ERROR_CODE_DICT["weibo hot topic OperationError"],
                                     keyword="",
                                     page_num=self.data.page_num
                                    )
                return False
            #need to log
            except Exception as err:
                if OPEN_WRITE_NOTUNIQUE_LOG:
                    my_log.write_notunique_log(
                                     log_id=self.data.topic,
                                     log_type=self.data.typeid,
                                     fail_code=OtherException.ERROR_CODE_DICT["weibo hot topic OtherError"],
                                     keyword="",
                                     page_num=self.data.page_num
                                    )
                return False
        else:
            #not unique, so record this duplicate
            if OPEN_WRITE_NOTUNIQUE_LOG:
                my_log.write_notunique_log(
                                     log_id=self.data.topic,
                                     log_type=self.data.typeid,
                                     fail_code=OtherException.ERROR_CODE_DICT["weibo hot topic NotUniqueError"],
                                     keyword="",
                                     page_num=self.data.page_num
                                    )
            
            return self._update(old_topic_in_store, topic_2_store, self.data)
        
    def _update(self, old_topic_in_store, topic_2_store, hot_topic):
        try:
            old_topic_in_store.update_one(
                                          set__rank=topic_2_store.rank,
                                          set__topic=topic_2_store.topic,
                                          set__url=topic_2_store.url,
                                          set__num_infor=topic_2_store.num_infor,
                                          set__host=topic_2_store.host
                                          )
        #need to log
        except NotUniqueError as err:
            if OPEN_WRITE_NOTUNIQUE_LOG:
                my_log.write_notunique_log(
                                     log_id=self.data.topic,
                                     log_type=self.data.typeid,
                                     fail_code=OtherException.ERROR_CODE_DICT["weibo hot topic NotUniqueError"],
                                     keyword="",
                                     page_num=self.data.page_num
                                    )
            return False
        except ValidationError as err:
            if OPEN_WRITE_NOTUNIQUE_LOG:
                my_log.write_notunique_log(
                                     log_id=self.data.topic,
                                     log_type=self.data.typeid,
                                     fail_code=OtherException.ERROR_CODE_DICT["weibo hot topic ValidationError"],
                                     keyword="",
                                     page_num=self.data.page_num
                                    )
            return False
        except OperationError as err:
            if OPEN_WRITE_NOTUNIQUE_LOG:
                my_log.write_notunique_log(
                                     log_id=self.data.topic,
                                     log_type=self.data.typeid,
                                     fail_code=OtherException.ERROR_CODE_DICT["weibo hot topic OperationError"],
                                     keyword="",
                                     page_num=self.data.page_num
                                    )
            return False
        #need to log
        except Exception as err:
            if OPEN_WRITE_NOTUNIQUE_LOG:
                my_log.write_notunique_log(
                                     log_id=self.data.topic,
                                     log_type=self.data.typeid,
                                     fail_code=OtherException.ERROR_CODE_DICT["weibo hot topic OtherError"],
                                     keyword="",
                                     page_num=self.data.page_num
                                    )
            return False
        
        return True
###############################################################################################
try:
    from storage_manager import connect_db
    from loginer import Loginer
except:
    s = traceback.format_exc()
    print s

if __name__ == '__main__':
    
    connect_db('test')
    
    wrapper = HotTopicURLWrapper()
    parser = HotTopicPageParser(wrapper)
    
    crawler = HotTopicCrawler(wrapper, parser)
    
    loginer = Loginer()
    
    print bool( loginer.login('chengchuan90@126.com','900119','./weibo_login_cookies.dat') )
    
    crawler.crawl(0)
