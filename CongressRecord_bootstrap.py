# -*- coding: utf-8 -*-
import os
import sys
import subprocess
from nltk.tokenize import sent_tokenize
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem.porter import PorterStemmer
import re 
import cPickle
import numpy as np
import scipy
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import HashingVectorizer
import scipy.io as sio
from sklearn.linear_model import LogisticRegression
from numpy.random import permutation
from random import shuffle
from sklearn import metrics
from sklearn.metrics import roc_auc_score
from sklearn.utils import shuffle
from sklearn.svm import SVR
from time import clock
# prepare training set
target_year = sys.argv[1] 
target_congressType = sys.argv[2]
reader = open('./data/CongressionalRecordData/speechText/speechText_' + target_year + '.txt','r')
'''
eachSingleSpeech.congressManName,
        eachSingleSpeech.congressType,
        eachSingleSpeech.party,
        eachSingleSpeech.state,
        eachSingleSpeech.dw_score,
        str(eachSingleSpeech.year),
        str(eachSingleSpeech.month),
        str(eachSingleSpeech.day),
        eachSingleSpeech.cleanText
'''
articleDict = {}
allKeys = []
for eachArticle in reader:
	[congressManName, congressType, party, state, dw_score, year, month, day, text] = eachArticle.split('##')
	if dw_score != 'null' and target_congressType in congressType.lower():
		temp_key = congressManName + '##' + state + '##' + dw_score + '##' + party
		if articleDict.has_key(temp_key):
			articleDict[temp_key] += text + ' '
		else:
			articleDict[temp_key] = text + ' '
			allKeys.append(temp_key)
print 'total' + target_congressType + ' congress people in ' + target_year + 'is: ' + str(len(allKeys))

total_regress_result = []
total_regress_target = []

total_class_result = []
total_class_target = []

for eachTestPeopleInfo in allKeys:

	target_congressManName, target_state, target_dw_score, target_party = eachTestPeopleInfo.split('##')
	total_regress_target.append(float(target_dw_score))
	if 'repub' in target_party:
		total_class_target.append(1)
	else:
		total_class_target.append(0)

	train_text = []
	train_label_regress = []
	train_label_class = []
	for temp_key, temp_text in articleDict.iteritems():
		if temp_key == eachTestPeopleInfo:
			target_text = temp_text
		else:
			temp_congressManName, temp_state, temp_dw_score, temp_party = temp_key.split('##')
			train_text.append(temp_text)
			train_label_regress.append(float(temp_dw_score))
			if 'repub' in temp_party.lower():
				train_label_class.append(1)
			else:
				train_label_class.append(0)
	train_text.append(target_text)
	vectorizer = TfidfVectorizer(ngram_range=(2,2),min_df=5, max_df = 1000,decode_error='ignore')
	# vectorizer = HashingVectorizer(ngram_range=(2,2), n_features = 20000,decode_error='ignore')
	allvector = vectorizer.fit_transform(train_text).toarray()
	trainVector = allvector[0 : len(train_label_class)]
	testVector = allvector[-1]
	clf = LogisticRegression(class_weight='auto')
	clf.fit(trainVector,train_label_class)
	temp_result_class = clf.predict_proba(testVector)
	total_class_result.append(temp_result_class[0][0])


	clf = SVR(C=1.0, epsilon=0.2)
	clf.fit(trainVector, train_label_regress) 
	temp_result_regressions = clf.predict(testVector)
	total_regress_result.append(temp_result_regressions[0])

cPickle.dump([total_regress_result,total_regress_target,total_class_result,total_class_target],open('CongressRecord_bootstrap','wb'))










