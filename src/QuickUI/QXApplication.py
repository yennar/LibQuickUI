#!/usr/bin/python

from PyQt4.QtCore import *
from PyQt4.QtGui import *
import platform
import sys
import re
import json

class QXApplication(QApplication):
    def __init__(self,*kargs):
        QApplication.__init__(self,*kargs)
        
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

        
        