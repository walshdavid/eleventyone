# -*- coding: utf-8 -*-
import sqlite3
from loggerhelpers import LoggerHelper

class DatabaseHelper():
    # This class is a singleton instance
    __instance = None
    
    @staticmethod
    def getInstance():
        if DatabaseHelper.__instance == None:
            DatabaseHelper()
        return DatabaseHelper.__instance
    '''Constructor'''
    def __init__(self):
        if DatabaseHelper.__instance != None:
            print("Returning Database Helper Instance")
        else:
            DatabaseHelper.__instance = self
            lh = LoggerHelper().getInstance()
            self.logger = lh.createLoggerWorker("dbhelper","DEBUG",2)
            self.create_tables()
        
    # Method to allow for easy connections to the database
    def connect_db(self):
        try:
            conn = sqlite3.connect('database.db',timeout = 10)
            print('[SUCCESS]: Connected to the Database')
            return conn
        except Exception as e:
            self.logger.error("Tried to connect to Database:Exception:{0}".format(e))
            
    # Creates tables at the start of instantiation
    def create_tables(self):
        try:
            conn = self.connect_db()
            cursor = conn.cursor()
            cursor.execute('''
                           CREATE TABLE IF NOT EXISTS users(ID INTEGER PRIMARY KEY AUTOINCREMENT,
                                                            username VARCHAR(20) NOT NULL UNIQUE,
                                                            password VARCHAR(20) NOT NULL,
                                                            sex VARCHAR(10) NOT NULL,
                                                            age int,
                                                            diagnosed int)
                           ''')
            cursor.execute('''
                           CREATE TABLE IF NOT EXISTS audio_recordings(ID INTEGER PRIMARY KEY AUTOINCREMENT,
                                                                       accuracypercentage float NOT NULL, 
                                                                       pitch_variance float NOT NULL,
                                                                       wordspermin float NOT NULL,
                                                                       modal_frequency float NOT NULL, 
                                                                       breath_time float NOT NULL,
                                                                       avg_amplitude float NOT NULL,
                                                                       filename text NOT NULL,
                                                                       userID int,
                                                                       FOREIGN KEY (userID) REFERENCES users(ID)
                                                                       )
                           ''')
            cursor.execute('''
                           CREATE TABLE IF NOT EXISTS prescreening(ID INTEGER PRIMARY KEY AUTOINCREMENT,
                                                                   recordID int,
                                                                   mood VARCHAR(10) NOT NULL,
                                                                   medication VARCHAR(10) NOT NULL,
                                                                   food VARCHAR(10),
                                                                   FOREIGN KEY(recordID) REFERENCES users(ID)
                                                                   )
                          ''')
            cursor.execute('''
                           CREATE TABLE IF NOT EXISTS config(ID INTEGER PRIMARY KEY AUTOINCREMENT,
                                                                   recordID int,
                                                                   time INTEGER NOT NULL,
                                                                   ch_acc INTEGER NOT NULL,
                                                                   ch_wpm INTEGER,
                                                                   ch_freq INTEGER,
                                                                   ch_mod_freq INTEGER,
                                                                   ch_avg_amp INTEGER,
                                                                   ch_breath INTEGER,
                                                                   ch_blink INTEGER,
                                                                   ch_jvib INTEGER,
                                                                   FOREIGN KEY(recordID) REFERENCES users(ID)
                                                                   )
                          ''')
            cursor.execute('''
                           CREATE TABLE IF NOT EXISTS video_recordings(ID INTEGER PRIMARY KEY AUTOINCREMENT,
                                                                           recordID int NOT NULL,
                                                                           total_blinks int NOT NULL,
                                                                           total_peaks int NOT NULL,
                                                                           total_troughs int NOT NULL,
                                                                           blinkspermin float NOT NULL,
                                                                           peakspermin float NOT NULL,
                                                                           troughspermin float NOT NULL,
                                                                           video_duration float NOT NULL,
                                                                           filename text NOT NULL,
                                                                           FOREIGN KEY(recordID) REFERENCES users(ID))
                           ''')
                           
            cursor.execute('''
                           CREATE TABLE IF NOT EXISTS text_preferences(ID INTEGER PRIMARY KEY AUTOINCREMENT,
                                                                           userID int NOT NULL,
                                                                           pref1 VARCHAR(10),
                                                                           pref2 VARCHAR(10),
                                                                           pref3 VARCHAR(10),
                                                                           pref4 VARCHAR(10),
                                                                           pref5 VARCHAR(10),
                                                                           pref6 VARCHAR(10),
                                                                           FOREIGN KEY(userID) REFERENCES users(ID))
                           ''')

            conn.commit()
            print("[SUCCESS]: Created the tables")
        except Exception as e:
            self.logger.error("Tried to Create Tables:Exception:{0}".format(e))
            conn.rollback()
        finally:
            conn.close()
        
    # Insersts users into the database
    def insert_users(self,username,password,sex,age,diagnosed,case):
        try:
            conn = self.connect_db()
            #conn = sqlite3.connect('database.db',timeout = 10)
            cursor = conn.cursor()
            cursor.execute('''
                           INSERT INTO users(username,password,sex,age,diagnosed) VALUES(?,?,?,?,?)
                           ''', (username,password,sex,age,diagnosed))
            print('[SUCCESS]: Inserted a user')
            if(case == "Testing"):
                conn.rollback()
                return
            else:
                conn.commit()
        except Exception as e:
            self.logger.error("Tried to Insert Users:Exception:{0}".format(e))
            raise e
            conn.rollback()
        finally:
            conn.close()
            
    # Inserts audio recording results into the database
    def insert_audiorecordings(self,userId,accuracypercent,filename,wpm,pitch_var,mfreq,breath_time,avgAmp,case):
        try:
            conn = self.connect_db()
            #conn = sqlite3.connect('database.db',timeout = 10)
            # INSERT VALUES
            cursor = conn.cursor()
            cursor.execute('''
                           INSERT INTO audio_recordings(accuracypercentage,filename,pitch_variance,wordspermin,modal_frequency, breath_time, avg_amplitude,userID)
                           VALUES(?,?,?,?,?,?,?,?)''',(accuracypercent,filename,pitch_var,wpm,mfreq,breath_time,avgAmp,userId))
            if(case == "Testing"):
                conn.rollback()
                return
            else:
                conn.commit()
        except Exception as e:
            self.logger.error("Tried to Insert Audio Recordings:{0}".format(e))
            raise e
            conn.rollback()
        finally:
            conn.close()
            
    # Inserts video analysis results into the database
    def insert_videorecordings(self,userId,blinks,peaks,troughs,blinkspermin,peakspermin,troughspermin,duration,filename,case):
        try:
            conn = self.connect_db()
            self.logger.info("Connected")
            self.logger.debug("Data passed in: UserID:{0}, Blinks:{1}, Peaks:{2}, Troughs:{3}, Blinkspermin:{4}, Peakspermin:{5}, Troughspermin:{6}, Duration{7}, Case{8}".format(userId,blinks,peaks,troughs,blinkspermin,peakspermin,troughspermin,duration,case))
            cursor = conn.cursor()
            cursor.execute('''
                           INSERT INTO video_recordings(recordID,total_blinks,total_peaks,total_troughs,blinkspermin,peakspermin,troughspermin,video_duration,filename)
                           VALUES(?,?,?,?,?,?,?,?,?)''',(userId,blinks,peaks,troughs,blinkspermin,peakspermin,troughspermin,duration,filename))
            self.logger.debug("Cursor Executed")
            if(case == "Testing"):
                conn.rollback()
                return
            else:
                conn.commit()
        except Exception as e:
            self.logger.error("Tried to Insert Video Recordings: Exception:{0}".format(e))
            conn.rollback()
        finally:
            conn.close()
            self.logger.info("Inserted")
            
    # Inserts prescreening answers into the database
    def insert_prescreening(self, mood,medication,food,userId,case):
        try:
            conn = self.connect_db()
            #conn = sqlite3.connect('database.db',timeout = 10)
            cursor = conn.cursor()
            cursor.execute('''
                           INSERT INTO prescreening(recordID,mood,medication,food) 
                           VALUES(?,?,?,?)''',(userId,mood,medication,food))
            print('[SUCCESS]: Inserted prescreening')
            if(case == "Testing"):
                conn.rollback()
                return
            else:
                
                conn.commit()
        except Exception as e:
            self.logger.error("Tried to Insert to Prescreen Table:Exception:{0}".format(e))
            raise e
            conn.rollback()
        finally:
            conn.close()
            
   # Inserts configurations into the database
    def insert_config(self,userId,time,ch_acc,ch_wpm,ch_freq,ch_mod_freq,ch_breath,ch_avg_amp,ch_blink,ch_jvib,case):
        try:
            conn = self.connect_db()
            #conn = sqlite3.connect('database.db',timeout = 10)
            cursor = conn.cursor()
            
            #Case for inserting the default values:
            if case == 'First Use':
                 selectcur = cursor.execute(' SELECT ID FROM users WHERE username = ?', (userId,))
                 userId = selectcur.fetchone()[0]
            
            cursor.execute('''
                           INSERT INTO config(recordID,time,ch_acc,ch_wpm,ch_freq,ch_mod_freq,ch_breath,ch_avg_amp,ch_blink,ch_jvib)
                           VALUES(?,?,?,?,?,?,?,?,?,?)''',(userId,time,ch_acc,ch_wpm,ch_freq,ch_mod_freq,ch_breath,ch_avg_amp,ch_blink,ch_jvib))
            print('[SUCCESS]: Inserted config')
            if(case == "Testing"):
                conn.rollback()
                return
            else:
                conn.commit()
        except Exception as e:
            self.logger.error("Tried to Insert to Config Table:Exception:{0}".format(e))
            raise e
            conn.rollback()
        finally:
            conn.close()   
            
    # Inserts users text preferences into the Database
    def insert_text_pref(self,userId,pref1,pref2,pref3,pref4,pref5,pref6,case):
        try:
            conn = self.connect_db()
            cursor = conn.cursor()
            cursor.execute('''
                           INSERT INTO text_preferences(userID,pref1,pref2,pref3,pref4,pref5,pref6)
                           VALUES(?,?,?,?,?,?,?)''',(userId,pref1,pref2,pref3,pref4,pref5,pref6))
            print('[SUCCESS]: Inserted preferences')
            if(case == "Testing"):
                conn.rollback()
                return
            else:
                conn.commit()
        except Exception as e:
            self.logger.error("Tried to Insert to text_pref Table:Exception:{0}".format(e))
            raise e
            conn.rollback()
        finally:
            conn.close()   
            
    # This function checks the database if username and password exists
    def checkUserCredentials(self,function,username,password):
        try:
            data = []
            conn = self.connect_db()
            #conn = sqlite3.connect('database.db')
            cursor = conn.cursor()
            selectcur = cursor.execute('''
                                       SELECT ID,username FROM users WHERE username = ? AND password = ?''',
                                       (username,password))
            row = selectcur.fetchone()
            # If from Login function
            if(function == 'Login'):
                # Check if user exists
                if row is None:
                    return "Invalid"
                else:
                    for member in row:
                        data.append(member)
                    # Check if the form username is the same as the Database
                    if(username == data[1]):
                        # Return the user ID at user table
                        return data[0]
                    else:
                        return 'Invalid'
            # Else if from Register function
            elif(function == 'Register'):
                if row is None:
                    return "Valid"
                else:
                    # User already exists in the Database
                    return "Invalid"
        except Exception as e:
            self.logger.error("Tried to Check User Credential:Exception:{0}".format(e))
            conn.rollback()
        finally:
            conn.close()
    
    # Returns audio recordings based of userId
    def return_audiorecordings(self,userId):
        try:
            conn = self.connect_db()
            #conn = sqlite3.connect('database.db')
            cursor = conn.cursor()
            selectcur = cursor.execute('''
                                       SELECT accuracypercentage, filename, pitch_variance,wordspermin,modal_frequency, breath_time, avg_amplitude FROM audio_recordings 
                                       WHERE userID = ?
                                       ''',(userId,))
            # This took me ages.....
            row = selectcur.fetchall()
            acc = []
            fn = []
            pitch_var = []
            wpm = []
            mFreq = []
            brTime = []
            avgAmp = []
            for i in row:
                acc.append(i[0])
                fn.append(i[1])
                pitch_var.append(i[2])
                wpm.append(i[3])
                mFreq.append(i[4])
                brTime.append(i[5])
                avgAmp.append(i[6])
                
            return acc, fn, wpm, pitch_var,mFreq,brTime,avgAmp
        except Exception as e:
            self.logger.error("Tried to Query Audio Recordings:Exception:{0}".format(e))
            conn.rollback()
        finally:
            conn.close()
            
    # This function returns all data from the video table based on userId     
    def return_videoRecordings(self,userId):
        try:
            conn = self.connect_db()
            cursor = conn.cursor()
            #select query on video records 
            selectcur = cursor.execute('''
                                       SELECT filename, total_blinks, total_peaks, total_troughs, blinkspermin, peakspermin, troughspermin, video_duration FROM video_recordings 
                                       WHERE recordID = ?
                                       ''',(userId,))
            # fech all data and sort into arrays
            row = selectcur.fetchall()
            filename = []
            total_blinks = []
            total_peaks = []
            total_troughs = []
            blinkspermin = []
            peakspermin = [] 
            troughspermin = []
            video_duration = []
            # loop and append the data to the arrays 
            for i in row:
                filename.append(i[0])
                total_blinks.append(i[1])
                total_peaks.append(i[2])
                total_troughs.append(i[3])
                blinkspermin.append(i[4])
                peakspermin.append(i[5])
                troughspermin.append(i[6])
                video_duration.append(i[7])
            #returns the video data
            return filename, total_blinks, total_peaks, total_troughs, blinkspermin, peakspermin, troughspermin, video_duration
        except Exception as e:
            self.logger.error("Tried to Query video Recordings:Exception:{0}".format(e))
            conn.rollback()
        finally:
            conn.close()
    
    # This function returns the configurations for the user
    def return_config(self,userID):
        try:
            conn = self.connect_db()
            cursor = conn.cursor()
            selectcur = cursor.execute('''
                                       SELECT ch_acc, ch_wpm, ch_freq, ch_mod_freq,ch_breath,ch_avg_amp,ch_blink,ch_jvib FROM config 
                                       WHERE recordID = ?
                                       ''',(userID,))
            row = selectcur.fetchall()
            acc = 0
            pitch_var = 0
            wpm = 0
            mFreq = 0
            brTime = 0
            avgAmp = 0
            blink = 0
            jvib= 0
            for i in row:
                acc = i[0]
                pitch_var = i[1]
                wpm = i[2]
                mFreq = i[3]
                brTime = i[4]
                avgAmp = i[5]
                blink = i[6]
                jvib = i[7]
            return acc,pitch_var,wpm,mFreq,brTime,avgAmp,blink,jvib
        except Exception as e:
            self.logger.error("Tried to Query Config Table:Exception:{0}".format(e))
            conn.rollback()
        finally:
            conn.close()
            
    # Returns pre screening results of the user
    def return_prescreen(self, userID):
        try:
            conn = self.connect_db()
            cursor = conn.cursor()
            selectcur = cursor.execute('''
                                       SELECT recordID,mood,medication,food FROM prescreening
                                       WHERE recordID = ?
                                       ''',(userID,))
            self.logger.debug("userID {0}".format(userID))
            row = selectcur.fetchall()
            self.logger.debug("ROW {0}".format(row))
            mood = ''
            medication = ''
            food = ''
            
            for i in row:
                mood,medication,food = i[1],i[2],i[3]
            
            return mood,medication,food
        except Exception as e:
            self.logger.error("Tried to Query prescreen Table:Exception:{0}".format(e))
            conn.rollback()
        finally:
            conn.close()
        
    # This function returns the filenames and processes them 
    def getTakenDays(self, userID):
        try:
            conn = self.connect_db()
            cursor = conn.cursor()
            selectcur = cursor.execute('''
                                       SELECT filename FROM audio_recordings
                                       WHERE userID = ?
                                       ''',(userID,))
            row = selectcur.fetchall()
            fname = []
            for i in row:
                fname.append(i)
            
            takenDays = []
            for g in fname:
                for f in g:
                    f = f.replace("_", " ")
                    f = f.replace("-"," ")
                    f = f.split()
                    takenDays.append(f[:3])
            
            return takenDays
        except Exception as e:
            print('[FAIL]: Failed to return filenames- DB error')
            raise e
            conn.rollback()
        finally:
            conn.close()
            
    # This function returns the text preferences of the user
    def return_text_pref(self,userID):
        try:
            conn = self.connect_db()
            cursor = conn.cursor()
            selectcur = cursor.execute('''
                                       SELECT pref1,pref2,pref3,pref4,pref5,pref6 FROM text_preferences
                                       WHERE userID = ?
                                       ''',(userID,))
            row = selectcur.fetchall()
            pref1 = ''
            pref2 = ''
            pref3 = ''
            pref4 = ''
            pref5 = ''
            pref6 = ''
            
            for i in row:
                pref1,pref2,pref3,pref4,pref5,pref6 = i[0],i[1],i[2],i[3],i[4],i[5]
            return list([pref1,pref2,pref3,pref4,pref5,pref6])
        except Exception as e:
            self.logger.error("Tried to Query text_pref Table:Exception:{0}".format(e))
            conn.rollback()
        finally:
            conn.close()
        a = []
        a.append("ERROR")
        return a
            