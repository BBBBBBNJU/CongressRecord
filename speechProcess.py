#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import subprocess
from nltk.tokenize import sent_tokenize
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem.porter import PorterStemmer
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
import re 
import cPickle
import numpy as np
from util import *


if __name__ == "__main__":
    year = sys.argv[1] 
    writer = open('./speechText/speechText_' + year + '.txt','w')
    speechInOneYear = cPickle.load(open('./speechDump/speech_' + year + '_dump','rb'))
    count  = 0
    for eachSingleSpeech in speechInOneYear:
        if len(eachSingleSpeech.text.split()) > 50:
            eachSingleSpeech.cleanArticle()
            articleInfo = [
            eachSingleSpeech.congressManName,
            eachSingleSpeech.congressType,
            eachSingleSpeech.party,
            eachSingleSpeech.state,
            eachSingleSpeech.dw_score,
            str(eachSingleSpeech.year),
            str(eachSingleSpeech.month),
            str(eachSingleSpeech.day),
            eachSingleSpeech.cleanText
            ]
            writer.write('##'.join(articleInfo) + '\n')
    os.system("echo \"finish year: " + year + "\" | mail -s \"update\" haoyan.wustl@gmail.com")
    writer.close()

