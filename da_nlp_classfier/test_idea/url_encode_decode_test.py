# -*- coding: utf-8 -*-
'''
Created on 2016年2月26日

@author: nlp
'''
from urllib import unquote_plus  ,quote

# /n/%E5%BF%85%E5%BA%94%E6%90%9C%E7%B4%A2
# http://weibo.cn/u/2997618404

def chuli_at_info(at_info):
    nickname_list = []
    for one in at_info.split("[fen_ge]"):
        nickname_list.append(one[:one.find(":")])    
    return nickname_list


if __name__ == '__main__':
#     nickname_list = chuli_at_info("花蕊夫人:@花蕊夫人[fen_ge]jack5500:@jack5500[fen_ge]ZSSH-SJM:@ZSSH-SJM[fen_ge]GOWE1130155891:@GOWE1130155891[fen_ge]花蕊夫人:@花蕊夫人")
#     print "   ".join(nickname_list)
#     
#     nickname_list = chuli_at_info("哎哟玮玮:@哎哟玮玮[fen_ge]静哥哥1968618953:@静哥哥1968618953[fen_ge]宜宾罗鸿:@宜宾罗鸿[fen_ge]杨兴珙县巡场三友:@杨兴珙县巡场三友")
#     print "   ".join(nickname_list)
    
    
    
#     print unquote_plus("%E5%BF%85%E5%BA%94%E6%90%9C%E7%B4%A2")
    print quote("陈一文顾问提出的质疑")
#     print quote("chobitsr")=="chobitsr"
#     print quote("2997618404")
    pass


# 花蕊夫人:@花蕊夫人[fen_ge]jack5500:@jack5500[fen_ge]ZSSH-SJM:@ZSSH-SJM[fen_ge]GOWE1130155891:@GOWE1130155891[fen_ge]花蕊夫人:@花蕊夫人
# 哎哟玮玮:@哎哟玮玮[fen_ge]静哥哥1968618953:@静哥哥1968618953[fen_ge]宜宾罗鸿:@宜宾罗鸿[fen_ge]杨兴珙县巡场三友:@杨兴珙县巡场三友