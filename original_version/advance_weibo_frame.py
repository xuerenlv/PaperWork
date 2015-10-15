#encoding=utf8
'''
Created on 2014��4��20��

@author: cc
'''
import traceback

from my_test import print_to_file


try:
    import requests  # @UnresolvedImport
    import cookielib
    
    from storage_manager import SingleWeibo,CommentAdv,RetweetAdv
    from mongoengine.errors import ValidationError, NotUniqueError, OperationError  # @UnresolvedImport
    from my_exceptions import OtherException
    from keyword_processor import keyword_processor
    from common_conf_manager import OPEN_WRITE_NOTUNIQUE_LOG,\
        GET_PAGE_TIMEOUT
        
    from weibo_branch import branch_weibo
    from bs4 import BeautifulSoup
except:
    s = traceback.format_exc()
    
    print s
    
####################################URLWrapper Related#########################################
class URLWrapper:
    
    ADV_KEYWORD_REAL_WEIBO = 1
    ADV_KEYWORD_REAL_WEIBO_COMMENT = 2
    ADV_KEYWORD_HOT_WEIBO = 3
    ADV_KEYWORD_HOT_WEIBO_COMMENT = 4
    HOT_TOPIC_WEIBO = 5
    ADV_KEYWORD_REAL_WEIBO_RETWEET = 6

    def __init__(self, url_type):
        
        self.url_type = url_type
    
    def tostring(self):
        
        pass
    
    def to_url(self):
        
        pass
    
    def get_url_type(self):

        return self.url_type
###############################################################################################

####################################URLParser Related##########################################
try:
    #parser related
    import re
    import json
    from lxml import etree
    from base62 import mid2url

    from my_exceptions import AdvKeywordWeiboPageParseException,AdvKeywordWeiboCommentPageParseException#, OtherException
    from my_log import get_log
except ImportError:

    s = traceback.format_exc()

    #need to process
    print s
    
#need to configure
DOM_TREE_CONSTRUCT_ENCODE = 'utf-8'

my_log = get_log()

class PageParser:
    def __init__(self, url_wrapper):
        self.url_wrapper = url_wrapper
        
        pass
    def parse(self, page):
        
        pass
#########################################高级搜索中单纯的评论获取, 开始############################################ 
ADV_KEYWORD_COMMENT_CONSTANT_DIC = {
                                    u"script" : u"/descendant::script",
                                    u"inside html mark" : u"PRF_modwrap PRF_onefeed clearfix",
                                    u"inside html regex" : u"view\((\{.*\})\)",
                                    u"single comment path" : u"/descendant::dl[@class='comment_list S_line1']",
                                    u"cid path" : u"/descendant::a[@action-type='replycomment']",
                                    u"cid attribute" : u"action-data",
                                    u"attached mid path" : u"/descendant::dl[@class='comment_list S_line1']",
                                    u"attached mid attribute" : u"mid",
                                    u"content path" : u"/descendant::dd/a",
                                    u"create time path" : u"/descendant::dd/span[@class='S_txt2']"
                                      }

class AdvKeywordCommentXMLTreeParser:
    '''
    This class maintains a comment's HTML tree and parses it to provide useful fields
    '''
    #need to faster
    def __init__(self, comment):
        self.comment = comment

    def get_cid(self):
        '''
        Raise AdvKeywordWeiboCommentPageParseException
        '''
        nrt_elmt_list = self.comment.xpath(ADV_KEYWORD_COMMENT_CONSTANT_DIC[u'cid path'] + '[1]')
        #for exception handle
        if len(nrt_elmt_list) is 0:
            raise AdvKeywordWeiboCommentPageParseException(AdvKeywordWeiboCommentPageParseException.ERROR_CODE_DICT['get cid element failed'])
        nrt_elmt = nrt_elmt_list[0]
        #for exception handle
        if not(ADV_KEYWORD_COMMENT_CONSTANT_DIC[u'cid attribute'] in nrt_elmt.attrib):
            raise AdvKeywordWeiboCommentPageParseException(AdvKeywordWeiboCommentPageParseException.ERROR_CODE_DICT[u'get cid attribute failed'])
        txt = nrt_elmt.get(ADV_KEYWORD_COMMENT_CONSTANT_DIC[u'cid attribute'])
        cid = self._extract_cid(txt)
        uid = self._extract_uid(txt)
        nickname = self._extract_nickname(txt)
        
        if cid ==  '-1':
            raise AdvKeywordWeiboCommentPageParseException(AdvKeywordWeiboCommentPageParseException.ERROR_CODE_DICT['extract cid failed'])
            cid = ""
        if uid == '-1':
            raise AdvKeywordWeiboCommentPageParseException(AdvKeywordWeiboCommentPageParseException.ERROR_CODE_DICT['extract uid failed'])
            uid = ""
        if nickname == '-1':
            raise AdvKeywordWeiboCommentPageParseException(AdvKeywordWeiboCommentPageParseException.ERROR_CODE_DICT['extract nickname failed'])
            nickname = ""
        return [ cid, uid, nickname ]

    def _extract_cid(self, text):
        #HTML relevant
        result = '-1'
        p = re.compile('cid[ ]*=[ ]*([0-9]+)')
        cid = p.search(text).group(1)
        if cid is not None:
            result = cid
        return result
    
    def _extract_uid(self, text):
        res = '-1'
        p = re.compile('ouid[ ]*=[ ]*([0-9]+)')
        uid = p.search(text).group(1)
        if uid is not None:
            res = uid
        return res
    
    def _extract_nickname(self,text):
        res = '-1'
        p = re.compile('&content[ ]*=[ ]*([^&]*)&')
        nickname = p.search(text).group(1)
        if nickname is not None:
            res = nickname
        return res
    
    def get_attached_mid(self):
        '''
        Raise AdvKeywordWeiboCommentPageParseException
        '''
        nrt_elmt_list = self.comment.xpath(ADV_KEYWORD_COMMENT_CONSTANT_DIC[u'attached mid path'] + '[1]')
        #for exception handle
        if len(nrt_elmt_list) is 0:
            raise AdvKeywordWeiboCommentPageParseException(AdvKeywordWeiboCommentPageParseException.ERROR_CODE_DICT[u'get attached mid element failed'])
        nrt_elmt = nrt_elmt_list[0]
        #for exception handle
        if not(ADV_KEYWORD_COMMENT_CONSTANT_DIC[u'attached mid attribute'] in nrt_elmt.attrib):
            raise AdvKeywordWeiboCommentPageParseException(AdvKeywordWeiboCommentPageParseException.ERROR_CODE_DICT[u'get attached mid attribute failed'])
        return nrt_elmt.get(ADV_KEYWORD_COMMENT_CONSTANT_DIC[u'attached mid attribute'])

    def get_content(self):
        '''
        Raise AdvKeywordWeiboCommentPageParseException
        '''
        nrt_elmt_list = self.comment.xpath(ADV_KEYWORD_COMMENT_CONSTANT_DIC[u"content path"])
        if len(nrt_elmt_list) is 0:
            raise AdvKeywordWeiboCommentPageParseException(AdvKeywordWeiboCommentPageParseException.ERROR_CODE_DICT[u'get content element failed'])
        result = ""
        for nrt_elmt in nrt_elmt_list:
#             etree_string = etree.tostring(nrt_elmt_list[0])
#             print etree_string
#             raw_input("press any key to continue")
            #need to process
            result += etree.tostring(nrt_elmt, method='text', encoding=DOM_TREE_CONSTRUCT_ENCODE)
        return result #''.join(result)

    def get_create_time(self):
        nrt_elmt_list = self.comment.xpath(ADV_KEYWORD_COMMENT_CONSTANT_DIC[u'create time path'] + '[1]')
        if len(nrt_elmt_list) is 0:
            return ''   
        nrt_elmt = nrt_elmt_list[0]
        return nrt_elmt.text[1:-1]
def find_inside_comment_trees_adv(page):
    '''
    Raise AdvKeywordWeiboCommentPageParseException
    '''
    inside_comment_trees = []
    
    try:
        
        key_values = json.loads(page)
        inner_html_text = key_values.get('data').get('html')
    except ValueError:
        
        raise AdvKeywordWeiboCommentPageParseException(AdvKeywordWeiboCommentPageParseException.ERROR_CODE_DICT['JSON decoded failed'])
    
    weibos_tree = etree.fromstring( inner_html_text, etree.HTMLParser() )
    if weibos_tree is None:
        raise AdvKeywordWeiboCommentPageParseException(AdvKeywordWeiboCommentPageParseException.ERROR_CODE_DICT['comment trees construct'])
    for weibo_tree in weibos_tree.xpath( ADV_KEYWORD_COMMENT_CONSTANT_DIC[u'single comment path']):
        #need to faster
        inside_comment_trees.append( etree.fromstring( etree.tostring(weibo_tree), etree.HTMLParser() ) )
    #for exception handle
    if len(inside_comment_trees) is 0:
        raise AdvKeywordWeiboCommentPageParseException(AdvKeywordWeiboCommentPageParseException.ERROR_CODE_DICT['comment trees construct'])
    return inside_comment_trees

def page_2_comment_trees_adv(page):
    
    trees = find_inside_comment_trees_adv(page)
    
    return trees

#########################################高级搜索中单纯的评论获取, 结束############################################ 
#########################################高级搜索中单纯的微博（不含评论）获取, 开始############################################    
ADV_KEYWORD_WEIBO_CONSTANT_DICT = {
                        u"script" : u"/descendant::script",
                        u"inside html mark" : u"search_feed\\\"",
                        u"inside html regex" : u"view\((\{.*\})\)",
                        u"single weibo path" : u"/descendant::div[starts-with(@class,'WB_cardwrap S_bg2 clearfix')]",#[re:match(text(), 'some text')]
                        u"mid path" : u"//dl[starts-with(@class,'feed_list W_texta')]",
                        u"mid attribute" : u"mid",
                        u"uid path" : u"//img[@usercard]",
                        u"uid attribute" : u"usercard",
                        u"weibo content path" : u"//p[@node-type='feed_list_content']/em",
                        u"weibo nickname path" : u"//p[@node-type='feed_list_content']/a",
                        u"is forward path" : u"//dl[starts-with(@class,'feed_list W_linecolor')]",
                        u"is forward attribute" : u"isforward",
                        u"forward ref path" : u"//dt[starts-with(@node-type,'feed_list_forwardContent')]/a",
                        u"forward ref attribute" : u"href",
                        u"forward uid path" : u"//dt[starts-with(@node-type,'feed_list_forwardContent')]/a",
                        u"forward uid attribute" : u"usercard",
                        u"forward content path" : u"//dt[starts-with(@node-type,'feed_list_forwardContent')]/em",
                        u"statistic infor path" : u"//p[starts-with(@class,'info W_linkb W_textb')]",
                        u"date path" : u".//a[@class='date']",
                        u"date attribute" : u"title",
                        u"like number key" : u"action-type",
                        u"like number value" : u"feed_list_like",
                        u"forward number key" : u"action-type",
                        u"forward number value" : u"feed_list_forward",
                        u"favorite number key" : u"action-type",
                        u"favorite number value" : u"feed_list_favorite",
                        u"comment number key" : u"action-type",
                        u"comment number value" : u"feed_list_comment"
                    }
class AdvKeywordWeiboXMLTreeParser():
    '''
    This class maintains a weibo's HTML tree and parses it to provide useful fields
    '''
    #need to faster
    def __init__(self, weibo):
        self.weibo = weibo
        self.text = etree.tostring(weibo)
        self.soup = BeautifulSoup(self.text)

    #
    def get_mid(self):
        '''
        Raise AdvKeywordWeiboPageParseException
        '''
        #nrt_elmt_list = self.weibo.xpath(ADV_KEYWORD_WEIBO_CONSTANT_DICT[u'mid path']+'[1]')
        ##for exception handle
        #if len(nrt_elmt_list) is 0:
        #    raise AdvKeywordWeiboPageParseException(AdvKeywordWeiboPageParseException.ERROR_CODE_DICT['get mid element failed'])
        #nrt_elmt = nrt_elmt_list[0]
        #if not (ADV_KEYWORD_WEIBO_CONSTANT_DICT[u'mid attribute'] in nrt_elmt.attrib):
        #    raise AdvKeywordWeiboPageParseException(AdvKeywordWeiboPageParseException.ERROR_CODE_DICT['get mid attribute failed'])
        #return nrt_elmt.get(ADV_KEYWORD_WEIBO_CONSTANT_DICT[u'mid attribute'])
        div = self.soup.find('div',{'action-type':'feed_list_item'})
        mid = div.get('mid')
        # try:
        # div = self.soup.find('div',{'action-type':'feed_list_item'})
        #            mid = div.get('mid')
        #            if not os.path.exists('html/'):
        #                os.mkdir('html')
        #
        #            num = len(os.listdir('html/'))
        #            with open('html/'+str(num+1)+'real.html','w') as f:
        #                f.write(self.text)
        #        except:
        #            if not os.path.exists('data/'):
        #                os.mkdir('data')
        #
        #            num = len(os.listdir('data/'))
        #            with open('data/'+str(num+1)+'real.html','w') as f:
        #                f.write(self.text)
        #            raise Exception
        return mid

    def get_uid(self):
        '''
        Raise AdvKeywordWeiboPageParseException
        '''
        #nrt_elmt_list = self.weibo.xpath( ADV_KEYWORD_WEIBO_CONSTANT_DICT[u'uid path'] + '[1]')
        ##for exception handle
        #if len(nrt_elmt_list) is 0:        
        #    raise AdvKeywordWeiboPageParseException(AdvKeywordWeiboPageParseException.ERROR_CODE_DICT['get uid element failed'])
        #nrt_elmt = nrt_elmt_list[0]
        ##for exception handle
        #if not (ADV_KEYWORD_WEIBO_CONSTANT_DICT[u'uid attribute'] in nrt_elmt.attrib):
        #    raise AdvKeywordWeiboPageParseException(AdvKeywordWeiboPageParseException.ERROR_CODE_DICT['get uid attribute failed'])
        #uid = re.findall('\d+',nrt_elmt.get( ADV_KEYWORD_WEIBO_CONSTANT_DICT[u'uid attribute']))
        #if len(uid) != 0:
        #    return ''.join(uid)
        #else:
        #    return ''
        uid = self.soup.find('a',{'class':'W_texta W_fb'}).get('usercard')[3:13] 
        return uid
        
    def get_nickname(self):
        res = ""
        '''
        Raise AdvKeywordWeiboPageParseException
        '''
        #nrt_elmt_list = self.weibo.xpath(ADV_KEYWORD_WEIBO_CONSTANT_DICT[u"weibo nickname path"] + '[1]')
        ##for exception handle
        #if len(nrt_elmt_list) is 0:
        #    raise AdvKeywordWeiboPageParseException(AdvKeywordWeiboPageParseException.ERROR_CODE_DICT['get nickname failed'])
        #nrt_elmt = nrt_elmt_list[0]
        #
        #try:
        #    res = nrt_elmt.text
        #except:
        #    pass
        #return res
        nickname = self.soup.find('a',{'class':'W_texta W_fb'}).get('nick-name') 
        return nickname
    
    def get_content(self):
        '''
        Raise AdvKeywordWeiboPageParseException
        '''
        #nrt_elmt_list = self.weibo.xpath(ADV_KEYWORD_WEIBO_CONSTANT_DICT[u"weibo content path"] + '[1]')
        ##for exception handle
        #if len(nrt_elmt_list) is 0:
        #    raise AdvKeywordWeiboPageParseException(AdvKeywordWeiboPageParseException.ERROR_CODE_DICT['get content element failed'])
        #nrt_elmt = nrt_elmt_list[0]
        #content =  etree.tostring(nrt_elmt, method='text', encoding=DOM_TREE_CONSTRUCT_ENCODE)
        #return content
        content = self.soup.find('p',{'class':'comment_txt'}).text.strip()
        return content

    def get_is_forward(self):
        #nrt_elmt_list = self.weibo.xpath(ADV_KEYWORD_WEIBO_CONSTANT_DICT[u'is forward path']+'[1]')
        ##for exception handle
        #if len(nrt_elmt_list) is 0:
        #    raise AdvKeywordWeiboPageParseException(AdvKeywordWeiboPageParseException.ERROR_CODE_DICT['get is forward element failed'])
        #nrt_elmt = nrt_elmt_list[0]
        #if not (ADV_KEYWORD_WEIBO_CONSTANT_DICT[u"is forward attribute"] in nrt_elmt.attrib):
        #    return False
        #is_forward = nrt_elmt.get(ADV_KEYWORD_WEIBO_CONSTANT_DICT[u"is forward attribute"])
        #return bool(is_forward)
        if self.soup.find('div',{'class':'comment'}): 
            self.ori_weibo = self.soup.find('div',{'class':'comment'})
            return True
        else:
            return False

    def get_forward_ref(self):
        '''
        Get the URL where this weibo is forwarded from
        '''
        #nrt_elmt_list = self.weibo.xpath(ADV_KEYWORD_WEIBO_CONSTANT_DICT[u"forward ref path"] + '[1]')
        #if len(nrt_elmt_list) is 0:
        #    return ''
        #nrt_elmt = nrt_elmt_list[0]
        #result = nrt_elmt.get(ADV_KEYWORD_WEIBO_CONSTANT_DICT[u"forward ref attribute"])
        #
        #if not result:
        #    result =  ''
        #return result
        try: 
            forward_ref = self.ori_weibo.find('a',{'class':'W_textb'}).get('href') 
        except:
            forward_ref = ''
            print traceback.format_exc()
        return forward_ref

    def get_forward_uid(self):
        '''
        Need to verify
        '''
        #nrt_elmt_list = self.weibo.xpath(ADV_KEYWORD_WEIBO_CONSTANT_DICT[u"forward uid path"] + '[1]')
        ##for exception handle
        #if len(nrt_elmt_list) is 0:
        #    raise AdvKeywordWeiboPageParseException(AdvKeywordWeiboPageParseException.ERROR_CODE_DICT["get forward uid element failed"])
        #nrt_elmt = nrt_elmt_list[0]
        #result = nrt_elmt.get(ADV_KEYWORD_WEIBO_CONSTANT_DICT[u"forward uid attribute"]) 
        ##for exception handle
#       #  if not result:
#       #      raise AdvKeywordWeiboPageParseException(AdvKeywordWeiboPageParseException.ERROR_CODE_DICT['get forward uid attribute failed'])
        #if not result:
        #    return ''
        #usercard = re.findall('\d+',result)
        #return ''.join(usercard)
        try:
            forward_uid = self.ori_weibo.find('a',{'class':'W_texta W_fb'}).get('usercard')[3:]  
        except:
            forward_uid = ''
        return forward_uid

    def get_forward_content(self):
        #nrt_elmt = self.weibo.xpath(ADV_KEYWORD_WEIBO_CONSTANT_DICT[u"forward content path"] + '[1]')
        #if len(nrt_elmt) is 0:
        #    return ''
        #result = etree.tostring(nrt_elmt[0], method='text', encoding=DOM_TREE_CONSTRUCT_ENCODE)
        #return result
        try:
            forward_content = self.ori_weibo.find('p',{'class':'comment_txt'}).text.strip()
        except:
            forward_content = ''
            print traceback.format_exc()
        return forward_content

    def get_stat_infor(self,is_forward):
        '''
        Get this weibo's statistic information
        [date, like number, forward number, favorite number, comment number]
        '''
        #corresponding to [date, like, forward, favorite, comment]
        infor = ["", 0, 0, 0, 0]
        #stat_root_list = self.weibo.xpath(ADV_KEYWORD_WEIBO_CONSTANT_DICT[u"statistic infor path"] + '[1]')
        #if len(stat_root_list) is 0:
        #    return infor
        #stat_root = stat_root_list[0]
        #date = self._get_date(stat_root)
        #n_like = self._get_like_num(stat_root)
        #n_forward = self._get_forward_num(stat_root)
        #n_favorite = self._get_favorite_num(stat_root)
        #n_comment = self._get_comment_num(stat_root)
        #infor = [date, n_like, n_forward, n_favorite, n_comment]
        #return infor
        l = []
        row4 = self.soup.find('ul',{'class':'feed_action_info feed_action_row4'})
        for li in row4.findAll('li'):
            num_regex = re.compile('\d+')
            text = li.text
            m =  num_regex.search(text)
            if m:
                l.append(int(m.group()))
            else:
                l.append(0)
        n_favorite,n_forward,n_comment,n_like = l

        if is_forward:
            create_time = self.soup.findAll('a',{'node-type':'feed_list_item_date'})[1].get('title')
        else:
            create_time = self.soup.find('a',{'node-type':'feed_list_item_date'}).get('title')
        infor = [create_time, n_like, n_forward, n_favorite, n_comment]
        return infor
        
        
    def _get_date(self, stat_root):
        nrt_elmt_list = stat_root.xpath(ADV_KEYWORD_WEIBO_CONSTANT_DICT[u"date path"] + '[1]')
        if len(nrt_elmt_list) is 0:
            return ""
        nrt_elmt = nrt_elmt_list[0]
        date = nrt_elmt.get("title")
        if not date:
            date = ""
        return date

    def _get_like_num(self, stat_root):
        return self._get_number_stat_infor(stat_root, ADV_KEYWORD_WEIBO_CONSTANT_DICT[u"like number key"], ADV_KEYWORD_WEIBO_CONSTANT_DICT[u"like number value"])

    def _get_forward_num(self, stat_root):
        return self._get_number_stat_infor(stat_root, ADV_KEYWORD_WEIBO_CONSTANT_DICT[u"forward number key"], ADV_KEYWORD_WEIBO_CONSTANT_DICT[u"forward number value"])

    def _get_favorite_num(self, stat_root):
        return self._get_number_stat_infor(stat_root, ADV_KEYWORD_WEIBO_CONSTANT_DICT[u"favorite number key"], ADV_KEYWORD_WEIBO_CONSTANT_DICT[u"favorite number value"])

    def _get_comment_num(self, stat_root):
        return self._get_number_stat_infor(stat_root, ADV_KEYWORD_WEIBO_CONSTANT_DICT[u"comment number key"], ADV_KEYWORD_WEIBO_CONSTANT_DICT[u"comment number value"])

    def _get_number_stat_infor(self, stat_root, action_type_key, action_type_value):
        stat_list = stat_root.xpath('.//a[@' + action_type_key + '=\'' + action_type_value +'\']' + '[1]')
        number = '0'
        if stat_list is not None:
            number_content = etree.tostring(stat_list[0], method='text', encoding=DOM_TREE_CONSTRUCT_ENCODE)#stat_list[0].xpath('.//text()')
            num = re.findall('\d+', number_content)
            if len(num) > 0:
                number = ''.join(num)
        return number

def find_inside_weibo_trees_adv(page):
    '''
    Get the inside weibo trees.  Return in array.
    A sigle tree looks like the following:
    <dl action-type="feed_list_item" class="feed_list W_linecolor" isforward="1" mid="3687102426727021">
    ...
    </dl>
    Raise AdvKeywordWeiboPageParseException
    '''
    tree = etree.fromstring(page, etree.HTMLParser())
    #for exception handle
    if tree is None:
        raise AdvKeywordWeiboPageParseException(AdvKeywordWeiboPageParseException.ERROR_CODE_DICT['total tree construct'])

#     print_to_file("test html", page)

#
#    print ADV_KEYWORD_WEIBO_CONSTANT_DICT[u'script']
#
#    print len(tree.xpath(u"/descendant::script"))
#    print ADV_KEYWORD_WEIBO_CONSTANT_DICT[u'script']
#
    script_eles = tree.xpath(ADV_KEYWORD_WEIBO_CONSTANT_DICT[u'script'])

#    print 'script_eles\'s size is: ' + str(len(script_eles))
    #for exception handle
    if len(script_eles) is 0:
        raise AdvKeywordWeiboPageParseException(AdvKeywordWeiboPageParseException.ERROR_CODE_DICT['script find failed'])
    #get string which matches ADV_KEYWORD_WEIBO_CONSTANT_DICT[u'inside html mark']
    content_inside_scripts = []
    for ele in script_eles:
        if ele.text and ADV_KEYWORD_WEIBO_CONSTANT_DICT[u'inside html mark'] in ele.text:
            inside_html_regex = re.compile(ADV_KEYWORD_WEIBO_CONSTANT_DICT[u'inside html regex'])
            m = inside_html_regex.search( ele.text )
            if m is not None:
                content_inside_script = m.group(1)
                #print content_inside_script
                content_inside_scripts.append(content_inside_script)
    #for exception handle
    if len(content_inside_scripts) is 0:
        page_str = etree.tostring(tree, method='html', pretty_print=True, encoding='utf-8')

#        if not os.path.exists('data/'):
        # os.mkdir('data')
        #
        # num = len(os.listdir('data/'))
        #        with open('data/'+str(num+1)+'real.html','w') as f:
        #            f.write(page)
        print_to_file('after tree.html', page_str)

        raise AdvKeywordWeiboPageParseException(AdvKeywordWeiboPageParseException.ERROR_CODE_DICT['content inside script find failed'])
    
#     tmp_tree = etree.fromstring(content_inside_scripts[0], etree.HTMLParser())
#     page_str = etree.tostring(tmp_tree, method='html', pretty_print=True, encoding='utf-8')
# # 
#     print_to_file('after tree.html', page_str)
        
    inside_weibo_trees = []
#     count = 1
    for content_inside_script in content_inside_scripts:
        #Get <html: html_content>'s html_content
        key_values = json.loads(content_inside_script)
        inner_html_text = key_values.get('html')
        #print inner_html_text
        weibos_tree = etree.fromstring( inner_html_text, etree.HTMLParser() )
        for weibo_tree in weibos_tree.xpath( ADV_KEYWORD_WEIBO_CONSTANT_DICT[u'single weibo path']):
            #need to faster
            inside_weibo_trees.append( etree.fromstring( etree.tostring(weibo_tree), etree.HTMLParser() ) )
    #for exception handle
    if len(inside_weibo_trees) is 0:
        raise AdvKeywordWeiboPageParseException(AdvKeywordWeiboPageParseException.ERROR_CODE_DICT['weibo trees construct'])
    return inside_weibo_trees

def page_2_weibo_trees_adv(searchpage):
    return find_inside_weibo_trees_adv(searchpage)   

def get_weibo_url(uid, mid):
    #need on third
    suffix = mid2url(int(mid))
    link = 'http://weibo.com/'+uid+'/'+suffix
    return link

def clean_page(page):
    '''
    Replace the '\r\n' with '' in the page
    '''
    p_re = r"(\r\n)"
    
    page = page.replace(p_re,'')

    return page
###############################################################################################
####################################WeiboCrawler Related#######################################
try:
    import urllib2
    import gzip
    from StringIO import StringIO
    
    from my_exceptions import AdvKeywordPageGetException
except ImportError as err:
    s = traceback.format_exc()
    print s
    
class PageValidityChecker:
    def __init__(self):
         
        pass
     
    def check(self, page, page_url=""):
        '''
        If the page exists, then check if this page is validity.
        If not validity, try _get_page_again()
        '''
        if page:
            if VERIFICATION_ERROR in page: #errorlog.verificationerror(keyword,1,time.strf(time))
            
                print 'veritification error'  
                return [ False, AdvKeywordPageGetException.ERROR_CODE_DICT['verification error'] ]
            
            elif COOKIE_OUTOFDATE_ERROR in page: 
               
                print 'cookie outofdate error'
                return [ False, AdvKeywordPageGetException.ERROR_CODE_DICT['cookie outofdate error'] ]
            elif PASS_CERTIFICATE_ERROR in page:
               
                print 'pass certificate error'
                return [ False, AdvKeywordPageGetException.ERROR_CODE_DICT['pass certificate error'] ]
            elif LOGIN_ING in page:
                print "正在登陆。。。"
                return [ False, AdvKeywordPageGetException.ERROR_CODE_DICT['cookie outofdate error']]
            #print "no errors" 
            return [ True, 0 ]
        else:
            print 'page not exist'
            return [ False, AdvKeywordPageGetException.ERROR_CODE_DICT['page not exist'] ]

page_validity_checker = PageValidityChecker()

def get_page_validity_checker():
    
    return page_validity_checker

PASS_CERTIFICATE_ERROR = '����ͨ��֤'
COOKIE_OUTOFDATE_ERROR = r'http://weibo.com/sso/login.php?ssosavestate'
VERIFICATION_ERROR = r'\u4f60\u7684\u884c\u4e3a\u6709\u4e9b\u5f02\u5e38\uff0c\u8bf7\u8f93\u5165\u9a8c\u8bc1\u7801\uff1a' #请输入验证码 
HTTP_HEADERS= {'User-Agent':'Mozilla/5.0 (X11; Linux i686; rv:8.0) Gecko/20100101 Firefox/8.0'}
LOGIN_ING = r'http://passport.weibo.com/wbsso/login?ssosavestate'

COMMENT_PER_PAGE_NUMBER = 20
RETWEET_PER_PAGE_NUMBER = 20
FIRST_PAGE_REGEX = r'(?<=&page=)\d+'


class WeiboCrawler:
    
    def __init__(self, url_wrapper, page_parser, cur_pro_IP="", proxy_used=False, proxy_cookie_file=""):
        
        self.url_wrapper = url_wrapper
        
        self.page_parser = page_parser
        
        self.page_validity_checker = get_page_validity_checker()
        
        self.proxy_IP = cur_pro_IP
        
        self.proxy_used = proxy_used
        
        self.proxy_cookie_file = proxy_cookie_file
        
    def crawl(self):
        
        pass
    
    def _get_page(self):
        
        search_url = self.url_wrapper.to_url()
        
        searchreq = urllib2.Request(url = search_url, headers = HTTP_HEADERS)
        searchreq.add_header('Accept-encoding','gzip')
        
        try:
            if not self.proxy_used:
                webpage = urllib2.urlopen(searchreq,timeout=GET_PAGE_TIMEOUT)
                
            else:
                cookie_jar  = cookielib.LWPCookieJar(self.proxy_cookie_file)
                cookie_jar.load(ignore_discard=True, ignore_expires=True)
                
                proxy_http = "http://" + self.proxy_IP
                proxy_support = urllib2.ProxyHandler({"http":proxy_http})
                cookie_support = urllib2.HTTPCookieProcessor(cookie_jar)
                opener = urllib2.build_opener(proxy_support, cookie_support)
                webpage = opener.open(searchreq, timeout=GET_PAGE_TIMEOUT)
                
        #for exception handle
        except requests.exceptions.ProxyError:
             
            raise AdvKeywordPageGetException(AdvKeywordPageGetException.ERROR_CODE_DICT['connect to proxy failed'], search_url)
         
        except :
            raise AdvKeywordPageGetException(AdvKeywordPageGetException.ERROR_CODE_DICT['urllib2 open failed'], search_url)
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
class AdvWeibo:
    
    def __init__(self, mid, uid, nickname, typeid, keyword, content, \
                 create_time, n_like, n_forward, n_favorite, n_comment, \
                 url='',page_num=1,is_forward=False, forwarded_uid='', forwarded_ref='', forwarded_content=''):
        
        self.mid = mid
        self.uid = uid
        self.nickname = nickname
        self.typeid = typeid
        self.keyword = keyword
        self.content = content
        self.create_time = create_time
        self.n_like = n_like
        self.n_forward = n_forward
        self.n_favorite = n_favorite
        self.n_comment = n_comment
        self.url = url
        
        self.page_num = page_num
        
        self.is_forward = is_forward
        self.forwarded_uid = forwarded_uid
        self.forwarded_ref = forwarded_ref
        self.forwarded_content = forwarded_content
        
class AdvWeiboComment:
    
    def __init__(self, attatched_mid, cid, uid, nickname, typeid, keyword='', page_num=1, content='', create_time='', ori_nickname='', ori_uid=''):
        
        self.attached_mid = attatched_mid
        self.cid = cid
        self.uid = uid
        self.nickname = nickname
        self.typeid = typeid
        self.keyword = keyword
        self.page_num = page_num
        self.content = content
        self.create_time = create_time
        self.ori_nickname = ori_nickname
        self.ori_uid = ori_uid
    
#####################################################################################    

class DataStorer:
    
    def __init__(self):
        pass
    
    def store(self):
        
        pass
    

class AdvKeywordWeiboRetweetStorer(DataStorer):
    def __init__(self,adv_weibo_rt):
        DataStorer.__init__(self)
        self.data = adv_weibo_rt

    def store(self):
        retweet_2_store = RetweetAdv()
        retweet_2_store.uid = self.data['uid']
        retweet_2_store.rid = self.data['rid']
        retweet_2_store.content = self.data['content']
        retweet_2_store.create_time = self.data['create_time']
        retweet_2_store.attached_mid = self.data['attached_mid']
        retweet_2_store.nickname = self.data['nickname']
        retweet_2_store.ori_uid = self.data['ori_uid']
        retweet_2_store.ori_nickname = self.data['ori_nickname']

        old_retweet_in_store = RetweetAdv.objects(rid=retweet_2_store.rid)

        if len(old_retweet_in_store) == 0:
            print "store start"
            retweet_2_store.save()
            print "store finished"
            return True
        else:
            print "duplicate error"
            return False
        print "store error"
        return False

class AdvKeywordWeiboCommentStorer(DataStorer):
    def __init__(self, adv_weibo_comment):
        DataStorer.__init__(self)
        
        self.data = adv_weibo_comment
    
    def store(self):
        
        comment_2_store = CommentAdv()
        
        comment_2_store.cid = self.data.cid
        comment_2_store.uid = self.data.uid
        comment_2_store.nickname = self.data.nickname
        comment_2_store.attached_mid = self.data.attached_mid
        comment_2_store.content = self.data.content
        comment_2_store.create_time = self.data.create_time
        comment_2_store.ori_uid = self.data.ori_uid
        comment_2_store.ori_nickname = self.data.ori_nickname
        
        old_comment_in_store = CommentAdv.objects(cid=comment_2_store.cid)  # @UndefinedVariable
        
        if len(old_comment_in_store) is 0:
            try:
                comment_2_store.save()
                
                return True
            #need to log
            except NotUniqueError as err:
                if OPEN_WRITE_NOTUNIQUE_LOG:
                    my_log.write_notunique_log(
                        log_id=comment_2_store.cid,
                        log_type=self.data.typeid,
                        fail_code=OtherException.ERROR_CODE_DICT['weibo comment store NotUniqueError'],
                        keyword=self.data.keyword,
                        page_num=self.data.page_num
                        )
                
                return False
            except ValidationError as err:
                if OPEN_WRITE_NOTUNIQUE_LOG:
                    my_log.write_notunique_log(
                        log_id=comment_2_store.cid,
                        log_type=self.data.typeid,
                        fail_code=OtherException.ERROR_CODE_DICT['weibo comment store ValidationErron'],
                        keyword=self.data.keyword,
                        page_num=self.data.page_num
                        )
                
                return False
            except OperationError as err:
                if OPEN_WRITE_NOTUNIQUE_LOG:
                    my_log.write_notunique_log(
                        log_id=comment_2_store.cid,
                        log_type=self.data.typeid,
                        fail_code=OtherException.ERROR_CODE_DICT['weibo comment store OperationError'],
                        keyword=self.data.keyword,
                        page_num=self.data.page_num
                        )
                
                return False
            except Exception as err:
                if OPEN_WRITE_NOTUNIQUE_LOG:
                    my_log.write_notunique_log(
                        log_id=comment_2_store.cid,
                        log_type=self.data.typeid,
                        fail_code=OtherException.ERROR_CODE_DICT['weibo comment store OtherError'],
                        keyword=self.data.keyword,
                        page_num=self.data.page_num
                        )  
                
                return False
        else:
            #not unique, so record this duplicate
            if OPEN_WRITE_NOTUNIQUE_LOG:
                my_log.write_notunique_log(
                        log_id=comment_2_store.cid,
                        log_type=self.data.typeid,
                        fail_code=OtherException.ERROR_CODE_DICT['weibo comment store NotUniqueError'],
                        keyword=self.data.keyword,
                        page_num=self.data.page_num
                        )
            
            return self._update(old_comment_in_store, comment_2_store)
            
    def _update(self, old_comment_in_store, comment_2_store):
        '''
        If the mid is already in the DB, then update this comment 
        '''
        #need to faster
        try:
            old_comment_in_store.update_one(
                                            set__cid=comment_2_store.cid,
                                            set__uid=comment_2_store.uid,
                                            set__nickname=comment_2_store.nickname,
                                            set__attached_mid=comment_2_store.attached_mid,
                                            set__content=comment_2_store.content,
                                            set__create_time=comment_2_store.create_time
                                            )
                
        #need to log
        except NotUniqueError as err:
            if OPEN_WRITE_NOTUNIQUE_LOG:
                my_log.write_notunique_log(
                        log_id=comment_2_store.cid,
                        log_type=self.data.typeid,
                        fail_code=OtherException.ERROR_CODE_DICT['weibo comment store NotUniqueError'],
                        keyword=self.data.keyword,
                        page_num=self.data.page_num
                        )
                
            return False
        except ValidationError as err:
            if OPEN_WRITE_NOTUNIQUE_LOG:
                my_log.write_notunique_log(
                        log_id=comment_2_store.cid,
                        log_type=self.data.typeid,
                        fail_code=OtherException.ERROR_CODE_DICT['weibo comment store ValidationErron'],
                        keyword=self.data.keyword,
                        page_num=self.data.page_num
                        )
            return False
        except OperationError as err:
            if OPEN_WRITE_NOTUNIQUE_LOG:
                my_log.write_notunique_log(
                        log_id=comment_2_store.cid,
                        log_type=self.data.typeid,
                        fail_code=OtherException.ERROR_CODE_DICT['weibo comment store OperationError'],
                        keyword=self.data.keyword,
                        page_num=self.data.page_num
                        )
                
            return False
        except Exception as err:
            if OPEN_WRITE_NOTUNIQUE_LOG:
                my_log.write_notunique_log(
                        log_id=comment_2_store.cid,
                        log_type=self.data.typeid,
                        fail_code=OtherException.ERROR_CODE_DICT['weibo comment store OtherError'],
                        keyword=self.data.keyword,
                        page_num=self.data.page_num
                        )  
            
            return False
        
        return True
class AdvKeywordWeiboStorer(DataStorer):
    
    def __init__(self, adv_weibo):
        
        DataStorer.__init__(self)
        
        self.data = adv_weibo
        
    def store(self):
        
        weibo_2_store = SingleWeibo()
        
        weibo_2_store.mid = self.data.mid
        weibo_2_store.uid = self.data.uid
        weibo_2_store.nickname = self.data.nickname
        weibo_2_store.typeid = self.data.typeid
        weibo_2_store.keyword = [self.data.keyword]
        weibo_2_store.content = self.data.content
        
        weibo_2_store.url = self.data.url
        weibo_2_store.is_forward = self.data.is_forward
        weibo_2_store.forward_uid = self.data.forwarded_uid
        weibo_2_store.original_ref = self.data.forwarded_ref
        weibo_2_store.original_cntnt = self.data.forwarded_content
        
        weibo_2_store.create_time = self.data.create_time
        weibo_2_store.n_like = self.data.n_like
        weibo_2_store.n_forward = self.data.n_forward
        weibo_2_store.n_favorite = self.data.n_favorite
        weibo_2_store.n_comment = self.data.n_comment
        
        for k in keyword_processor.get_keywords():
            if k in self.data.content and (k not in weibo_2_store.keyword):
                weibo_2_store.keyword.append(k)
        
        old_weibo_in_store = SingleWeibo.objects(mid=weibo_2_store.mid)  # @UndefinedVariable
        
        branch_weibo(weibo_2_store)
         
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
                                     keyword=self.data.keyword,
                                     page_num=self.data.page_num
                                    )
                return False
            except ValidationError as err:
                if OPEN_WRITE_NOTUNIQUE_LOG:
                    my_log.write_notunique_log(
                                     log_id=weibo_2_store.mid,
                                     log_type=weibo_2_store.typeid,
                                     fail_code=OtherException.ERROR_CODE_DICT["weibo store ValidationError"],
                                     keyword=self.data.keyword,
                                     page_num=self.data.page_num
                                    )
                return False
            except OperationError as err:
                if OPEN_WRITE_NOTUNIQUE_LOG:
                    my_log.write_notunique_log(
                                     log_id=weibo_2_store.mid,
                                     log_type=weibo_2_store.typeid,
                                     fail_code=OtherException.ERROR_CODE_DICT["weibo store OperationError"],
                                     keyword=self.data.keyword,
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
                                     keyword=self.data.keyword,
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
                                     keyword=self.data.keyword,
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
                                      set__nickname=weibo_2_store.nickname,
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
        #need to log
        except NotUniqueError as err:
            if OPEN_WRITE_NOTUNIQUE_LOG:
                my_log.write_notunique_log(
                                            log_id=weibo_2_store.mid,
                                            log_type=weibo_2_store.typeid,
                                            fail_code=OtherException.ERROR_CODE_DICT["weibo store NotUniqueError"],
                                            keyword=self.data.keyword,
                                            page_num=self.data.page_num
                                            )
            return False
        
        except ValidationError as err:
            if OPEN_WRITE_NOTUNIQUE_LOG:
                my_log.write_notunique_log(
                                     log_id=weibo_2_store.mid,
                                     log_type=weibo_2_store.typeid,
                                     fail_code=OtherException.ERROR_CODE_DICT["weibo store ValidationError"],
                                     keyword=self.data.keyword,
                                     page_num=self.data.page_num
                                    )
            return False
        except OperationError as err:
            if OPEN_WRITE_NOTUNIQUE_LOG:
                my_log.write_notunique_log(
                                     log_id=weibo_2_store.mid,
                                     log_type=weibo_2_store.typeid,
                                     fail_code=OtherException.ERROR_CODE_DICT["weibo store OperationError"],
                                     keyword=self.data.keyword,
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
                                     keyword=self.data.keyword,
                                     page_num=self.data.page_num
                                    )
            
            return False
            
        return False
###############################################################################################
