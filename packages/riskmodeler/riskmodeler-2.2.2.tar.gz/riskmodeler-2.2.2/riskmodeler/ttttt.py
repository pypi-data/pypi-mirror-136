# Project: US Information Tools
# Program: US Info Tool.py
# Created: Tianyi Xia 2021/10
# **********************************************************************;
# *** Import Packages ***
# **********************************************************************;
#import pymysql
import re
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import tensorflow as tf
import nltk
import sklearn
import configparser
import unicodedata
import warnings
import xml.etree.ElementTree
import pyspark.sql.functions as f
from scipy import stats
from tensorflow import keras
from keras.preprocessing.text import text_to_word_sequence
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from nltk.stem import WordNetLemmatizer
from nltk.corpus import wordnet
from nltk.tokenize import word_tokenize
from nltk import pos_tag
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.model_selection import train_test_split
from sklearn import svm
from sklearn.naive_bayes import MultinomialNB
from sklearn.naive_bayes import GaussianNB
from sklearn.metrics import roc_auc_score
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report
from sklearn.metrics import auc, accuracy_score, confusion_matrix, mean_squared_error
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_selection import SelectPercentile
from sklearn.feature_selection import chi2
from langdetect import detect
from tqdm import tqdm
from sklearn.datasets import fetch_20newsgroups
from sklearn.preprocessing import FunctionTransformer
from sklearn.linear_model import SGDClassifier
from sklearn.model_selection import train_test_split
from sklearn.semi_supervised import SelfTrainingClassifier
from sklearn.semi_supervised import LabelSpreading
from sklearn.metrics import f1_score

tqdm.pandas()
from pandas.core.common import SettingWithCopyWarning
from sklearn.exceptions import DataConversionWarning

warnings.simplefilter(action="ignore", category=SettingWithCopyWarning)
warnings.filterwarnings(action='ignore', category=DataConversionWarning)

import matplotlib.pyplot as plt

import wordsegment
from wordsegment import load, segment


# **********************************************************************;
# *** Initialize ***
# **********************************************************************;
def readSettings():
    config = configparser.ConfigParser()
    config.read('./Settings/USITNPL.ini')
    period_list = config.get('PREPROCESS', 'Period1').split(',')
    site_list = config.get('PREPROCESS', 'Site').split(',')
    pat_list = []
    for key in config['PATTERN']:
        pat_list.append(config['PATTERN'][key])
    return period_list, site_list, pat_list


# **********************************************************************;
# *** Read Data ***
# **********************************************************************;
def readData():
    train = pd.read_csv('./weekly/w1105/train.csv')
    unlabel = pd.read_csv('./weekly/w1105/test.csv')
    return train, unlabel


# **********************************************************************;
# *** Bag of Words & Tf-idf Vector ***
# **********************************************************************;
def Vectorizer(data, data1):
    ##### Instantiate CountVectorizer()
    def preprocess_text(text):
        text = text.lower()
        text = re.sub(r'\d+', '', text)
        return text

    cv = CountVectorizer(preprocessor=preprocess_text, analyzer='word', stop_words='english')

    ##### This steps generates word counts for the words in your docs
    data = data[data['Text'].isna() == False].reset_index(drop=True)
    data1 = data1[data1['Text'].isna() == False].reset_index(drop=True)

    word_count_vector = cv.fit_transform([data['Text'][i] for i in range(0, len(data['Text']))])
    word_count_vector.shape

    ##### Bag of Words
    bow = pd.DataFrame(word_count_vector.toarray(), columns=cv.get_feature_names())

    ##### Remove low-frequency words (after rename pcnlistpcn)
    for col, val in bow.iteritems():
        keep = val == 0
        if sum(keep) >= len(bow) - 1:
            bow = bow.drop([col], axis=1)

    ##### Tf-idf transformer
    tfidf = TfidfVectorizer(decode_error='ignore', min_df=2)
    # tfidf = TfidfVectorizer(decode_error='ignore')

    X_tfidf = tfidf.fit_transform(data['Text'])
    y_tfidf = tfidf.transform(data1['Text'])
    #  ##### Get idf values
    #  df_idf = pd.DataFrame(tfidf.idf_, index=tfidf.get_feature_names(),columns=["idf_weights"])
    #
    #  ##### Sort ascending
    #  df_idf.sort_values(by=['idf_weights'])
    #
    #  ##### Get tfidf vector for first document
    #  first_document_vector=X_tfidf[79]
    #
    #  ##### Get the scores
    #  df = pd.DataFrame(first_document_vector.T.todense(), index=tfidf.get_feature_names(), columns=["tfidf"])
    #  df.sort_values(by=["tfidf"],ascending=False)[:10]
    #
    return X_tfidf, y_tfidf


if __name__ == '__main__':
    period_list, site_list, pat_list = readSettings()
    label, unlabel = readData()
    X_tfidf, y_tfidf = Vectorizer(label, unlabel)
###Prediction###
# X_train = label[['Text','PCN_count']][0:140]
# y_train = label[['Relevant','Side effect','Recall']][0:140]
# X_test = label[['Text','PCN_count']][140:]
# y_test = label[['Relevant','Side effect','Recall']][140:]

# X_train = np.array(label[['Text']][0:140])
# y_train = np.array(label[['Relevant']][0:140])
# X_test = label[['Text']][140:]
# y_test = np.array(label[['Relevant']][140:]).reshape(-1,1)

##MultinomialNB - Relevant
##71/77 0.9221 0.8940
from sklearn.naive_bayes import MultinomialNB

X_train = X_tfidf[0:100]
X_test = X_tfidf[100:]
y_train = np.array(label[['Relevant']][0:100])
y_test = np.array(label[['Relevant']][100:])

clf = MultinomialNB()
clf.fit(X_train, y_train)
pred = clf.predict(X_test)

# Check acc&auc
anslist = [item for sublist in y_test for item in sublist]
predlist = list(pred)

right = 0
for i in range(0, len(anslist)):
    if anslist[i] == predlist[i]:
        right += 1
print(right)
print(len(anslist))
print(right / len(anslist))

sklearn.metrics.roc_auc_score(y_test, pred, average='macro', sample_weight=None, max_fpr=None, multi_class='raise',
                              labels=None)
test_accuracy = round(accuracy_score(pred, y_test), 4)
print(confusion_matrix(y_test, pred))

##MultinomialNB - Side effect
##57/77 0.7403 0.5
from sklearn.naive_bayes import MultinomialNB

X_train = X_tfidf[0:100]
X_test = X_tfidf[100:]
y_train = np.array(label[['Side effect']][0:100])
y_test = np.array(label[['Side effect']][100:])

clf = MultinomialNB()
clf.fit(X_train, y_train)
pred = clf.predict(X_test)

# Check acc&auc
anslist = [item for sublist in y_test for item in sublist]
predlist = list(pred)

right = 0
for i in range(0, len(anslist)):
    if anslist[i] == predlist[i]:
        right += 1
print(right)
print(len(anslist))
print(right / len(anslist))

sklearn.metrics.roc_auc_score(y_test, pred, average='macro', sample_weight=None, max_fpr=None, multi_class='raise',
                              labels=None)
test_accuracy = round(accuracy_score(pred, y_test), 4)
print(confusion_matrix(y_test, pred))

##MultinomialNB - Recall
##70/77 0.9091 0.8656
from sklearn.naive_bayes import MultinomialNB

X_train = X_tfidf[0:100]
X_test = X_tfidf[100:]
y_train = np.array(label[['Recall']][0:100])
y_test = np.array(label[['Recall']][100:])

clf = MultinomialNB()
clf.fit(X_train, y_train)
pred = clf.predict(X_test)

# Check acc&auc
anslist = [item for sublist in y_test for item in sublist]
predlist = list(pred)

right = 0
for i in range(0, len(anslist)):
    if anslist[i] == predlist[i]:
        right += 1
print(right)
print(len(anslist))
print(right / len(anslist))

sklearn.metrics.roc_auc_score(y_test, pred, average='macro', sample_weight=None, max_fpr=None, multi_class='raise',
                              labels=None)
test_accuracy = round(accuracy_score(pred, y_test), 4)
print(confusion_matrix(y_test, pred))

##Random Forest - Relevant
##72/77 0.9351 0.9321
from sklearn.naive_bayes import MultinomialNB

X_train = X_tfidf[156:]
X_test = X_tfidf[0:156]
y_train = np.array(label[['Relevant']][156:])
y_test = np.array(label[['Relevant']][0:156])

clf = RandomForestClassifier(n_estimators=100, criterion='entropy', random_state=42)
clf.fit(X_train, y_train)
pred = clf.predict(X_test)

# Check acc&auc
anslist = [item for sublist in y_test for item in sublist]
predlist = list(pred)

right = 0
for i in range(0, len(anslist)):
    if anslist[i] == predlist[i]:
        right += 1
print(right)
print(len(anslist))
print(right / len(anslist))

sklearn.metrics.roc_auc_score(y_test, pred, average='macro', sample_weight=None, max_fpr=None, multi_class='raise',
                              labels=None)
test_accuracy = round(accuracy_score(pred, y_test), 4)
print(confusion_matrix(y_test, pred))
print(classification_report(y_test, pred))

##Random Forest - Side effect
##60/77 0.7792 0.5912
from sklearn.naive_bayes import MultinomialNB

X_train = X_tfidf[156:]
X_test = X_tfidf[0:156]
y_train = np.array(label[['Side effect']][156:])
y_test = np.array(label[['Side effect']][0:156])

clf = RandomForestClassifier(n_estimators=100, criterion='entropy', random_state=42)
clf.fit(X_train, y_train)
pred = clf.predict(X_test)

# Check acc&auc
anslist = [item for sublist in y_test for item in sublist]
predlist = list(pred)

right = 0
for i in range(0, len(anslist)):
    if anslist[i] == predlist[i]:
        right += 1
print(right)
print(len(anslist))
print(right / len(anslist))

sklearn.metrics.roc_auc_score(y_test, pred)
test_accuracy = round(accuracy_score(pred, y_test), 4)
print(confusion_matrix(y_test, pred))
print(classification_report(y_test, pred))

##Random Forest - Recall
##71/77 0.9221 0.9206
from sklearn.naive_bayes import MultinomialNB

X_train = X_tfidf[156:]
X_test = X_tfidf[0:156]
y_train = np.array(label[['Recall']][156:])
y_test = np.array(label[['Recall']][0:156])

clf = RandomForestClassifier(n_estimators=100, criterion='entropy', random_state=42)
clf.fit(X_train, y_train)
pred = clf.predict(X_test)

# Check acc&auc
anslist = [item for sublist in y_test for item in sublist]
predlist = list(pred)

right = 0
for i in range(0, len(anslist)):
    if anslist[i] == predlist[i]:
        right += 1
print(right)
print(len(anslist))
print(right / len(anslist))

sklearn.metrics.roc_auc_score(y_test, pred, average='macro', sample_weight=None, max_fpr=None, multi_class='raise',
                              labels=None)
test_accuracy = round(accuracy_score(pred, y_test), 4)

print(confusion_matrix(y_test, pred))
print(classification_report(y_test, pred))

# xgb
from sklearn.metrics import auc, accuracy_score, confusion_matrix, mean_squared_error
from sklearn.model_selection import cross_val_score, GridSearchCV, KFold, RandomizedSearchCV, train_test_split

import xgboost as xgb

xgb_model = xgb.XGBClassifier(objective="binary:logistic", random_state=42)
xgb_model.fit(X_train, y_train)

pred = xgb_model.predict(X_test)

#####################
##Try All together
# Random Forest
X_train = X_tfidf[0:100]
X_test = X_tfidf[100:]
y_train = np.array(label[['Relevant', 'Side effect', 'Recall']][0:100])
y_test = np.array(label[['Relevant', 'Side effect', 'Recall']][100:])

clf = RandomForestClassifier(n_estimators=100, criterion='entropy', random_state=42)
clf.fit(X_train, y_train)

pred = clf.predict_proba(X_test)

pred = clf.predict(X_test)

# Check acc&auc
anslist = [item for sublist in y_test for item in sublist]
predlist = list(pred)

sklearn.metrics.roc_auc_score(y_test, pred, average='macro', sample_weight=None, max_fpr=None, multi_class='raise',
                              labels=None)
round(accuracy_score(pred, y_test), 4)

predDF = pd.DataFrame(pred)
ansDF = pd.DataFrame(y_test)
predDF.to_csv('./weekly/w1105/RFpred.csv')
ansDF.to_csv('./weekly/w1105/RFans.csv')

##Try Self Learning
# Random Forest-Recall
Testing = label[['TrainingID', 'Recall']]  #
Testing['Recall'][30:] = 0  #

index_list = [i for i in range(0, 30)]
# label['TrainingID']=label.index
Testing['TrainingID'] = Testing.index

keeprunning = True
itera = 0
while keeprunning:
    itera += 1
    nonind_list = []
    for i in range(0, len(Testing)):
        if i not in index_list:
            nonind_list.append(i)
    X_train = X_tfidf[index_list]
    X_test = X_tfidf[nonind_list]
    y_train_o = Testing[['TrainingID', 'Recall']].iloc[index_list]
    y_test_o = Testing[['TrainingID', 'Recall']].iloc[nonind_list]
    y_train = np.array(Testing[['Recall']].iloc[index_list])
    y_test = np.array(Testing[['Recall']].iloc[nonind_list])

    clf = RandomForestClassifier(n_estimators=100, criterion='entropy', random_state=42)
    clf.fit(X_train, y_train)
    print('#######')
    print(itera)
    # print(len(nonind_list))
    pred = clf.predict_proba(X_test)
    temp_score = []
    for i in pred:
        temp_score.append(i[1])
    temp_score = np.array(temp_score)
    temp_ranking = np.argsort(temp_score)[::-1]
    score_sort = sorted(temp_score, reverse=True)
    cnt = 0
    for i in score_sort:
        if cnt < 5:
            if i > 0.5:
                turnID = y_test_o['TrainingID'].iloc[temp_ranking[cnt]]
                index_list.append(turnID)
                Testing['Recall'][turnID] = 1
            else:
                if cnt == 0:
                    keeprunning = False
                break
        else:
            break
        cnt += 1
    print(len(index_list))

sklearn.metrics.roc_auc_score(Testing['Recall'][30:], label['Recall'][30:], average='weighted')
round(accuracy_score(Testing['Recall'][30:], label['Recall'][30:]), 4)

Testing['Recall'][30:].to_csv('./weekly/w1105/RFSL.csv')
label['Recall'][30:].to_csv('./weekly/w1105/LASL.csv')

# Random Forest-Recall/Side
col = 'Recall'
col = 'Side effect'
col = 'Relevant'
Testing = label[['TrainingID', col]]  #
Testing[col][0:156] = 0  #

index_list = [i for i in range(156, 177)]
# label['TrainingID']=label.index
Testing['TrainingID'] = Testing.index

keeprunning = True
itera = 0
cutoff = 0.9
while keeprunning:
    itera += 1
    nonind_list = []
    for i in range(0, len(Testing)):
        if i not in index_list:
            nonind_list.append(i)
    X_train = X_tfidf[index_list]
    X_test = X_tfidf[nonind_list]
    y_train_o = Testing[['TrainingID', col]].iloc[index_list]
    y_test_o = Testing[['TrainingID', col]].iloc[nonind_list]
    y_train = np.array(Testing[[col]].iloc[index_list])
    y_test = np.array(Testing[[col]].iloc[nonind_list])

    clf = RandomForestClassifier(n_estimators=100, criterion='entropy', random_state=42)
    clf.fit(X_train, y_train)
    #  print('#######')
    #  print(itera)
    # print(len(nonind_list))
    pred = clf.predict_proba(X_test)
    # print(pred)
    temp_score = []
    for i in pred:
        temp_score.append(i[1])
    temp_score = np.array(temp_score)
    temp_ranking = np.argsort(temp_score)[::-1]
    score_sort = sorted(temp_score, reverse=True)
    cnt = 0
    for i in score_sort:
        if cnt < 5:
            if i > cutoff:
                turnID = y_test_o['TrainingID'].iloc[temp_ranking[cnt]]
                index_list.append(turnID)
                Testing[col][turnID] = 1
            else:
                if cnt == 0:
                    keeprunning = False
                break
        else:
            break
        cnt += 1
    cutoff -= 0.011
    #  if cutoff<0.7:
    #    cutoff=0.7
    print(len(index_list))

# sklearn.metrics.roc_auc_score(Testing[col][30:], label[col][30:], average='macro', sample_weight=None, max_fpr=None, multi_class='raise', labels=None)
# round(accuracy_score(Testing[col][30:], label[col][30:]),4)
# sklearn.metrics.roc_auc_score(label[col][0:156], Testing[col][0:156],average='weighted')
# sklearn.metrics.recall_score(label[col][0:156], Testing[col][0:156])
round(accuracy_score(label[col][0:156], Testing[col][0:156]), 4)
print(confusion_matrix(label[col][0:156], Testing[col][0:156]))
# sklearn.metrics.balanced_accuracy_score(label[col][0:156], Testing[col][0:156],adjusted=True)
print(classification_report(label[col][0:156], Testing[col][0:156]))

###Try both low&high
# Random Forest-Recall/Side
col = 'Recall'
col = 'Side effect'
col = 'Relevant'
Testing = label[['TrainingID', col]]  #
Testing[col][0:56] = 0  #

index_list = [i for i in range(56, 177)]
# label['TrainingID']=label.index
Testing['TrainingID'] = Testing.index

keeprunning = True
keeprunningh = True
keeprunningl = True
itera = 0
hcutoff = 0.8
lcutoff = 0.2
while keeprunning:
    itera += 1
    nonind_list = []
    for i in range(0, len(Testing)):
        if i not in index_list:
            nonind_list.append(i)
    X_train = X_tfidf[index_list]
    X_test = X_tfidf[nonind_list]
    y_train_o = Testing[['TrainingID', col]].iloc[index_list]
    y_test_o = Testing[['TrainingID', col]].iloc[nonind_list]
    y_train = np.array(Testing[[col]].iloc[index_list])
    y_test = np.array(Testing[[col]].iloc[nonind_list])

    clf = RandomForestClassifier(n_estimators=100, criterion='entropy', random_state=42)
    clf.fit(X_train, y_train)
    #  print('#######')
    #  print(itera)
    # print(len(nonind_list))
    pred = clf.predict_proba(X_test)
    # print(pred)
    temp_score = []
    for i in pred:
        temp_score.append(i[1])
    temp_score = np.array(temp_score)
    htemp_ranking = np.argsort(temp_score)[::-1]
    ltemp_ranking = np.argsort(temp_score)
    hscore_sort = sorted(temp_score, reverse=True)
    lscore_sort = sorted(temp_score, reverse=False)
    cnt = 0
    for i in hscore_sort:
        if cnt < 3:
            if i > hcutoff:
                turnID = y_test_o['TrainingID'].iloc[htemp_ranking[cnt]]
                index_list.append(turnID)
                Testing[col][turnID] = 1
            else:
                if cnt == 0:
                    keeprunningh = False
                break
        else:
            break
        cnt += 1
    cnt = 0
    for i in lscore_sort:
        if cnt < 3:
            if i < lcutoff:
                turnID = y_test_o['TrainingID'].iloc[ltemp_ranking[cnt]]
                index_list.append(turnID)
                Testing[col][turnID] = 0
            else:
                if cnt == 0:
                    keeprunningl = False
                break
        else:
            break
        cnt += 1
    if not (keeprunningh or keeprunningl):
        keeprunning = False
    #  cutoff-=0.011
    #  if cutoff<0.7:
    #    cutoff=0.7
    print(len(index_list))

# sklearn.metrics.roc_auc_score(Testing[col][30:], label[col][30:], average='macro', sample_weight=None, max_fpr=None, multi_class='raise', labels=None)
# round(accuracy_score(Testing[col][30:], label[col][30:]),4)
# sklearn.metrics.roc_auc_score(label[col][0:156], Testing[col][0:156],average='weighted')
# sklearn.metrics.recall_score(label[col][0:156], Testing[col][0:156])
round(accuracy_score(label[col][0:56], Testing[col][0:56]), 4)
print(confusion_matrix(label[col][0:56], Testing[col][0:56]))
# sklearn.metrics.balanced_accuracy_score(label[col][0:56], Testing[col][0:156],adjusted=True)
print(classification_report(label[col][0:56], Testing[col][0:56]))

temp_ranking[:5]
y_test_o['TrainingID'].iloc[temp_ranking[:5]]
k = np.array(y_test_o['TrainingID'].iloc[temp_ranking[:5]])
for turnID in k:
    index_list.append(turnID)
    label[['Recall']].iloc[turnID] = 1

pred = clf.predict(X_test)

# Check acc&auc
anslist = [item for sublist in y_test for item in sublist]
predlist = list(pred)

sklearn.metrics.roc_auc_score(y_test, pred, average='macro', sample_weight=None, max_fpr=None, multi_class='raise',
                              labels=None)
round(accuracy_score(pred, y_test), 4)

label.to_csv('./weekly/w1105/labelans.csv')
##Try Active Learning
# Random Forest
X_train = X_tfidf
X_test = y_tfidf
y_train = np.array(label[['Relevant', 'Side effect', 'Recall']])
y_test = np.array(label[['Relevant', 'Side effect', 'Recall']])

clf = RandomForestClassifier(n_estimators=100, criterion='entropy', random_state=42)
clf.fit(X_train, y_train)

pred = clf.predict(X_test)

# Check acc&auc
anslist = [item for sublist in y_test for item in sublist]
predlist = list(pred)

sklearn.metrics.roc_auc_score(y_test, pred, average='macro', sample_weight=None, max_fpr=None, multi_class='raise',
                              labels=None)
round(accuracy_score(pred, y_test), 4)

predDF = pd.DataFrame(pred)
ansDF = pd.DataFrame(y_test)
predDF.to_csv('./weekly/w1105/RFpred.csv')
ansDF.to_csv('./weekly/w1105/RFans.csv')

################
# Random Forest (Manual Relevant)
X_train = X_tfidf[0:100]
X_test = X_tfidf[100:]
y_train = np.array(label[['Side effect', 'Recall']][0:100])
y_test = np.array(label[['Relevant', 'Side effect', 'Recall']][100:])

clf = RandomForestClassifier(n_estimators=100, criterion='entropy', random_state=42)
clf.fit(X_train, y_train)

pred = clf.predict(X_test)

pred = pred.tolist()
for i in range(0, len(pred)):
    if pred[i][0] + pred[i][1] > 0:
        pred[i].insert(0, 1)
    else:
        pred[i].insert(0, 0)

sklearn.metrics.roc_auc_score(y_test, pred, average='macro', sample_weight=None, max_fpr=None, multi_class='raise',
                              labels=None)

# LR
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score
from sklearn.multiclass import OneVsRestClassifier

# Using pipeline for applying logistic regression and one vs rest classifier
LogReg_pipeline = Pipeline([
    ('clf', OneVsRestClassifier(LogisticRegression(solver='sag'), n_jobs=-1)),
])
categories = ['Relevant', 'Side effect', 'Recall']
for category in categories:
    print('**Processing {} comments...**'.format(category))

    # Training logistic regression model on train data
    LogReg_pipeline.fit(X_train, y_train)

    # calculating test accuracy
    prediction = LogReg_pipeline.predict(X_test)
    print('Test accuracy is {}'.format(accuracy_score(y_test, prediction)))
    print("\n")

# Label Propagation
X_train = X_tfidf[0:100]
X_test = X_tfidf[100:]
y_train = np.array(label[['Relevant']][0:100])
y_test = np.array(label[['Relevant']][100:])

lp_model = LabelSpreading(gamma=0.25, max_iter=20)
lp_model.fit(X_train.toarray(), y_train)
predicted_labels = lp_model.transduction_[X_test]
true_labels = y[unlabeled_indices]

X = X_tfidf.toarray()
y = np.array(label[['Relevant']])

n_total_samples = len(y)
n_labeled_points = 100
max_iterations = 5

unlabeled_indices = np.arange(n_total_samples)[n_labeled_points:]
f = plt.figure()

for i in range(max_iterations):
    if len(unlabeled_indices) == 0:
        print("No unlabeled items left to label.")
        break
    y_train = np.copy(y)
    y_train[unlabeled_indices] = -1

    lp_model = LabelSpreading(gamma=0.25, max_iter=20)
    lp_model.fit(X, y_train)

    predicted_labels = lp_model.transduction_[unlabeled_indices]
    true_labels = y[unlabeled_indices]

    cm = confusion_matrix(true_labels, predicted_labels, labels=lp_model.classes_)

    print("Iteration %i %s" % (i, 70 * "_"))
    print(
        "Label Spreading model: %d labeled & %d unlabeled (%d total)"
        % (n_labeled_points, n_total_samples - n_labeled_points, n_total_samples)
    )

    print(classification_report(true_labels, predicted_labels))

    print("Confusion matrix")
    print(cm)

    # compute the entropies of transduced label distributions
    pred_entropies = stats.distributions.entropy(lp_model.label_distributions_.T)

    # select up to 5 digit examples that the classifier is most uncertain about
    uncertainty_index = np.argsort(pred_entropies)[::-1]
    uncertainty_index = uncertainty_index[
                            np.in1d(uncertainty_index, unlabeled_indices)
                        ][:5]

    # keep track of indices that we get labels for
    delete_indices = np.array([], dtype=int)

    # for more than 5 iterations, visualize the gain only on the first 5
    if i < 5:
        f.text(
            0.05,
            (1 - (i + 1) * 0.183),
            "model %d\n\nfit with\n%d labels" % ((i + 1), i * 5 + 10),
            size=10,
        )
    for index, image_index in enumerate(uncertainty_index):
        #        image = images[image_index]
        #
        #        # for more than 5 iterations, visualize the gain only on the first 5
        #        if i < 5:
        #            sub = f.add_subplot(5, 5, index + 1 + (5 * i))
        #            sub.imshow(image, cmap=plt.cm.gray_r, interpolation="none")
        #            sub.set_title(
        #                "predict: %i\ntrue: %i"
        #                % (lp_model.transduction_[image_index], y[image_index]),
        #                size=10,
        #            )
        #            sub.axis("off")

        # labeling 5 points, remote from labeled set
        (delete_index,) = np.where(unlabeled_indices == image_index)
        delete_indices = np.concatenate((delete_indices, delete_index))

    unlabeled_indices = np.delete(unlabeled_indices, delete_indices)
    n_labeled_points += len(uncertainty_index)

f.suptitle(
    "Active learning with Label Propagation.\nRows show 5 most "
    "uncertain labels to learn with the next model.",
    y=1.15,
)
plt.subplots_adjust(left=0.2, bottom=0.03, right=0.9, top=0.9, wspace=0.2, hspace=0.85)
plt.show()

# Try AL
import numpy as np
from small_text.active_learner import PoolBasedActiveLearner
from small_text.classifiers import ConfidenceEnhancedLinearSVC
from small_text.classifiers.factories import SklearnClassifierFactory
from small_text.query_strategies import PoolExhaustedException, EmptyPoolException
from small_text.query_strategies import RandomSampling

nb = Pipeline([('tfidf', Vectorizer()),
               ('clf', MultinomialNB()),
               ])
nb.fit(X_train, y_train)

test_predict = nb.predict(X_test)
print("Naive Bayes Train Accuracy Score : {}% ".format(train_accuracy))
print("Naive Bayes Test Accuracy Score  : {}% ".format(test_accuracy))
print()
print(classification_report(test_predict, Y_test, target_names=target_category))

# Parameters
sdg_params = dict(alpha=1e-5, penalty='l2', loss='log')
vectorizer_params = dict(min_df=2)
# Supervised Pipeline
pipeline = Pipeline([
    ('vect', CountVectorizer(**vectorizer_params)),
    ('tfidf', TfidfTransformer()),
    ('clf', SGDClassifier(**sdg_params)),
])
# SelfTraining Pipeline
st_pipeline = Pipeline([
    ('vect', CountVectorizer(**vectorizer_params)),
    ('tfidf', TfidfTransformer()),
    ('clf', SelfTrainingClassifier(SGDClassifier(**sdg_params), verbose=True)),
])
# LabelSpreading Pipeline
ls_pipeline = Pipeline([
    ('vect', CountVectorizer(**vectorizer_params)),
    ('tfidf', TfidfTransformer()),
    # LabelSpreading does not support dense matrices
    ('todense', FunctionTransformer(lambda x: x.todense())),
    ('clf', LabelSpreading()),
])

clf = pipeline


def eval_and_print_metrics(clf, X_train, y_train, X_test, y_test):
    print("Number of training samples:", len(X_train))
    print("Unlabeled samples in training set:",
          sum(1 for x in y_train if x == -1))
    clf.fit(X_train, y_train)
    y_pred = clf.predict(X_test)
    print("Micro-averaged F1 score on test set: "
          "%0.3f" % f1_score(y_test, y_pred, average='micro'))
    print("-" * 10)
    print()


print("Supervised SGDClassifier on 100% of the data:")
eval_and_print_metrics(pipeline, X_train, y_train, X_test, y_test)

import os

import numpy as np

from sklearn.datasets import fetch_20newsgroups
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.preprocessing import FunctionTransformer
from sklearn.linear_model import SGDClassifier
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.semi_supervised import SelfTrainingClassifier
from sklearn.semi_supervised import LabelSpreading
from sklearn.metrics import f1_score

data = fetch_20newsgroups(subset='train', categories=None)
print("%d documents" % len(data.filenames))
print("%d categories" % len(data.target_names))
print()

# Parameters
sdg_params = dict(alpha=1e-5, penalty='l2', loss='log')
vectorizer_params = dict(ngram_range=(1, 2), min_df=2)

# Supervised Pipeline
pipeline = Pipeline([
    ('vect', CountVectorizer(**vectorizer_params)),
    ('tfidf', TfidfTransformer()),
    ('clf', SGDClassifier(**sdg_params)),
])
# SelfTraining Pipeline
st_pipeline = Pipeline([
    ('vect', CountVectorizer(**vectorizer_params)),
    ('tfidf', TfidfTransformer()),
    ('clf', SelfTrainingClassifier(SGDClassifier(**sdg_params), verbose=True)),
])
# LabelSpreading Pipeline
ls_pipeline = Pipeline([
    ('vect', CountVectorizer(**vectorizer_params)),
    ('tfidf', TfidfTransformer()),
    # LabelSpreading does not support dense matrices
    ('todense', FunctionTransformer(lambda x: x.todense())),
    ('clf', LabelSpreading()),
])


def eval_and_print_metrics(clf, X_train, y_train, X_test, y_test):
    print("Number of training samples:", len(X_train))
    print("Unlabeled samples in training set:",
          sum(1 for x in y_train if x == -1))
    clf.fit(X_train, y_train)
    y_pred = clf.predict(X_test)
    print("Micro-averaged F1 score on test set: "
          "%0.3f" % f1_score(y_test, y_pred, average='micro'))
    print("-" * 10)
    print()


if __name__ == "__main__":
    X, y = data.data, data.target
    X_train, X_test, y_train, y_test = train_test_split(X, y)

    print("Supervised SGDClassifier on 100% of the data:")
    eval_and_print_metrics(pipeline, X_train, y_train, X_test, y_test)

    # select a mask of 20% of the train dataset
    y_mask = np.random.rand(len(y_train)) < 0.2

    # X_20 and y_20 are the subset of the train dataset indicated by the mask
    X_20, y_20 = map(list, zip(*((x, y)
                                 for x, y, m in zip(X_train, y_train, y_mask) if m)))
    print("Supervised SGDClassifier on 20% of the training data:")
    eval_and_print_metrics(pipeline, X_20, y_20, X_test, y_test)

    # set the non-masked subset to be unlabeled
    y_train[~y_mask] = -1
    print("SelfTrainingClassifier on 20% of the training data (rest "
          "is unlabeled):")
    eval_and_print_metrics(st_pipeline, X_train, y_train, X_test, y_test)

    if 'CI' not in os.environ:
        # LabelSpreading takes too long to run in the online documentation
        print("LabelSpreading on 20% of the data (rest is unlabeled):")
        eval_and_print_metrics(ls_pipeline, X_train, y_train, X_test, y_test)




