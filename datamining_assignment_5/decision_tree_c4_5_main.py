# -*- coding: utf-8 -*-
'''
Created on Nov 30, 2015

@author: xhj
'''
import math

# 决策树 C4.5
class DecisionTree():
    
    def __init__(self, data_list, lable_list, feature_is_discrete, used_feature):
        self.isLeaf = True if len(set(lable_list)) == 1 or len(feature_is_discrete) == len(used_feature) else False
        self.lable = 99  # 随意设置的一个初始值
        self.branch = {}
        self.branch_used_feature_index = -1
        self.train(data_list, lable_list, feature_is_discrete, used_feature)
        self.lable_list = lable_list
        pass
    
    # 决策树训练
    def train(self, data_list, lable_list, feature_is_discrete, used_feature):
        if self.isLeaf :  # 符合单节点条件
            if len(set(lable_list)) == 1: 
                self.lable = lable_list[0]
            else:
                lable_count = {}
                for one_lable in set(lable_list):
                    lable_count[one_lable] = lable_list.count(one_lable)
                max_count = max(lable_count.values())
                for one_lable in set(lable_list):
                    if lable_count[one_lable] == max_count:
                        self.lable = one_lable
                        break    
        else:  # 要进行节点分裂
            self.lable = 'not_leaf_node'
            max_info_gain = 0.0
            max_info_gain_index = -1
            data_lable_map_fenge = {}
            need_to_add_used_feature = []
            for index_fea in range(len(feature_is_discrete)):
                if index_fea not in  used_feature:
                    info_gain, data_lable_map_fenge_candiate = calc_info_gain_ratio(data_list, lable_list, calc_data_set_empirical_entropy(lable_list), feature_is_discrete, index_fea)
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
                self.train(data_list, lable_list, feature_is_discrete, used_feature)
                return
            # 节点分裂
            used_feature.append(max_info_gain_index)
            self.branch_used_feature_index = max_info_gain_index
            for key_in in data_lable_map_fenge:  # key_in 是 data_lable_map_fenge 的key，对于离散性特征就是可能的值，连续性就是划分区间
                if len(data_lable_map_fenge[key_in][0]) > 0:
                    self.branch[key_in] = DecisionTree(data_lable_map_fenge[key_in][0], data_lable_map_fenge[key_in][1], feature_is_discrete, used_feature)
        pass
    
    # 决策树剪枝,返回 True 表示树没有收敛，需要继续减枝； False 就不需要
    def decision_tree_prnuing(self):
        if self.isLeaf:
            return False
        else:
            all_child_is_leaf = True
            for key_in in self.branch:
                all_child_is_leaf = False if not self.branch[key_in].isLeaf or all_child_is_leaf == False else True
            
            if all_child_is_leaf:  # 所有子节点均为叶子节点
                this_empirical_entropy = calc_data_set_empirical_entropy(self.lable_list) * len(self.lable_list)
                all_child_empirical_entropy = 0.0
                for key_in in self.branch:
                    all_child_empirical_entropy += calc_data_set_empirical_entropy(self.branch[key_in].lable_list) * len(self.branch[key_in].lable_list)
                
                if all_child_empirical_entropy - this_empirical_entropy > -0.000001:  # 满足条件，进行减枝
                    self.isLeaf = True
                    self.branch = {}
                    lable_count = {}
                    for one_lable in set(self.lable_list):
                        lable_count[one_lable] = self.lable_list.count(one_lable)
                    max_count = max(lable_count.values())
                    for one_lable in set(self.lable_list):
                        if lable_count[one_lable] == max_count:
                            self.lable = one_lable
                            break    
                    return True
            else:  # 不满足所有子节点均为叶子节点，对其分枝进行进一步的减枝
                changed = False
                for key_in in self.branch:
                    changed = True if self.branch[key_in].decision_tree_prnuing() or changed == True else False
                return changed
    
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
                        predict_result = self.branch[key_in].predict(one_data)
                        return  predict_result if predict_result is not None else -1 
                else:
                    if feature - key_in[0] > -0.0000001 and key_in[1] - feature > -0.0000001:
                        predict_result = self.branch[key_in].predict(one_data)
                        return  predict_result if predict_result is not None else -1 
                    

# 计算特征 i 对数据集的信息增益比
def calc_info_gain_ratio(data_list, lable_list, empirical_entropy, feature_is_discrete, i):
    lable_map_in_lable = {} 
    data_lable_map_fenge = {}  # 若按照这个特征进行划分, 分出的 data_list 与 lable_list
    if feature_is_discrete[i] :  # feature 是 discrete
        for index in range(len(data_list)):
            # 纪录可能的值对应的类别的个数
            if lable_map_in_lable.has_key(data_list[index][i]):
                lable_map_in_lable[data_list[index][i]].append(lable_list[index])
            else:
                lable_map_in_lable[data_list[index][i]] = [lable_list[index]]
            # 划分数据集 与 lable集
            if data_lable_map_fenge.has_key(data_list[index][i]):
                data_lable_map_fenge[data_list[index][i]][0].append(data_list[index])
                data_lable_map_fenge[data_list[index][i]][1].append(lable_list[index])
            else:
                data_lable_map_fenge[data_list[index][i]] = [[], []]
                data_lable_map_fenge[data_list[index][i]][0].append(data_list[index])
                data_lable_map_fenge[data_list[index][i]][1].append(lable_list[index])
        # 开始计算 h_d_a 与 h_a_d，返回结果
        h_d_a = h_a_d = 0.0
        for key_in in  lable_map_in_lable:
            h_d_a += float(len(lable_map_in_lable[key_in])) / len(lable_list) * calc_data_set_empirical_entropy(lable_map_in_lable[key_in])
            h_a_d -= (float(len(lable_map_in_lable[key_in])) / len(lable_list)) * math.log(float(len(lable_map_in_lable[key_in])) / len(lable_list), 2)
        return ((empirical_entropy - h_d_a) / h_a_d if not h_a_d == 0.0 else -100.0, data_lable_map_fenge)    
    else:  # feature 是 numeric
        feature_i_list = list(set([data_list[index][i] for index in range(len(data_list))]))
        feature_i_list.sort()
        fenlie_point = []  # 分裂点
        for i_index in range(len(feature_i_list) - 1):
            fenlie_point.append((feature_i_list[i_index] + feature_i_list[i_index + 1]) / 2.0)
        all_qu_jian = []  # 所有的划分方法
        for fen_lie in fenlie_point:
            all_qu_jian.append([(feature_i_list[0], fen_lie), (fen_lie, feature_i_list[-1])])
            
        max_info_gain = 0.0  # 最大信息增益
        max_h_a_d = 0.0
        max_data_lable_map_fenge = {}
        h_d_a = h_a_d = 0.0
        for qu_jian in all_qu_jian:  # 对于每一个区间
            lable_map_in_lable.clear()
            data_lable_map_fenge.clear()
            for index in range(len(data_list)):
                for key_in in qu_jian:
                    if data_list[index][i] - key_in[0] > -0.0000001 and key_in[1] - data_list[index][i] > -0.0000001 :
                        # 纪录可能的值对应的类别的个数
                        if lable_map_in_lable.has_key(key_in):
                            lable_map_in_lable[key_in].append(lable_list[index])
                        else:
                            lable_map_in_lable[key_in] = [lable_list[index]]
                        # 划分数据集 与 lable集
                        if data_lable_map_fenge.has_key(key_in):
                            data_lable_map_fenge[key_in][0].append(data_list[index])
                            data_lable_map_fenge[key_in][1].append(lable_list[index])
                        else:
                            data_lable_map_fenge[key_in] = [[], []]
                            data_lable_map_fenge[key_in][0].append(data_list[index])
                            data_lable_map_fenge[key_in][1].append(lable_list[index])
                        break
            # 计算信息增益
            for key_in in  lable_map_in_lable:
                h_d_a += float(len(lable_map_in_lable[key_in])) / len(lable_list) * calc_data_set_empirical_entropy(lable_map_in_lable[key_in])
                h_a_d -= (float(len(lable_map_in_lable[key_in])) / len(lable_list)) * math.log(float(len(lable_map_in_lable[key_in])) / len(lable_list), 2)
            info_gain = empirical_entropy - h_d_a
            if info_gain > max_info_gain:
                max_info_gain = info_gain
                max_data_lable_map_fenge = data_lable_map_fenge
                max_h_a_d = h_a_d
        return (max_info_gain / max_h_a_d if not max_h_a_d == 0.0 else -100.0, max_data_lable_map_fenge)
    

# 计算数据集的经验熵，只需要这个数据集的lable
def calc_data_set_empirical_entropy(lable_list):
    lable_size = [lable_list.count(lab) for lab in set(lable_list)]
    h_d = 0.0
    for one_size in lable_size:
        h_d -= (float(one_size) / len(lable_list)) * math.log((float(one_size) / len(lable_list)), 2)
    return h_d

# 读取文件信息，返回文件内容列表，特征信息，类别信息
def read_file(file_name):
    file_list = []
    feature_is_discrete = []
    lable_list = [] 
    for one_line in open(file_name).readlines():
        one_line_li = one_line[:-1].split(',')
        if len(feature_is_discrete) == 0:
            feature_is_discrete = [True if w == '1' else False for w in one_line_li]
        else:
            lable_list.append(float(one_line_li[-1]))
            del one_line_li[-1]
            file_list.append([float(fea) for fea in one_line_li])
    return (file_list, lable_list, feature_is_discrete)


# 划分数据集和测试集，用于交叉验证
def fenge_file_for_validation(file_list, lable_list, validation_num):
    fenge = [([], [], [], []) for i in range(validation_num)]
    for i in range(validation_num):
        start_index = int(i * len(file_list) / float(validation_num))
        end_index = int((i + 1) * len(file_list) / float(validation_num))
        fenge[i][0].extend(file_list[start_index:end_index])  # test file
        fenge[i][1].extend(lable_list[start_index:end_index])  # test lable
        if not start_index == 0:
            fenge[i][2].extend(file_list[:start_index])
            fenge[i][3].extend(lable_list[:start_index])
        if not end_index == len(file_list):
            fenge[i][2].extend(file_list[end_index:])
            fenge[i][3].extend(lable_list[end_index:])
    return fenge
    
# 传入文件名，使用决策树
def chuli_file(file_name):    
    file_list, lable_list, feature_is_discrete = read_file(file_name)
    fenge = fenge_file_for_validation(file_list, lable_list, 10)
    total_precision = 0.0
    for one_fenge in fenge:
        decision_tree_obj = DecisionTree(one_fenge[2], one_fenge[3], feature_is_discrete, [])
        while decision_tree_obj.decision_tree_prnuing():  # 对决策树进行减枝
            decision_tree_obj.decision_tree_prnuing()
        count = 0.0
        for i in range(len(one_fenge[0])):
            if decision_tree_obj.predict(one_fenge[0][i]) == one_fenge[1][i]:
                count += 1.0
        pre = count / len(one_fenge[0])
        total_precision += pre
        print 'precision :', pre
    print 'mean precision :', total_precision / 10
    pass


                                                           
if __name__ == '__main__':
    print "处理文件   breast-cancer-assignment5.txt ，分成10分，9分用于训练，一份用于测试"
    chuli_file('breast-cancer-assignment5.txt')
    print "处理文件   german-assignment5.txt ，分成10分，9分用于训练，一份用于测试"
    chuli_file('german-assignment5.txt')
    pass
