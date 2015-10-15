# encoding=utf8
'''
Created on 2014��4��20��

@author: cc
'''
import traceback
import os
import urllib
import re
import time

try:
    from bs4 import BeautifulSoup
    from mongoengine.errors import ValidationError, NotUniqueError, OperationError
    from advance_weibo_frame import URLWrapper, \
        PageParser, AdvKeywordCommentXMLTreeParser, page_2_comment_trees_adv, \
        AdvKeywordWeiboXMLTreeParser, get_weibo_url, page_2_weibo_trees_adv, \
        AdvWeiboComment, AdvWeibo, DataStorer, \
        WeiboCrawler, FIRST_PAGE_REGEX, COMMENT_PER_PAGE_NUMBER, \
        AdvKeywordWeiboStorer, \
        AdvKeywordWeiboCommentStorer

    from my_exceptions import AdvKeywordWeiboCommentPageParseException, AdvKeywordWeiboPageParseException, \
        AdvKeywordPageGetException, OtherException
    from my_log import get_log

    from conf import BOOL_GETCOMMENTS as IF_GETCOMMENTS
    from common_conf_manager import MAX_CRAWL_COMMENT_PAGE_NUMBER, \
        OPEN_WRITE_NOTUNIQUE_LOG
except ImportError as err:

    s = traceback.format_exc()

    print s

my_log = get_log()

BOOL_GETCOMMENTS = IF_GETCOMMENTS
##############################Implement Customized AdvKeywordHotURLWrapperGenerator##########################

class AdvKeywordHotURLWrapperGenerator:
    def __init__(self):
        pass

    def generate_first_page_url_adv_keyword_hot(self, keyword, max_page_num, start_time="", end_time=""):

        return AdvKeywordHotWeiboURLWrapper(keyword, start_time, end_time, str(1), str(max_page_num))

    def generate_follow_page_urls_adv_keyword_hot(self, url_wrapper, new_page_num):

        result = []

        keyword = url_wrapper.keyword
        page_num = new_page_num
        start_time = url_wrapper.start_time
        end_time = url_wrapper.end_time

        if int(url_wrapper.page_num) > 1 or (url_wrapper.is_first_parse is False):
            return result

        url_wrapper.is_first_parse = False
        max_page = int(page_num)

        for index in range(2, max_page + 1):
            result.append(
                AdvKeywordHotWeiboURLWrapper(keyword, start_time, end_time, str(index), url_wrapper.max_page_num))

        return result


url_wrapper_generator = AdvKeywordHotURLWrapperGenerator()


def get_url_wrapper_generator():
    return url_wrapper_generator


###############################################################################################

##############################Implement Customized URLWrapper##################################
class AdvKeywordHotWeiboURLWrapper(URLWrapper):
    def __init__(self, keyword, start_time, end_time, page_num, max_page_num='1'):
        '''
        Notice that page_num's type is string
        '''
        URLWrapper.__init__(self, URLWrapper.ADV_KEYWORD_HOT_WEIBO)
        self.keyword = keyword
        self.start_time = start_time
        self.end_time = end_time
        self.page_num = page_num
        self.max_page_num = max_page_num
        self.is_first_parse = True
        self.last_mid = '0'

    def tostring(self):

        return 'url_type:' + str(self.url_type) + '    ' \
               + 'keyword:' + str(self.keyword) + '    ' \
               + 'page number:' + str(self.page_num)

    def to_url(self):

        keyword_in_url = urllib.quote(str(self.keyword))

        url_part1 = 'http://s.weibo.com/weibo/' + keyword_in_url

        if self.start_time == "" and self.end_time == "":
            url_part2 = '&xsort=hot'
        else:
            url_part2 = '&xsort=hot&timescope=custom:' + self.start_time + ':' + self.end_time

        url_part3 = '&page=' + str(self.page_num)

        return url_part1 + url_part2 + url_part3


class AdvKeywordHotWeiboCommentURLWrapper(URLWrapper):
    def __init__(self, keyword='', mid='', uid='', page_num='', max_page_num=''):
        URLWrapper.__init__(self, URLWrapper.ADV_KEYWORD_HOT_WEIBO_COMMENT)
        self.keyword = keyword
        self.mid = mid
        self.uid = uid
        self.page_num = page_num
        self.max_page_num = max_page_num

    def tostring(self):
        return 'url_type:' + str(self.url_type) + '    ' \
               + 'keyword:' + str(self.keyword) + '    ' \
               + "mid:" + str(self.mid) \
               + 'uid:' + str(self.uid) + '    ' \
               + 'page number' + str(self.page_num)

    def to_url(self):
        url_part1 = 'http://weibo.com/aj/comment/big?_wv=5&id=' + self.mid
        url_part2 = '&filter=0&page=' + self.page_num

        return url_part1 + url_part2


###############################################################################################

##############################Implement Customized URLParser###################################
def comment_tree_2_comment_adv(keyword, comment_tree, comment_type, page_num):
    comment = AdvKeywordCommentXMLTreeParser(comment_tree)
    [cid, uid, nickname] = comment.get_cid()
    attached_mid = comment.get_attached_mid()
    content = comment.get_content()
    create_time = comment.get_create_time()

    return AdvWeiboComment(attached_mid, cid, uid, nickname, comment_type, keyword, page_num, content, create_time)


class AdvKeywordHotWeiboCommentParser(PageParser):
    def __init__(self, url_wrapper):

        PageParser.__init__(self, url_wrapper)

    def parse(self, page):
        url_wrapper = self.url_wrapper

        search_url = url_wrapper.to_url()
        comment_type = url_wrapper.get_url_type()
        page_num = url_wrapper.page_num

        comment_trees = []
        crawl_feed_count = 0
        new_feed_count = 0

        try:
            comment_trees = page_2_comment_trees_adv(page)
        #need to log
        except AdvKeywordWeiboCommentPageParseException as err:
            raise err

        if not comment_trees:
            return [crawl_feed_count, new_feed_count]

        for comment_tree in comment_trees:
            comment = None
            crawl_feed_count += 1

            try:
                comment = comment_tree_2_comment_adv(self.url_wrapper.keyword, comment_tree, comment_type, page_num)
                #need to log
            except AdvKeywordWeiboCommentPageParseException as err:
                my_log.write_log(
                    log_type=comment_type,
                    operation_status=0,
                    fail_code=err.get_error_code(),
                    err_msg=search_url
                )

            if not comment:
                continue

            storer = AdvKeywordHotWeiboCommentStorer(comment)

            if storer.store() is True:
                new_feed_count += 1

        return [crawl_feed_count, new_feed_count]


def weibo_tree_2_weibo_adv(keyword, weibo_tree, page_num, weibo_type):
    '''
    Transform the tree of a weibo into a weibo which is expressed in own weibo structure
    '''
    weibo = AdvKeywordWeiboXMLTreeParser(weibo_tree)

    #The following may raise AdvKeywordWeiboPageParseException
    mid = weibo.get_mid()
    uid = weibo.get_uid()
    nickname = weibo.get_nickname()
    keyword = keyword
    content = weibo.get_content()

    #The following will not raise AdvKeywordWeiboPageParseException
    is_forward = weibo.get_is_forward()
    original_ref = ''
    forward_uid = ''
    original_cntnt = ''
    url = get_weibo_url(uid, mid)
    if is_forward:
        original_ref = weibo.get_forward_ref()
        forward_uid = weibo.get_forward_uid()
        original_cntnt = weibo.get_forward_content()

    weiboinfo = weibo.get_stat_infor(is_forward)
    create_time = weiboinfo[0]
    n_like = int(weiboinfo[1])
    n_forward = int(weiboinfo[2])
    n_favorite = int(weiboinfo[3])
    n_comment = int(weiboinfo[4])

    result = AdvWeibo(mid=mid,
                      uid=uid,
                      nickname=nickname,
                      typeid=weibo_type,
                      keyword=keyword,
                      content=content,
                      create_time=create_time,
                      n_like=n_like,
                      n_forward=n_forward,
                      n_favorite=n_favorite,
                      n_comment=n_comment,
                      url=url,
                      page_num=page_num,
                      is_forward=is_forward,
                      forwarded_uid=forward_uid,
                      forwarded_ref=original_ref,
                      forwarded_content=original_cntnt)
    return result


class AdvKeywordHotWeiboParser(PageParser):
    def __init__(self, url_wrapper):
        PageParser.__init__(self, url_wrapper)

    def parse(self, page):
        '''
        Parse the page, store weibos into DB and return {weibo id, weibo comment number}
        If the trees getting failed(Exception), stop consequent processing and raise AdvKeywordWeiboPageParseException

        Return [crawl_feed_count, new_feed_count, {mid:n_comment}]
        '''
        url_wrapper = self.url_wrapper

        search_url = url_wrapper.to_url()
        weibo_type = url_wrapper.get_url_type()
        page_num = url_wrapper.page_num

        weibo_comment_infor = {}
        crawl_feed_count = 0
        new_feed_count = 0

        increment = 0
        increment_mark = True
        last_mid = '0'
        last_mid_mark = True

        weibo_trees = []
        try:
            weibo_trees = page_2_weibo_trees_adv(page)
        except AdvKeywordWeiboPageParseException as err:
            #for exception hanlde, if the weibo_trees parse failed, this page process failed
            raise err

        if not weibo_trees:
            return [crawl_feed_count, new_feed_count, weibo_comment_infor]

        for weibo_tree in weibo_trees:
            weibo = None
            crawl_feed_count += 1
            try:
                weibo = weibo_tree_2_weibo_adv(self.url_wrapper.keyword, weibo_tree, page_num, weibo_type)

            #need to log_type
            except AdvKeywordWeiboPageParseException as err:
                my_log.write_log(log_type=weibo_type,
                                 operation_status=0,
                                 fail_code=err.get_error_code(),
                                 err_msg=search_url)
            if not weibo:
                continue

            storer = AdvKeywordHotWeiboStorer(weibo)
            weibo_comment_infor[weibo.mid] = weibo.n_comment

            if storer.store() is True:
                new_feed_count += 1

            if last_mid_mark:
                last_mid = weibo.mid
                last_mid_mark = False

            if weibo.mid == self.url_wrapper.last_mid:
                increment_mark = False

            if increment_mark:
                increment += 1

        if increment < new_feed_count:
            increment = new_feed_count

        self.url_wrapper.last_mid = last_mid

        return [crawl_feed_count, new_feed_count, increment, weibo_comment_infor]


#############################################################################################

##############################Implement Customized WeiboCrawler################################

class AdvKeywordHotWeiboCommentCrawler(WeiboCrawler):
    def __init__(self, url_wrapper, page_parser, proxy_IP="", proxy_used=False, proxy_cookie_file=""):

        WeiboCrawler.__init__(self, url_wrapper, page_parser, proxy_IP, proxy_used, proxy_cookie_file)

    def crawl(self):
        '''
        For a url, request for the page, parse the page into comments, store these comments into DB.
        Return [ page_is_validity, page_error_code, is_crawl_success, crawl_error_code ]
        If page is validity, page_error_code is 0
        '''
        start_time = time.clock()
        wait_time = 0

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

            return [False, [], crawl_feed_count, new_feed_count]

        [validity_check, error_code] = self.page_validity_checker.check(page, self.url_wrapper.to_url())

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

            return [False, [], crawl_feed_count, new_feed_count]
        try:
            [crawl_feed_count, new_feed_count] = self.page_parser.parse(page)
        except AdvKeywordWeiboCommentPageParseException as err:
            end_time = time.clock()
            run_time = (int)((end_time + wait_time - start_time) * 1000)

            my_log.write_log(
                log_type=self.url_wrapper.get_url_type(),
                operation_status=0,
                fail_code=err.get_error_code(),
                err_msg=self.url_wrapper.to_url(),
                run_time=run_time
            )
            return [True, [], crawl_feed_count, new_feed_count]

        #this page is crawled successfully, store related information into the DB
        end_time = time.clock()
        run_time = (int)((end_time + wait_time - start_time) * 1000)
        #need to log
        my_log.write_log(
            log_type=self.url_wrapper.get_url_type(),
            operation_status=1,
            fail_code=0,
            err_msg=self.url_wrapper.to_url(),
            crawl_feed_count=crawl_feed_count,
            new_feed_count=new_feed_count,
            run_time=run_time
        )

        return [True, [], crawl_feed_count, new_feed_count]


class AdvKeywordHotWeiboCrawler(WeiboCrawler):
    def __init__(self, url_wrapper, page_parser, proxy_IP="", proxy_used=False, proxy_cookie_file=""):

        WeiboCrawler.__init__(self, url_wrapper, page_parser, proxy_IP, proxy_used, proxy_cookie_file)

    def crawl(self):
        '''
        For a url, request for the page, parse the page into weibos, store these weibos into DB.
        While parsing the page, get those comments number, construct AdvKeywordHotWeiboCommentURLWrapper and return those url_wrappers.
        If this url is the first page, also return the page number about this (keyword and this time interval)  
        Return [crawl_feed_count, new_feed_count, page_number, page_is_validity, page_error_code, is_crawl_success, crawl_error_code, [ new_url1, new_url2, ... ,new_urln ] ]
        crawl_feed_count: weibo number contained int this page
        new_feed_count: weibo number successfully parsed and stored into the database
        If page is validity, page_error_code is 0
        If page_numbre is -1, this url is not the first page for a keyword and it can be ignored
        '''
        start_time = time.clock()
        wait_time = 0

        crawl_feed_count = 0
        new_feed_count = 0
        increment = 0

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

            return [False, [], crawl_feed_count, new_feed_count, increment]

        if "noresult_tit" in page:
            print 'hot noresult'
            print self.url_wrapper.to_url()
            # if not os.path.exists('data/'):
            # os.mkdir('data')
            #
            #            num = len(os.listdir('data/'))
            #            with open('data/'+str(num+1)+'hot.html','w') as f:
            #                f.write(page)
            return [True, [], crawl_feed_count, new_feed_count, increment]

        [validity_check, error_code] = self.page_validity_checker.check(page, self.url_wrapper.to_url())

        weibo_type = self.url_wrapper.get_url_type()
        cur_url = self.url_wrapper.to_url()

        if not validity_check:

            #test start #
            if not os.path.exists('data/'):
                os.mkdir('data')

            num = len(os.listdir('data/'))
            with open('data/' + str(num + 1) + 'hot.html', 'w') as f:
                f.write(page)

            #test end"

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

            return [False, [], crawl_feed_count, new_feed_count, increment]

        page_number = -1

        if int(self.url_wrapper.page_num) is 1:

            try:
                page_number = self._howmanypgs(page)

            #need to log
            except AdvKeywordWeiboPageParseException as err:
                end_time = time.clock()
                run_time = (int)((end_time + wait_time - start_time) * 1000)

                my_log.write_log(
                    log_type=weibo_type,
                    operation_status=0,
                    fail_code=err.get_error_code(),
                    err_msg=cur_url,
                    run_time=run_time
                )

                return [False, [], crawl_feed_count, new_feed_count, increment]
        try:
            [crawl_feed_count, new_feed_count, increment, comment_dict] = self.page_parser.parse(page)
        except AdvKeywordWeiboPageParseException as err:
            end_time = time.clock()
            run_time = (int)((end_time + wait_time - start_time) * 1000)

            my_log.write_log(
                log_type=self.url_wrapper.get_url_type(),
                operation_status=0,
                fail_code=err.get_error_code(),
                err_msg=self.url_wrapper.to_url(),
                run_time=run_time
            )
            return [True, [], crawl_feed_count, new_feed_count, increment]

        #this page is crawled successfully, store related information into the DB
        end_time = time.clock()
        run_time = (int)((end_time + wait_time - start_time) * 1000)
        #need to log
        my_log.write_log(
            log_type=self.url_wrapper.get_url_type(),
            operation_status=1,
            fail_code=0,
            err_msg=self.url_wrapper.to_url(),
            crawl_feed_count=crawl_feed_count,
            new_feed_count=new_feed_count,
            run_time=run_time
        )
        new_url_list = []

        #if comment considered, the new comment URLWrapper should be return 
        if bool(BOOL_GETCOMMENTS):
            for key in comment_dict:

                mid = key
                n_comment = int(comment_dict[mid])

                if int(n_comment) is not 0:

                    max_page_number = (int(n_comment / COMMENT_PER_PAGE_NUMBER))

                    if (n_comment % COMMENT_PER_PAGE_NUMBER) is not 0:
                        max_page_number += 1

                    if MAX_CRAWL_COMMENT_PAGE_NUMBER < max_page_number:
                        max_page_number = MAX_CRAWL_COMMENT_PAGE_NUMBER

                    for pagenum in range(1, max_page_number + 1):
                        new_url_list.append(
                            AdvKeywordHotWeiboCommentURLWrapper(keyword=self.url_wrapper.keyword, mid=mid,
                                                                page_num=str(pagenum)))

        new_page_num = int(self.url_wrapper.max_page_num)

        if new_page_num > page_number:
            new_page_num = page_number

        #add the following new weibo URLWrappers
        for new_url in url_wrapper_generator.generate_follow_page_urls_adv_keyword_hot(self.url_wrapper, new_page_num):
            new_url_list.append(new_url)

        return [True, new_url_list, crawl_feed_count, new_feed_count, increment]

    def _howmanypgs(self, first_page):

        pagerange = '0'
        availablepgs = re.findall(FIRST_PAGE_REGEX, first_page)

        #for log handle
        #        if not availablepgs:
        # raise AdvKeywordWeiboPageParseException(AdvKeywordWeiboPageParseException.ERROR_CODE_DICT['get howmannypgs failed'])
        #
        # if len(availablepgs):
        #            pagerange = availablepgs[-2]
        if not availablepgs:
            pagerange = 1
        else:
            pagerange = availablepgs[-2]
        print "page_range", pagerange
        return int(pagerange)


#############################################################################################

##############################Implement Customized DataStorer##################################

class AdvKeywordHotWeiboCommentStorer(DataStorer):
    def __init__(self, adv_weibo_comment):
        DataStorer.__init__(self)

        self.data = adv_weibo_comment

    def store(self):
        storer = AdvKeywordWeiboCommentStorer(self.data)

        result = storer.store()

        return result


class AdvKeywordHotWeiboStorer(DataStorer):
    def __init__(self, adv_weibo):

        DataStorer.__init__(self)

        self.data = adv_weibo

    def store(self):

        storer = AdvKeywordWeiboStorer(self.data)

        result = storer.store()

        #         weibo_2_store = SingleWeiboAdvHot()
        #
        # weibo_2_store.mid = self.data.mid
        # weibo_2_store.uid = self.data.uid
        #         weibo_2_store.typeid = self.data.typeid
        #         weibo_2_store.keyword = self.data.keyword
        #         weibo_2_store.content = self.data.content
        #
        #         weibo_2_store.url = self.data.url
        #         weibo_2_store.is_forward = self.data.is_forward
        #         weibo_2_store.forward_uid = self.data.forwarded_uid
        #         weibo_2_store.original_ref = self.data.forwarded_ref
        #         weibo_2_store.original_cntnt = self.data.forwarded_content
        #
        #         weibo_2_store.create_time = self.data.create_time
        #         weibo_2_store.n_like = self.data.n_like
        #         weibo_2_store.n_forward = self.data.n_forward
        #         weibo_2_store.n_favorite = self.data.n_favorite
        #         weibo_2_store.n_comment = self.data.n_comment
        #
        #         old_weibo_in_store = SingleWeiboAdvHot.objects(mid=weibo_2_store.mid)  # @UndefinedVariable
        #
        #         self._save(old_weibo_in_store, weibo_2_store)

        return result

    def _save(self, old_weibo_in_store, weibo_2_store):
        if len(old_weibo_in_store) is 0:
            try:
                weibo_2_store.save()

                return True
            #need to log
            except NotUniqueError as err:
                if OPEN_WRITE_NOTUNIQUE_LOG:
                    my_log.write_notunique_log(
                        log_id=weibo_2_store.mid,
                        log_type=weibo_2_store.typeid,
                        fail_code=OtherException.ERROR_CODE_DICT["weibo store NotUniqueError"],
                        keyword=weibo_2_store.keyword,
                        page_num=self.data.page_num
                    )
                return False
            except ValidationError as err:
                if OPEN_WRITE_NOTUNIQUE_LOG:
                    my_log.write_notunique_log(
                        log_id=weibo_2_store.mid,
                        log_type=weibo_2_store.typeid,
                        fail_code=OtherException.ERROR_CODE_DICT["weibo store ValidationError"],
                        keyword=weibo_2_store.keyword,
                        page_num=self.data.page_num
                    )
                return False
            except OperationError as err:
                if OPEN_WRITE_NOTUNIQUE_LOG:
                    my_log.write_notunique_log(
                        log_id=weibo_2_store.mid,
                        log_type=weibo_2_store.typeid,
                        fail_code=OtherException.ERROR_CODE_DICT["weibo store OperationError"],
                        keyword=weibo_2_store.keyword,
                        page_num=self.data.page_num
                    )
                return False
            #need to log
            except Exception as err:
                if OPEN_WRITE_NOTUNIQUE_LOG:
                    my_log.write_notunique_log(
                        log_id=weibo_2_store.mid,
                        log_type=weibo_2_store.typeid,
                        fail_code=OtherException.ERROR_CODE_DICT["weibo store OtherError"],
                        keyword=weibo_2_store.keyword,
                        page_num=self.data.page_num
                    )
                return False
        else:
            #not unique, so record this duplicate
            if OPEN_WRITE_NOTUNIQUE_LOG:
                my_log.write_notunique_log(
                    log_id=weibo_2_store.mid,
                    log_type=weibo_2_store.typeid,
                    fail_code=OtherException.ERROR_CODE_DICT["weibo store NotUniqueError"],
                    keyword=weibo_2_store.keyword,
                    page_num=self.data.page_num
                )

            return self._update(old_weibo_in_store, weibo_2_store)

    def _update(self, old_weibo_in_store, weibo_2_store):
        '''
        If the mid is already in the DB, then update this weibo 
        '''
        #need to faster
        try:
            old_weibo_in_store.update_one(
                set__uid=weibo_2_store.uid,
                set__typeid=weibo_2_store.typeid,
                set__keyword=weibo_2_store.keyword,
                set__content=weibo_2_store.content,
                set__url=weibo_2_store.url,
                set__is_forward=weibo_2_store.is_forward,
                set__forward_uid=weibo_2_store.forward_uid,
                set__original_ref=weibo_2_store.original_ref,
                set__original_cntnt=weibo_2_store.original_cntnt,
                set__create_time=weibo_2_store.create_time,
                set__n_like=weibo_2_store.n_like,
                set__n_forward=weibo_2_store.n_forward,
                set__n_favorite=weibo_2_store.n_favorite,
                set__n_comment=weibo_2_store.n_comment
            )
        # need to log
        except NotUniqueError as err:
            if OPEN_WRITE_NOTUNIQUE_LOG:
                my_log.write_notunique_log(
                    log_id=weibo_2_store.mid,
                    log_type=weibo_2_store.typeid,
                    fail_code=OtherException.ERROR_CODE_DICT["weibo store NotUniqueError"],
                    keyword=weibo_2_store.keyword,
                    page_num=self.data.page_num
                )
            return False

        except ValidationError as err:
            if OPEN_WRITE_NOTUNIQUE_LOG:
                my_log.write_notunique_log(
                    log_id=weibo_2_store.mid,
                    log_type=weibo_2_store.typeid,
                    fail_code=OtherException.ERROR_CODE_DICT["weibo store ValidationError"],
                    keyword=weibo_2_store.keyword,
                    page_num=self.data.page_num
                )
            return False
        except OperationError as err:
            if OPEN_WRITE_NOTUNIQUE_LOG:
                my_log.write_notunique_log(
                    log_id=weibo_2_store.mid,
                    log_type=weibo_2_store.typeid,
                    fail_code=OtherException.ERROR_CODE_DICT["weibo store OperationError"],
                    keyword=weibo_2_store.keyword,
                    page_num=self.data.page_num
                )
            return False
        #need to log
        except Exception as err:
            if OPEN_WRITE_NOTUNIQUE_LOG:
                my_log.write_notunique_log(
                    log_id=weibo_2_store.mid,
                    log_type=weibo_2_store.typeid,
                    fail_code=OtherException.ERROR_CODE_DICT["weibo store OtherError"],
                    keyword=weibo_2_store.keyword,
                    page_num=self.data.page_num
                )

            return False

        return True

#############################################################################################

if __name__ == '__main':
    pass
