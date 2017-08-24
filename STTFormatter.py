# -*- coding: utf-8 -*-
"""
Created on Wed Jun 14 16:38:03 2017

@author: datkin10
"""

import re
from num2words import num2words
import inflect

class STTFormatter:
    
    def __init__(self):
        self.wordBase = ""
      
#==============================================================================
#   This is a catch all function for a number of cases such as numbers in 
#   brackets, times and road names
#==============================================================================
    def formatSpecialNumberCases(self, word):
        p = re.compile('([0-9][0-9]|[0-9])(:|\.)([0-9][0-9])(pm|am)', re.IGNORECASE )#Time format
        p1 = re.compile('([0-9]+)')#age in brackets
        p2 = re.compile('[A-Z][0-9]+')#Road names
        p3 = re.compile('[0-9][0-9][0-9][0-9]s')
        if re.search(p, word):
            word = ""
        elif re.match(p1, word):
            word = word.replace('(', "")
            word = word.replace(')', "")
        elif re.match(p2, word):
            word = ""
        elif re.search(p3, word):
            word = ""
            
        word = word.replace("-", " ")
            
        return word
#==============================================================================
#     This function replaces currency symbols at the front of a number to the
#     spoken form. eg $10 to 10 dollars
#==============================================================================
    def testFrontChar(self,word):#Currently just currency signs at the front of the word
        if word[0] == '$':
            word = word.replace('$',"")
            word += ' ' + "dollars"
            return word
        elif word[0] == '£':
            word = word.replace('£',"")
            word += ' ' + "pounds"
        elif word[0] == '€':
            word = word.replace('€',"")
            word += ' ' + "euro"
            
        return word
      
#==============================================================================
#     This function deals with suffix abbreviations such as m for million, as 
#     well as signs such as the % sign, converting 90% to 90 percent etc
#==============================================================================
    def testEndChar(self,word):#Deal with % sign and also m for million b for billion etc
        p = re.compile('[0-9]+[mbkMBK]')
        pM = re.compile('m', re.IGNORECASE)
        pB = re.compile('b', re.IGNORECASE)
        pK = re.compile('k', re.IGNORECASE)
        
        if word[-1] == "\%":
            word.replace('\%', ' ')
            word += "percent"
        elif re.match(p, word):
            word = pM.sub(' million', word)
            word = pB.sub(' billion', word)
            word = pK.sub(' thousand', word)
    
        return word
#==============================================================================
#     This function formats decimal numbers into 8 point 9 etc
#==============================================================================
    def testMidChar(self,word):#Deal with 8.9etc
        p = re.compile(r'[0-9]+\.[0-9]+')
        if re.search(p , word) is not None:
            word = word.replace('.'," point ", 1)
        
        return word
        
#==============================================================================
#     This function removes all punctuation in the list of words except for 
#     apostrophes and spaces
#==============================================================================
    def removePunctuation(self,wordList):#Remove all remaining punctuation except for special cases
        for i in range(1,len(wordList)):
            if wordList[i] is not None:
                for j in wordList[i]:
                    if not j.isalnum() and j != ' ' and j != '\'':
                        wordList[i] = wordList[i].replace(j,"")
        
        return wordList
    
#==============================================================================
#     This function takes in a string and if it is a number converts it to the 
#     english language text form of that number. If the word taken in is an 
#     ordinal number (1st,2nd etc), it converts it to the correct ordinal form
#==============================================================================
    
    def convertNumToText(self,word):
        p0 = re.compile('[0-9]+(th|nd|rd|st)', re.IGNORECASE)
        p01 = re.compile('(th|nd|rd|st)', re.IGNORECASE)
        p1 = re.compile('[0-9]+')

        if re.match(p0,word):
            inf = inflect.engine()
            word = p01.sub('', word)
            word = inf.number_to_words(inf.ordinal(int(word)))
            word = word.replace('-', ' ')
        elif re.match(p1,word):
            try:
                word = num2words(int(word))
                word = word.replace('-', ' ')
            except ValueError as e:
                word = ""
        
            
        return word
    
#==============================================================================
#     This function takes in a list of words, and removes any words it
#     that have accented vowels. As these words cannot be English words,
#     they will not be in the audio module dictionary.
#==============================================================================
    def removeNonEnglishWords(self, sent):
        p1 = re.compile("[íáéóú]")
        wordsToRemove = []
        if sent is not None:
            for word in sent:
                if re.search(p1, word):
                    wordsToRemove.append(word)
        
        L = [value for value in sent if value not in wordsToRemove]
        
        return L
#==============================================================================
#     This is a simple function that removes any proper nouns within the list of
#     that it takes in.
#==============================================================================
    def removeProperNouns(self, sent):
        
        p = re.compile("[A-Z][a-z]+")#Pattern for a proper noun
        p1 = re.compile("[A-Za-z0-9]+.")#Pattern for a word at the end of a sentence
        lastWord = ""
        wordsToRemove = []
        if sent is not None:
            for word in sent:
                if re.match(p, word):
                    if not re.match(p1, lastWord):
                        wordsToRemove.append(word)
            
            lastWord = word
        
        L = [value for value in sent if value not in wordsToRemove]
        
        return L
    
    
#==============================================================================
#     This function simply runs in the correct order all other functions within
#     this class.
#==============================================================================
    def performOperations(self,eStr):#Run the operations contained in this class
        eStr = self.removeProperNouns(eStr)
        eStr = self.removeNonEnglishWords(eStr)
        for i in range(0,len(eStr)):
            eStr[i] = self.formatSpecialNumberCases(eStr[i])
            if eStr[i] != "":
                eStr[i] = self.testFrontChar(eStr[i])
            if eStr[i] != "":
                eStr[i] = self.testMidChar(eStr[i])
            if eStr[i] != "":
                eStr[i] = self.testEndChar(eStr[i])
            if eStr[i] != "":
                eStr[i] = eStr[i].lower()
                tempList = eStr[i].split()
                if i != len(eStr)-1:
                    tempList += eStr[i+1:]
                eStr = eStr[:i] + tempList

        eStr = self.removePunctuation(eStr) 
        for word in eStr:
            index = eStr.index(word)
            word = self.convertNumToText(word)
            tempList = word.split()
            if index != len(eStr)-1:
                tempList += eStr[index+1:]
                
            eStr = eStr[:index] + tempList
       
        for word in eStr:
            if word == '':
                eStr.remove(word)
        
        return eStr
    
        
        