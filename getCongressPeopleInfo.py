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

class congressMan():
    def __init__(self, name):
        self.name = name
        self.lastname = name.split()[len(name.split())-1]

    def setType(self, type):
        self.type = type

    def setParty(self,party):
        self.party = party

    def setState(self,state):
        self.state = state

    def setStateBrief(self,state_brief):
        self.state_brief = state_brief

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

def getServeTime(unicodePage):
	target='<li>(.*?)</li>'
	myItems = re.findall(target,unicodePage,re.DOTALL)
	serveTime = myItems[0]
	return serveTime

def getCongressPeopleData(baseUrl, pageIndex):
		congressPeopleDict = {}
	# try:
		temp_url = baseUrl + pageIndex
		unicodePage=getunicodePage(temp_url)
		target='<span class="result-heading"><a href="(.*?)</ul>'
		myItems = re.findall(target,unicodePage,re.DOTALL)
		myItems = list(set(myItems))
		for eachitem in myItems:
			tempName = getName(eachitem)
			tempParty = getParty(eachitem)
			tempServeTime = getServeTime(eachitem)
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
for year, pageInfo in year_number_page_dict.iteritems():
	[classNumber, totalPageNumber] = pageInfo
	baseUrl = 'https://www.congress.gov/members?q={"congress":"'+classNumber+'"}&page='
	congressPeopleDict = {}
	for i in range(totalPageNumber):
		congressPeopleDict.update(getCongressPeopleData(baseUrl, str(i+1)))
	cPickle.dump(congressPeopleDict,open('congressPeopleDict_'+congressNumber,'wb'))
	print len(congressPeopleDict)
	print congressPeopleDict['Thune, John']
