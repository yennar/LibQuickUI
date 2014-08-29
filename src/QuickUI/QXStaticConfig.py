#!/usr/bin/python

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from QXApplication import QXApplication

import platform
import sys
import re
import quick_ui_res
import json

class QXCheckBox(QCheckBox):
    
    checkedChanged = pyqtSignal(bool)
    
    def __init__(self,text,init,parent = None):
        QCheckBox.__init__(self,parent)
        self.setTristate(False)
        self.stateChanged.connect(self.onStateChange)
        self.setText(text)
        self.setChecked(init)
        
    def onStateChange(self,s):
        b = False
        if s > 0:
            b = True
        self.checkedChanged.emit(b)

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
        if platform.system() == 'Darwin':
            c.setOption(QFontDialog.NoButtons)
            c.currentFontChanged.connect(self.onFontChange)
        if c.exec_():
            self.onFontChange(c.selectedFont())
        

    
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
        if platform.system() == 'Darwin':
            c.setOption(QColorDialog.NoButtons)
            c.currentColorChanged.connect(self.onColorChange)
        if c.exec_():
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


class QXSelects(QWidget):
    optionsChanged = pyqtSignal(list)

    SUB_TYPE_CHECKBOX = 1
    SUB_TYPE_RADIO    = 2
    SUB_TYPE_COMBO    = 3
    
    def __init__(self,init,sub_type = SUB_TYPE_CHECKBOX,parent = None):
        QWidget.__init__(self,parent)
        
        self.chk = {}
        self.init = init
        self.sub_type = sub_type
        
        l = QVBoxLayout()
        l.setMargin(0)

        if sub_type == self.SUB_TYPE_COMBO:
            cbx = QComboBox(parent)

        cbx_init_index = 0
        
        for i,item in enumerate(init):
            if sub_type == self.SUB_TYPE_COMBO:
                cbx.addItem(item[0],item[1])  
                if item[2]:
                    cbx_init_index = i
            else:
                
                if sub_type == self.SUB_TYPE_RADIO:
                    chk = QRadioButton(item[0])
                else:
                    chk = QCheckBox(item[0])
                chk.setChecked(item[2])
                self.chk[item[1]] = chk
                
                l.addWidget(chk)
                chk.clicked.connect(self.onCheckChange)
                
        if sub_type == self.SUB_TYPE_COMBO:
            l.addWidget(cbx)
            cbx.setCurrentIndex(cbx_init_index)
            cbx.currentIndexChanged.connect(self.onCurrentIndexChanged)
        self.setLayout(l)
    
    def onCurrentIndexChanged(self,index):
        for i,item in enumerate(self.init):
            if i == index:
                self.init[i][2] = True
            else:
                self.init[i][2] = False
        self.optionsChanged.emit(self.init)
        
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
    YesNo = 8
    List = 9
    
    def __init__(self,parent = None):
        QMainWindow.__init__(self,parent)
        
        self.tbrMain = self.addToolBar("Main")
        self.tbrMain.setFloatable(False)
        self.tbrMain.setMovable(False)
        self.actions = []
        self.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        self.mainWidget = QStackedWidget() 
        
        if platform.system == 'Darwin':                   
            self.setCentralWidget(self.mainWidget)
        else:
            self.btns = QDialogButtonBox()
            self.btnExport = self.btns.addButton("Export...",QDialogButtonBox.ActionRole)
            self.btnImport = self.btns.addButton("Import...",QDialogButtonBox.ActionRole)
            self.btnRestoreDefaults = self.btns.addButton(QDialogButtonBox.RestoreDefaults)
            self.btnClose = self.btns.addButton(QDialogButtonBox.Close)

            self.btns.clicked.connect(self.onDlgBtnBoxClicked)
            
            self.central = QWidget()
            lay = QVBoxLayout()
            lay.addWidget(self.mainWidget)
            lay.addWidget(self.btns)
            self.central.setLayout(lay)
            self.setCentralWidget(self.central)
        
        
        
        self.pageID = 0
        self.setUnifiedTitleAndToolBarOnMac(True)   
        self.setMinimumWidth(640)
        self.setMinimumHeight(480)
        #self.resize(640,480)
        
        if QApplication.organizationName() == '':
            QApplication.setOrganizationName('TinyUtils')
        
        if QApplication.applicationName() == '':
            QApplication.setApplicationName(QXApplication.appName())
            
        appName = QApplication.applicationName()
        
        if QDir(QDir.currentPath()).exists("%s.rc" % appName):
            self.settings = QSettings("%s/%s.rc" % (QDir.currentPath(),appName),QSettings.IniFormat)
        else:
            self.settings = QSettings()
        
        self.confs = []
        self.pages = []

    def onDlgBtnBoxClicked(self,btn):
        if btn == self.btnExport:
            self.doExport()
        elif btn == self.btnImport:
            self.doImport()
        elif btn == self.btnRestoreDefaults:
            self.doReset()
        elif btn == self.btnClose:
            self.close()

    def doReload(self):
        for i,conf in enumerate(self.confs):
            self.setupConfigPage(conf, i)

    def doReset(self):
        self.settings.clear()
        self.settings.sync()
        self.doReload()

    def doExport(self):

        file_export = QFileDialog.getSaveFileName(self,"Export",QDir.currentPath(),"Configuration (*.ini);; All Files (*.*)")
        if not file_export is None and file_export != '':
            settings = QSettings(file_export,QSettings.IniFormat,self)
            for k in self.settings.allKeys():
                settings.setValue(k,self.settings.value(k))
            settings.sync()
        
    def doImport(self):

        file_import = QFileDialog.getOpenFileName(self,"Export",QDir.currentPath(),"Configuration (*.ini);; All Files (*.*)")
        if not file_import is None and file_import != '' and QDir().exists(file_import):
            settings = QSettings(file_import,QSettings.IniFormat,self)
            for k in settings.allKeys():
                self.settings.setValue(k,settings.value(k))
            self.settings.sync()        
            self.doReload()
            
    def doClose(self):
        self.close()
        
    def cloOnAction(self,page_id):
        def onAction():
            self.mainWidget.setCurrentIndex(page_id)
        return onAction
    
    def cloGetActionSetIcon(self,page_id):
        def setIcon(icon):
            self.actions[page_id].setIcon(icon)
        return setIcon
    
    def addConfigPage(self,conf):
        
        page = QWidget()
        self.confs.append(conf)
        self.pages.append(page)
        
        action = QAction(conf['icon'],conf['title'],self,triggered = self.cloOnAction(self.pageID))
        self.tbrMain.addAction(action)
        self.actions.append(action)
        self.setupConfigPage(conf, self.pageID)
        self.mainWidget.addWidget(page)
        self.pageID += 1
        
        
    def setupConfigPage(self,conf,pageID):
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

        
        
        group_items = conf['items']
        page = self.pages[pageID]
        self.mainWidget.removeWidget(page)
        page.deleteLater()
        page = QWidget()
        self.mainWidget.insertWidget(pageID,page)
        
        self.pages[pageID] = page
        
        if len(group_items) == 1:         
            lay_groups = self.createGroup("%d-0-%s" % ( pageID , conf['title'] ),group_items[0],page)
            page.setLayout(lay_groups)
        else:
            pagex = QTabWidget()
            for i,item in enumerate(group_items):
                sub_page = QWidget()
                lay_groups = self.createGroup("%d-%d-%s" % ( pageID , i , conf['title'] ),item,sub_page)              
                sub_page.setLayout(lay_groups)
                pagex.addTab(sub_page,item['group_title'])
                     

            lay = QHBoxLayout()  
            lay.addWidget(pagex)
            page.setLayout(lay)            
                
        
    
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
                elif item['item_type'] == self.YesNo:
                    try:
                        d = item['item_default']
                    except:
                        d = False
                    d = self.settings.value(key_item,d).toBool()
                    
                    widget = QXCheckBox(item['item_title'],d,group)

                    item['call_back'](d) 
                    widget.checkedChanged.connect(item['call_back'])
                    widget.checkedChanged.connect(self.cloSync(key_item,'str'))
                    lay_group.addWidget(widget,index,0,1,2)
                    index += 1
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
                elif item['item_type'] == self.Options or item['item_type'] == self.Selection or item['item_type'] == self.List:
                    try:
                        d = item['item_default']
                    except:
                        try:
                            d = item['item_data']
                        except:
                            d = []
                    name_dict = str(self.settings.value(key_item,d).toString())
                    if name_dict != '':
                        ds = json.loads(name_dict)
                    else:
                        ds = []

                    if len(d) != len(ds):
                        try:
                            ddict = {}
                            for item_d in ds:
                                ddict[item_d[0] + item_d[1]] = item_d[2]
                            nd = []
                            for item_d in d:
                                key = item_d[0] + item_d[1]
                                if key in ddict.keys():
                                    item_d[2] = ddict[key]
                                nd.append(item_d)
                            d = nd
                        except:
                            pass
                    
                    sub_type = QXSelects.SUB_TYPE_CHECKBOX
                    if item['item_type'] == self.Selection:
                        sub_type = QXSelects.SUB_TYPE_RADIO
                    elif item['item_type'] == self.List:
                        sub_type = QXSelects.SUB_TYPE_COMBO
                        
                    widget = QXSelects(d,sub_type,self)
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
            {'group_title' : 'group1', 'items' : []},
            {'group_title' : 'group2' , 'items' : [
                {'section_title' : 'foo', 'items' : [
                    {'item_title' : 'Name', 'item_type' : QXStaticConfig.Text, 'call_back' : w.nullCallback },
                    {'item_title' : 'May', 'item_type' : QXStaticConfig.YesNo, 'call_back' : w.nullCallback },
                    {'item_title' : 'Edu', 'item_type' : QXStaticConfig.Options,'item_default' : [
                             ['Prim School','optPrim',True],
                             ['Mid School','optMid',False],
                        ], 'call_back' : w.nullCallback },
                    {'item_title' : 'Adv Edu', 'item_type' : QXStaticConfig.Selection,'item_default' : [
                             ['Prim School','optPrim',True],
                             ['Mid School','optMid',False],
                        ], 'call_back' : w.nullCallback },
                    {'item_title' : 'Adv Edu', 'item_type' : QXStaticConfig.List,'item_default' : [
                             ['Prim School','optPrim',True],
                             ['Mid School','optMid',False],
                        ], 'call_back' : w.nullCallback }                    
                    ]},
                {'section_title' : 'bar', 'items' : []}
            ]}
        ]})    
    
    w.show()
    app.exec_()
