# -*- coding: utf-8 -*-

'''
Created on Nov 9, 2015

@author: nlp
'''







# 计算P（w｜c）
def calc_w_c(one_word, class_lable, positive_list, negative_list, vocabulary_size, positive_size, negative_size):
    if class_lable > 0:
        count = 0
        for words in positive_list:
            for w in words:
                if w == one_word:
                    count += 1
        if count == 0:
            count = 1
        return float(count) / float(positive_size + vocabulary_size) 
    else:
        count = 0
        for words in negative_list:
            for w in words:
                if w == one_word:
                    count += 1
        if count == 0:
            count = 1
        return float(count) / float(negative_size + vocabulary_size) 
    
# 计算P（c）
def calc_p_c(positive_list, negative_list, class_lable):
    p = len(positive_list)
    n = len(negative_list)
    return float(p) / float(p + n) if class_lable > 0 else float(n) / float(p + n)
    
# 计算当前句子属于所说类的概率
def cal_sentence_pro(words_list, class_lable, positive_list, negative_list, vocabulary_size, positive_size, negative_size):
    pro = calc_p_c(positive_list, negative_list, class_lable)
    for one_word in words_list:
        pro *= calc_w_c(one_word, class_lable, positive_list, negative_list, vocabulary_size, positive_size, negative_size)
    return pro

# 1,binaized
if __name__ == '__main__':
    file_lable = open('train2.rlabelclass')
    file_tran = open('merged_train2.txt')
    
    lable_dict = {}
    
    for lable_line in file_lable.readlines():
        name_lable = lable_line[:-1].split(' ')
        lable_dict[name_lable[0]] = name_lable[1]
    
    # # 对 train 文件的处理
    positive_list = []
    negative_list = []
    vocabulary_size = 0
    positive_size = 0
    negative_size = 0
    for tran_line in file_tran.readlines():
        file_name = tran_line[1:tran_line.find(']')]
        file_words = tran_line[tran_line.rfind('['):-1].split(' ')
        vocabulary_size += len(file_words)
        if lable_dict[file_name] == u'+1':
            positive_size += len(file_words)
            positive_list.append(list(file_words))
        else:
            negative_size += len(file_words)
            negative_list.append(list(file_words))
    
   
    # # 对 test 文件进行预测        
    test_file_lable = open('test2.rlabelclass')
    test_file = open('merged_test2.txt')
    
    test_lable_dict = {}
    for lable_line in test_file_lable.readlines():
        name_lable = lable_line[:-1].split(' ')
        test_lable_dict[name_lable[0]] = int(name_lable[1])
    
    
    predicted_lable_dict = {}
    for test_line in test_file.readlines():
        file_name = test_line[1:test_line.find(']')]
        file_words = set(test_line[test_line.rfind('['):-1].split(' '))
        positive = cal_sentence_pro(file_words, 1, positive_list, negative_list, vocabulary_size, positive_size, negative_size)
        negtive = cal_sentence_pro(file_words, -1, positive_list, negative_list, vocabulary_size, positive_size, negative_size)
        predicted_lable_dict[file_name] = 1 if positive - negtive > 0.00000001 else -1
    
    # # 对分类结果进行评价
    TP = 0 
    TN = 0
    FP = 0
    FN = 0
    for file_name in test_lable_dict.keys():
        if test_lable_dict[file_name] > 0 and test_lable_dict[file_name] == predicted_lable_dict[file_name]:
            TP += 1
        if test_lable_dict[file_name] < 0 and test_lable_dict[file_name] == predicted_lable_dict[file_name]:
            TN += 1
        if test_lable_dict[file_name] > 0 and test_lable_dict[file_name] != predicted_lable_dict[file_name]:
            FN += 1
        if test_lable_dict[file_name] < 0 and test_lable_dict[file_name] != predicted_lable_dict[file_name]:
            FP += 1
    
    print TP, FN, FP, TN
    print '精确率:', float(TP) / float(TP + FP)
    print '召回率:', float(TP) / float(TP + FN)        
    print 'F1值:', float(2 * TP) / float(2 * TP + FP + FN)        
    pass
