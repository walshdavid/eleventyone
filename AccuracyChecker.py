# -*- coding: utf-8 -*-
"""
Created on Wed Jun 14 09:36:14 2017

@author: datkin10

This contains the accuracy checker for the STT
"""
import io
import speech_recognition as sr
from STTRecognizer import pocketSphinxRecognizer
from STTFormatter import STTFormatter


class AccuracyChecker:
    '''Constructor'''
    def __init__(self):
        print('[BOOTING]: Audio Recognition Module')
        self.percentageAccuracy=0
        language_directory = ("pocketsphinx-data/en-US")
        acoustic_parameters_directory = (language_directory + "/acoustic-model")
        language_model_file =  (language_directory + "/language-model.lm.bin")
        phoneme_dictionary_file = (language_directory + "/pronounciation-dictionary.dict")
        self.r = pocketSphinxRecognizer(acoustic_parameters_directory,language_model_file,phoneme_dictionary_file)
        self.frames = io.BytesIO()
        
    def convertSentenceToWords(self,Str):#convert a string to an array of words, allows for use to test whether words were received correctly
        if Str is not None:    
            word = Str.split()
            return word
        else:
            print("Error no recording found")
            return "Error no recording found"

       
    #sent1 is the control string, sent2 is the read string    
    def compareSentences(self,sent1,sent2):#compare the two sentences and determine accuracy
        numDifferences = 0
        
        
        for word in sent1:
            if word.lower() not in sent2:
                numDifferences+=1
    
        if len(sent1) > len(sent2):
            self.percentageAccuracy = 100 - ((numDifferences/len(sent1))*100)
        else:
            self.percentageAccuracy = (100 - ((numDifferences/len(sent2))*100))
    
    #Take in the wav file and record from it to get the audio data
    def record(self, WAV_FILE):

        with sr.AudioFile(WAV_FILE) as source:
            self.m =source
            seconds_per_buffer = (source.CHUNK + 0.0) / source.SAMPLE_RATE
            elapsed_time = 0
        
            while True:  # loop for the total number of chunks needed
                buffer = source.stream.read(source.CHUNK)
                if len(buffer) == 0: break
                elapsed_time += seconds_per_buffer
                self.frames.write(buffer)#write each frame for use later
                self.timeTaken = elapsed_time

        return
                
    def getWordsperMin(self):
        wpm = self.numword/((self.timeTaken)/60)
        self.WpM = wpm
        return self.WpM
    
    def performAnalysis(self,expectedStr):
        #Format the expected result to remove words that cant be recognized correctly
        formatter = STTFormatter()
        expectedStr = self.convertSentenceToWords(expectedStr)
        expectedStr = formatter.performOperations(expectedStr)
        frame_data = self.frames.getvalue()
        #Create the audio data from the frames
        recievedData = sr.AudioData(frame_data, self.m.SAMPLE_RATE, self.m.SAMPLE_WIDTH)
        #generate the raw data for processing
        rd = self.r.getRawData(recievedData)
        #decode
        self.r.decodeAudio(rd)
        val = self.r.genHypothesis()
        print(val)
        self.numword = len(val.split())
        #Test the accuracy
        val = self.convertSentenceToWords(val)
        self.compareSentences(expectedStr,val)
        #Check to ensure wpm defaults to lowest possibe
        if len(expectedStr) < len(val):
            self.numword = len(expectedStr)
        else:
            self.numword = len(val)
            
        
        wpm = self.getWordsperMin()
        #return the accuracy and wpm
        return self.percentageAccuracy,wpm
        
    
    
    
