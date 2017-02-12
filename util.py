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
        if i > 0:
            textafterDeleteEnd = ' '.join(OriginalSentences[0:i])
        else:
            textafterDeleteEnd = ' '.join(OriginalSentences)

        sentencesCutEndsent_tokenize = sent_tokenize(textafterDeleteEnd)
        if len(sentencesCutEndsent_tokenize) > 1:
            original = ' '.join(sentencesCutEndsent_tokenize[1:len(sentencesCutEndsent_tokenize)])
        else:
            original = textafterDeleteEnd

        # original process
        original = ' '.join(self.text.split())
        remainText = ""
        for i in range(len(original)):
            eachword = original[i]
            try:
                eachword.encode('ascii', 'ignore')
                remainText += original[i]
            except:
                continue

        remainText = re.sub(r'``','"',remainText)
        remainText = re.sub(r'\'\'','"',remainText)
        remainText = re.sub(r'\?','.',remainText)
        remainText = re.sub(r'!','.',remainText)
        
        allwords = remainText.split()
        leftwords = []
        for eachword in allwords:
            tempword = eachword.lower()
            if tempword.isalpha() or (tempword[0:len(tempword)-1].isalpha() and tempword[len(tempword)-1] in leftPunctuation):
                if not (tempword in en_stop or (tempword[0:len(tempword)-1] in en_stop and (tempword[len(tempword)-1].isalpha() or tempword[len(tempword)-1] in leftPunctuation))):
                    leftwords.append(tempword)
            else:
                leftwords.append(' ')
        self.cleanText = ' '.join(leftwords)
        self.cleanText = ' '.join(self.cleanText.split())


