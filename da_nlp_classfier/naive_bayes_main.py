# -*- coding: utf-8 -*-

'''
Created on Nov 9, 2015

@author: nlp
'''

# 计算P（w｜c）
def calc_w_c(one_word, class_lable, vocabulary_size, positive_train_files, nagetative_train_files):
    count = 0.0
    if class_lable > 0:
        for file_name in positive_train_files:
            if (positive_train_files[file_name]).has_key(one_word):
                count += positive_train_files[file_name][one_word]        

    else:
        for file_name in nagetative_train_files:
            if (nagetative_train_files[file_name]).has_key(one_word):
                count += nagetative_train_files[file_name][one_word]       
    return count if count != 0.0 else 0.009
    
# 计算P（c）
def calc_p_c(positive_train_files, nagetative_train_files, class_lable):
    p = len(positive_train_files)
    n = len(nagetative_train_files)
    return float(p) / float(p + n) if class_lable > 0 else float(n) / float(p + n)
    
    
# 计算当前句子属于所说类的概率
def cal_sentence_pro(words_list, class_lable, vocabulary_size, positive_train_files, nagetative_train_files):
    pro = calc_p_c(positive_train_files, nagetative_train_files, class_lable)
    for one_word in words_list:
        pro *= calc_w_c(one_word, class_lable, vocabulary_size, positive_train_files, nagetative_train_files)
    return pro


if __name__ == '__main__':
    file_lable = open('train2.rlabelclass')
    file_tran = open('merged_train2.txt')
    
    lable_dict = {}  # 存放filename，value为对应的文档类别
    for lable_line in file_lable.readlines():
        name_lable = lable_line[:-1].split(' ')
        lable_dict[name_lable[0]] = int(name_lable[1])
    
    
     
    # # 对 train 文件的处理
    train_files = {}
    idf_calc = {}
    for tran_line in file_tran.readlines():
        file_name = tran_line[1:tran_line.find(']')]
        train_files[file_name] = {}
        file_words = tran_line[tran_line.rfind('['):-1].split(' ')
        set_file_words = set(file_words)
        file_len = len(file_words)
        
        # 计算 TF
        for one_word in set_file_words:
            count = 0
            for another_word in file_words:
                count += 1 if one_word == another_word else 0
            train_files[file_name][one_word] = float(count) / float(file_len)
            
            if idf_calc.has_key(one_word):
                idf_calc[one_word] += 1
            else:
                idf_calc[one_word] = 1
    
    # # 计算 TF－IDF
    train_files_len = len(lable_dict)
    for file_name in train_files:
        for one_word in train_files[file_name]:
            train_files[file_name][one_word] *= float(idf_calc[one_word]) / float(train_files_len)
    
    
    # # 对 train 进行分割，切分出正类的与负类的
    positive_train_files = {}
    nagetative_train_files = {}
    vocabulary_size = 0
    for file_name in train_files:
        vocabulary_size += len(train_files[file_name])
        if lable_dict[file_name] > 0:
            positive_train_files[file_name] = train_files[file_name]
        else:
            nagetative_train_files[file_name] = train_files[file_name]
   
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
        positive = cal_sentence_pro(file_words, 1, vocabulary_size, positive_train_files, nagetative_train_files)
        negtive = cal_sentence_pro(file_words, -1, vocabulary_size, positive_train_files, nagetative_train_files)
        predicted_lable_dict[file_name] = 1 if positive - negtive > 0.00000001 else -1
    
    # # 对分类结果进行评价
    TP = 0 
    TN = 0
    FP = 0
    FN = 0
    for file_name in test_lable_dict.keys():
        if test_lable_dict[file_name] == predicted_lable_dict[file_name]:
            if test_lable_dict[file_name] > 0: 
                TP += 1
            else:
                TN += 1
        else:
            if test_lable_dict[file_name] > 0: 
                FN += 1
            else:
                FP += 1
    print TP, TN, FP, FN
    print '精确率:', float(TP) / float(TP + FP)
    print '召回率:', float(TP) / float(TP + FN)        
    print 'F1值:', float(2 * TP) / float(2 * TP + FP + FN)        
    pass



# 412 1912 88 1588
# 精确率: 0.827
# 召回率: 0.206
# F1值: 0.3296
