#!/usr/bin/python

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from QXApplication import QXApplication

import platform
import sys
import re
import quick_ui_res
import json

class QXFontSelector(QLineEdit):
    fontChanged = pyqtSignal(QFont)
    
    def __init__(self,font,parent = None):
        QLineEdit.__init__(self,parent)
        self.font = font
        self.setReadOnly(True)
        self.setText("%s (Click to change)" % (font.toString()))              
        self.setFont(font)

    def onFontChange(self,font):
        self.font = font
        self.setFont(font)
        self.setText("%s (Click to change)" % (font.toString())) 
        self.fontChanged.emit(font)
    
    def mouseReleaseEvent(self,e):
        c = QFontDialog(self.font,self)
        c.setWindowTitle("Get Font")
        c.setOption(QFontDialog.NoButtons)
        c.currentFontChanged.connect(self.onFontChange)
        c.exec_()
        self.onFontChange(self.font)
        

    
class QXColorSelector(QLineEdit):
    
    colorChanged = pyqtSignal(QColor)
    
    def __init__(self,color,parent = None):
        QLineEdit.__init__(self,parent)
        self.color = color
        self.setReadOnly(True)
        self.setText("#%02X%02X%02X (Click to change)" % (color.red(),color.green(),color.blue()))              
        self.paint()

    def onColorChange(self,color):
        self.color = color
        self.paint()
        self.colorChanged.emit(color)
    
    def mouseReleaseEvent(self,e):
        c = QColorDialog(self.color,self)
        c.setWindowTitle("Get Color")
        c.setOption(QColorDialog.NoButtons)
        c.currentColorChanged.connect(self.onColorChange)
        c.exec_()
        self.onColorChange(c.currentColor())
        
    def paint(self):
        color = self.color
        self.setStyleSheet(
            "QLineEdit { background-color : #%02X%02X%02X ; color : #%02X%02X%02X; }" % (
                color.red(),
                color.green(),
                color.blue(),
                255 - color.red(),
                255 - color.green(),
                255 - color.blue(),                
                ))
        

class QXFileSelector(QWidget):
    fileChanged = pyqtSignal(str)
    def __init__(self,init,path_or_file,file_filter,parent = None):
        QWidget.__init__(self,parent)
        self.init = init
        self.edt = QLineEdit(init)
        self.edt.textChanged.connect(self.onFileChanged)
        self.btn = QPushButton("Select")
        self.path_or_file = path_or_file
        self.file_filter = file_filter
        self.btn.clicked.connect(self.onButton)
        
        l = QHBoxLayout()
        l.setMargin(0)
        l.setSpacing(2)
        l.addWidget(self.edt)
        l.addWidget(self.btn)
        self.setLayout(l)
        
    def onFileChanged(self,fileName):
        d = QDir(QDir.currentPath())        
        if d.exists(fileName):
            self.fileChanged.emit(fileName)
            
    def onButton(self):
        d = QDir(QDir.currentPath())
        if d.exists(self.edt.text()):
            self.init = self.edt.text()
            fi = QFileInfo(self.init)
            self.path_or_file = fi.isDir()

        if self.path_or_file:
            #path
            d = QDir(self.init)
            d.cdUp()
            #print d.absolutePath()
            fileName = QFileDialog.getExistingDirectory(self,"Select Directory",d.absolutePath())  
        else:
            #print self.init
            d = QFileInfo(self.init).path()
            fileName = QFileDialog.getOpenFileName(self,"Select File",d,self.file_filter)
        if not fileName is None and fileName != "":
            self.edt.setText(fileName)


class QXCheckBoxes(QWidget):
    optionsChanged = pyqtSignal(list)
    def __init__(self,init,radio = False,parent = None):
        QWidget.__init__(self,parent)
        
        self.chk = {}
        self.init = init
        self.radio = radio
        
        l = QVBoxLayout()
        l.setMargin(0)
        
        for item in init:
            if radio:
                chk = QRadioButton(item[0])
            else:
                chk = QCheckBox(item[0])
            chk.setChecked(item[2])
            self.chk[item[1]] = chk
            
            l.addWidget(chk)
            chk.clicked.connect(self.onCheckChange)
            
        self.setLayout(l)
            
    def onCheckChange(self):
        for i,item in enumerate(self.init):
            chk = self.chk[item[1]]
            self.init[i][2] = chk.isChecked()
        self.optionsChanged.emit(self.init)
            

class QXStaticConfig(QMainWindow):
    
    Text = 1
    Range = 2 
    Color = 3
    Font = 4
    File = 5
    Options = 6
    Selection = 7
    
    def __init__(self,parent = None):
        QMainWindow.__init__(self,parent)
        
        self.tbrMain = self.addToolBar("Main")
        self.mainWidget = QStackedWidget()        
        self.setCentralWidget(self.mainWidget)
        self.pageID = -1
        self.setUnifiedTitleAndToolBarOnMac(True)   
        self.resize(640,480)
        
        if QApplication.organizationName() == '':
            QApplication.setOrganizationName('TinyUtils')
        
        if QApplication.applicationName() == '':
            QApplication.setApplicationName(QXApplication.appName())
            
        appName = QApplication.applicationName()
        
        if QDir(QDir.currentPath()).exists("%s.rc" % appName):
            self.settings = QSettings("%s/%s.rc" % (QDir.currentPath(),appName),QSettings.IniFormat)
        else:
            self.settings = QSettings()
        
    def cloOnAction(self,page_id):
        def onAction():
            self.mainWidget.setCurrentIndex(page_id)
        return onAction
        
    def addConfigPage(self,conf):
        """
        conf = {
            'title' : str
            'icon'  : QIcon
            'items' : [
                {
                     'group_title' : str
                     'items' : [
                          {
                               'section_title' : str
                               'items' : [
                                    {
                                         'item_title' : str
                                         'item_type'  : QXStaticConfig.Text | QXStaticConfig.Range | QXStaticConfig.Color |
                                                        QXStaticConfig.Font | QXStaticConfig.File | QXStaticConfig.Options | 
                                                        QXStaticConfig.Selection 
                                         'item_data'  : var
                                         'item_default' : str
                                         'call_back'  : code
                                    }                               
                               ]
                          }
                     ]
                }
            ]
        }
        """
        self.pageID += 1
        
        action = QAction(conf['icon'],conf['title'],self,triggered = self.cloOnAction(self.pageID))
        self.tbrMain.addAction(action)
        
        
        group_items = conf['items']

        if len(group_items) == 1:
            
            page = QWidget()
            lay_groups = self.createGroup(conf['title'],group_items[0],page)
            page.setLayout(lay_groups)
        else:
            pagex = QTabWidget()
            for item in group_items:
                sub_page = QWidget()
                lay_groups = self.createGroup(conf['title'],item,sub_page)                
                sub_page.setLayout(lay_groups)
                pagex.addTab(sub_page,item['group_title'])
            lay = QHBoxLayout()
            lay.addWidget(pagex)
            page = QWidget()
            page.setLayout(lay)            
                
        self.mainWidget.addWidget(page)
    
    def cloSync(self,key,typ):
        def onSync(*kargs):
            if typ == 'str':
                self.settings.setValue(key,kargs[0])
            if typ == 'dict':
                self.settings.setValue(key,json.dumps(kargs[0]))
                
            self.settings.sync()
        return onSync
    
    def createGroup(self,key,conf_group_item,parent):
        lay = QVBoxLayout()

        for section in conf_group_item['items']:
            lay_group = QGridLayout()
            group = QGroupBox(section['section_title'],parent)
            index = 0
            key_sec = key + '/' + section['section_title']
            for item in section['items']:
                label = QLabel(item['item_title'])
                label.setAlignment(Qt.AlignLeft)
                key_item = key_sec + '/' + item['item_title']
                
                if item['item_type'] == self.Text:
                    try:
                        d = item['item_default']
                    except:
                        d = ''
                    d = str(self.settings.value(key_item,d).toString())
                    try:
                        passwd = item['item_data'][0]
                    except:
                        passwd = False

                    widget = QLineEdit(d,group)
                    if passwd:
                        widget.setEchoMode(QLineEdit.Password)
                    item['call_back'](d)    
                    widget.textChanged.connect(item['call_back'])
                    widget.textChanged.connect(self.cloSync(key_item,'str'))
                    lay_group.addWidget(label,index,0)
                    lay_group.addWidget(widget,index + 1,0,1,2)
                    index += 2
                elif item['item_type'] == self.Range:
                    try:
                        d = int(item['item_default'])
                    except:
                        d = 0
                    d = self.settings.value(key_item,d).toInt()[0]
                    try:
                        vmin = item['item_data'][0]
                        vmax = item['item_data'][1]
                    except:
                        vmin = 0
                        vmax = 0
                        
                    try:
                        dec = item['item_data'][2]
                    except:
                        dec = 4
                        
                    widget = QSpinBox(group)
                    widget.setRange(vmin,vmax)
                    widget.setValue(d)
                    #widget.setValidator(QValidator(vmin,vmax,4,widget))
                    item['call_back'](d) 
                    widget.valueChanged.connect(item['call_back'])
                    widget.valueChanged.connect(self.cloSync(key_item,'str'))
                    lay_group.addWidget(label,index,0)
                    lay_group.addWidget(widget,index + 1,0,1,2)
                    index += 2
                elif item['item_type'] == self.Color:
                    try:
                        d = item['item_default']
                    except:
                        d = QColor(0,0,0)
                    name_color = self.settings.value(key_item,d.name()).toString()
                    d.setNamedColor(name_color)
                    widget = QXColorSelector(d,group)
                    widget.colorChanged.connect(self.cloSync(key_item,'str'))
                    widget.colorChanged.connect(item['call_back'])
                    item['call_back'](d) 
                    lay_group.addWidget(label,index,0)
                    lay_group.addWidget(widget,index + 1,0,1,2)
                    index += 2
                elif item['item_type'] == self.Font:
                    try:
                        d = item['item_default']
                    except:
                        d = QApplication.font()
                    name_font = self.settings.value(key_item,d.toString()).toString()
                    d.fromString(name_font)
                    widget = QXFontSelector(d,group)
                    widget.fontChanged.connect(self.cloSync(key_item,'str'))
                    widget.fontChanged.connect(item['call_back'])
                    item['call_back'](d) 
                    lay_group.addWidget(label,index,0)
                    lay_group.addWidget(widget,index + 1,0,1,2)
                    index += 2  
                elif item['item_type'] == self.File:
                    try:
                        d = item['item_default']
                    except:
                        d = QDir.currentPath()
                    d = str(self.settings.value(key_item,d).toString())
                    path_or_file = False    
                    try:
                        flt = item['item_data']
                        if flt == '/':
                            path_or_file = True
                    except:
                        flt = "All Files (*.*)"

                    widget = QXFileSelector(d,path_or_file,flt,group)
                    widget.fileChanged.connect(self.cloSync(key_item,'str'))
                    widget.fileChanged.connect(item['call_back'])
                    item['call_back'](d) 
                    lay_group.addWidget(label,index,0)
                    lay_group.addWidget(widget,index + 1,0,1,2)
                    index += 2   
                elif item['item_type'] == self.Options or item['item_type'] == self.Selection:
                    try:
                        d = item['item_default']
                    except:
                        try:
                            d = item['item_data']
                        except:
                            d = []
                    name_dict = str(self.settings.value(key_item,d).toString())
                    if name_dict != '':
                        d = json.loads(name_dict)
                    
                    radio = False
                    if item['item_type'] == self.Selection:
                        radio = True
                        
                    widget = QXCheckBoxes(d,radio,self)
                    widget.optionsChanged.connect(self.cloSync(key_item,'dict'))
                    widget.optionsChanged.connect(item['call_back'])
                    item['call_back'](d)
                    lay_group.addWidget(label,index,0)
                    lay_group.addWidget(widget,index + 1,0,1,2)
                    index += 2                     
            lay_group_wrap = QVBoxLayout()
            lay_group_wrap.addLayout(lay_group)
            lay_group_wrap.addStretch()
            group.setLayout(lay_group_wrap)
            lay.addWidget(group)
        return lay
    
    def nullCallback(self,*kargs):
        print kargs
    
if __name__ == '__main__':    
    app = QApplication(sys.argv)
    #w = QXColorSelector(QColor(123,45,6))
    
    w = QXStaticConfig()
    
    w.addConfigPage({
        'title' : 'foo',
        'icon'  : QIcon(':/copy.png'),
        'items' : [{'group_title' : 'bar' , 'items' : [
            {'section_title' : 'foo', 'items' : [
                {'item_title' : 'Money', 'item_type' : QXStaticConfig.Range, 'item_data' : [2,100], 'call_back' : w.nullCallback },
                {'item_title' : 'Door', 'item_type' : QXStaticConfig.Color, 'item_default' : QColor(255,128,4), 'call_back' : w.nullCallback },
                {'item_title' : 'DoorFont', 'item_type' : QXStaticConfig.Font, 'item_default' : QApplication.font(), 'call_back' : w.nullCallback },
                {'item_title' : 'App', 'item_type' : QXStaticConfig.File, 'item_default' : sys.argv[0],'item_data' : 'All Files (*.*)', 'call_back' : w.nullCallback },
                {'item_title' : 'Path', 'item_type' : QXStaticConfig.File, 'item_default' : '.','item_data' : '/', 'call_back' : w.nullCallback },
            ]}
        ]}]
    })

    w.addConfigPage({
        'title' : 'bar',
        'icon'  : QIcon(':/paste.png'),
        'items' : [
            {'group_title' : 'bar', 'items' : []},
            {'group_title' : 'car' , 'items' : [
                {'section_title' : 'foo', 'items' : [
                    {'item_title' : 'Name', 'item_type' : QXStaticConfig.Text, 'call_back' : w.nullCallback },
                    {'item_title' : 'Edu', 'item_type' : QXStaticConfig.Options,'item_default' : [
                             ['Prim School','optPrim',True],
                             ['Mid School','optMid',False],
                        ], 'call_back' : w.nullCallback },
                    {'item_title' : 'Adv Edu', 'item_type' : QXStaticConfig.Selection,'item_default' : [
                             ['Prim School','optPrim',True],
                             ['Mid School','optMid',False],
                        ], 'call_back' : w.nullCallback },
                    {'item_title' : 'Adv Edu', 'item_type' : QXStaticConfig.Selection,'item_default' : [
                             ['Prim School','optPrim',True],
                             ['Mid School','optMid',False],
                        ], 'call_back' : w.nullCallback }                     
                    ]},
                {'section_title' : 'bar', 'items' : []}
            ]}
        ]})    
    
    w.show()
    app.exec_()
