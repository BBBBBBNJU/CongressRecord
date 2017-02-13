# -*- coding: utf-8 -*- 
import os
import re
from nltk.tokenize import sent_tokenize
import cPickle
from nltk.tokenize import word_tokenize
import sys
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer
space = ' '
stop = stopwords.words('english')
reader = open('stopwords.txt','r')
for eachline in reader:
    stop.append(eachline.strip())
en_stop = list(set(stop))
p_stemmer = PorterStemmer()
htmlentities = ["&quot;","&nbsp;","&amp;","&lt;","&gt;","&OElig;","&oelig;","&Scaron;","&scaron;","&Yuml;","&circ;","&tilde;","&ensp;","&emsp;","&thinsp;","&zwnj;","&zwj;","&lrm;","&rlm;","&ndash;","&mdash;","&lsquo;","&rsquo;","&sbquo;","&ldquo;","&rdquo;","&bdquo;","&dagger;","&Dagger;","&permil;","&lsaquo;"]
validElement = [',','.','"','\'']
leftPunctuation = ['.']


def sentencePreProcess(raw):
    raw = raw.encode('ascii','ignore')
    tokens = word_tokenize(raw.lower())
    stopped_tokens = [j for j in tokens if not j in en_stop]
    stemmed_tokens = [p_stemmer.stem(j) for j in stopped_tokens]
    return space.join(stemmed_tokens)

def preProcess(plainText):
    plainText = re.sub(u'``','"',plainText)
    plainText = re.sub(u'#',' ',plainText)
    plainText = re.sub(u'\'\'',' " ',plainText)
    plainText = re.sub(r'\?','.',plainText)
    plainText = re.sub(r'!','.',plainText)
    allsentences = sent_tokenize(plainText)
    afterProcess = ""
    for i in range(len(allsentences)):
        if i != 0:
            tempSentence = sentencePreProcess(allsentences[i])
            afterProcess += tempSentence + ' '
    return afterProcess


class congressMan():
    def __init__(self, name):
        self.name = name
    
    def setLastName(self, lastname):
        self.lastname = lastname

    def setCongressType(self, congress_type):
        self.congress_type = congress_type

    def setParty(self,party):
        self.party = party

    def setState(self,state):
        self.state = state

    def setStateBrief(self,state_brief):
        self.state_brief = state_brief

    def setDWNScore(self, dw_score):
        self.dw_score = dw_score

    def printCongressPeople(self):
        print self.name
        print self.lastname
        print self.congress_type
        print self.party
        print self.state
        print self.state_brief
        print self.dw_score
        print '======'

class singleSpeech():
    def __init__(self, text):
        self.text = text

    def setParty(self,party):
        self.party = party

    def setCongressman(self,congressManName):
        self.congressManName = congressManName

    def setCongressType(self, congressType):
        self.congressType = congressType

    def setState(self,state):
        self.state = state

    def setDWNScore(self, dw_score):
        self.dw_score = dw_score

    def setTime(self,year,month,day):
        self.year = year
        self.month = month
        self.day = day

    def printSingleSpeech(self):
        print self.congressManName
        print self.party
        print self.congressType
        print self.state
        print self.dw_score
        print str(self.year)+'/'+str(self.month)+'/'+str(self.day)
        print self.text
        print '========='

    def cleanArticle(self):
        # delete the first sentence and last paragraph
        OriginalSentences = self.text.split('\n')
        finalCut = 0
        for i in range(len(OriginalSentences)):
            if '  ' == OriginalSentences[i][0:2]:
                finalCut = i
        if finalCut > 0 and i - finalCut <= 2:
            textafterDeleteEnd = ' '.join(OriginalSentences[0:finalCut])
        else:
            textafterDeleteEnd = ' '.join(OriginalSentences)

        sentencesCutEndsent_tokenize = sent_tokenize(textafterDeleteEnd)
        if len(sentencesCutEndsent_tokenize) > 2:
            self.original_cut = ' '.join(sentencesCutEndsent_tokenize[2:len(sentencesCutEndsent_tokenize)])
        else:
            self.original_cut = textafterDeleteEnd

        # original process
        remainText = ""
        for i in range(len(self.original_cut)):
            eachword = self.original_cut[i]
            try:
                eachword.encode('ascii', 'ignore')
                remainText += self.original_cut[i]
            except:
                continue
        
        self.cleanText = preProcess(remainText)



