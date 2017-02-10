import os
import re
from nltk.tokenize import sent_tokenize
import cPickle
from nltk.tokenize import word_tokenize
import sys
from nltk.corpus import stopwords
from util import *

def getTime(eachline):
    times =  eachline.split('/')
    year = int(times[0])
    month = int(times[1])
    day = int(times[2])
    return year,month,day

def cleanLine(eachline):
    eachline = re.sub(r'<a href="(.*?)</a>','',eachline)
    eachline = re.sub(r'<a href="(.*?)>','',eachline)
    eachline = re.sub(r'\<(.*?)\>',' ',eachline)
    eachline = re.sub(r'\[\[(.*?)\]\]',' ',eachline)
    eachline = re.sub(r'\[(.*?)\]',' ',eachline)
    eachline = re.sub(r'\((.*?)\)',' ',eachline)
    return eachline

def detectStart(originalSentence):
    eachline = re.sub(r',',' ',originalSentence)
    eachline = re.sub(r'\.',' ',eachline)
    wordFirstSentence = eachline.split()
    congressManCondition = False
    SpeakerCondition = False
    congressManName = ""
    if len(wordFirstSentence)>=6:
        if '.' in ' '.join(originalSentence.split()[1:4]):
            if  wordFirstSentence[0] in m_stuff and wordFirstSentence[1].isupper() and ( wordFirstSentence[1].lower() in Dem or wordFirstSentence[1].lower() in Rep):
                congressManCondition = True
                congressManName = wordFirstSentence[1].lower()
            if wordFirstSentence[0].isupper() and ( wordFirstSentence[0].lower() in Dem or wordFirstSentence[0].lower() in Rep):
                congressManCondition = True
                congressManName = wordFirstSentence[0].lower()
            if congressManCondition == False:
                if wordFirstSentence[0] in m_stuff and getridpossibleLower(wordFirstSentence[1]).isupper() and ( wordFirstSentence[1].lower() in Dem or wordFirstSentence[1].lower() in Rep):
                    congressManCondition = True
        
        if wordFirstSentence[0] == 'The' and ((wordFirstSentence[1].isupper() and wordFirstSentence[1].lower() in officer) or wordFirstSentence[1]=='Clerk' or (wordFirstSentence[2].isupper() and wordFirstSentence[2].lower() in officer)):
            SpeakerCondition = True 
        return congressManCondition,SpeakerCondition,congressManName
    else:
        return False,False,congressManName



def getSpeechOneArticle(oneArticleDir, firstLayerIndex, repeatNameList):
    filepage = open(oneArticleDir,"r")
    FirstLine = True
    speechInThisPage = []
    newSpeech = ""
    currentParty = ''
    speachStatus = False
    congressManCondition = False
    SpeakerCondition = False
    currentCongressManName = ''
    for eachline in filepage:
        if FirstLine == True:
            year,month,day = getTime(eachline)
            FirstLine = False
        eachline = cleanLine(eachline)
        congressManCondition, SpeakerCondition,currentCongressManName = detectStart(eachline)
        stopCondition = detectStop(eachline)
        if speachStatus:
            if congressManCondition:
                if len(newSpeech) != 0:
                    tempSpeech = singleSpeech(newSpeech)
                    tempSpeech.setParty(currentParty)
                    tempSpeech.setCongressman(currentCongressManName)
                    tempSpeech.setTime(year,month,day)
                    tempSpeech.cleanArticle()
                    speechInThisPage.append(tempSpeech)
                currentParty = getParty(eachline)
                newSpeech = FirstLineSpeech(eachline)
            elif SpeakerCondition or stopCondition:
                if len(newSpeech) != 0:
                    tempSpeech = singleSpeech(newSpeech)
                    tempSpeech.setParty(currentParty)
                    tempSpeech.setCongressman(currentCongressManName)
                    tempSpeech.setTime(year,month,day)
                    tempSpeech.cleanArticle()
                    speechInThisPage.append(tempSpeech)
                currentParty = ''
                currentCongressManName = ''
                newSpeech = ''
                speachStatus = False
            elif (eachline !='\n') and (('   ' != eachline[0:3] and '  ' == eachline[0:2]) or (' ' != eachline[0])):
                newSpeech += eachline
        else:
            if congressManCondition:
                speachStatus = True
                currentParty = getParty(eachline)
                newSpeech = FirstLineSpeech(eachline)
    
    if len(newSpeech) !=0 :
        tempSpeech = singleSpeech(newSpeech)
        tempSpeech.setParty(currentParty)
        tempSpeech.setCongressman(currentCongressManName)
        tempSpeech.setTime(year,month,day)
        tempSpeech.cleanArticle()
        speechInThisPage.append(tempSpeech)
        
    return speechInThisPage


if __name__ == "__main__":
    year = sys.argv[1] 
    totalCongressPeopleDict = cPickle.load(open('./data/congressPeopleDict','rb'))
    congressPeopleDict = totalCongressPeopleDict[year]
    # the key is lastName+'#'+State+'#'+CongressType
    firstLayerIndex = {}
    repeatNameList = []
    for key, congressInfo in congressPeopleDict.iteritems():
    	[lastName, state, congressType] = key.split('#')
    	lastName = lastName.lower()
    	if firstLayerIndex.has_key(lastName):
    		firstLayerIndex[lastName] = [key+'#'+congressInfo.party+'#'+str(congressInfo.dw_score)+'#']
    	else:
    		firstLayerIndex[lastName].append(key+'#'+congressInfo.party+'#'+str(congressInfo.dw_score)+'#')
    		repeatNameList.append(lastName)
    speech_listFile = open("./speechArticleList/speech_"+year+".txt","r")
    speechInOneYear = []
    for eachline in speech_listFile:
        try:
            speechInOneYear += getSpeechOneArticle(eachline.strip(), firstLayerIndex, repeatNameList)
        except:
            print "fail at: "+eachline
    cPickle.dump(speechInOneYear,open('./speechDump/speech_'+year+'_dump','wb'))
