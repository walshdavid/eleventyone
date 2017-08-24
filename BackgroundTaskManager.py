# -*- coding: utf-8 -*-
"""
Created on Mon Aug 14 14:07:01 2017

@author: datkin10
"""

from ArticleExtractor import ArticleExtractor
import time
import threading

class BackgroundTaskManager:
    
    def __init__(self):
        self.thread = threading.Thread(target=(self.timedTasks))
    
    def timedTasks(self):
        ae = ArticleExtractor()
        while True:
            ae.updateArticles()
            
            time.sleep(86400)
            
    def begin(self):
        self.thread.start()

        