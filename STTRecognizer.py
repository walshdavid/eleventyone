   
"""
Created on Mon Jul  3 10:42:52 2017

@author: datkin10
"""

import pocketsphinx
import os

class pocketSphinxRecognizer:
    
    def __init__(self,acoustic_parameters_directory,language_model_file,phoneme_dictionary_file):
        self.config = pocketsphinx.Decoder.default_config()
        self.config.set_string("-hmm", acoustic_parameters_directory)  # set the path of the hidden Markov model (HMM) parameter files
        self.config.set_string("-lm", language_model_file)
        self.config.set_string("-dict", phoneme_dictionary_file)
        self.config.set_string("-logfn", os.devnull)
        self.decoder = pocketsphinx.Decoder(self.config)
        
    # This function returns the Audio Data Raw
    def getRawData(self, AudioData):
        rd = AudioData.get_raw_data()
        return rd
    
    # This function decodes the raw audio data
    def decodeAudio(self, rawData):
        self.decoder.start_utt()
        self.decoder.process_raw(rawData, False, True)
        self.decoder.end_utt()
    
    # This function generates a hypothesis
    def genHypothesis(self):
        hyp = self.decoder.hyp()
        return hyp.hypstr