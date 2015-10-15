# -*- coding: utf-8 -*-
'''
    weibosearch db configuration

    @MOdified by cheng chuan
    on 2014/4/11
    Modified by lyuxiao
    on 2013.11.1


    @author Jiajun Huang
    Created on 2013/10/17
'''
try:
    import sys
    import yaml
    import os
except ImportError:
    print >> sys.stderr
    sys.exit()

try:
    curpath=os.path.normpath( os.path.join( os.getcwd(), os.path.dirname(__file__) ) ) 
    conf_file = open(curpath+"/weibosearch.yaml", 'r')
except:
    try:
        conf_file = open("../weibosearch.yaml", 'r')
    except:
        print 'weibo.yaml not found'
    
conf_dic = yaml.load(conf_file)
conf_file.close()

###########The following are configuration data about database##########
DBNAME = conf_dic['searchdb']['dbname']
DBHOST = conf_dic['searchdb']['host']
DBPORT = conf_dic['searchdb']['port']

BOOL_GETCOMMENTS = conf_dic['searchdb']['BOOL_getcomments']


###########The following are configuration data about sinaweibo login in#
# USERNAME = conf_dic['login'][0]['username']
# PASSWORD = conf_dic['login'][0]['password']
# USERNAME_1 = conf_dic['login'][1]['username']
# PASSWORD_1 = conf_dic['login'][1]['password']
# USERNAME_2 = conf_dic['login'][2]['username']
# PASSWORD_2 = conf_dic['login'][2]['password']
# USERNAME_3 = conf_dic['login'][3]['username']
# PASSWORD_3 = conf_dic['login'][3]['password']
# USERNAME_4 = conf_dic['login'][4]['username']
# PASSWORD_4 = conf_dic['login'][4]['password']
# USERNAME_5 = conf_dic['login'][5]['username']
# PASSWORD_5 = conf_dic['login'][5]['password']
# USERNAME_6 = conf_dic['login'][6]['username']
# PASSWORD_6 = conf_dic['login'][6]['password']
# USERNAME_7 = conf_dic['login'][7]['username']
# PASSWORD_7 = conf_dic['login'][7]['password']
# USERNAME_8 = conf_dic['login'][8]['username']
# PASSWORD_8 = conf_dic['login'][8]['password']
# USERNAME_9 = conf_dic['login'][9]['username']
# PASSWORD_9 = conf_dic['login'][9]['password']
# USERNAME_10 = conf_dic['login'][10]['username']
# PASSWORD_10 = conf_dic['login'][10]['password']
# USERNAME_11 = conf_dic['login'][11]['username']
# PASSWORD_11 = conf_dic['login'][11]['password']
# USERNAME_12 = conf_dic['login'][12]['username']
# PASSWORD_12 = conf_dic['login'][12]['password']
# 
# COOKIE_FILE = conf_dic['cookie_file']

COOKIE_FILE = conf_dic['cookie_file']

LOGIN_USER_INFOR = []
for login_infor in conf_dic['login']:
    LOGIN_USER_INFOR.append({"username":str(login_infor["username"]), "password":str(login_infor["password"])})
    
###########The following are configuration data about log database
LOGDB = str(conf_dic['logdb']['dbname'])
LOGHOST = str(conf_dic['logdb']['host'])
LOGUSER = str(conf_dic['logdb']['user'])
LOGPW = str(conf_dic['logdb']['password'])
CHARSET = str(conf_dic['logdb']['charset'])

############The following are configuration data about mysql log database#######

MINCACHED = int(conf_dic['mysqldb_pool']['mincached'])
MAXCACHED = int(conf_dic['mysqldb_pool']['maxcached'])
MAXCONNECTIONS = int(conf_dic['mysqldb_pool']['maxconnections'])
BLOCKING = bool(conf_dic['mysqldb_pool']['blocking'])
MAXUSAGE = int(conf_dic['mysqldb_pool']['maxusage'])
SETSESSION = None if conf_dic['mysqldb_pool']['setsession'] == 'None' else None
RESET = bool(conf_dic['mysqldb_pool']['reset'])
FAILURES = bool(conf_dic['mysqldb_pool']['failures'])
PING = int(conf_dic['mysqldb_pool']['ping'])

PROXIES = []
for proxy in conf_dic['proxies']:
    PROXIES.append(proxy['ip'])

if __name__ == '__main__':
    print DBNAME, DBHOST, DBPORT
    print COOKIE_FILE
    print LOGDB, LOGHOST, LOGUSER, LOGPW

    for login_infor in LOGIN_USER_INFOR:
        print 'username: ' + login_infor['username'] + '\t' + "password: " + login_infor['password']
