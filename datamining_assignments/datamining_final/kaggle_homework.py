# -*- coding: utf-8 -*-
'''
Created on Dec 12, 2015

@author: nlp
'''
import datetime

from ml_metrics import quadratic_weighted_kappa
from scipy.optimize import fmin_powell
from sklearn import linear_model
from sklearn import svm
from sklearn import tree
from sklearn.cross_validation import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.ensemble.weight_boosting import AdaBoostClassifier
from sklearn.feature_extraction import DictVectorizer
from sklearn.naive_bayes import GaussianNB
from sklearn.preprocessing.data import StandardScaler

import numpy as np
import pandas as pd
import xgboost as xgb


# 对训练集中的数据进行处理 看看那种方法好
def process(train_datas, train_lables):
    data_train, data_test, target_train, target_test = train_test_split(train_datas, train_lables)
    estimators = {}
    estimators['bayes'] = GaussianNB()
    estimators['tree'] = tree.DecisionTreeClassifier() 
    estimators['logistic '] = linear_model.LogisticRegression()
    estimators['ada boost '] = AdaBoostClassifier(linear_model.LogisticRegression(), algorithm="SAMME", n_estimators=400)
    estimators['ada boost '] = AdaBoostClassifier(tree.DecisionTreeClassifier(), algorithm="SAMME", n_estimators=400)
    estimators['forest_3000'] = RandomForestClassifier(n_estimators=3000)
    estimators['forest_2000'] = RandomForestClassifier(n_estimators=2000)
    estimators['forest_1000'] = RandomForestClassifier(n_estimators=1000)
    estimators['forest_900'] = RandomForestClassifier(n_estimators=900)
    estimators['forest_700'] = RandomForestClassifier(n_estimators=700)
    estimators['forest_500'] = RandomForestClassifier(n_estimators=500)
    estimators['forest_300'] = RandomForestClassifier(n_estimators=300)
    estimators['forest_100'] = RandomForestClassifier(n_estimators=100)
    estimators['forest_10'] = RandomForestClassifier(n_estimators=10)
    estimators['svm_c_rbf'] = svm.SVC()
    estimators['ada boost '] = AdaBoostClassifier(RandomForestClassifier(n_estimators=300), n_estimators=400)
    estimators['svm_c_sigmoid'] = svm.SVC(kernel='sigmoid') 
    estimators['svm_c_precomputed'] = svm.SVC(kernel='precomputed')
    estimators['svm_c_poly'] = svm.SVC(kernel='poly')
    estimators['svm_linear'] = svm.LinearSVC()
    estimators['svm_nusvc'] = svm.NuSVC()
    for k in estimators.keys():
        start_time = datetime.datetime.now()
        print '----%s----' % k
        estimators[k] = estimators[k].fit(data_train, target_train)
        print("%s Score: %0.2f" % (k, estimators[k].score(data_test, target_test)))        
        end_time = datetime.datetime.now()
        time_spend = end_time - start_time
        print("%s Time: %0.2f" % (k, time_spend.total_seconds()))
    pass


def determined_train_and_predict(train_datas, train_lables, test_ids, test_datas):
    class_fier = AdaBoostClassifier(RandomForestClassifier(n_estimators=300), algorithm="SAMME", n_estimators=400)
#     class_fier = RandomForestClassifier(n_estimators=300)
    class_fier.fit(train_datas, train_lables)
    
    predict_lables = class_fier.predict(test_datas)
    result_dic = {}
    result_dic['Id'] = test_ids
    result_dic['Response'] = predict_lables
    out_file_content = pd.DataFrame(result_dic)
    out_file_content.to_csv('sample3.csv', index=False)


def eval_wrapper(yhat, y):  
    y = np.array(y)
    y = y.astype(int)
    yhat = np.array(yhat)
    yhat = np.clip(np.round(yhat), np.min(y), np.max(y)).astype(int)   
    return quadratic_weighted_kappa(yhat, y)

def apply_offset(data, bin_offset, sv, scorer=eval_wrapper):
    # data has the format of pred=0, offset_pred=1, labels=2 in the first dim
    data[1, data[0].astype(int) == sv] = data[0, data[0].astype(int) == sv] + bin_offset
    score = scorer(data[1], data[2])
    return score        

# 使用 xgboost
def determined_train_and_predict_xgboost(train_datas, train_lables, test_ids, test_datas):
    params = {}
    params["objective"] = "reg:linear"     
    params["eta"] = 0.1
    params["min_child_weight"] = 80
    params["subsample"] = 0.75
    params["colsample_bytree"] = 0.30
    params["silent"] = 1
    params["max_depth"] = 9
    num_round = 250
    dtrain = xgb.DMatrix(train_datas, label=train_lables)
    dtest = xgb.DMatrix(test_datas)
    bst = xgb.train(params, dtrain, num_round)
    print("Training the model")
    train_preds = bst.predict(dtrain, ntree_limit=bst.best_iteration)
    test_preds = bst.predict(dtest, ntree_limit=bst.best_iteration)
    
    train_preds = np.clip(train_preds, -0.99, 8.99)
    test_preds = np.clip(test_preds, -0.99, 8.99)
    num_classes = 8
    # 训练集偏差
    offsets = np.ones(num_classes) * -0.5
    offset_train_preds = np.vstack((train_preds, train_preds, train_lables))
    for j in range(num_classes):
        train_offset = lambda x:-apply_offset(offset_train_preds, x, j)
        offsets[j] = fmin_powell(train_offset, offsets[j])  
    # 应用到测试集
    data = np.vstack((test_preds, test_preds, [-1 for i in range(len(test_preds))]))
    for j in range(num_classes):
        data[1, data[0].astype(int) == j] = data[0, data[0].astype(int) == j] + offsets[j] 
    final_test_preds = np.round(np.clip(data[1], 1, 8)).astype(int)
    preds_out = pd.DataFrame({"Id": test_ids, "Response": final_test_preds})
    preds_out = preds_out.set_index('Id')
    preds_out.to_csv('xgboost_my_1.csv')
    pass


def output_function(x):
    if x < 1:
        return 1
    elif x > 8:
        return 8
    elif int(round(x)) == 3:
        return 2
    else:
        return int(round(x))

# 读取 train.csv 中的数据 和 test.csv 中的数据
# 并对数据进行预处理
def read_file():
    file_content = pd.read_csv('train.csv')
    exc_cols = [u'Id', u'Response']
    cols = [c for c in file_content.columns if c not in exc_cols]
    train_datas = file_content.ix[:, cols]
    train_lables = file_content['Response'].values
    
    test_file = pd.read_csv('test.csv')
    test_ids = test_file['Id'].values
    test_datas = test_file.ix[:, [c for c in test_file.columns if c not in [u'Id']]]
    
    # 填充平均值
    test_datas = test_datas.fillna(-1)
    train_datas = train_datas.fillna(-1)
    all_datas = pd.concat([train_datas, test_datas], axis=0) 
    
    # 对数据进行一下划分
    categoricalVariables = ["Product_Info_1", "Product_Info_2", "Product_Info_3", "Product_Info_5", "Product_Info_6", "Product_Info_7", "Employment_Info_2", "Employment_Info_3", "Employment_Info_5", "InsuredInfo_1", "InsuredInfo_2", "InsuredInfo_3", "InsuredInfo_4", "InsuredInfo_5", "InsuredInfo_6", "InsuredInfo_7", "Insurance_History_1", "Insurance_History_2", "Insurance_History_3", "Insurance_History_4", "Insurance_History_7", "Insurance_History_8", "Insurance_History_9", "Family_Hist_1", "Medical_History_2", "Medical_History_3", "Medical_History_4", "Medical_History_5", "Medical_History_6", "Medical_History_7", "Medical_History_8", "Medical_History_9", "Medical_History_10", "Medical_History_11", "Medical_History_12", "Medical_History_13", "Medical_History_14", "Medical_History_16", "Medical_History_17", "Medical_History_18", "Medical_History_19", "Medical_History_20", "Medical_History_21", "Medical_History_22", "Medical_History_23", "Medical_History_25", "Medical_History_26", "Medical_History_27", "Medical_History_28", "Medical_History_29", "Medical_History_30", "Medical_History_31", "Medical_History_33", "Medical_History_34", "Medical_History_35", "Medical_History_36", "Medical_History_37", "Medical_History_38", "Medical_History_39", "Medical_History_40", "Medical_History_41"]
    all_file_data = all_datas.ix[:, [c for c in all_datas.columns if c not in categoricalVariables]]
    all_file_cate = all_datas.ix[:, [c for c in categoricalVariables]]
 
    # 归一化 对数值数据
    scalar_this = StandardScaler()
    scalar_this.fit_transform(all_file_data)
    
    # 重新组合数据
    train_datas = pd.concat([all_file_data[:train_datas.shape[0]], all_file_cate[:train_datas.shape[0]]], axis=1)
    test_datas = pd.concat([all_file_data[file_content.shape[0]:], all_file_cate[file_content.shape[0]:]], axis=1)
    
    # 向量化
    train_datas = DictVectorizer().fit_transform(train_datas.to_dict(outtype='records')).toarray()
    test_datas = DictVectorizer().fit_transform(test_datas.to_dict(outtype='records')).toarray()
    
    return (train_datas, train_lables, test_ids, test_datas)
    

if __name__ == '__main__':
    train_datas, train_lables, test_ids, test_datas = read_file()
#     process(train_datas, train_lables)
#     determined_train_and_predict(train_datas, train_lables, test_ids, test_datas)
    
    determined_train_and_predict_xgboost(train_datas, train_lables, test_ids, test_datas)
    pass
