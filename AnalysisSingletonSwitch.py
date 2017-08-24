# -*- coding: utf-8 -*-
"""
Created on Mon Aug 14 13:43:40 2017

@author: datkin10
"""

from loggerhelpers import LoggerHelper

class AnalysisSingletonSwitch:
    
    __instance = []
    __completedUsers = []
    
    @staticmethod
    def getInstance(userID):
        for instance in AnalysisSingletonSwitch.__instance:
            if instance.userID == userID:
                return instance
        
        instance = AnalysisSingletonSwitch(userID)
        return instance
    
    @staticmethod
    def removeInstance(userID):
        for instance in AnalysisSingletonSwitch.__instance:
            if instance.userID == userID:
                if userID not in AnalysisSingletonSwitch.__completedUsers:
                    AnalysisSingletonSwitch.__completedUsers.append(userID)
                    
                AnalysisSingletonSwitch.__instance.remove(instance)
                
                
    
    def __init__(self,userID):
        self.audioFinished = False
        self.facialFinished = False
        self.userID = userID
        self.isUser = False
        self.userChecked = False
        AnalysisSingletonSwitch.__instance.append(self)
        lh = LoggerHelper().getInstance()
        self.logger = lh.createLoggerWorker("Analysis Singleton","DEBUG",2)
        self.logger.info("Analysis Manager Created for user: {}".format(self.userID))
        self.logger.debug("{}".format(AnalysisSingletonSwitch.__instance))
        