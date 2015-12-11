# -*- coding: utf-8 -*-
'''
Created on Dec 3, 2015

@author: xhj
'''
from decision_tree_c4_5_main import read_file, fenge_file_for_validation, \
    DecisionTree
import math
import random



# AdaBoost 算法
class AdaBoost:
    
    def __init__(self, data_list, lable_list, feature_is_discrete, M):
        self.M = M
        self.result_coefficient = []  # 存储最终的分类器线性组合的系数
        self.result_base_tree = []  # 存储最终的分类器 中的基本分类器
        init_quzhi_fenbu = [1.0 / len(data_list) for i in range(len(data_list))]  # 初始化权值分布
        self.train(data_list, lable_list, feature_is_discrete, init_quzhi_fenbu, 0)
        pass
    
    # AdaBoost的训练
    def train(self, data_list, lable_list, feature_is_discrete, init_quzhi_fenbu, index_fenleiqi):
        if index_fenleiqi == self.M:
            return
        base_decision_tree = DecisionTree(data_list, lable_list, feature_is_discrete, [])  # 训练出的基本分类器
        
        e_m = 0.0  # 分类误差率 
        for index in range(len(data_list)):
            if base_decision_tree.predict(data_list[index]) != lable_list[index]:
                e_m += init_quzhi_fenbu[index]
        
        # 计算系数
        a_m = (1.0 / 2.0) * math.log((1.0 - e_m) / e_m)
        self.result_base_tree.append(base_decision_tree)
        self.result_coefficient.append(a_m)  
        
        # 更新权值分布
        quanzhi_fenbu = []
        
        z_m = 0.0
        for index_2 in range(len(data_list)):
            z_m += init_quzhi_fenbu[index_2] * math.exp(-1.0 * a_m * base_decision_tree.predict(data_list[index_2]))
        
        for index_3 in range(len(data_list)):
            quanzhi_fenbu.append((init_quzhi_fenbu[index_3] / z_m) * math.exp(-1.0 * a_m * base_decision_tree.predict(data_list[index_3])))
        
        # 依据权值分布，进行数据抽样
        new_data_list = []
        new_lable_list = []
        for index_4 in range(len(data_list)):
            rand_num = random.uniform(0,1)
            for index_5 in range(len(data_list)):
                if rand_num > 0:
                    rand_num -= quanzhi_fenbu[index_5]
                else:
                    new_data_list.append(data_list[index_5-1])
                    new_lable_list.append(lable_list[index_5-1])
                    break
           
            
        self.train(new_data_list, new_lable_list, feature_is_discrete, quanzhi_fenbu, index_fenleiqi + 1)
        pass
    
    # 预测
    def predict(self, one_data):
        f_x = 0.0
        for index in range(self.M):
            coefficient = self.result_coefficient[index] 
            repredict = self.result_base_tree[index].predict(one_data)
            repredict = repredict if repredict is not None else 1
            f_x += coefficient * repredict
        return -1.0 if f_x < 0.0 else 1.0
        
        




# 传入文件名，使用 AdaBoost
def chuli_file(file_name, M):    
    file_list, lable_list, feature_is_discrete = read_file(file_name)
    lable_list = [1 if lable > 0 else -1 for lable in lable_list]  # 对二类分类的 lable 做优化
    fenge = fenge_file_for_validation(file_list, lable_list, 10)
    pre_all = []
    for one_fenge in fenge:
        decision_tree_obj = AdaBoost(one_fenge[2], one_fenge[3], feature_is_discrete, M)
        count = 0.0
        for i in range(len(one_fenge[0])):
            if decision_tree_obj.predict(one_fenge[0][i]) == one_fenge[1][i]:
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
    chuli_file('breast-cancer-assignment5.txt', 5)
    print "处理文件   german-assignment5.txt ，分成10分，9分用于训练，一份用于测试"
    chuli_file('german-assignment5.txt', 10)
    pass
