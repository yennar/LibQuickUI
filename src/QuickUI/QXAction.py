#!/usr/bin/python

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from QXApplication import *
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
                t = self.text().replace('&','').replace('.','')
                try:
                    kq = QKeySequence(eval('QKeySequence.%s' % t))
                except:
                    pass
        self.setShortcut(kq)
        
        if not kq.isEmpty():
            self.setToolTip("%s (%s)" % (self.text().replace('&','').replace('.',''),kq.toString(QKeySequence.NativeText)))
        
        image_name = self.text().replace('&','').replace('.','').toLower()
        if image_name == 'preferences':
            image_name = 'configure'
        self.setIcon(QXApplication.findIcon(image_name,'default',self.setIcon)) 
                  