# -*- coding: utf-8 -*-
import logging
import os
    
             
# singleton
class LoggerHelper():
    
    __instance = None
    @staticmethod
    def getInstance():
        if LoggerHelper.__instance == None:
            LoggerHelper()
        return LoggerHelper.__instance
    
    def __init__(self):
        if LoggerHelper.__instance != None:
            print("Returning Logger Helper Instance")
        else:
            LoggerHelper.__instance = self
            # Formatter settings for the log file and creates a PATH
            self.formatter = logging.Formatter("%(levelname)s %(asctime)s - %(message)s")
            self.HANDLER_PATH = str(os.getcwd()+"/logfiles/")
        
    # This function sets the logger level
    def setLoggerLevel(self,logger,loggerlevel):
        if loggerlevel == "DEBUG":
            logger.setLevel(logging.DEBUG)
        elif loggerlevel == "INFO":
            logger.setLevel(logging.INFO)
        elif loggerlevel == "WARNING":
            logger.setLevel(logging.WARNING)
        elif loggerlevel == "ERROR":
            logger.setLevel(logging.ERROR)
        elif loggerlevel == "CRITICAL":
            logger.setLevel(logging.CRITICAL)
            
    # This class sets the level of the filehandler that the user wants
    def fileHandlerSetter(self,classname,file_handler_level):
        fileHandlerList = []
        if file_handler_level == 1:
            file_handler1 = logging.FileHandler(self.HANDLER_PATH+classname+"_debug.log", mode = 'w')
            file_handler1.setLevel(logging.DEBUG)
            file_handler1.setFormatter(self.formatter)
            return file_handler1
        elif file_handler_level == 2:
            fileHandlerList.append(logging.FileHandler(self.HANDLER_PATH+classname+"_debug.log", mode = 'w'))
            fileHandlerList[0].setLevel(logging.DEBUG)
            fileHandlerList[0].setFormatter(self.formatter)
            fileHandlerList.append(logging.FileHandler(self.HANDLER_PATH+classname+"_info.log", mode = 'w'))
            fileHandlerList[1].setLevel(logging.INFO)
            fileHandlerList[1].setFormatter(self.formatter)
            return fileHandlerList
        elif file_handler_level == 3:
            fileHandlerList.append(logging.FileHandler(self.HANDLER_PATH+classname+"_debug.log", mode = 'w'))
            fileHandlerList[0].setLevel(logging.DEBUG)
            fileHandlerList[0].setFormatter(self.formatter)
            fileHandlerList.append(logging.FileHandler(self.HANDLER_PATH+classname+"_info.log", mode = 'w'))
            fileHandlerList[1].setLevel(logging.INFO)
            fileHandlerList[1].setFormatter(self.formatter)
            fileHandlerList.append(logging.FileHandler(self.HANDLER_PATH+classname+"_warning.log", mode = 'w'))
            fileHandlerList[2].setLevel(logging.WARNING)
            fileHandlerList[2].setFormatter(self.formatter)
            return fileHandlerList
        elif file_handler_level == 4:
            fileHandlerList.append(logging.FileHandler(self.HANDLER_PATH+classname+"_debug.log", mode = 'w'))
            fileHandlerList[0].setLevel(logging.DEBUG)
            fileHandlerList[0].setFormatter(self.formatter)
            fileHandlerList.append(logging.FileHandler(self.HANDLER_PATH+classname+"_info.log", mode = 'w'))
            fileHandlerList[1].setLevel(logging.INFO)
            fileHandlerList[1].setFormatter(self.formatter)
            fileHandlerList.append(logging.FileHandler(self.HANDLER_PATH+classname+"_warning.log", mode = 'w'))
            fileHandlerList[2].setLevel(logging.WARNING)
            fileHandlerList[2].setFormatter(self.formatter)
            fileHandlerList.append(logging.FileHandler(self.HANDLER_PATH+classname+"_error.log", mode = 'w'))
            fileHandlerList[3].setLevel(logging.ERROR)
            fileHandlerList[3].setFormatter(self.formatter)
            return fileHandlerList
        elif file_handler_level == 5:
            fileHandlerList.append(logging.FileHandler(self.HANDLER_PATH+classname+"_debug.log", mode = 'w'))
            fileHandlerList[0].setLevel(logging.DEBUG)
            fileHandlerList[0].setFormatter(self.formatter)
            fileHandlerList.append(logging.FileHandler(self.HANDLER_PATH+classname+"_info.log", mode = 'w'))
            fileHandlerList[1].setLevel(logging.INFO)
            fileHandlerList[1].setFormatter(self.formatter)
            fileHandlerList.append(logging.FileHandler(self.HANDLER_PATH+classname+"_warning.log", mode = 'w'))
            fileHandlerList[2].setLevel(logging.WARNING)
            fileHandlerList[2].setformatter(self.formatter)
            fileHandlerList.append(logging.FileHandler(self.HANDLER_PATH+classname+"_error.log", mode = 'w'))
            fileHandlerList[3].setLevel(logging.ERROR)
            fileHandlerList[3].setformatter(self.formatter)
            fileHandlerList.append(logging.FileHandler(self.HANDLER_PATH+classname+"_critical.log", mode = 'w'))
            fileHandlerList[4].setLevel(logging.CRITICAL)
            fileHandlerList[4].setformatter(self.formatter)
            return fileHandlerList
        
    # This function creates a logger worker
    # it takes the name of the class, the logger level, and file handler level
    # It then creates a logger using those set configurations
    def createLoggerWorker(self,classname,loggerlevel,file_handler_level):
        logger = logging.getLogger(classname)
        self.setLoggerLevel(logger,loggerlevel)
        
        file_handler = self.fileHandlerSetter(classname, file_handler_level)
        
        if type(file_handler) is list:
            for i in range(len(file_handler)):
                logger.addHandler(file_handler[i])
        else:
            logger.addHandler(file_handler)

        return logger
        
        