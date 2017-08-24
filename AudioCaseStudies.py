#-*- coding: utf-8 -*-
"""
Created on Thu Jul 13 14:42:48 2017

@author: datkin10
"""

from AccuracyChecker import AccuracyChecker
from AudioFeatureAnalyzer import AudioFeatureAnalyzer



file = 'fox2017.wav'
    
ac = AccuracyChecker()
ac.record('Audio-Case-Study-Files/Converted-Wav/' + file)
afa = AudioFeatureAnalyzer('Audio-Case-Study-Files/Converted-Wav/' + file)
f = file.replace('.wav','.txt')
acc,wpm = ac.performAnalysis(open('Audio-Case-Study-Files/Texts/' + f).read())
avgAmp = afa.calcAverageAmplitude()
modF = afa.calcModalFrequency()
breath = afa.calcTimeSpentBreathing()
freqVar = afa.calcFrequencyVariance()
    
print("***   " + file.replace('.wav','') + "   ***")
print("Accuracy:           {}".format(acc))
print("Words per Minute:   {}".format(wpm))
print("Average Amplitude:  {}".format(avgAmp))
print("Modal Frequency:    {}".format(modF))
print("Breathiness:        {}".format(breath))
print("Frequency Variance: {}".format(freqVar))

