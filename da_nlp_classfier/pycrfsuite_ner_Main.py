# -*- coding: utf-8 -*-
'''
Created on Dec 7, 2015

@author: nlp
'''
import pycrfsuite
import jieba
import sys  
reload(sys)  
sys.setdefaultencoding('utf8') 

# 提取特征 针对训练集
def word2features(sent, i):
    word = sent[i][0]
    postag = sent[i][1]
    # 提取词本身的特征
    features = [
        'bias',
        'word=' + word,  # 词本身
        '0_in_word=' + str('0' in word),  # 词是否包含0
        '1_in_word=' + str('1' in word),  # 词是否包含1
        '2_in_word=' + str('2' in word),  # 词是否包含2
        '3_in_word=' + str('3' in word),  # 词是否包含3
        '4_in_word=' + str('4' in word),  # 词是否包含4
        '5_in_word=' + str('5' in word),  # 词是否包含5
        '6_in_word=' + str('6' in word),  # 词是否包含6
        '7_in_word=' + str('7' in word),  # 词是否包含7
        '8_in_word=' + str('8' in word),  # 词是否包含8
        '9_in_word=' + str('9' in word),  # 词是否包含9
        'word_len=' + str(len(word)),  # 词长度
        'word[-3:]=' + word[-3:],  # 词后三个字符
        'word[-2:]=' + word[-2:],  # 词后2个字符
        'word[-1:]=' + word[-1:],  # 词后1个字符
        'postag=' + postag,  # 词的tag
    ]
    # 提取前一个词的特征
    if i > 0:
        word1 = sent[i - 1][0]
        postag1 = sent[i - 1][1]
        features.extend([
            '-1:word=' + word1,
            '-0_in_word=' + str('0' in word1),
            '-1_in_word=' + str('1' in word1),
            '-2_in_word=' + str('2' in word1),
            '-3_in_word=' + str('3' in word1),
            '-4_in_word=' + str('4' in word1),
            '-5_in_word=' + str('5' in word1),
            '-6_in_word=' + str('6' in word1),
            '-7_in_word=' + str('7' in word1),
            '-8_in_word=' + str('8' in word1),
            '-9_in_word=' + str('9' in word1),
            '-1:word_len=' + str(len(word1)),
            '-1:word[-3:]=' + word1[-3:],
            '-1:word[-2:]=' + word1[-2:],
            '-1:word[-1:]=' + word1[-1:],
            '-1:postag=' + postag1,
        ])
    else:
        features.append('BOS')
    # 提取后一个词的特征
    if i < len(sent) - 1:
        word1 = sent[i + 1][0]
        postag1 = sent[i + 1][1]
        features.extend([
            '+1:word=' + word1,
            '+0_in_word=' + str('0' in word1),
            '+1_in_word=' + str('1' in word1),
            '+2_in_word=' + str('2' in word1),
            '+3_in_word=' + str('3' in word1),
            '+4_in_word=' + str('4' in word1),
            '+5_in_word=' + str('5' in word1),
            '+6_in_word=' + str('6' in word1),
            '+7_in_word=' + str('7' in word1),
            '+8_in_word=' + str('8' in word1),
            '+9_in_word=' + str('9' in word1),
            '+1:word_len=' + str(len(word1)),
            '＋1:word[-3:]=' + word1[-3:],
            '＋1:word[-2:]=' + word1[-2:],
            '＋1:word[-1:]=' + word1[-1:],
            '+1:postag=' + postag1,
        ])
    else:
        features.append('EOS')
    return features


# 提取特征 针对测试集
def word_to_feature_te(word_list, i):
    word = word_list[i]
    # 提取词本身的特征
    features = [
        'bias',
        'word=' + word,
        '0_in_word=' + str('0' in word),
        '1_in_word=' + str('1' in word),
        '2_in_word=' + str('2' in word),
        '3_in_word=' + str('3' in word),
        '4_in_word=' + str('4' in word),
        '5_in_word=' + str('5' in word),
        '6_in_word=' + str('6' in word),
        '7_in_word=' + str('7' in word),
        '8_in_word=' + str('8' in word),
        '9_in_word=' + str('9' in word),
        'word_len=' + str(len(word)),
        'word[-3:]=' + word[-3:],
        'word[-2:]=' + word[-2:],
        'word[-1:]=' + word[-1:],
    ]
    # 提取前一个词的特征
    if i > 0:
        word1 = word_list[i - 1]
        features.extend([
            '-1:word=' + word1,
            '-0_in_word=' + str('0' in word1),
            '-1_in_word=' + str('1' in word1),
            '-2_in_word=' + str('2' in word1),
            '-3_in_word=' + str('3' in word1),
            '-4_in_word=' + str('4' in word1),
            '-5_in_word=' + str('5' in word1),
            '-6_in_word=' + str('6' in word1),
            '-7_in_word=' + str('7' in word1),
            '-8_in_word=' + str('8' in word1),
            '-9_in_word=' + str('9' in word1),
            '-1:word_len=' + str(len(word1)),
            '-1:word[-3:]=' + word1[-3:],
            '-1:word[-2:]=' + word1[-2:],
            '-1:word[-1:]=' + word1[-1:],
        ])
    else:
        features.append('BOS')
    # 提取后一个词的特征
    if i < len(word_list) - 1:
        word1 = word_list[i + 1]
        features.extend([
            '+1:word=' + word1,
            '+0_in_word=' + str('0' in word1),
            '+1_in_word=' + str('1' in word1),
            '+2_in_word=' + str('2' in word1),
            '+3_in_word=' + str('3' in word1),
            '+4_in_word=' + str('4' in word1),
            '+5_in_word=' + str('5' in word1),
            '+6_in_word=' + str('6' in word1),
            '+7_in_word=' + str('7' in word1),
            '+8_in_word=' + str('8' in word1),
            '+9_in_word=' + str('9' in word1),
            '+1:word_len=' + str(len(word1)),
            '＋1:word[-3:]=' + word1[-3:],
            '＋1:word[-2:]=' + word1[-2:],
            '＋1:word[-1:]=' + word1[-1:],
        ])
    else:
        features.append('EOS')
    return features

# 对一个词串中的所有词提取特征  测试集
def word_list_to_feature_list(word_list):
    return [word_to_feature_te(word_list, i) for i in range(len(word_list))]

# 对一个句子中的所有词提取特征
def sent2features(sent):
    return [word2features(sent, i) for i in range(len(sent))]

# 获取一个句子中的所有词
def sent2word(sent):
    return [word for word, postag in sent]    

# 获取一个句子中的所有 tag
def sent2tag(sent):
    return [postag for word, postag in sent]   




# 读取文件 返回 sent： [(u'\u4e3b\u6301\u4eba', 'Word'), (u'\u5b8b\u5f3a', u'person_name'), ,,,,,,,,.]
def read_file(file_name):
    all_sents = []
    for line in open(file_name).readlines():
        line_list, tag_list = process_line(str(line)[:-1])
        all_sents.append(zip(line_list, tag_list))
    return all_sents

# 处理文件的一行 提取 tag 与对应的词
# time         时间实体
# location     位置实体
# person_name  人命实体
# org_name     机构名实体
# company_name 公司名实体
# product_name 产品名实体
# Symbol       符号
# Word         词 
def process_line(line):
    raw_list = [w for w in jieba.cut(line)]
    line_list = []
    tag_list = []
    
    index = 0
    while index < len(raw_list):
        if raw_list[index] == '' or raw_list[index] == ' ':  # 空格，或为空不进行处理
            index += 1
            continue
        if raw_list[index] == '\\' and raw_list[index + 1] == 'n':  # 处理 \n
            index += 2
            continue
        if raw_list[index] == '{' and raw_list[index + 1] == '{':  # 一个命名实体
            index += 2
            
            ner_tag = ''
            while raw_list[index] != ':':
                ner_tag += raw_list[index]
                index += 1
            tag_list.append(ner_tag)
            
            word = ''
            index += 1
            while raw_list[index] != '}':
                word += raw_list[index]
                index += 1
            line_list.append(word) 
            index += 2
        elif raw_list[index] == '[' or raw_list[index] == ']' or raw_list[index] == ',' or raw_list[index] == '·' \
            or raw_list[index] == '，' or raw_list[index] == '。' or raw_list[index] == '(' or raw_list[index] == '/' \
            or raw_list[index] == '?' or raw_list[index] == '!' or raw_list[index] == '(' or raw_list[index] == ')' \
            or raw_list[index] == ':' or raw_list[index] == '{' or raw_list[index] == '}' or raw_list[index] == '“' \
            or raw_list[index] == '”' or raw_list[index] == '‘' or raw_list[index] == '’'or raw_list[index] == '；':  # 如果是符号
            line_list.append(raw_list[index])
            tag_list.append('Symbol')
            index += 1
        else:  # 一个普通的词
            line_list.append(raw_list[index])
            tag_list.append('Word')
            index += 1
    return (line_list, tag_list)
            
            
            
            
            
if __name__ == '__main__':
    all_sents = read_file('BosonNLP_NER_6C.txt')
    
    train_sents = all_sents[1:]
    test_sents = all_sents[0:1]
    
    
    X_train = [sent2features(s) for s in train_sents]
    y_train = [sent2tag(s) for s in train_sents]
     
    trainer = pycrfsuite.Trainer(verbose=False)
    for xseq, yseq in zip(X_train, y_train):
        trainer.append(xseq, yseq)
    trainer.set_params({
                        'c1': 1.0,  # coefficient for L1 penalty
                        'c2': 1e-3,  # coefficient for L2 penalty
                        'max_iterations': 50,  # stop earlier
 
                        # include transitions that are possible, but not observed
                        'feature.possible_transitions': True
    })
    trainer.train('esp.crfsuite')
    
    
    tagger = pycrfsuite.Tagger()
    tagger.open('esp.crfsuite')
    
    example_sent = test_sents[0]
    predict_list = tagger.tag(word_list_to_feature_list(sent2word(example_sent)))
    correct_list = sent2tag(example_sent)

    print ' '.join(sent2word(example_sent))
    print("Predicted:", ' '.join(predict_list))
    print("Correct:  ", ' '.join(correct_list))
    
    count = 0
    for pre_tag, cor_tag in zip(predict_list, correct_list):
        count += 1 if pre_tag == cor_tag else 0
    print 'precision : ', float(count) / len(predict_list)
    
    pass
