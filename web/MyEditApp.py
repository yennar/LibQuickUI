#!/usr/bin/python

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from QuickUI.QXApplication import *
from QuickUI.QXSingleDocmainWindow import *


import sys
app = QXApplication(sys.argv,'MyEditApp')
w = QXSingleDocMainWindow(QTextEdit())
w.resize(600,400)
w.show()
app.exec_()