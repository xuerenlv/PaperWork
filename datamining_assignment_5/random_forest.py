# -*- coding: utf-8 -*-
'''
Created on Dec 3, 2015

@author: xhj
'''

import random
from decision_tree_c4_5_main import read_file, fenge_file_for_validation,\
    calc_data_set_empirical_entropy, calc_info_gain_ratio
import math

# 随机森林
class RandomForest:
    
    def __init__(self, sample_data_list, sample_lable_list, feature_is_discrete, used_feature, m):
        self.isLeaf = True if len(set(sample_lable_list)) == 1 or len(feature_is_discrete) == len(used_feature) else False
        self.lable = 99  # 随意设置的一个初始值
        self.branch = {}
        self.branch_used_feature_index = -1
        self.train(sample_data_list, sample_lable_list, feature_is_discrete, used_feature, m)
        pass
    
    # 决策树训练
    def train(self, sample_data_list, sample_lable_list, feature_is_discrete, used_feature, m):
        if self.isLeaf :  # 符合单节点条件
            if len(set(sample_lable_list)) == 1: 
                self.lable = sample_lable_list[0]
            else:
                lable_count = {}
                for one_lable in set(sample_lable_list):
                    lable_count[one_lable] = sample_lable_list.count(one_lable)
                max_count = max(lable_count.values())
                for one_lable in set(sample_lable_list):
                    if lable_count[one_lable] == max_count:
                        self.lable = one_lable
                        break    
        else:  # 要进行节点分裂
            self.lable = 'not_leaf_node'
            max_info_gain = 0.0
            max_info_gain_index = -1
            data_lable_map_fenge = {}
            need_to_add_used_feature = []
            
            un_used_feature = []  # 在没有使用过的特征中，随机选取，最多 m 个
            for index_fea in range(len(feature_is_discrete)):
                if index_fea not in  used_feature and random.uniform(0, 1) - 0.5 > -0.000001 and len(un_used_feature) <= m:
                    un_used_feature.append(index_fea)
            for index_fea in un_used_feature:
                info_gain, data_lable_map_fenge_candiate = calc_info_gain_ratio(sample_data_list, sample_lable_list, calc_data_set_empirical_entropy(sample_lable_list), feature_is_discrete, index_fea)
                if info_gain == -100.0:
                    need_to_add_used_feature.append(index_fea)
                    break
                if info_gain > max_info_gain :
                    max_info_gain = info_gain
                    max_info_gain_index = index_fea
                    data_lable_map_fenge = data_lable_map_fenge_candiate
            used_feature.extend(need_to_add_used_feature)
            if len(feature_is_discrete) == len(used_feature):
                self.isLeaf = True
                self.train(sample_data_list, sample_lable_list, feature_is_discrete, used_feature,m)
                return
            # 节点分裂
            used_feature.append(max_info_gain_index)
            self.branch_used_feature_index = max_info_gain_index
            for key_in in data_lable_map_fenge:  # key_in 是 data_lable_map_fenge 的key，对于离散性特征就是可能的值，连续性就是划分区间
                if len(data_lable_map_fenge[key_in][0]) > 0:
                    self.branch[key_in] = RandomForest(data_lable_map_fenge[key_in][0], data_lable_map_fenge[key_in][1], feature_is_discrete, used_feature,m)
        pass
    
    # 计算叶子节点的个数
    def count_leaf_num(self):
        count = 0
        if self.isLeaf:
            count = 1
        else:
            for key_in in self.branch:
                count += self.branch[key_in].count_leaf_num()
        return count
    
    # 输出所有叶子节点的类别
    def print_leaf_lable(self):
        if self.isLeaf:
            print self.lable
        else:
            for key_in in self.branch:
                print type(key_in)
                self.branch[key_in].print_leaf_lable()
        pass
    
    # 决策树预测,给定 one_data 预测其所属类别
    def predict(self, one_data):
        if self.isLeaf:
            return self.lable
        else:
            feature = one_data[self.branch_used_feature_index]
            for key_in in self.branch:
                if type(key_in) == float:
                    if feature == key_in:
                        return self.branch[key_in].predict(one_data)
                else:
                    if feature - key_in[0] > -0.0000001 and key_in[1] - feature > -0.0000001:
                        return self.branch[key_in].predict(one_data)
    
# 传入文件名，使用随机森林
def chuli_file(file_name , t, m):    
    file_list, lable_list, feature_is_discrete = read_file(file_name)
    fenge = fenge_file_for_validation(file_list, lable_list, 10)
    pre_all = []
    for one_fenge in fenge:
        
        data_list = one_fenge[2]
        lable_list = one_fenge[3]
        
        t_ge_random_forests = []  # t 个 random forest
        for i_t in range(t):  # 生成 t 个树
            sample_data_list = []
            sample_lable_list = []
            for num in range(len(data_list)):  # 进行抽样
                random_i = int(random.uniform(0, len(data_list)))
                sample_data_list.append(data_list[random_i])
                sample_lable_list.append(lable_list[random_i])
            t_ge_random_forests.append(RandomForest(sample_data_list, sample_lable_list, feature_is_discrete, [], m))

        # 进行测试            
        count = 0.0
        for i in range(len(one_fenge[0])):
            t_predict = []
            for i_p in range(t):
                t_predict.append(t_ge_random_forests[i_p].predict(one_fenge[0][i]))
            predict_re = -99  # 预测结果
            for i_p in range(t):
                if predict_re == -99 or(t_predict[i_p] != predict_re and t_predict.count(t_predict[i_p]) > t_predict.count(predict_re)):
                    predict_re = t_predict[i_p]
            if predict_re == one_fenge[1][i]:
                count += 1.0
        pre = count / len(one_fenge[0])
        pre_all.append(pre)
        print 'precision :', pre
    mean_pre = sum(pre_all) / 10.0
    print 'mean precision      :', mean_pre
    print 'standard deviation  :',math.sqrt(sum([(w-mean_pre)**2 for w in pre_all]))
    pass


                                                           
if __name__ == '__main__':
    print "处理文件   breast-cancer-assignment5.txt ，分成10分，9分用于训练，一份用于测试"
    chuli_file('breast-cancer-assignment5.txt',20,15)
    print "处理文件   german-assignment5.txt ，分成10分，9分用于训练，一份用于测试"
    chuli_file('german-assignment5.txt',20,15)
    pass



