#!/usr/bin/python

from PyQt4.QtCore import *
from PyQt4.QtGui import *
import platform
import sys
import re
import quick_ui_res
import json

class QXAction(QAction):

   
    def __init__(self,*kargs,**kwargs):
        QAction.__init__(self,*kargs,**kwargs)
        kq = QKeySequence.mnemonic(self.text())
        if kq.isEmpty() or platform.system() == 'Windows':
            if self.text().contains('&'):
                t = self.text().replace('&','')
                try:
                    kq = QKeySequence(eval('QKeySequence.%s' % t))
                except:
                    pass
        self.setShortcut(kq)
        
        if not kq.isEmpty():
            self.setToolTip("%s (%s)" % (self.text().replace('&',''),kq.toString(QKeySequence.NativeText)))
        
        image_name = "%s.png" % self.text().replace('&','').toLower()
        dir = QDir(QDir.currentPath());
        if dir.exists(image_name):
            self.setIcon(QIcon(image_name))
        else:
            image_name = ":" + image_name
            if dir.exists(image_name):
                self.setIcon(QIcon(image_name))   