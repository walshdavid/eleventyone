
# -*- coding: utf-8 -*-
"""
Created on Wed Jul  5 11:37:30 2017

@author: jsalomo1
"""

import flask
import os
from STTFileImporter import STTFileImporter
from FileImporter import FileImporter
from dbhelper import DatabaseHelper
from AnalysisManager import AnalysisManager
from loggerhelpers import LoggerHelper
from functools import wraps
from NotificationManager import NotificationManager
from BackgroundTaskManager import BackgroundTaskManager
import pandas as pd
import json
import fnmatch
import codecs

''' Decorator Functions'''
# This decorator runs at first login to the system
def test_firstLogin(f):
    @wraps(f)
    def wrap(*args,**kwargs):
        nm = NotificationManager.getInstance(flask.session['sessionID'])
        dbh = DatabaseHelper.getInstance()
        acc,filename,wpm,var,mFreq,brTime,avgAmp = dbh.return_audiorecordings(flask.session['sessionID'])
        if len(filename) == 0:
            if not nm.newStartGiven:
                nm.addNotification("Hi " + flask.session['user'] + ', and welcome to PAPA! It seems to be your first time using this app. Please click the help button to get started.', "help", "PAPA Team")
                nm.newStartGiven = True
        return f(*args,**kwargs)
  
    return wrap

# This decorator notifies a deterioration at menu page.
def notify_deterioration(f):
   @wraps(f)
   def wrap(*args,**kwargs):
       nm = NotificationManager.getInstance(flask.session['sessionID'])
       dbh = DatabaseHelper.getInstance()
       acc,filename,wpm,var,mFreq,brTime,avgAmp = dbh.return_audiorecordings(flask.session['sessionID'])
       ch_acc,ch_wpm,ch_var,ch_mFreq,ch_breath,ch_avgAmp,ch_blink,ch_jvib = dbh.return_config(flask.session['sessionID'])   
       filename,total_blinks,total_peaks,total_troughs,blinkspermin,peakspermin,troughspermin,video_duration = dbh.return_videoRecordings(flask.session['sessionID'])
       try:
            if len(acc) >5:
                avg_acc = (sum(acc) - acc[-1])/(len(acc) - 1)
                avg_wpm = (sum(wpm) - wpm[-1])/(len(wpm) - 1)
                avg_var = (sum(var) - var[-1])/(len(var) - 1)
                avg_mFreq = (sum(mFreq) - mFreq[-1])/(len(mFreq) - 1)
                avg_brTime = (sum(brTime) - brTime[-1])/(len(brTime) - 1)
                avg_avgAmp = (sum(avgAmp) - avgAmp[-1])/(len(avgAmp) - 1)
                avg_blinkspermin = (sum(blinkspermin) - blinkspermin[-1])/(len(blinkspermin) - 1)
                avg_peakspermin = (sum(peakspermin) - peakspermin[-1])/(len(peakspermin) - 1)
           
            if (((acc[-1]/avg_acc)-100) <= -ch_acc) or (((wpm[-1]/avg_wpm)-100) <= -ch_wpm) or (((var[-1]/avg_var)-100) <= -ch_var) or (((brTime[-1]/avg_brTime)-100) <= ch_breath) or (((avg_avgAmp[-1]/avg_avgAmp)-100) <= -ch_avgAmp) or (((mFreq[-1]/avg_mFreq)-100) <= -ch_mFreq or (((blinkspermin[-1]/avg_blinkspermin)-100) <= -ch_blink) or (((peakspermin[-1]/avg_peakspermin)-100) <= ch_jvib)):
                nm.addNotification('We have noticed some changes in your results, your doctor has been notified, but you may wish to book an appointment',"deterioration","Analysis Team")
                nm.sendDoctorNotifications("Hello", "declan_atkins@optum.com")
                return flask.render_template('menu.html', message=nm.getUserNotifications(), days=json.dumps(dbh.getTakenDays(flask.session['sessionID'])))
       except:
            return flask.render_template('menu.html', message=nm.getUserNotifications(), days=json.dumps(dbh.getTakenDays(flask.session['sessionID'])))
       return f(*args,**kwargs)
  
   return wrap

#This decorator stops users that have not logged in from running functions
def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'user' in flask.session:
            return f(*args,**kwargs)
        else:
            flask.flash("You need to login first")
            return flask.redirect(flask.url_for('login_page'))
    return wrap

# This decorator stops an existing online user from running functions
def already_loggedin(f):
    @wraps(f)
    def wrap(*args,**kwargs):
        if 'user' in flask.session:
            flask.flash("You need to log out first")
            dbh = DatabaseHelper.getInstance()
            nm = NotificationManager.getInstance(flask.session['sessionID'])
            return flask.render_template('menu.html', message=nm.getUserNotifications(), days=json.dumps(dbh.getTakenDays(flask.session['sessionID'])))
        else:
            return f(*args,**kwargs)
    return wrap

# This is the Recording Class, All functions here are related to recording modules
class AudioRec(flask.Flask):
    def __init__(self, import_name):
        super(AudioRec, self).__init__(import_name)
        
        self.route("/audiorec/")(self.audiorec)
        self.route("/select")(self.selectArticlePage)
        self.route("/loading-results/")(self.loadScreen)
        self.route("/selectfunc", methods=['GET','POST'])(self.text_choice_func)
        self.fi = STTFileImporter()
        self.am = AnalysisManager()
        self.dbh = DatabaseHelper().getInstance()
        self.tipSelector = FileImporter()
        lh = LoggerHelper().getInstance()
        self.recordinglogger = lh.createLoggerWorker("recording","DEBUG",2)
        self.recordinglogger.info("Audio Rec Instantiated")
        
    def text_choice_func(self):
        if flask.request.method == "POST":
            file = flask.request.form['file']
            file += '.txt'
            orderNames = self.fi.getOrdering(flask.session['sessionID'])
            for val in orderNames:
                text_files = fnmatch.filter(os.listdir('files/daily-articles/' + val + '/' ), '*.txt')
                
                if file in text_files:
                    try:
                        f = open('files/daily-articles/' + val + '/' + file)
                    except:
                        f = codecs.open('files/daily-articles/' + val + '/' + file, "r", encoding="windows-1252")
                    self.text = f.read()
                    self.text = self.fi.trimText(self.text)
                    return flask.jsonify('complete')

        return flask.render_template('wrong.html')
    
    @login_required
    def selectArticlePage(self):
        orderNames = self.fi.getOrdering(flask.session['sessionID'])
        orderImages = []
        orderhead1 = []
        orderhead2 = []
        orderhead3 = []
        
        countEmpty = 0
        self.flasklogger.debug("{}".format(orderNames))
        for val in orderNames:
            with open('files/Daily-Articles/ArticleSites.txt') as f:
                for line in f:
                    line = line.split()
                    if line[0] == val:
                        orderImages.append(line[3])
            
            text_files = fnmatch.filter(os.listdir('files/daily-articles/' + val + '/' ), '*.txt')
            self.flasklogger.debug("text files: {}".format(text_files))
           
            while len(text_files)< 3:
                text_files.append("EMPTY")
                countEmpty += 1
                self.flasklogger.debug("Number of empty values: {}".format( countEmpty))
            orderhead1.append(text_files[0].replace(".txt", ''))
            orderhead2.append(text_files[1].replace(".txt", ''))
            orderhead3.append(text_files[2].replace(".txt", ''))
        
        if countEmpty < 9:
            ser_imgs = pd.Series(orderImages, index = [orderNames], name = "images")
            ser_head1 = pd.Series(orderhead1, index = [orderNames], name = "head1")
            ser_head2 = pd.Series(orderhead2, index = [orderNames], name = "head2")
            ser_head3 = pd.Series(orderhead3, index = [orderNames], name = "head3")
        
            frame = pd.concat([ser_imgs,ser_head1,ser_head2,ser_head3],axis=1)
            frame.to_json("static/json/prefs.json")
            f = open("static/json/prefs.json", 'r')
            jsonstring = f.read()
            return flask.render_template('selectArticle.html', jsonstring=jsonstring)
        else:
            self.flasklogger.debug("Number of empty values: {}".format( countEmpty))
            self.text = self.fi.loadFile()
            return flask.redirect('/audiorec/')
        
    # This function deals with the recording page
    @login_required    
    def audiorec(self):
        try:
            self.tip = self.tipSelector.loadFile()
            self.userID = flask.session['sessionID']
            self.username = flask.session['user']
            return flask.render_template('recordnew.html', value = self.text, username=self.username,
                                         filename=self.am.generateFilename(self.username))
        except Exception as e:
            self.recordinglogger.error("Recording Page Failed: Exception:{0}".format(e))
            return flask.render_template('wrong.html', error = "{}".format(e))
    # This function starts the analysis threads
    @login_required
    def loadScreen(self):
        try:
            self.am.startAnalysis(self.userID,self.text)
            return flask.render_template('loading.html', value = self.tip)
        except Exception as e:
            self.recordinglogger.error("Load Screen Failed: Exception:{0}".format(e))
            return flask.render_template('wrong.html', error = "{}".format(e))
        
# This is a Flask Server Class. all functions here related to the Server Controller
class FlaskServer(AudioRec):
    def __init__(self, import_name):
        super(FlaskServer, self).__init__(import_name)
        bt = BackgroundTaskManager()
        bt.begin()
        self.secret_key = os.urandom(24)
        self.route("/")(self.login_page)
        self.route("/register/")(self.register_page)
        self.route("/login-user/", methods=['POST'])(self.login_user)
        self.route('/logout/')(self.logout)
        self.route('/menu_page/', methods=['GET','POST'])(self.menu_page)
        self.route('/menu/')(self.menu)
        self.route("/res/")(self.result_page)
        self.route("/graphs/")(self.graph_page)
        self.route("/lingraph/")(self.lingraph_page)
        self.route("/configf/", methods=['POST'])(self.config_func)
        self.route("/config/")(self.config_page)
        self.route("/info/")(self.info_page)
        self.route('/register_user/', methods=['POST'])(self.register_user)
        self.route("/notifications")(self.updateNotifications)
        self.route('/pref_func/', methods=['POST'])(self.pref_func)
        self.route("/textpreferences")(self.getPreferences)
        self.dbh = DatabaseHelper().getInstance()
        # Check if these directories exist
        if(os.path.isdir("recordings_audio") == False):
            os.makedirs("recordings_audio")
        if(os.path.isdir("recordings_video") == False):
            os.makedirs("recordings_video")
        if(os.path.isdir("logfiles") == False):
            os.makedirs("logfiles")
        lh = LoggerHelper().getInstance()
        self.flasklogger = lh.createLoggerWorker("flaskserver","DEBUG",2)
        self.flasklogger.info("Flask Server Instantiated")
        self.loggedUsers = []#Users who have already logged in today
        self.registeredUsers = []#Users who have registered for the first time
        
    
    # This function returns the login page
    @already_loggedin
    def login_page(self):
        try:
            self.flasklogger.debug("logged in")
            return flask.render_template('login.html')
        except Exception as e:
            self.flasklogger.error("Login Page Failed: Exception:{0}".format(e))
            return flask.render_template('wrong.html', error = "{}".format(e))
        
    # This function returns the register page
    @already_loggedin
    def register_page(self):
        try:
            return flask.render_template('register.html')
        except Exception as e:
            self.flasklogger.error("Register Page Failed:Exception:{0}".format(e))
            return flask.render_template('wrong.html', error = "{}".format(e))
        
    # This function takes username and password and checks the database to log in the user
    @already_loggedin
    def login_user(self):
        try:
            user = flask.request.form['username']
            password = flask.request.form['password']
            if len(user) and len(password) == 0:
                flask.flash("Please input your username and password correctly")
                return flask.render_template("login.html")
            check = self.dbh.checkUserCredentials("Login",user,password)
            if(check == 'Invalid'):
                flask.flash("Invalid Credentials, Try Again")
                return flask.render_template('login.html')
            else:   
                PATH = 'recordings_audio/' + user
                if not os.path.exists(PATH):
                    os.makedirs(PATH)
                PATH = 'recordings_video/' + user
                if not os.path.exists(PATH):
                    os.makedirs(PATH)
                flask.flash("You have successfully logged in")
                # Add session ID
                flask.session['sessionID'] = check
                flask.session['user'] = user
                if user not in self.loggedUsers:
                    self.loggedUsers.append(user)
                    return flask.render_template('prescreen.html',
                                             user_id = flask.session['sessionID'],
                                             username = flask.session['user'])
                else:#Only show the prescreening on their first login of the day
                    return flask.redirect('/menu/')
        except Exception as e:
            self.flasklogger.error("Login User Function Failed:Exception:{0}".format(e))
            return flask.render_template('wrong.html', error = "{}".format(e))
        
    # This function logs a user out
    @login_required
    def logout(self):
        try:
            NotificationManager.removeInstance(flask.session['sessionID'])
            flask.session.clear()
            flask.flash("You have been logged out!")
            return flask.redirect(flask.url_for('login_page'))
        except Exception as e:
            self.flasklogger.error("Logout Failed:Exception:{0}".format(e))
            return flask.render_template('wrong.html', error = "{}".format(e))
        
    # This function returns the menu page and activates a notification
    @login_required
    @notify_deterioration 
    def menu(self):
        try:
            nm = NotificationManager.getInstance(flask.session['sessionID'])
            return flask.render_template('menu.html', message=nm.getUserNotifications(), days=json.dumps(self.dbh.getTakenDays(flask.session['sessionID'])))
        except Exception as e:
            self.flasklogger.error("Menu Page Failed:Exception:{0}".format(e))
            return flask.render_template('wrong.html', error = "{}".format(e))
    
    # This function inserts prescreening answers and puts it into the database
    # and then send a message to the client to redirect to the menu page
    @test_firstLogin    
    def menu_page(self):
        try:
            if flask.request.method == "POST":
                mood = flask.request.form['q1']
                food = flask.request.form['q2']
                medication = flask.request.form['q3']
                userId = flask.session['sessionID']
                self.dbh.insert_prescreening(mood,medication,food,userId,"Insert")
                return flask.jsonify("Data Inserted")
        except Exception as e:
            self.flasklogger.error("Pre Menu Page(Data Insert) Failed:Exception:{0}".format(e))
            return flask.render_template('wrong.html', error = "{}".format(e))
        
    # This function pulls recording data from the Database, creates a JSON string and then sends it through the Graph Page-Client Side
    @login_required
    def result_page(self):
        try:
            self.tip = self.tipSelector.loadFile()
            #import audio data from db and convert to a json string
            accuracy_percentage,filename,wpm,variance,mFreq,brTime,avgAmp = self.dbh.return_audiorecordings(flask.session['sessionID'])
            filenamestripwav = []
            for val in filename:
                filenamestripwav.append(val.strip('.wav'))
            ser_accp = pd.Series(accuracy_percentage, index = [filenamestripwav], name = "accuracy")
            ser_wpm = pd.Series(wpm, index = [filenamestripwav], name = "words")
            ser_var = pd.Series(variance, index = [filenamestripwav], name = "variance")
            ser_mFreq = pd.Series(mFreq, index = [filenamestripwav], name = "modalFrequency")
            ser_brTime = pd.Series(brTime, index = [filenamestripwav], name = "brTime")
            ser_avgAmp = pd.Series(avgAmp, index = [filenamestripwav], name = "avgAmp")
            # Turn Series into a DataFrame and convert it to json using pandas
            frame = pd.concat([ser_accp,ser_wpm,ser_var,ser_mFreq,ser_brTime,ser_avgAmp], axis = 1)
            frame.to_json('static\json\graphdata.json')
            file = open('static\json\graphdata.json','r')
            self.jsonstring = file.read()
            #import video data and export as json
            
            filename, total_blinks, total_peaks, total_troughs, blinkspermin, peakspermin, troughspermin, video_duration = self.dbh.return_videoRecordings(flask.session['sessionID'])
            filenamestripavi = []
            for val in filename:
                filenamestripavi.append(val.strip('.avi'))
            f_total_blinks = pd.Series(total_blinks, index = [filenamestripavi], name = "total blinks")
            f_total_peaks = pd.Series(total_peaks, index = [filenamestripavi], name = "total peaks")
            f_total_troughs = pd.Series(total_troughs, index = [filenamestripavi], name = "total troughs")
            f_blinkspermin = pd.Series(blinkspermin, index = [filenamestripavi], name = "blinkspermin")
            f_peakspermin = pd.Series(peakspermin, index = [filenamestripavi], name = "peakspermin")
            f_troughspermin = pd.Series(troughspermin, index = [filenamestripavi], name = "troughs per min")
            f_video_duration = pd.Series(video_duration, index = [filenamestripavi], name = "video duration")
            # Turn Series into a DataFrame and convert it to json using pandas
            frame2 = pd.concat([f_total_blinks,f_total_peaks,f_total_troughs,f_blinkspermin,f_peakspermin,f_troughspermin,f_video_duration], axis = 1)
            frame2.to_json('static\json\graphdata2.json')
            file2 = open('static\json\graphdata2.json','r')
            self.videojsonstring = file2.read()
            ch_acc,ch_wpm,ch_var,ch_mFreq,ch_breath,ch_avgAmp,ch_blink,ch_jvib = self.dbh.return_config(flask.session['sessionID'])
            self.flasklogger.debug("{0},{1},{2},{3},{4},{5},{6},{7}".format(ch_acc,ch_wpm,ch_var,ch_mFreq,ch_breath,ch_avgAmp,ch_blink,ch_jvib))
            mood,medication,food = self.dbh.return_prescreen(flask.session['sessionID'])
            self.flasklogger.debug("{0},{1},{2}".format(mood,medication,food))
            return flask.render_template('result.html',
                                         jsonstring = self.jsonstring, videojsonstring = self.videojsonstring,
                                         ch_acc = ch_acc, ch_wpm = ch_wpm, ch_var = ch_var, ch_breath = ch_breath, ch_blink = ch_blink, ch_jvib = ch_jvib,
                                         mood = mood,medication = medication, food = food, value = self.tip)
        except Exception as e:
            self.flasklogger.error("Result Page Failed:Exception:{0}".format(e))
            return flask.render_template('wrong.html', error = "{}".format(e))
    
    # This function pulls the results json file and creates a radar graph
    @login_required
    def graph_page(self):
        try:
            ch_acc,ch_wpm,ch_var,ch_mFreq,ch_breath,ch_avgAmp,ch_blink,ch_jvib = self.dbh.return_config(flask.session['sessionID'])
            return flask.render_template('graphs.html',
                                         jsonstring = self.jsonstring, videojsonstring = self.videojsonstring,
                                         ch_mFreq = ch_mFreq, ch_avgAmp = ch_avgAmp)
        except Exception as e:
            self.flasklogger.error("Graph page Failed:Exception:{0}".format(e))
            return flask.render_template('wrong.html')
    
    # This functions pulls the results from json file and creates line graphs
    @login_required
    def lingraph_page(self):
        try:
            return flask.render_template('lingraph.html',
                                         jsonstring = self.jsonstring, videojsonstring = self.videojsonstring)
        except Exception as e:
            self.flasklogger.error("Line Graph Failed:Exception:{0}".format(e))
            return flask.render_template('wrong.html', error = "{}".format(e))
        
    @login_required
    def info_page(self):
        try:
            return flask.render_template('info.html')
        except Exception as e:
            self.flasklogger.error("Info Page Failed:Exception:{0}".format(e))
            return flask.render_template('wrong.html', error = "{}".format(e))
    
    # This function pulls the configuration page
    @login_required
    def config_page(self):
        try:
            return flask.render_template('config.html')
        except Exception as e:
            self.flasklogger.error("Configuration Page Failed:Exception:{0}".format(e))
            return flask.render_template('wrong.html', error = "{}".format(e))
        
    # This function takes the config page form, inserts into the database and creates a notification preference
    def config_func(self):
        try:
            userId = flask.session['sessionID']
            time = flask.request.form['time']
            ch_acc = flask.request.form['ch_acc']
            ch_wpm = flask.request.form['ch_wpm']
            ch_freq = flask.request.form['ch_freq']
            ch_mod_freq = flask.request.form['ch_mod_freq']
            ch_avg_amp = flask.request.form['ch_avg_amp']
            ch_breath = flask.request.form['ch_breath']
            ch_blink = flask.request.form['ch_blink']
            ch_jvib = flask.request.form['ch_jvib']
            self.dbh.insert_config(userId,time,ch_acc,ch_wpm,ch_freq,ch_mod_freq,ch_breath,ch_avg_amp,ch_blink,ch_jvib,"save")
            nm = NotificationManager.getInstance(flask.session['sessionID'])
            nm.addNotification("Your changes have been saved.", "config", "SYSTEM")
            return flask.render_template("menu.html",message = nm.getUserNotifications(), days=json.dumps(self.dbh.getTakenDays(flask.session['sessionID'])))
        except Exception as e:
            self.flasklogger.error("Configuration Function Failed:Exception:{0}".format(e))
            return flask.render_template('wrong.html', error = "{}".format(e))
        
    # This function registers a user into the database
    @already_loggedin
    def register_user(self):
        try:
            user = flask.request.form['username']
            password = flask.request.form['password']
            sex = flask.request.form['sex']
            age = flask.request.form['age']
            diagnosed = flask.request.form['diagnosed']
            if len(user) == 0 or len(password) == 0:
                flask.flash("Please input your username and password correctly")
                return flask.render_template("register.html")
            check = self.dbh.checkUserCredentials("Register",user,password)
            if( check == 'Valid'):
                self.registeredUsers.append(user)
                self.dbh.insert_users(user,password,sex,age,diagnosed,"Register")
                PATH = 'recordings_audio/' + user
                if not os.path.exists(PATH):
                    os.makedirs(PATH)
                self.dbh.insert_config(user,1,10,10,10,10,10,10,10,10,'First Use')
                flask.flash("You have successfully registered")
                return flask.render_template('login.html')
            else:
                flask.flash("Invalid Credentials, Try again")
                return flask.render_template('register.html')
        except Exception as e:
            self.flasklogger.error("Register User Function Failed:Exception:{0}".format(e))
            return flask.render_template('wrong.html', error = "{}".format(e))
        
        
    # This function updates the notification instance
    def updateNotifications(self):
        try:
            nm = NotificationManager.getInstance(flask.session['sessionID'])
            self.flasklogger.debug("CurrList:{}".format(self.registeredUsers))
            return nm.getUserNotifications()
        except Exception as e:
            self.flasklogger.error("Update Notification Function:Exception:{0}".format(e))
            return flask.render_template('wrong.html', error = "{}".format(e))
        
        
    # This function returns the text preferences page
    @login_required
    def getPreferences(self):
        try:
            return flask.render_template("textpreferences.html")
        except Exception as e:
            self.flasklogger.error("Text Preferences Page Failed To return:{0}".format(e))
            return flask.render_template('wrong.html',error="{}".format(e))
    
    # This function takes the users preferences of articles and stores them into the Database
    def pref_func(self):
        try:
            userID = flask.session['sessionID']
            pref1  = flask.request.form.get('irishindependent')
            pref2  = flask.request.form.get('irishtimes')
            pref3  = flask.request.form.get('rte')
            pref4  = flask.request.form.get('rtesport')
            pref5  = flask.request.form.get('guardian')
            pref6  = flask.request.form.get('skysports')
            
            self.dbh.insert_text_pref(userID,
                                      dict(p1=('irishindependent' if pref1 == 'true' else "NULL"))['p1'],
                                      dict(p2=('irishtimes' if pref2 == 'true' else "NULL"))['p2'],
                                      dict(p3=('rte' if pref3 == 'true' else "NULL"))['p3'],
                                      dict(p4=('rtesport' if pref4 == 'true' else "NULL"))['p4'],
                                      dict(p5=('guardian' if pref5 == 'true' else "NULL"))['p5'],
                                      dict(p6=('skysports' if pref6 == 'true' else "NULL"))['p6'],
                                      "INSERT")
            
            nm = NotificationManager.getInstance(flask.session['sessionID'])
            nm.addNotification("Your changes have been saved", "preferences", "System")
            return flask.redirect('/menu')
        except Exception as e:
            self.flasklogger.error("Preferences function failed:{0}".format(e))
            return flask.render_template('wrong.html',error="{}".format(e))
        
app = FlaskServer(__name__)

if __name__ == '__main__':
    app.run()