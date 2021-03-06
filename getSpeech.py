import os
import re
from nltk.tokenize import sent_tokenize
import cPickle
from nltk.tokenize import word_tokenize
import sys
from nltk.corpus import stopwords
from util import *

officer = ['speaker','clerk','chairman','president','officer']
m_stuff = ['Mr','Mrs','Ms','Senator','Madam','Senator']
m_stuff_delete = ['mr','mrs','ms','mr.','mrs.','ms.','senator','madam','madam.']

def getTime(eachline):
    times =  eachline.split('/')
    year = int(times[0])
    month = int(times[1])
    day = int(times[2])
    return year,month,day

def FirstLineSpeech(eachline):
    # try:
    #     return sent_tokenize(eachline)[1]
    # except:
    #     return eachline
    return eachline

def detectStop(eachline):
    eachline = re.sub(r',',' ',eachline)
    eachline = re.sub(r'\.',' ',eachline)
    eachline = re.sub(r'\"',' ',eachline)
    eachline = re.sub(r';',' ',eachline)
    eachline = re.sub(r':',' ',eachline)
    eachline = re.sub(r'\'',' ',eachline)
    count= 0.0
    for i in range(len(eachline)):
        if eachline[i].isalpha() and eachline[i].isupper():
            count += 1.0
    if count/len(eachline)>0.5:
        return True
    else:
        return False

def getridpossibleLower(lastnameInput):
    lastnameInput = re.sub(r'Des','DES',lastnameInput)
    lastnameInput = re.sub(r'Del','DEL',lastnameInput)
    lastnameInput = re.sub(r'De','DE',lastnameInput)
    lastnameInput = re.sub(r'Mc','MC',lastnameInput)
    lastnameInput = re.sub(r'Ba','BA',lastnameInput)
    lastnameInput = re.sub(r'La','LA',lastnameInput)
    lastnameInput = re.sub(r'Lo','LO',lastnameInput)
    lastnameInput = re.sub(r'Le','LE',lastnameInput)
    return lastnameInput


def cleanLine(eachline):
    eachline = re.sub(r'<a href="(.*?)</a>','',eachline)
    eachline = re.sub(r'<a href="(.*?)>','',eachline)
    eachline = re.sub(r'\<(.*?)\>',' ',eachline)
    eachline = re.sub(r'\[\[(.*?)\]\]',' ',eachline)
    eachline = re.sub(r'\[(.*?)\]',' ',eachline)
    eachline = re.sub(r'\((.*?)\)',' ',eachline)
    return eachline

def findLastName(initialIndex, wordFirstSentence, allNameList):
    congressManName = []
    i = initialIndex
    while i < len(wordFirstSentence) and wordFirstSentence[i].isupper():
        congressManName.append(wordFirstSentence[i].lower())
        i += 1
    temp_name = ' '.join(congressManName)

    if not temp_name in allNameList:
        temp_name = 'null'
    return temp_name
        

def detectStart(congressType, originalSentence, firstLayerIndex, allNameList, repeatNameList):
    eachline = re.sub(r',',' ',originalSentence)
    eachline = re.sub(r'\.',' ',eachline)
    eachline = re.sub(r'-',' ',eachline)
    wordFirstSentence = eachline.split()
    wordFirstSentence_lower = eachline.lower().split()
    congressManCondition = False
    SpeakerCondition = False
    congressManName = ""
    congressManInfo = ""
    if len(wordFirstSentence)>=6:
        if '.' in ' '.join(originalSentence.split()[1:6]):
            if  wordFirstSentence[0] in m_stuff and wordFirstSentence[1].isupper():
                congressManCondition = True
                congressManName = findLastName(1, wordFirstSentence, allNameList)
            if wordFirstSentence[0].isupper() and len(wordFirstSentence[0]) >= 2:
                congressManCondition = True
                congressManName = findLastName(0, wordFirstSentence, allNameList)

            if congressManCondition == False:
                if wordFirstSentence[0] in m_stuff and getridpossibleLower(wordFirstSentence[1]).isupper():
                    congressManCondition = True
                    wordFirstSentence[1] = getridpossibleLower(wordFirstSentence[1])
                    congressManName = findLastName(1, wordFirstSentence, allNameList)

            if congressManCondition and congressManName != 'null':
                if congressManName not in repeatNameList:
                    congressManInfo  = firstLayerIndex[congressManName][0]
                else:
                    # multiple congress people with same last name, need chekc congress type and state
                    for eachPossibleCongressManInfo in firstLayerIndex[congressManName]:
                        temp_lastName, temp_state, temp_congressType, temp_party, temp_dw_score = eachPossibleCongressManInfo.split('#')
                        if temp_state in wordFirstSentence_lower[0:6] and temp_congressType == congressType:
                            congressManInfo = eachPossibleCongressManInfo

        if wordFirstSentence[0] == 'The' and ((wordFirstSentence[1].isupper() and wordFirstSentence[1].lower() in officer) or wordFirstSentence[1]=='Clerk' or (wordFirstSentence[2].isupper() and wordFirstSentence[2].lower() in officer)):
            SpeakerCondition = True 
        return congressManCondition,SpeakerCondition,congressManName,congressManInfo
    else:
        return False,False,congressManName,congressManInfo



def getSpeechOneArticle(congressType, oneArticleDir, firstLayerIndex, allNameList, repeatNameList):
    filepage = open(oneArticleDir,"r")
    speechInThisPage = []
    FirstLine = True
    newSpeech = ""
    speachStatus = False
    congressManCondition = False
    SpeakerCondition = False
    currentCongressManName = ''
    currentCongressManInfo = ''
    previousCongressManName = ''
    previousCongressManInfo = ''
    for eachline in filepage:
        if FirstLine == True:
            year,month,day = getTime(eachline)
            FirstLine = False

        eachline = cleanLine(eachline)

        congressManCondition, SpeakerCondition, currentCongressManName, currentCongressManInfo = detectStart(congressType, eachline, firstLayerIndex, allNameList, repeatNameList)
        if len(currentCongressManInfo) > 0:
            temp_lastName, currentCongressManState, temp_congressType, currentCongressManParty, currentCongressManDwScore = currentCongressManInfo.split('#')
        else:
            currentCongressManState = 'null'
            currentCongressManParty = 'null'
            currentCongressManDwScore = 'null'
        stopCondition = detectStop(eachline)


        if speachStatus:
            if congressManCondition:
                if len(newSpeech) != 0:
                    tempSpeech = singleSpeech(newSpeech)
                    tempSpeech.setCongressman(previousCongressManName)
                    tempSpeech.setParty(previousCongressManParty)
                    tempSpeech.setTime(year,month,day)
                    tempSpeech.setCongressType(congressType)
                    tempSpeech.setState(previousCongressManState)
                    tempSpeech.setDWNScore(previousCongressManDwScore)
                    if tempSpeech.congressManName != 'null':
                        speechInThisPage.append(tempSpeech)

                newSpeech = FirstLineSpeech(eachline)
                previousCongressManName = currentCongressManName
                previousCongressManParty = currentCongressManParty
                previousCongressManState = currentCongressManState
                previousCongressManDwScore = currentCongressManDwScore

            elif SpeakerCondition or stopCondition:
                if len(newSpeech) != 0:
                    tempSpeech = singleSpeech(newSpeech)
                    tempSpeech.setCongressman(previousCongressManName)
                    tempSpeech.setParty(previousCongressManParty)
                    tempSpeech.setTime(year,month,day)
                    tempSpeech.setCongressType(congressType)
                    tempSpeech.setState(previousCongressManState)
                    tempSpeech.setDWNScore(previousCongressManDwScore)
                    if tempSpeech.congressManName != 'null':
                        speechInThisPage.append(tempSpeech)
                currentCongressManInfo = ''
                currentCongressManName = ''
                newSpeech = ''
                speachStatus = False
            elif (eachline !='\n') and (('   ' != eachline[0:3] and '  ' == eachline[0:2]) or (' ' != eachline[0])):
                newSpeech += eachline
        else:
            if congressManCondition:
                speachStatus = True
                newSpeech = FirstLineSpeech(eachline)
                previousCongressManName = currentCongressManName
                previousCongressManParty = currentCongressManParty
                previousCongressManState = currentCongressManState
                previousCongressManDwScore = currentCongressManDwScore

    
    if len(newSpeech) !=0 :
        tempSpeech = singleSpeech(newSpeech)
        tempSpeech.setCongressman(previousCongressManName)
        tempSpeech.setParty(previousCongressManParty)
        tempSpeech.setTime(year,month,day)
        tempSpeech.setCongressType(congressType)
        tempSpeech.setState(previousCongressManState)
        tempSpeech.setDWNScore(previousCongressManDwScore)
        tempSpeech.cleanArticle()
        if tempSpeech.congressManName != 'null':
            speechInThisPage.append(tempSpeech)
    


    return speechInThisPage


if __name__ == "__main__":
    year = sys.argv[1] 
    totalCongressPeopleDict = cPickle.load(open('./data/congressPeopleDict','rb'))
    congressPeopleDict = totalCongressPeopleDict[year]
    # the key is lastName+'#'+State+'#'+CongressType
    # basically, we will compare the strings in lower() mode
    firstLayerIndex = {}
    repeatNameList = []
    allNameList = []
    for key, congressInfo in congressPeopleDict.iteritems():
        [lastName, state, congressType] = key.lower().split('#')
        if not firstLayerIndex.has_key(lastName):
            firstLayerIndex[lastName] = [key.lower()+'#'+congressInfo.party.lower()+'#'+str(congressInfo.dw_score)]
        else:
            firstLayerIndex[lastName].append(key.lower()+'#'+congressInfo.party.lower()+'#'+str(congressInfo.dw_score))
            repeatNameList.append(lastName)
        allNameList.append(lastName)
    allNameList = list(set(allNameList))

    speech_listFile = open("./speechArticleList/speech_"+year+".txt","r")
    speechInOneYear = []
    # count = 0
    for eachline in speech_listFile:
        try:
            if 'H' in eachline:
                speechInOneArticle = getSpeechOneArticle('house',eachline.strip(), firstLayerIndex, allNameList, repeatNameList)
            else:
                speechInOneArticle = getSpeechOneArticle('senate',eachline.strip(), firstLayerIndex, allNameList, repeatNameList)
            speechInOneYear += speechInOneArticle
        except:
            print "fail at: "+eachline
            
            
            # if len(speechInOneArticle) > 2:
            #     count += 1
            #     print eachline
            #     for eachSpeech in speechInOneArticle:
            #         eachSpeech.printSingleSpeech()
            # if count > 5:
            #     break
    cPickle.dump(speechInOneYear,open('./speechDump/speech_'+year+'_dump','wb'))
    os.system("echo \"finish year: " + year + "\" | mail -s \"update\" haoyan.wustl@gmail.com")
