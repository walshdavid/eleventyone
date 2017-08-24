# -*- coding: utf-8 -*-
"""
Created on Tue Jul 11 11:27:05 2017

@author: datkin10
"""

import wave
import numpy as np
import struct
import math

import matplotlib.pyplot as plt


class AudioFeatureAnalyzer:
    
    def __init__(self, filename):
        self.filename = filename
        wav_file = wave.open(filename, 'rb')
        self.nFrames = wav_file.getnframes()
        self.frate = wav_file.getframerate()
        self.data_size = math.floor(wav_file.getnframes())
        data = wav_file.readframes(self.data_size)
        wav_file.close()
        self.error = False
        try:
            self.data = struct.unpack('{n}h'.format(n=self.data_size), data)
            self.data = np.array(self.data)
            self.frames = data
        except:
            print("Error on struct unpack")
            self.error = True
        
    # This function calculates and returns Power Spectrum Density and a list of frequencies
    def generatePSD(self):
        if self.error:
            return 0
        
        talkVals, nt = self.removeNonTalkingSound()
        fftData = np.fft.fft(talkVals)
        freqList = np.fft.fftfreq(len(talkVals))
    
        ind = np.arange(1,len(talkVals))
        psd = abs(fftData[ind]**2) + abs(fftData[-ind]**2)
    
    
        freqList = freqList[np.arange(1,len(talkVals))]
        
        endSpeechRangeIndex = 0
        startSpeechRangeIndex = 0
        for i in range(len(freqList)):
            freqList[i] *=self.frate
            if freqList[i] > 280:
                endSpeechRangeIndex = i
                break
            elif freqList[i] <= 60:
                startSpeechRangeIndex = i
                
        
        psd = psd[startSpeechRangeIndex:endSpeechRangeIndex]
        freqList =  freqList[startSpeechRangeIndex:endSpeechRangeIndex]
        
        return psd,freqList
        
    # This function removes the non worded sounds the STT generates
    def removeNonTalkingSound(self):
        maxi = abs(self.data[0])
        for val in self.data:
            if abs(val) > maxi:
                maxi = abs(val)
        talkingVals = []
        non_talkingVals = []
        
        for i in range(len(self.data)):
            if abs(self.data[i]) >= maxi/100:
                talkingVals.append(np.longdouble(abs(self.data[i])))
            else:
                non_talkingVals.append(np.longdouble(abs(self.data[i])))
        
        
        return talkingVals,non_talkingVals
    
    # This function calculates the Average Amplitude of the recording
    def calcAverageAmplitude(self):
        
        talkingVals,nt = self.removeNonTalkingSound()
        avgAmp = float(sum(talkingVals)/len(talkingVals))
        return avgAmp

    # This function calculates the modal frequency
    def calcModalFrequency(self):
        psd,freqList = self.generatePSD()
        m = max(psd)
        indx =0
        for i in range(len(psd)):
            if psd[i] == m:
                indx = i
                
        return freqList[indx]
    
    # This function calculates the frequency variance
    def calcFrequencyVariance(self):
        psd,freqList = self.generatePSD()
        m = max(psd)
        sumPSD = np.longdouble(sum(psd))
        indx = 0
        for i in range(len(psd)):
            if psd[i] == m:
                indx = i
                break
        var_sum = np.longdouble(0)
        
        for i in range(len(psd)):
            var_sum += psd[i]*((freqList[i] - freqList[indx])**2)
        
        
        return math.sqrt(var_sum/(sumPSD-1))

    # This function calculates the time spent breathing on a recording
    def calcTimeSpentBreathing(self): 
        talkingVals, nonTalkingVals = self.removeNonTalkingSound()
        duration = self.nFrames/self.frate
        ratio = len(nonTalkingVals)/len(self.data)
        return duration*ratio
    
