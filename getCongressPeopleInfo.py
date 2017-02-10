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

def getDWScore(tempLastName, tempState, DWScoreDict):



def getCongressPeopleData(baseUrl, pageIndex, stateNameDict, DWScoreDict):
		congressPeopleDict = {}
	# try:
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
			tempDWScore = getDWScore(tempLastName, tempState, DWScoreDict)


			congressPeopleDict[tempName] = [tempParty, tempServeTime]
		return congressPeopleDict
	# except:
	# 	return congressPeopleDict

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

reader = open('./abbreviations.txt','r')
stateNameDict = {}
for eachline in reader:
	[fullname,abbrName] = eachline.strip().split(',')
	stateNameDict[fullname.lower()] = abbrName.lower()

congressPeopleDict = {}
for year, pageInfo in year_number_page_dict.iteritems():
	[classNumber, totalPageNumber] = pageInfo
	baseUrl = 'https://www.congress.gov/members?q={"congress":"'+classNumber+'"}&page='
	congressPeopleDict_oneYear = {}
	for i in range(totalPageNumber):
		congressPeopleDict_oneYear.update(getCongressPeopleData(baseUrl, str(i+1),stateNameDict))
	congressPeopleDict[year] = congressPeopleDict_oneYear
cPickle.dump(congressPeopleDict,open('congressPeopleDict','wb'))
	
