# -*- coding: utf-8 -*-
"""
Created on Thu Jul 27 10:44:28 2017

@author: datkin10
"""

from loggerhelpers import LoggerHelper
import datetime
import json
import pandas
import smtplib
import re
# This class is a singleton instance
class NotificationManager: 
    
    __instance = []
    
    @staticmethod
    def getInstance(userID):
        for instance in NotificationManager.__instance:
            if instance.userID == userID:
                return instance
        
        instance = NotificationManager(userID)
        return instance
    
    @staticmethod
    def removeInstance(userID):
        for instance in NotificationManager.__instance:
            if instance.userID == userID:
                NotificationManager.__instance.remove(instance)
    
    def __init__(self, userID):
        self.userID = userID
        self.notificationList = []
        self.typeList =[]
        self.fromList = []
        self.indexList = []
        self.index = 0
        self.EMAIL_HOST = "mailo2.uhc.com"
        self.EMAIL_PORT = 25
        self.FROM = "parkinsontracker@optum.com"
        self.newStartGiven = False
        lh = LoggerHelper().getInstance()
        self.logger = lh.createLoggerWorker("Notification Manager","DEBUG",2)
        self.logger.info("Instantiated for user: {}".format(self.userID))
        
        # Appends the users online singleton list
        NotificationManager.__instance.append(self)
        
        
    # This function sets a notification for a user
    def addNotification(self, notification,nType,nFrom):
        
        if nType == 'deterioration':
            for t in self.typeList:
                if t == 'deterioration':
                    return
        time =  datetime.datetime.now()
        timeStamp = time.strftime("%H:%M:%S - ")
        self.indexList.append(self.index)
        self.index+=1
        self.notificationList.append(timeStamp + notification)
        self.typeList.append(nType)
        self.fromList.append(nFrom)
        
        self.logger.debug("Added Notifcicatio: {}\n {}\n {}\n".format(notification,nType,nFrom))
               
            
    # not tested yet
    # This function sends an email to a Doctor.
    def sendDoctorNotification(self,message,doctorEmail):
        try:
            server = smtplib.SMTP(self.EMAIL_HOST,self.EMAIL_PORT)
            server.sendmail(self.FROM,doctorEmail,message)
            server.quit()
        except Exception as e:
            return False
        
    # This function gets a notification by creating a JSON and returning that JSON back.
    def getUserNotifications(self):
        
        if len(self.notificationList) == 0:
            return json.dumps("No notifications to display")
        else:
            message = pandas.Series(data = self.notificationList,index=self.indexList,name="message")
            ntype = pandas.Series(data = self.typeList,index=self.indexList,name="type")
            nfrom = pandas.Series(data = self.fromList,index=self.indexList,name="from")
                
            frame = pandas.concat([message,ntype,nfrom], axis=1)
        
        
        if re.search("welcome to PAPA",self.notificationList[0]):
            self.notificationList.remove(self.notificationList[0])
            self.typeList.remove(self.typeList[0])
            self.fromList.remove(self.fromList[0])
            
        frame.to_json('static/json/notifications.json')
        file = open('static/json/notifications.json','r')
        jsonstring = file.read()
        return jsonstring
    