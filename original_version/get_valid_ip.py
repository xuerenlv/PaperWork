#encoding=utf8
'''
Created on 2014��5��7��

@author: cc
'''
import traceback
from my_test import print_to_file
import urllib2
from StringIO import StringIO
import gzip
try:
    import threading
    import re
    import time
    from lxml import etree  # @UnresolvedImport
    import requests  # @UnresolvedImport
    import datetime
    from BeautifulSoup import BeautifulSoup  # @UnresolvedImport
    from common_conf_manager import SCAN_FREE_DAILI
    from conf import PROXIES
except:
    s = traceback.format_exc()
    print s
    
HTTP_HEADERS= {'User-Agent':'Mozilla/5.0 (X11; Linux i686; rv:8.0) Gecko/20100101 Firefox/8.0'}
# HTTP_HEADERS = {'User-Agent' : "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.153 Safari/537.36"}
def removeDuplicate(seq):
    seen = set()
    seen_add = seen.add
    return [x for x in seq if x not in seen and not seen_add(x)]

def get_page(search_url):
    searchreq = urllib2.Request(url = search_url, headers = HTTP_HEADERS)
    searchreq.add_header('Accept-encoding','gzip')
    
    webpage = urllib2.urlopen(searchreq)
    
    if webpage.info().get('Content-Encoding') == 'gzip':
        buf = StringIO(webpage.read())
        f = gzip.GzipFile(fileobj = buf)
        searchpage = f.read()
    else:
            #print 'webpage.info encoding : ',webpage.info().get('Content-Encoding')
            
        searchpage = webpage.read()
        
    return searchpage 

def getLinks_youdaili():
    links = []
    t_links = []
    for i in range(1,2): 
        proxyUrl = 'http://www.youdaili.cn/Daili/guonei/list_'+str(i)+'.html'
#         r = requests.get(proxyUrl)
        
        r = get_page(proxyUrl)
        
#         print_to_file("proxy_page.html", r)
        
        proxyPage = etree.HTML(r.encode('utf-8'))  # @UndefinedVariable
        
        hrefs = proxyPage.xpath(u"//ul[@class='newslist_line']/*/a")
        
        t_links.extend([href.attrib['href'] for href in hrefs])
        
        for t_link in t_links:
            links.append(t_link)
            
            n_r = get_page(t_link)
            proxyPage = etree.HTML(n_r.encode('utf-8'))  # @UndefinedVariable
            
            hrefs = proxyPage.xpath(u"/descendant::div[@class='content_full']/*/*/div[@class='newsdetail_cont']/div[@class='cont_font']/div[@class='dede_pages']/ul[@class='pagelist']/li/a")
            
            
            proxy_head = 'http://www.youdaili.cn/Daili/guonei/'
            for href in hrefs:
                if u'href' in href.attrib:
                    if href.attrib['href'] != "#" and href.text != "下一页":
                        links.append(proxy_head + href.attrib['href'])
            
    return links

'''
返回的是一个[IP:port]列表，其中可能有重复的IP
'''
def getIP_youdaili(links):
    IPPool = []
    for link in links:
#         r = requests.get(link)

        r = get_page(link)
        IPpage = etree.HTML(r.encode('utf-8'))  # @UndefinedVariable
        IPs = IPpage.xpath(u"//div[@class='cont_font']/p/text()")
        IPPool.extend([IP.split('@')[0].replace('\r\n','') for IP in IPs])
    return IPPool

'''
从 http://www.youdaili.cn/获取待检测IPs
'''
def getIPs_youdaili():
    links = getLinks_youdaili()
    
    IPs = getIP_youdaili(links)
    
    return IPs

'''
从http://cn-proxy.com/获取待检测IPs
'''
def getIPs_cn_proxy():
    IPs = []
    
    proxy_url = "http://cn-proxy.com/"
    
    try:
        r = get_page(proxy_url)
        
        proxyPage = etree.HTML(r.encode('utf-8'))  # @UndefinedVariable
        
        IP_tables = proxyPage.xpath(u"//table[@class='sortable']")
        
        for table in IP_tables:
            t_IPs = table.xpath(u"tbody/tr")
            
            for IP in t_IPs: 
                row = IP.xpath(u"td")
                
                ip = row[0].text
                port = row[1].text
                
                IPs.append(ip + ":" + str(port))
    except:
        pass
    
    return IPs

'''
从http://www.xici.net.co/获取待检测IPs
'''
def getIPs_xici():
    IPs = []
    
    proxy_url = "http://www.xici.net.co/"
    
    try:
        r = get_page(proxy_url)
        
        proxyPage = etree.HTML(r.encode('utf-8'))  # @UndefinedVariable
        
        IP_table = proxyPage.xpath(u"//table[@id='ip_list']")[0]
        
        rows = IP_table.xpath(u"//tr[@class='odd']")
        
        for row in rows:
#             print etree.tostring(row, encoding='utf8')
            ip = row.xpath(u"td")[1].text
            port = row.xpath(u"td")[2].text
            
            IPs.append(ip + ":" + str(port))
        rows = IP_table.xpath(u"//tr[@class='']")
        
        for row in rows:
#             print etree.tostring(row, encoding='utf8')
            ip = row.xpath(u"td")[1].text
            port = row.xpath(u"td")[2].text
            
            IPs.append(ip + ":" + str(port))
#             print ip + ":" + str(port)
    except:
        t = traceback.format_exc()
        print t
    
    return IPs

def getIPs_proxy_digger():
    socket_list = []
    url = 'http://www.site-digger.com/html/articles/20110516/proxieslist.html'
    r = requests.get(url)
    soup = BeautifulSoup(r.content)
    tbody = soup.find('tbody')
    trs = tbody.findAll('tr')
    for tr in trs:
        tds = tr.findAll('td')
        socket_address = tds[0].text
        proxy_type = tds[1].text
        location = tds[2].text
        if proxy_type == 'Anonymous' :#and location == 'China':
            ip,port = socket_address.split(':')
            socket_list.append(ip+':'+port)
            
    return socket_list

def getIPs_org_pachong():
    socket_list = []
    url = 'http://pachong.org/anonymous.html'
    r = requests.get(url)
    soup = BeautifulSoup(r.content)
    tbody = soup.find('tbody')
    trs = tbody.findAll('tr')
    for tr in trs:
        tds = tr.findAll('td')
        ip = tds[1].text
        port = tds[2].text
        socket_address = ip + ':' +port
        proxy_type = tds[4].a.text
        if proxy_type == 'high':
            socket_list.append(socket_address)
    return socket_list

def getIPs():
    IPPool = []
    
    try:
        IPPool.extend(getIPs_youdaili())
    except:
        pass
    try:
        IPPool.extend(getIPs_cn_proxy())
    except:
        pass
    try:
        IPPool.extend(getIPs_xici())
    except:
        pass
    try:
        IPPool.extend(getIPs_proxy_digger())
    except:
        pass
    try:
        IPPool.extend(getIPs_org_pachong())
    except:
        pass
    
#     try:
#         t_l = getIPs_proxy_digger()
#         IPPool.extend(t_l)
#         print "getIPs_proxy_digger size:" + str(len(t_l))
#     except:
#         pass
#    t_l = getIPs_proxy_digger()
#    IPPool.extend(t_l)
#    print "getIPs_proxy_digger size:" + str(len(t_l))
    
    IPPool = removeDuplicate(IPPool)
    
    print "total IPs: " + str(len(IPPool))
    
    return IPPool

##########################################################################################################################################
TEST_URL = 'http://iframe.ip138.com/ic.asp'
try:
    import logging
    from common_conf_manager import PROXY_IP_UPDATE_INTERVAL,\
           GOOD_PROXY_IP_THRESHOLD
#            DATABASE_SUFFIX
    from storage_manager import ProxyIp
except:
    s = traceback.format_exc()
    print s

# connect_db(DATABASE_SUFFIX)
proxy_logger = logging.getLogger("proxyLog")

proxy_ip_db_mutex = threading.Lock()
class ProxyVerifier(threading.Thread):
    
    def __init__(self, thread_name, ip_list, proxy_manager):
        
        threading.Thread.__init__(self)
        self.name = thread_name
        self.ip_list = ip_list
        self.proxy_manager = proxy_manager
    
    def run(self):
        
        for ip in self.ip_list:
            validity = False
            try:
                validity = self._verify_ip(ip)
            except:
                pass
            
            if validity:
                self.proxy_manager.add_ip(ip)
                
                global proxy_ip_db_mutex
                if proxy_ip_db_mutex.acquire():
                    new_proxy_ip = ProxyIp()
                    new_proxy_ip.ip = ip
                    
                    try:
                        new_proxy_ip.save()
                    except:
                        pass
                    finally:
                        proxy_ip_db_mutex.release()
    
    def _verify_ip(self, socket_address):
        
        proxies = {"http":"http://" + socket_address}
        try:
    #        start = time.time()
            
    #        r = requests.get(TEST_URL, proxies=proxies, timeout=GOOD_PROXY_IP_THRESHOLD)
    #        returnIP = re.findall(r'[0-9]+(?:\.[0-9]+){3}',r.text)[0]
    #        inputIP = ip.split(':')[0]
    #        
    #        end = time.time()
    #        
    #        if inputIP == returnIP and (end - start) < GOOD_PROXY_IP_THRESHOLD:
    #            proxy_logger.info('inputIP: ' + inputIP)
    #            proxy_logger.info('returnIP:' + returnIP)
    #            proxy_logger.info("validity time cost:" + str(end - start))
            ip = socket_address.split(':')[0] 
            verify_url1 = 'http://luckist.sinaapp.com/test_ip'
            verify_url2 = 'http://members.3322.org/dyndns/getip'

            r1 = requests.get(verify_url1,proxies=proxies,timeout=3)
            r2 = requests.get(verify_url2,proxies=proxies,timeout=3)
            return_ip1 = r1.content.strip() 
            return_ip2 = r2.content.strip()

            if ip == return_ip1 and ip == return_ip2:
                return True
            else:
                return False
        except:
            return False

threadLock = threading.Lock()
try:
    from common_conf_manager import VERIFY_PROXY_IP_NUMBER
except:
    s = traceback.format_exc()
    
    print s 
 

class ProxyIPManager(threading.Thread):
    """
    Maintain a list of effective IPs.
    These IPs are gotten from http://www.youdaili.cn.
    To verify a IP is validity, a request should be sent to http://iframe.ip138.com/ic.asp. 
    A response will be gotten, the response contains a IP address, 
    if this address is the same to which the request come from, 
    it is validity, otherwise, it is not. 
    """
    
    def __init__(self, thread_name="proxyIPmanager"):
        
        threading.Thread.__init__(self)
        self.name = thread_name
        self.ip_list = []
        self.mid_ip_list = []
        self.cur_index = 0
        self.stop_me = False
        
    def run(self):
        
        while not self.stop_me:
            verify_threads = []
            ProxyIp.drop_collection()  # @UndefinedVariable
            
            proxy_logger.info("new proxy ips updating:")
            
            start = time.time()
            try:
                if SCAN_FREE_DAILI:
                    IPPool = getIPs()
                    for thread_id in range(0, VERIFY_PROXY_IP_NUMBER):
                        ips = []
                        index = thread_id
                        while index < len(IPPool):
                            ips.append(IPPool[index])
                            index += VERIFY_PROXY_IP_NUMBER
                        verify_threads.append(ProxyVerifier("verify " + str(thread_id), ips, self))
                     
                        print "verify thread %d, ip_list'size is %d" % (thread_id, len(ips))
                
                self.mid_ip_list = []
                self._add_clear_proxys()
            
                if SCAN_FREE_DAILI:
                    for verify_thread in verify_threads:
                    
                        verify_thread.start()
                
                    for verify_thread in verify_threads:
                     
                        verify_thread.join()
                
                    proxy_logger.info("all verify threads end!")
                
                self.ip_list = self.mid_ip_list
            
                end = time.time()
            
                proxy_logger.info("end proxy ips updating: {total time: " + str(end - start) + ", nowtime: " + str(datetime.datetime.now()) + ", current ip_list siz: " + str(len(self.ip_list)) + "}")
                
                proxy_logger.info("current available ips: ")
                
                for ip in self.ip_list:
                    proxy_logger.info(ip)
            except :
                s = traceback.format_exc()
                print s
                pass
                
            self._sleep_for_next_update()
            
    def get_ip(self):
        
        if not self.has_enough_ips():
            return ""

        list_size = len(self.ip_list)
        ip = ""
        try:
            ip = self.ip_list[self.cur_index % list_size]
            self.cur_index = (self.cur_index + 1) % list_size
        except:
            self.cur_index = 0
            pass
        
        return ip
    
    def _add_clear_proxys(self):
        clear_proxys = []
        if SCAN_FREE_DAILI is False:
#            clear_proxys.append("benxiaohai:1328257811@106.186.18.67:62011")
#            clear_proxys.append("benxiaohai:1328257811@106.186.18.67:62012")
#            clear_proxys.append("benxiaohai:1328257811@106.186.18.67:62013")
#            clear_proxys.append("benxiaohai:1328257811@106.186.18.67:62014")
#            clear_proxys.append("benxiaohai:1328257811@106.186.18.67:62015")
#            clear_proxys.append("benxiaohai:1328257811@106.186.18.67:62016")
#            clear_proxys.append("benxiaohai:1328257811@106.186.18.67:62017")
#            clear_proxys.append("benxiaohai:1328257811@106.186.18.67:62018")
#            clear_proxys.append("benxiaohai:1328257811@106.186.18.67:62019")
#            clear_proxys.append("benxiaohai:1328257811@106.186.18.67:62020")
            clear_proxys.extend(PROXIES)
        
        global proxy_ip_db_mutex
        if proxy_ip_db_mutex.acquire():
            for ip in clear_proxys:
                new_proxy_ip = ProxyIp()
                new_proxy_ip.ip = ip
                        
                try:
                    new_proxy_ip.save()
                    self.add_ip(ip)
                except:
                    pass
                
            proxy_ip_db_mutex.release()
            
    def _sleep_for_next_update(self):
        
        time.sleep(PROXY_IP_UPDATE_INTERVAL)
        
    def has_enough_ips(self):
        if len(self.ip_list) >= 10:
            return True
        else:
            return False
    
    def get_ip_number(self):
        return len(self.ip_list)
    
    def add_ip(self, new_ip):
        global threadLock
        threadLock.acquire()
        try:
            self.mid_ip_list.append(new_ip)
        except:
            pass
        finally:
            threadLock.release()
    
    def stop_me(self):
        self.stop_me = True
        
proxy_ip_manager = ProxyIPManager()

if __name__ == '__main__':
       
    global proxy_ip_manager
    proxy_ip_manager.start()
    
    start = time.time()
    while True:
        if proxy_ip_manager.has_enough_ips():
            print "has enough ips"
            end = time.time()
            print str(end - start) + "s"
        else:
            print "does not have enough ips"
        
        time.sleep(10)
#     getIPs_cn_proxy()
#     getIPs_xici()

