# -*- coding: utf-8 -*-
"""
Created on Mon Jun 19 13:40:51 2017

@author: datkin10
"""
import random,re
import os, fnmatch, codecs
from dbhelper import DatabaseHelper

class STTFileImporter:
    
    def __init__(self):
        self.fStr = ""
    # This function laods the Daily Articles and the Text Files for the recordings
    def loadFile(self):
        

        text_files_path = "./files/Backup-Text/"
        text_files = fnmatch.filter(os.listdir(text_files_path), '*.txt')
        
        files = {value: text_files_path + text_file for (value, text_file) in zip(range(0,len(text_files)),text_files)}

        r = random.randint(0,len(text_files)-1)
        filename = files[r]
        s = ""
        file = codecs.open(filename, "r", encoding='windows-1252')
        
        s = file.read()
        self.fStr =s 
            
        return self.fStr
    
    # Getter function to return the string.
    def getStr(self):
        return self.fStr
    
    def getOrdering(self, userID):
        
        listFilled = []
        dbh = DatabaseHelper.getInstance()
        prefs = dbh.return_text_pref(userID)
        
        for i in prefs:
            if i != "NULL" and i != '':
                listFilled.append(i)
                
        for i in os.listdir('files/daily-articles/'):
            if i not in listFilled and i != 'ArticleSites.txt' and i != ".DS_Store":
                listFilled.append(i)
        
        
        return listFilled
        
    def trimText(self,s):
        
        self.fStr = ''
        count = 0
        for word in s.split():
            count+= 1
            self.fStr += word + ' '
            if count > 260 and re.search('.', word):
                break
        
        return self.fStr
    
