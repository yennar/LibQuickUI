#!/usr/bin/python

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from QXThemeManager import *

import platform
import sys
import re
import json



class QXApplication(QApplication):
    
    _themeManager = None
    
    def __init__(self,appArgv,organizationName,appName = ''):
        QApplication.__init__(self,appArgv)
        QApplication.setOrganizationName(organizationName)
        if appName == '':
            appName = QXApplication.appName()
        QApplication.setApplicationName(appName)
        QXApplication._themeManager = QXThemeManager()

    @staticmethod
    def getStyleList(*kargs):
        return QXApplication._themeManager.getStyleList(*kargs)

    @staticmethod
    def getStyleCallBack(*kargs):
        return QXApplication._themeManager.setStyle
    
    @staticmethod
    def findIcon(*kargs):
        return QXApplication._themeManager.findIcon(*kargs)

    @staticmethod
    def getIconThemeList(*kargs):
        return QXApplication._themeManager.getIconThemeList(*kargs)

    @staticmethod
    def getIconThemeCallBack(*kargs):
        return QXApplication._themeManager.setIconTheme
    
    @staticmethod
    def themeManager():
        return QXApplication._themeManager
    
    @staticmethod
    def appName():
        appName = re.sub(r'^.*[\/\\]','',sys.argv[0])
        return re.sub(r'\..*$','',appName)
    
    @staticmethod
    def invokeSelf(args = []):
        appExec = QCoreApplication.applicationFilePath()
        appFile = sys.argv[0]
        executeName = ''
        #print platform.system(),appExec,appFile
        if platform.system() == 'Darwin' or platform.system() == 'Linux':
            appExecDir = QDir(appExec)
            if appExecDir.dirName().toLower() == 'python':
                # The script is executed by python
                executeName = "\"%s\" \"%s\"" % (appExec,appFile)
            else:
                executeName = "\"%s\"" %appExec
        elif platform.system() == 'Windows':
            appExecDir = QDir(appExec)
            if appExecDir.dirName().toLower() == 'python.exe' or appExecDir.dirName().toLower() == 'pythonw.exe':
                # The script is executed by python
                executeName =  "\"%s\" \"%s\"" % (appExec,appFile)
            else:
                executeName = "\"%s\"" %appExec
        QProcess.startDetached(executeName + ' ' + " ".join(args))

        
        