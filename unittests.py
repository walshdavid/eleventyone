# -*- coding: utf-8 -*-

import unittest2
from flaskserver import app
from dbhelper import DatabaseHelper
from faceAnalyze import FacialAnalyzer
from AccuracyChecker import AccuracyChecker
from AudioFeatureAnalyzer import AudioFeatureAnalyzer
from FileImporter import FileImporter
from STTFileImporter import STTFileImporter
from STTFormatter import STTFormatter
from STTRecognizer import pocketSphinxRecognizer
from loggerhelpers import LoggerHelper
import speech_recognition as sr
import os

class FlaskServerTests(unittest2.TestCase):
    
    def test_json_folder_exists(self):
        try:
            checker = os.path.isdir('static/json')
            self.assertTrue(checker, True)
        except Exception as e:
            logger.error("Tried to test json folder exists: Exception:{0}".format(e))
    def test_recordings_audio_exists(self):
        try:
            checker = os.path.isdir('recordings_audio')
            self.assertTrue(checker,True)
        except Exception as e:
            logger.error("Tried to check if recordings audio exists: Exception:{0}".format(e))
    def test_recordings_video_exists(self):
        try:
            checker = os.path.isdir('recordings_video')
            self.assertTrue(checker,True)
        except Exception as e:
            logger.error("Tried to check if video directory exists: Exception:{0}".format(e))
    def test_sessions(self):
        try:
            tester = app.test_client(self)
            with tester as c:
                with c.session_transaction() as sess:
                    sess['user'] = "Test User"
                response = tester.get('/menu/')
            self.assertTrue(response.status_code,200)
        except Exception as e:
            logger.error("Tried to test sessions: Exception:{0}".format(e))
    # Response code 2
    def test_login_page_load(self):
        try:
            tester = app.test_client(self)
            response = tester.get('/',content_type='html/text')
            self.assertTrue(response.status_code,200)
        except Exception as e:
            logger.error("Tried to test login page Exception:{0}".format(e))

    # response returns 302 for decorator redirects
    def test_register_page_loads(self):
        try:
            tester = app.test_client(self)
            response = tester.get('/register/')
            self.assertTrue(response.status_code,200)
        except Exception as e:
            logger.error("Tried to test register page: Exception:{0}".format(e))
        
    def test_menu_page_loads(self):
        try:
            tester = app.test_client(self)
            response = tester.get('/menu/')
            self.assertTrue(response.status_code,302)
        except Exception as e:
            logger.error("Tried to test menu page: Exception:{0}".format(e))
        
    def test_graph_page_loads(self):
        try:
            tester = app.test_client(self)
            response = tester.get('/graph/')
            self.assertTrue(response.status_code,302)
        except Exception as e:
            logger.error("Tried to test graph page: Exception:{0}".format(e))


class Test_Database(unittest2.TestCase):
    def testConnect(self):
        try:
            dbh.connect_db()
        except Exception as e:
            logger.error("Tried to test Database Connect: Exception:{0}".format(e))
            self.fail("Failed to connect to the Database")
            
    def test_create(self):
        try:
            dbh.create_tables()
        except Exception as e:
            logger.error("Tried to test create tables: Exception:{0}".format(e))
            self.fail("Failed to create tables")
            
    def test_insert_users(self):
        try:
            dbh.insert_users("testuser","testpassword","male",70,14,"Testing")
        except Exception as e:
            logger.error("Tried to test user insert: Exception:{0}".format(e))
            self.fail("Failed to insert user")
            
    def test_insert_audio_recordings(self):
        try:
            dbh.insert_audiorecordings(1,99,"filename.test",12,12,12,12,12,"Testing")
        except Exception as e:
            logger.error("Tried to test insert audio recordings: Exception:{0}".format(e))
            self.fail("Failed to insert audio recordings")

        
    def test_insert_video_recordings(self):
        try:
            dbh.insert_videorecordings(1,20,30,10,20,30,10,10,"testfilename.avi","Testing")
        except Exception as e:
            logger.error("Tried to unit test video recording: Exception:{0}".format(e))
            self.fail("Failed to insert into video recordings")
            
        
    def test_prescreening_table_insert(self):
        try:
            dbh.insert_prescreening("Good","Yes","Yes",12,"Testing")
        except Exception as e:
            logger.error("Tried to test prescreening table: Exception:{0}".format(e))
            self.fail("Failed to insert into prescreening table")
            
    def test_check_credentials_login(self):
        try:
            check = dbh.checkUserCredentials("Login","testusername","testpassword")
            if(check == "Valid"):
                self.assertTrue(check,"Valid")
            elif(check == "Invalid"):
                self.assertTrue(check,"Invalid")
            else:
                self.fail("Return statement is wrong")
        except Exception as e:
            logger.error("Tried to test check credentials login: Exception:{0}".format(e))
            self.fail("Something messed up")
        
    def test_return_audio_recordings(self):
        try:
            acc,fn,var,wpm,mfreq,brtime,avgamp = dbh.return_audiorecordings(1)
            if acc is not None and fn is not None and wpm is not None and mfreq is not None and brtime is not None and avgamp is not None:
                pass
            else:
                self.fail("Acc and Fn is null")
        except Exception as e:
            logger.error("Tried to test return audio recordings: Exception:{0}".format(e))
            self.fail("Failed to return audio recordings")
    
    def test_insert_config(self):
        try:
            dbh.insert_config(1,2,12,12,12,12,12,12,"Testing")
        except Exception as e:
            logger.error("Tried to test insert config: Exception:{0}".format(e))
            self.fail("Failed to insert config")
    
    def test_return_config(self):
        try:
            acc,var,wpm,mfreq,brtime,avgamp = dbh.return_config(1)
            if acc is not None and wpm is not None and mfreq is not None and brtime is not None and avgamp is not None:
                pass
            else:
                self.fail("Acc and Fn is null")
        except Exception as e:
            logger.error("Tried to test return config: Exception:{0}".format(e))
            self.fail("Failed to return config")
            
    
    
class Test_Audio(unittest2.TestCase):
    def test_convertSentenceToWords(self):
        try:
            res = ac.convertSentenceToWords("testing the audio")
            if res != ["testing", "the", "audio"]:
                self.fail("Failed convertSentenceToWords : Incorrect Result")
        except Exception as e:
            logger.error("Tried to test sentence to words function: Exception:{0}".format(e))
            self.fail("Failed convertSentenceToWords")
    
    def test_compareSentences(self):
        try:
            ac.compareSentences("testing the whole world".split(), "testing the hole world".split())
            if ac.percentageAccuracy != 75:
                self.fail("Failed compareSentences: incorrect result: {}".format(ac.percentageAccuracy))
        except Exception as e:
            logger.error("Tried to test compare sentences: Exception:{0}".format(e))
            self.fail("Failed compareSentences")
            
    def test_record(self):
        try:
            ac.record("UnittestAudio\\TestCase.wav")
        except Exception as e:
            logger.error("Tried to test audio record: Exception:{0}".format(e))
            self.fail("Failed record")

    def test_wordsPerMin(self):
        ac.numword = 7
        ac.timeTaken = 60
        try:
            num = ac.getWordsperMin()
            if num != 7:
                logger.error("Failed words per min")
                self.fail("Failed at words per min : Incorrect Result : {}".format(num))
        except Exception as e:
            logger.error("Tried to test wordspermin: Exception:{0}".format(e))
            self.fail("Failed at words per min")
    

class Test_AdvancedAudioFeatures(unittest2.TestCase):
    def test_calcFrequencyVariance(self):
        try:
            res = afa.calcFrequencyVariance()
            if res != 74.7013688489388:
                logger.error("Failed calculating freq range, incorrect result")
                self.fail("Failed calculating frequency range: Incorrect result {}".format(res))
        except Exception as e:
            logger.error("Tried to test frequency variance: Exception:{0}".format(e))
            self.fail("Failed calculating frequency range")
    
    def test_calcModalFrequency(self):
        try:
            res = afa.calcModalFrequency()
            if res < 93.8904 or res > 93.8905:
                logger.error("Failed calculating modal freq, incorrect result")
                self.fail("Failed calculating modal frequency: Incorrect result {}".format(res))
        except Exception as e:
            logger.error("Tried to test modal frequency Exception:{0}".format(e))
            self.fail("Failed calculating modal frequency")
    
    def test_calcTimeSpentBreathing(self):
        try:
            res = afa.calcTimeSpentBreathing()
            if res != 4.46453514739229:
                logger.error("Failed calculating time spent breathing Incorrect result")
                self.fail("Failed calculating time spent breathing: Incorrect result {}".format(res))
        except Exception as e:
            logger.error("Tried to test time spent breathing:{0}".format(e))
            self.fail("Failed calculating time spent breathing")
    
    def test_calcAvgAmplitude(self):
        try:
            res = afa.calcAverageAmplitude()
            if res < 2130.97608774 or res > 2130.97608775:
                logger.error("Failed calculating average amplitude")
                self.fail("Failed calculating average amplitude: Incorrect result {}".format(res))
        except Exception as e:
            logger.error("Tried to test time spent breathing:{0}".format(e))
            self.fail("Failed calculating average amplitude")
    
class Test_FileImporters(unittest2.TestCase):
    
    def test_sttLoad(self):
        try:
            sfi.loadFile()
        except Exception as e:
            logger.error("Tried to test stt loader".format(e))
            self.fail("Failed loading files")      
            
    def test_sttGetStr(self):
        try:
            sfi.getStr()
        except Exception as e:
            logger.error("Tried to test stt get str".format(e))
            self.fail("Failed returning file string")  
            
    
    def test_fiLoad(self):
        try:
            fi.loadFile()
        except Exception as e:
            logger.error("Tried to test fi loadfile".format(e))
            self.fail("Failed loading files")
            
    def test_GetStr(self):
        try:
            fi.getStr()
        except Exception as e:
            logger.error("Failed to return file string".format(e))
            self.fail("Failed returning file string")  
            
class Test_FileFormatter(unittest2.TestCase):
    
    def test_SpecialNumberCases(self):
        try:
            formatter.formatSpecialNumberCases("27-8")
        except Exception as e:
            logger.error("Tried to test special number cases:{0}".format(e))
            self.fail("failed formatting special number cases")
            
    def test_TestFrontChar(self):
        try:
            res = formatter.testFrontChar("$20")
            if res != ("20 dollars"):
                self.fail("failed formatting front character: Incorrect Result")
        except Exception as e:
            logger.error("Tried to test front char{0}".format(e))
            self.fail("failed formatting front character")
            
    def test_testEndChar(self):
        try:
            res = formatter.testEndChar("20m")
            if res != ("20 million"):
                self.fail("failed formatting end character: Incorrect Result")
        except Exception as e:
            logger.error("Tried to test end char:{0}".format(e))
            self.fail("failed formatting end character")
    
    def test_TestMidChar(self):
        try:
            res = formatter.testMidChar("8.9")
            if res != ("8 point 9"):
                logger.error("Formatting middle char has incorrect result")
                self.fail("failed formatting middle character: Incorrect Result")
        except Exception as e:
            logger.error("Tried to format middle character:{0}".format(e))
            self.fail("failed formatting middle character")
    
    def test_removePunctuation(self):
        try:
            res = formatter.removePunctuation(["My","name,", "is!","Declan."])
            if res != (["My", "name", "is", "Declan"]):
                logger.error("Failed formatting punctuation")
                self.fail("failed formatting punctuation: Incorrect Result")
        except Exception as e:
            logger.error("Tried to remove punctuation:{0}".format(e))
            self.fail("failed formatting punctuation")
            
    def test_convertNumToText(self):
        try:
            res = formatter.convertNumToText("27")
            if res != "twenty seven":
                logger.error("Tried convert num to text")
                self.fail("failed formatting number (standard format): Incorrect Result")
            
            res = formatter.convertNumToText("26th")
            if res != "twenty sixth":
                logger.error("Tried convert num to text")
                self.fail("failed formatting number (ordinal format): Incorrect Result")
        except Exception as e:
            logger.error("Tried to convert num to text:{0}".format(e))
            self.fail("failed formatting number")
            
    def test_removeProperNouns(self):
        
        try:
            res = formatter.removeProperNouns(['at', 'the', 'cross', 'of', 'St', 'Patrick'])
            if res != ['at', 'the', 'cross', 'of']:
                logger.error("Tried to remove proper nouns Incorrect result")
                self.fail("Failed removing proper nouns: Incorrect Result")
        except Exception as e:
            logger.error("Tried to remove proper nouns:{0}".format(e))
            self.fail("Failed removing proper nouns")
            
    def test_removeNonEnglishWords(self):
        try:
            res = formatter.removeNonEnglishWords(["tá", "red", "blue"])
            if res != ["red","blue"]:
                logger.error("Tried to remove non english words Incorrect result")
                self.fail("Failed removing non english words: Incorrect Result")
        except Exception as e:
            logger.error("Tried to remove non english words:{0}".format(e))
            self.fail("Failed removing non english words")
    
    def test_performOperations(self):
        
        try:
            res = formatter.performOperations(["Declan", "will", "get", "$40.5m", "on", "the", "26th"])
            if res != ["will", "get", "forty", "point" ,"five" ,"million", "dollars", "on", "the", "twenty","sixth"]:
                logger.error("Failed to perform operations: incorrect result")
                self.fail("Failed performing operations: Incorrect Result: {}".format(res))
        except Exception as e:
            logger.error("Failed to perform operations".format(e))
            self.fail("Failed performing operations")

class Test_Recognizer(unittest2.TestCase):
    def test_getRawData(self):
        f = sr.AudioFile("UnittestAudio\\TestCase.wav")
        r = sr.Recognizer()
        with f as source:
            ad = r.record(source)
           
        try:    
            psr.getRawData(ad)
        except Exception as e:
            logger.error("Failed to get raw data".format(e))
            self.fail("Failed generating raw data")
    
    def test_decodeRaw(self):
        f = sr.AudioFile("UnittestAudio\\TestCase1.wav")
        r = sr.Recognizer()
        with f as source:
            ad = r.record(source)
        
        rd = psr.getRawData(ad)
        try:    
            psr.decodeAudio(rd)
        except Exception as e:
            logger.error("Failed to decode raw data".format(e))
            self.fail("Failed analyzing raw data")
    
    def test_generateHypothesis(self):
         try:             
             psr.genHypothesis()
         except Exception as e:
             logger.error("Failed to generate hypothesis".format(e))
             self.fail("Failed generating hypothesis")
             
class FacialAnalyzerTestCases(unittest2.TestCase):
    def test_analysis_thread(self):
        try:
            facialAnalyzer.beginAnalysisThread("test_img_no_delete",1010,dbh,"testfilename","TEST")
        except Exception as e:
            logger.error("Facial Analyzer Thread Failed".format(e))
            self.fail("Facial Analyzer Thread Failed")
  
if __name__ == '__main__':
    lh = LoggerHelper().getInstance()
    logger = lh.createLoggerWorker("unittest","DEBUG",2)
    dbh = DatabaseHelper().getInstance()
    facialAnalyzer = FacialAnalyzer()
    ac = AccuracyChecker()
    afa = AudioFeatureAnalyzer("UnittestAudio\\TestCase.wav")
    sfi = STTFileImporter()
    fi = FileImporter()
    formatter = STTFormatter()
    psr = pocketSphinxRecognizer("pocketsphinx-data\\en-US\\acoustic-model",'pocketsphinx-data\\en-US\\language-model.lm.bin','pocketsphinx-data\\en-US\\pronounciation-dictionary.dict')
    unittest2.main()