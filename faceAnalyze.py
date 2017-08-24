''' Video Facial Analyzer Module
        Needs hachoir to be installed
        pip install -U hachoir3
    Developed By: jsalomo1
'''
import cv2
import dlib
import math
import os
import threading
import fnmatch
import numpy as np
from imutils import face_utils
from hachoir.parser import createParser
from hachoir.metadata import extractMetadata
from loggerhelpers import LoggerHelper
from dbhelper import DatabaseHelper
from AnalysisSingletonSwitch import AnalysisSingletonSwitch
import time

class FacialAnalyzer():
    def __init__(self):
        self.fourcc = cv2.VideoWriter_fourcc(*'XVID')
        self.detector = dlib.get_frontal_face_detector()
        self.predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")
        self.blinks = 0
        self.blinkReset = False
        self.angleList = []
        self.peaks = 0
        self.troughs = 0
        self.duration = 0
        self.userId = 0
        self.username = ""
        self.filename = ""
        self.case = ""
        lh = LoggerHelper().getInstance()
        self.logger = lh.createLoggerWorker("facialanalyzer","DEBUG",2)
        self.logger.info("Facial Analyzer Module Instantiated")
        
    # This function begins the Analysis Thread
    def beginAnalysisThread(self,user,userId,dbh,filename,case):
        try:
            self.case = case
            self.filename = filename + ".avi"
            self.dbh = DatabaseHelper.getInstance()
            self.username = user
            self.userId = userId
            self.VIDEOPATH = str(os.getcwd() + "\\recordings_video\\"+self.username+"\\"+self.filename)
            self.out = cv2.VideoWriter(self.VIDEOPATH,self.fourcc, 20.0, (320,240))
            self.logger.info("Video Created at:{0}".format(self.VIDEOPATH))
            self.logger.info("Analysis Thread has Begun(user:{0}, userId:{1},filename:{2})".format(self.username,self.userId,self.filename))
            self.Thread = threading.Thread(target=self.analyzeVideoRecording, args=(case,filename,user,userId))
            self.Thread.start()
            return True
        except Exception as e:
            self.logger.error("Tried to Begin Thread:{0}".format(e))
            return False
        
    # This function takes in 3 points of a Triangle and returns the angle
    def calculateAngle(self,pointA, pointB, pointC):
        try:
            # Calculate Euclidean Distance
            distanceA = np.linalg.norm(pointB - pointC)
            distanceB = np.linalg.norm(pointA - pointC)
            distanceC = np.linalg.norm(pointA - pointB)
            
            # using Cos to calculate the required angle.
            dividerA = 2*(distanceB * distanceC)
            cosA = ((distanceB**2 + distanceC**2) - distanceA**2) / dividerA
            angleResult = math.degrees(math.acos(cosA))
            
            return angleResult
        except Exception as e:
            self.logger.error("Failed to calculate Angle of A".format(e))
            return False
            
    # This function calculates the number of blinks per recording
    def blinkExtractor(self,shape):
        try:
            # Left Eye Points
            ATL = shape[37:38]
            ABL = shape[41:42]
            ABR = shape[39:40]
            # Right Eye Points
            BTR = shape[44:45]
            BBL = shape[42:43]
            BBR = shape[46:47]
            
            # Left Eye Angle
            angleA = self.calculateAngle(ABR,ATL,ABL)
            # Right Eye Angle
            angleB = self.calculateAngle(BBL,BTR,BBR)
                    
            if(angleA > 22 or angleB > 22):
                self.blinkReset = True
                
            if(self.blinkReset == True):
                if(angleA < 18 or angleB < 18):
                    self.blinks += 1
                    self.blinkReset = False
            return True
        except:
            self.logger.error("Blink Extractor Function Failed(ATL{0}, ABL{1},ABR{2})".format(ATL,ABL,ABR))
            return False
        
    # This function extracts the Jaw Angles from a recording
    def jawAngleExtractor(self,shape):
        try:
            # Facial Points for Jaw
            jawPointLeft = shape[3:4]
            nosePointMid = shape[27:28]
            jawPointBottom = shape[8:9]
            
            jawAngle = self.calculateAngle(jawPointLeft,jawPointBottom,nosePointMid)
        
            self.angleList.append(str(jawAngle))
            return True
        except:
            self.logger.error("Jaw Angle Extractor Failed")
            return False
        
    # This function calculates the peaks and troughs value of a list of jaw angles
    def peaksTroughsExtractor(self):
        try:
            # Float conversion
            # Array to hold the jaw angles
            floatArray = [float(self.angleList[i]) for i in range(len(self.angleList))]
            self.logger.debug("Float Array Values:{0}".format(floatArray))
            # Calculating Peaks
            peaksArray = [floatArray[i] for i in range(1,len(floatArray)-1) if(floatArray[i] > floatArray[i-1] and floatArray[i] > floatArray[i+1])]
            self.logger.debug("Peaks Array Values:{0}".format(floatArray))
            self.peaks = len(peaksArray)
            # Calculating Troughs
            troughsArray = [floatArray[i] for i in range(1,len(floatArray)-1) if(floatArray[i] < floatArray[i-1] and floatArray[i] < floatArray[i+1])]
            self.troughs = len(troughsArray)
            self.logger.info("Analysis Result: Peaks{0}, Troughs{1}".format(self.peaks,self.troughs))
        except Exception as e:
            self.logger.error("Tried to Extract Peaks and Troughs:{0}".format(e))
            return False
        
    # This function calculates per min values and inserts them into the Database
    def insertAnalyzeData(self):
        try:
            peakspermin = (self.peaks / self.duration) * 60
            self.logger.debug("PeaksPerMin = {}")
            troughspermin = (self.troughs / self.duration) * 60
            self.logger.debug("troughspermin")
            blinkspermin = (self.blinks / self.duration) * 60
            self.logger.debug("blinkspermin")
            self.dbh = DatabaseHelper.getInstance()
            self.dbh.insert_videorecordings(self.userId,self.blinks,self.peaks,self.troughs,blinkspermin,peakspermin,troughspermin,self.duration,self.filename,self.case)
            self.logger.info("Data has been inserted into the Database")
            self.resetValues()
            return True
        except:
            self.logger.error("Insert Analyze Failed")
            return False
        
    
    # This function resets the values of Analysis set in the class
    def resetValues(self):
        try:
            self.peaks,self.troughs,self.blinks,self.duration = 0,0,0,0
            self.blinkReset = False
            self.angleList.clear()
            self.userId = 0
            self.username = ""
            self.VIDEOPATH = ""
            self.logger.info("Analysis values has been reset")
            return True
        except Exception as e:
            self.logger.error("Tried to Reset Values:{0}".format(e))
            return False
        
    # This function sorts the images and puts them in the right format
    def imagePathsProcessor(self):
        try:
            # Read in the images and sort them
            image_path = str(os.getcwd() + "\\recordings_video\\" + self.username + "\\")
            self.logger.debug("Image Path:{0}".format(image_path))
            unsorted_imageArrayNames = fnmatch.filter(os.listdir(image_path), '*.jpg')
            imageArray = [int(unsorted_imageArrayNames[i].strip('.jpg')) for i in range(len(unsorted_imageArrayNames))]
            imageArray.sort(key=int)
            sorted_imageArrayNames = [str(imageArray[i])+".jpg" for i in range(0,len(imageArray))]
            self.logger.info("Images have been read and sorted")
            [self.logger.debug("Sorted Image Array Names:{0}".format(i)) for i in sorted_imageArrayNames]
            return image_path, sorted_imageArrayNames
        except Exception as e:
            self.logger.error("Tried to Process Image Paths:{0}".format(e))
            return False
        
    # This function pulls video metadata after the video has been created
    def extractMetaData(self):
        try:
            parser = createParser(self.VIDEOPATH)
            metadata = extractMetadata(parser)
            durationString = [i for i in metadata.exportPlaintext() if "Duration" in i]
            self.logger.info("Meta Data Extraction Completed")
            [self.logger.debug("Meta Data Values: {0}".format(i)) for i in metadata.exportPlaintext()]
            self.logger.debug("Duration of the video is:{0}".format(durationString))
            return durationString
        except Exception as e:
            self.logger.error("Tried to Extract Video MetaData:{0}".format(e))
            return False
        
    # This function converts a stringlist to a float list and then calculates the duration
    def stringToFloatConverter(self,durationString):
        try:
            durationString = durationString[0]
            listNums =[i for i in durationString.split() if i.isdigit()]
            intSec = int(listNums[0])
            floatMs = float("."+listNums[1])
            self.duration = intSec + floatMs
            return True
        except Exception as e:
            self.logger.error("Tried to convert String to Float:{0}".format(e))
            return False
        
    # This is the root function of the Thread.
    def analyzeVideoRecording(self,case,filename,user,userId):
        try:
            self.logger.info("Processing Images")
            path, imageArray = self.imagePathsProcessor()
            self.logger.debug("Return Path Value:{0}".format(path))
            [self.logger.debug("Return Sorted Image Array:{0}".format(i)) for i in imageArray]
            for i in range(len(imageArray)):
                frame = cv2.imread(path + imageArray[i])
                gray = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
                # Detect faces in the grayscale frame
                rects = self.detector(frame,0)
                # Loop over the face detections
                for rect in rects:
                    # Determine the facial landmarks for the face region
                    # Then convert the facial landmark (x,y)
                    # coordinates to a NumPy array
                    shape = self.predictor(gray,rect)
                    shape = face_utils.shape_to_np(shape)
                    self.blinkExtractor(shape)
                    self.jawAngleExtractor(shape)
                    for(x,y) in shape:
                        cv2.circle(frame, (x, y), 2, (0, 0, 255), -1)
                cv2.putText(frame,"Number of Blinks:"+str(self.blinks),(10,20),cv2.FONT_HERSHEY_SIMPLEX,1,(0,0,0),2)
                self.out.write(frame)
                self.logger.debug("Frame has been written")
            # Finish the recording
            self.out.release()
            self.logger.info("Video Created")
            durationString = self.extractMetaData()
            if not durationString:
                self.logger.error("No Duration Value")
                return False
            else:
                self.stringToFloatConverter(durationString)
                self.logger.debug("Duration{0}, Blinks{1}".format(self.duration,self.blinks))
                self.peaksTroughsExtractor()
                aS = AnalysisSingletonSwitch.getInstance(userId)
                self.logger.info("got switch instance !")
                while not aS.userChecked:
                    time.sleep(5)
                    aS = AnalysisSingletonSwitch.getInstance(userId)
                    
                if aS.isUser:
                    self.insertAnalyzeData()
                    self.logger.info("Analysis Complete !")
                    if self.case is not "TEST":
                        [os.remove(path + i) for i in imageArray]
                    
                    self.logger.info("userID is {}".format(userId))
                    aS = AnalysisSingletonSwitch.getInstance(userId)
                    self.logger.info("got switch instance !")
                    aS.facialFinished = True
                    self.logger.info("Complete!")
                return True
        except Exception as e:
            self.logger.error("Root Video Analysis Failed:{0}".format(e))
            return False
