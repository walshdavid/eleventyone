# -*- coding: utf-8 -*-
"""
Created on Thu Jul 13 09:08:43 2017

@author: jkenny10
"""
import random
import os, fnmatch, codecs
class FileImporter:
    
    def __init__(self):
        self.fStr = ""
    # This functions loads the health tips text files
    def loadFile(self):
        
        text_files_path = "./healthtips/"
        text_files = fnmatch.filter(os.listdir(text_files_path), '*.txt')
        
        files = {value: text_files_path + text_file for (value, text_file) in zip(range(0,len(text_files)),text_files)}

        r = random.randint(0,len(text_files)-1)
        filename = files[r]
        s = ""
        file = codecs.open(filename, "r", encoding='windows-1252')
        
        s = file.read()
        self.fStr =s 
            
        return s
    # Getter function to return the String
    def getStr(self):
        return self.fStr
    