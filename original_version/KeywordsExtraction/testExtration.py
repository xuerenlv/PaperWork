#encoding=utf8
'''
Created on 2014年8月14日 上午10:27:11

@author: GreatShang
@environment: win7 sp1 64, eclipse 4.4, Pydev 3.6, Python 3.4
'''
import ChineseDealing

import sys
reload(sys)
sys.setdefaultencoding("utf-8")

#####################################################
################使用方法如下所示######################
#代码文件夹包含文件chinesenews.txt，内容为一篇中文新闻#
'''
input_file = open('chinesenews.txt',encoding= 'utf8')
fileContent = input_file.read()
tags = ChineseDealing.extract_tags(fileContent, topK=5)
print ('1'+",".join(tags))
'''
str1 = u'记者10日从公安部获悉，全国公安交通管理部门将从10月11日至12月31日开展公路重点交通违法行为专项整治工作，对高速公路及重点国、省道上的超速行驶、客车超员、疲劳驾驶3种严重违法行为进行集中整治。'
keystr1 = u'整治交通违法'
print(keystr1)
print(str1)
for word in ChineseDealing.extractForumTag(str1):
    print word

str2 = '10日10时50分左右，重庆綦江县境内发生一起重大交通事故，一辆中型客车由于方向盘突然失灵，客车从山间公路上侧翻掉入河中，目前已确定7人死亡、15人受伤。'
keystr2 = '重庆重大车祸'
print(keystr2)
print(str2)
print(ChineseDealing.extractForumTag(str2))

str3 = '一位石油业内专家认为，国内成品油价格可能出现“象征性”的下调。'
keystr3 = '油价'
print(keystr3)
print(str3)
print(ChineseDealing.extractNewsTag(str3))

str4 = '铁道部公安局政委张庆和昨日表示，预计明年4月我国列车将实现第六次大提速，在一些区段客车运行时速可达200公里。'
keystr4 = '列车提速'
print(keystr4)
print(str4)
print(ChineseDealing.extract_tags(str4, topK=2))

str5 = '记者10日从陕西省渭南市政府了解到，当地大面积滑坡灾害最后一名遇难者遗体已被发现，此次灾害被埋13位村民中有1人获救、12人死亡。'
keystr5 = '陕西滑坡'
print(keystr5)
print(str5)
print(ChineseDealing.extract_tags(str5, topK=2))

str6 = '绑架杀害内蒙古自治区知名民营企业家云全民的两名凶手潘永忠和刘志强，在10日的一审宣判中被呼和浩特市中级人民法院判处死刑，剥夺政治权利终身。'
keystr6 = '内蒙古绑架杀人案'
print(keystr6)
print(str6)
print(ChineseDealing.extract_tags(str6, topK=2))

str7 = '昨日，发改委、教育部等七部委联合发出通知，决定从10月上旬开始至11月底，在全国范围内开展教育收费专项检查。据记者了解，我国55万所中小学中，每年择校费收入至少百亿元以上。'
keystr7 = '择校费'
print(keystr7)
print(str7)
print(ChineseDealing.extract_tags(str7, topK=2))

str8 = '去年发生在云南文山“10·18”的校园惨案中，一名未满18周岁的中学生因怀恨同村同学，深夜悄悄潜入宿舍，杀死熟睡的同学。就在他走出凶案现场时，遇见了另外两个同学，第二天晚上，凶手再次进入宿舍杀人灭口。此案震惊全国。记者昨日获悉，云南省高院对这起凶杀案作出终审判决：维持一审法院判处凶手无期徒刑，并由被告人家属及其所在学校共同赔偿死者家属15万元。'
keystr8 = '云南校园惨案追踪'
print(keystr8)
print(str8)
print(ChineseDealing.extract_tags(str8, topK=2))

str9 = '近日，一位阳光型的准未婚妈妈却用她的坚强和乐观感染了身边的朋友和许多网民。地瓜猪(blog)——北京某报一名文化记者，在几个月前突遇感情变故，却毅然决定留下肚里的孩子，亲切地称这个孩子为“猪娃”，并在博客中用轻松、调侃的语言记录下怀孕期间的点点滴滴，该博客的点击率在一周内突破30万。'
keystr9 = '未婚妈妈开博客'
print(keystr9)
print(str9)
print(ChineseDealing.extract_tags(str9, topK=2))
