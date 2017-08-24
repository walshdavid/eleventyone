# -*- coding: utf-8 -*-
"""
Created on Wed Jul 26 14:29:35 2017

@author: datkin10, jsalomo1
"""

from AccuracyChecker import AccuracyChecker
from AudioFeatureAnalyzer import AudioFeatureAnalyzer
from dbhelper import DatabaseHelper
from faceAnalyze import FacialAnalyzer
import datetime
import threading
from AnalysisSingletonSwitch import AnalysisSingletonSwitch
from NotificationManager import NotificationManager
from userFaceRecognizer import FacialRecognizer
import time
from loggerhelpers import LoggerHelper
class AnalysisManager():
    
    def __init__(self):
        self.facialAnalyzer = FacialAnalyzer()
        self.audioAnalysisStatus = False
        self.dbh =DatabaseHelper().getInstance()
        lh = LoggerHelper().getInstance()
        self.logger = lh.createLoggerWorker("Analysis Manager","DEBUG",2)
        self.logger.info("Analysis Manager Instantiated")
        
    # This function generates a date time stamp and uses that as a filename
    def generateFilename(self,username):
        time = datetime.datetime.now()
        self.username =username
        self.filename = time.strftime("%d-%m-%y_%H-%M-%S")
        return self.filename
    
    # Root function for Audio Analysis on the Thread
    def performAudioAnalysis(self,userID,expectedStr):
        
        try:
            ac = AccuracyChecker()
            ac.record("recordings_audio/"+ self.username + '/' + self.filename + ".wav")
            accuracy,wpm = ac.performAnalysis(expectedStr)
            afa = AudioFeatureAnalyzer("recordings_audio/"+ self.username + '/' + self.filename + ".wav")
            variance = afa.calcFrequencyVariance()
            mFrequency = afa.calcModalFrequency()
            breathTime = afa.calcTimeSpentBreathing()
            avgAmp = afa.calcAverageAmplitude()
            self.logger.info("userID is {}".format(userID))
            aS = AnalysisSingletonSwitch.getInstance(userID)
        
            while not aS.userChecked:
               self.logger.debug('waiting for recognzizer')
               time.sleep(5)
               self.logger.info("userID is {}".format(userID))
               aS = AnalysisSingletonSwitch.getInstance(userID)
            
            if aS.isUser:
                self.dbh.insert_audiorecordings(userID,accuracy,self.filename,wpm,variance,mFrequency,breathTime,avgAmp,"INSERT")
                self.logger.debug('Inserted Audio')
                count = 0
                while not aS.facialFinished:
                    if count == 6:
                        break
                    self.logger.debug('waiting for face analyzer')
                    time.sleep(5)
                    count += 1
                    aS = AnalysisSingletonSwitch.getInstance(userID)
                nm = NotificationManager.getInstance(userID)
                nm.addNotification("Your results are ready for display","results","Analysis Team")
                self.logger.debug('Added Notification')
                aS.removeInstance(userID)
            else:
                nm = NotificationManager.getInstance(userID)
                nm.addNotification("We're sorry but we couldn't recognize you from your recording, please try again later.","info","Analysis Team")
        except Exception as e:
            self.logger.error('Error: {}'.format(e))
        
    # This function runs the audio and facial analysis threads
    def startAnalysis(self,userID,expectedStr):
        fr = FacialRecognizer()
        fr.beginUserRecognizerThread(self.username, userID)
        
        self.thread = threading.Timer(interval=5,function=self.performAudioAnalysis,args=(userID,expectedStr))
        self.thread.start()
        # Runs the face analyzer module
        # args: username, userid, dbh,filename
        self.facialAnalyzer.beginAnalysisThread(self.username,userID,self.dbh, self.filename,'insert')
        return
                