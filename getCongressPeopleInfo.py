# -*- coding: utf-8 -*- 
import cPickle
import urllib2
import urllib  
import re  
from nltk.tokenize import word_tokenize
from nltk.tokenize import sent_tokenize
import thread  
import requests
import time
import codecs
import os
import sys
from util import *

def getunicodePage(Url):
	headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
	page = requests.get(Url,headers=headers)
	html_contents = page.text
	unicodePage = ""
	for eachElement in html_contents:
		try:
			eachElement.decode("ascii",'ignore')
			unicodePage += eachElement
		except:
			continue
	return unicodePage

def checkUrl(tempUrl):
	response = urllib2.urlopen(tempUrl)
	redirected = response.geturl() == tempUrl
	return redirected,response.geturl()

def getName(unicodePage):
	target='https://www.congress.gov/(.*?)">(.*?)</a>'
	myItems = re.findall(target,unicodePage,re.DOTALL)
	job_name = myItems[0][1].split()
	name = ' '.join(job_name[1:len(job_name)])
	return name

def getParty(unicodePage):
	target='Party:(.*?)<span>(.*?)</span>'
	myItems = re.findall(target,unicodePage,re.DOTALL)
	party = myItems[0][1]
	return party

def getCongressType(unicodePage):
	target='<li>(.*?)</li>'
	myItems = re.findall(target,unicodePage,re.DOTALL)
	congressType = myItems[0].split(':')[0]
	return congressType

def getState(unicodePage):
	target='State:(.*?)<span>(.*?)</span>'
	myItems = re.findall(target,unicodePage,re.DOTALL)
	party = myItems[0][1]
	return party	

def getDWScore(congressPeopleLastName, congressPeopleState, congressPeoplePartyType, DWScoreDict):
	# for DW dict, the key is name+'#'+state+'#'+partyType
	for key, probValue in DWScoreDict.iteritems():
		[tempLastName, tempState, tempPartyType] = key.split('#')
		if tempLastName.lower() in congressPeopleLastName.lower() or tempLastName[0:len(tempLastName)-1] in congressPeopleLastName.lower():
			if tempState.lower() in congressPeopleState.lower():
				if tempPartyType.lower() == congressPeoplePartyType.lower():
					return probValue
	return 'null'


def getCongressPeopleData(baseUrl, pageIndex, stateNameDict, DWScoreDict):
	congressPeopleDict = {}
	temp_url = baseUrl + pageIndex
	unicodePage=getunicodePage(temp_url)
	target='<span class="result-heading"><a href="(.*?)</ul>'
	myItems = re.findall(target,unicodePage,re.DOTALL)
	myItems = list(set(myItems))
	for eachitem in myItems:
		tempName = getName(eachitem)
		tempLastName = tempName.split(',')[0]
		tempParty = getParty(eachitem)
		tempState = getState(eachitem)
		tempState = tempState.lower()
		tempStateBrief = stateNameDict[tempState]
		tempCongressType = getCongressType(eachitem)
		tempDWScore = getDWScore(tempLastName, tempState, tempParty, DWScoreDict)
		tempKey = tempLastName+'#'+tempState+'#'+tempCongressType
		
		tempPeople = congressMan(tempName)
		tempPeople.setLastName(tempLastName)
		tempPeople.setCongressType(tempCongressType)
		tempPeople.setParty(tempParty)
		tempPeople.setState(tempState)
		tempPeople.setStateBrief(tempStateBrief)
		tempPeople.setDWNScore(tempDWScore)

		congressPeopleDict[tempKey] = tempPeople			
	return congressPeopleDict


def DW_file_parseSentence(eachline):
    time = eachline[0:4].strip()
    state = eachline[22:33].strip()
    party_number = eachline[33:37].strip()
    if party_number == '200':
    	party = 'Republican'
    else:
    	party = 'Democratic'
    name = eachline[45:59].strip().split()[0]
    prob_1 = float(eachline[59:65].strip())
    prob_2 = float(eachline[68:74].strip())
    return [time,state,party,name,prob_1,prob_2]

def parseDWOrginalFile(classNumber):
	totalProb = []
	ProbDict = {}
	reader = open('./data/DW_scores.txt')
	for eachline in reader:
		[time,state,party,name,prob_1,prob_2] = DW_file_parseSentence(eachline)
		if time == classNumber:
			name = name.lower()
			storeKey = name+'#'+state+'#'+party
			ProbDict[storeKey] = prob_1
	return ProbDict

year_number_page_dict = {
	'2006':['109',6],
	'2007':['110',6],
	'2008':['110',6],
	'2009':['111',6],
	'2010':['111',6],
	'2011':['112',6],
	'2012':['112',6],
	'2013':['113',6],
	'2014':['113',6],
	'2015':['114',6],
	'2016':['114',6]
}

reader = open('./data/abbreviations.txt','r')
stateNameDict = {}
for eachline in reader:
	[fullname,abbrName] = eachline.strip().split(',')
	stateNameDict[fullname.lower()] = abbrName.lower()
cPickle.dump(stateNameDict,open('stateNameDict','wb'))

congressPeopleDict = {}
for year, pageInfo in year_number_page_dict.iteritems():
	[classNumber, totalPageNumber] = pageInfo
	DWScoreDict = parseDWOrginalFile(classNumber)
	baseUrl = 'https://www.congress.gov/members?q={"congress":"'+classNumber+'"}&page='
	congressPeopleDict_oneYear = {}
	for i in range(totalPageNumber):
		congressPeopleDict_oneYear.update(getCongressPeopleData(baseUrl, str(i+1), stateNameDict, DWScoreDict))
	congressPeopleDict[year] = congressPeopleDict_oneYear
	print year + ' stat: '
	print 'total number: '+ str(len(congressPeopleDict_oneYear))
	count = 0
	for key, people in congressPeopleDict_oneYear.iteritems():
		if people.dw_score == 'null':
			count += 1
	print 'loss number: '+ str(count)
	print '=============='
	os.system("echo \"finishe year: " + year + "\" | mail -s \"update\" haoyan.wustl@gmail.com")

cPickle.dump(congressPeopleDict,open('congressPeopleDict','wb'))


	
