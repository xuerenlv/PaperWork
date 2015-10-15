#encoding=utf8
'''
Created on 2014��5��13��

@author: cc
'''

import traceback
try:
    import threading
    import urllib2
    from StringIO import StringIO
    import gzip
    from random import randint
    import time
    import os
    
    from page_parser import parse_user_profile
    import storage 
    from errors import UnsuspectedPageStructError, JsonDataParsingError, URLError
    
    from loginer import get_loginer
    from common_conf_manager import MAX_RELOGIN_TRIAL_NUMBER
    from weibo_scheduler import normal_cookie_queue,\
        NormalCookieManager
    from advance_weibo_frame import page_validity_checker
except:
    s = traceback.format_exc()
    print s
    
MAXSLEEPINGTIME = 20
#########################################################################################################
class VipUrlWrapperListManager(threading.Thread):
    recycle_url_wrapper_list = []
    non_recycle_url_wrapper_list = []
    
    def __init__(self, thread_name="vip url wrapper list manager"):
        threading.Thread.__init__(self)
        self.name = thread_name
    
    def run(self):
        pass
#########################################################################################################

#########################################################################################################
loginer = get_loginer()
class PersonInforGetter(threading.Thread):
    
    def __init__(self, uid, thread_name="person information getter"):
        threading.Thread.__init__(self)
        self.name = thread_name
        self.uid= uid
        
    def run(self):
        
        print "before get size: " + str(normal_cookie_queue.qsize())
        [cur_username, cur_password, cur_cookie_file] = normal_cookie_queue.get()
        print cur_username, cur_password, cur_cookie_file
        print "after get size: " + str(normal_cookie_queue.qsize())
        
        uid = "1198367585"
        info = self.get_infor(uid, cur_username, cur_password, cur_cookie_file)
        user, create = storage.WeiboUser.objects.get_or_create(uid=uid)  # @UndefinedVariable
        if info:
            user.info = info
            print "Information fetching succeed - uid: %s" % uid
        else:
            print "Infromation fetching fail - uid: %s" % uid
            return 
        try:
            user.save()
        except Exception, e:
            print "Mongo Error"
    
    def crawl(self):
        print "before get size: " + str(normal_cookie_queue.qsize())
        [cur_username, cur_password, cur_cookie_file] = normal_cookie_queue.get()
        print cur_username, cur_password, cur_cookie_file
        print "after get size: " + str(normal_cookie_queue.qsize())
        
        uid = self.uid
        info = self.get_infor(uid, cur_username, cur_password, cur_cookie_file)
        user, create = storage.WeiboUser.objects.get_or_create(uid=uid)  # @UndefinedVariable
        if info:
            user.info = info
            print "Information fetching succeed - uid: %s" % uid
        else:
            print "Infromation fetching fail - uid: %s" % uid
            return 
        try:
            user.save()
        except Exception, e:
            print "Mongo Error"
            
    def get_infor(self, uid, cur_username, cur_password, cur_cookie_file, weibo_user_type=1001):
        """
        If get faild return None.
        """
        relog_trial = MAX_RELOGIN_TRIAL_NUMBER + 1
        info = None
        while relog_trial > 0:
            relog_trial -= 1
            if loginer.login(cur_username, cur_password, cur_cookie_file):
                    try:
                        url = 'http://weibo.com/' + uid + '/info'
                        html = self.urlfetch(url)
                    except URLError:
                        print "URLError! - url: %s" % url
                        time.sleep(randint(1, MAXSLEEPINGTIME))
                        continue
                    else:
                        try:
                            info = parse_user_profile(html, weibo_user_type)
                        except UnsuspectedPageStructError:
                            print "Unsuspected page structure! - url: %s" % url
                        else:
                            return info
            else:
                print "Login fail!"
                try:
                    os.remove(cur_cookie_file)
                except:
                    pass
        return info
            
    def urlfetch(self, url):
        '''
        open the url and return html, may raise URLError
        '''
        HTTP_HEADERS= {'User-Agent':'Mozilla/5.0 (X11; Linux i686; rv:8.0) Gecko/20100101 Firefox/8.0'}
        request = urllib2.Request(url, headers=HTTP_HEADERS)
        request.add_header('Accept-encoding', 'gzip')
        response = urllib2.urlopen(request)
        if response.info().get('Content-Encoding') == 'gzip':
            #print 'gzip'
            buf = StringIO(response.read())
            f = gzip.GzipFile(fileobj=buf)
            data = f.read()
            return data
        else:
            return response.read()
######################################################################################################### 

if __name__ == "__main__":
    threads = []
    
    threads.append(NormalCookieManager())
    threads.append(PersonInforGetter())
    
    for t in threads:
        print "thread " + t.name + " starts!"
        t.start()
        
    for t in threads:
        t.join()