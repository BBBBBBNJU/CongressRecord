# -*- coding: utf-8 -*- 
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

