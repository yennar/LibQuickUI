#!/usr/bin/python

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from QXAction import *

import platform
import sys
import re
import quick_ui_res
import json

class QXToolBar(QToolBar):
    def __init__(self,parent = None):
        QToolBar.__init__(self,parent)
        
        