#!/usr/bin/python

from PyQt4.QtCore import *
from PyQt4.QtGui import *
import quick_ui_res
import json
import platform
import re

class QXThemeManager(QWidget):
    def __init__(self,parent = None):
        QWidget.__init__(self,parent)
        self.settings = QSettings()
        self.selected_theme = 'default'
        self.selected_theme_path = ''
        self.icon_db = None
        self.getIconThemeList()
        self.callbacks = {}
        
        #self.defaultStyleName = QApplication.style().metaObject().className()
        #print self.defaultStyleName
        
        
    def findIcon(self,iconName,sizeSpec='default',callback=None):
        #print "findInon",iconName
        if not callback is None:
            if not iconName in self.callbacks.keys():
                self.callbacks[iconName] = []
            self.callbacks[iconName].append(callback)
        
        if self.icon_db is None or self.selected_theme_path == '':
            #print "Use compability icon"
            return QIcon(':%s.png' % str(iconName).lower())

        theme_path = QDir(self.selected_theme_path)
        
        if not theme_path.exists(sizeSpec):
            for sizeSpec in theme_path.entryList(QDir.AllDirs | QDir.NoDotAndDotDot):
                if sizeSpec == '32x32' or sizeSpec == 'default':
                    break
                
        if not theme_path.exists(sizeSpec):
            for sizeSpec in theme_path.entryList(QDir.AllDirs | QDir.NoDotAndDotDot):
                if sizeSpec == '16x16' or sizeSpec == '48x48':
                    break
        
        icon_name_alias = [iconName]
        if iconName == 'configure':
            icon_name_alias.append('references')
            icon_name_alias.append('reference')
                
        for iconName in icon_name_alias:
            for d in [QDir(self.selected_theme_path + '/' + sizeSpec),
                      QDir(self.selected_theme_path + '/' + sizeSpec + '/actions'),
                      QDir(self.selected_theme_path + '/' + sizeSpec + '/categories')]:
                #print d.absolutePath(),iconName
                for picName in d.entryList(['%s.png' % str(iconName).lower()]):
                    #print "Find",picName
                    return QIcon(d.absolutePath() + '/' + picName) 
                for cato in ['document','edit']:
                    for picName in d.entryList(['%s-%s.png' % (cato,str(iconName).lower())]):
                        #print "Find",picName
                        return QIcon(d.absolutePath() + '/' + picName)             
        
                for picName in d.entryList(['*-%s.png' % str(iconName).lower()]):
                    #print "Find",picName
                    return QIcon(d.absolutePath() + '/' + picName)         
                for picName in d.entryList(['*%s*' % str(iconName).lower()]):
                    #print "Find",picName
                    return QIcon(d.absolutePath() + '/' + picName)

        return QIcon()

    def setIconTheme(self,d):
        for item in d:
            if item[2]:
                self.selected_theme = item[0]
                self.selected_theme_path = item[1]
                break
        for item in self.callbacks:
            funcs = self.callbacks[item]
            for func in funcs:
                func(self.findIcon(item))
            
    def getIconThemeList(self):
        if self.icon_db is None:
            
            possible_icon_path = [
                '/usr/share/icons',
                ':/usr/share/icons',
                './usr/share/icons',
                './icons',
                QApplication.applicationDirPath() + '/icons',
                QDesktopServices.storageLocation(QDesktopServices.PicturesLocation) + '/icons',
                QDesktopServices.storageLocation(QDesktopServices.HomeLocation) + '/icons',
                QDesktopServices.storageLocation(QDesktopServices.HomeLocation) + '/share/icons'
            ]
            for icon_path in possible_icon_path:
                #print 'Try %s' % icon_path
                iconPath = QFileInfo(icon_path)
                if iconPath.exists() and iconPath.isDir(): 
                    #print 'Search %s' % icon_path
                    iconPath = QDir(icon_path)
                    themeRoots = iconPath.entryInfoList(QDir.AllDirs | QDir.NoDotAndDotDot | QDir.Readable)
                    for themeRoot in themeRoots:
                        theme_name = themeRoot.fileName()
                        #print '%s exists' % theme_name
                        themeDir = QDir(themeRoot.filePath())
                        if themeDir.exists('index.theme') or themeDir.exists('index.theme.in'):
                            #print 'index.theme exists'
                            if self.icon_db is None:
                                self.icon_db = {}
                            self.icon_db[str(theme_name)] = str(themeRoot.filePath())
            #print self.icon_db
        rsj = str(self.settings.value('0-0-General/Theme/Icon Theme','').toString())
        #print rsj
        rsj_db = {}
        if rsj != '':
            try:
                rsj_p = json.loads(rsj)
                for item in rsj_p:
                    k = str(item[0] + '-' + item[1])
                    rsj_db[k] = item[2]
                    #print k,len(k)
            except:
                pass
        #print rsj_db
        r = []
        for item in self.icon_db:
            t = False
            k = item + '-' + self.icon_db[item]
            #print "?",k,len(k),
            if k in rsj_db.keys() and rsj_db[k]:
                t = True
                self.selected_theme = item
                #print "Select Icon Theme",item
                                
        for item in self.icon_db:        
            t = False
            if item == self.selected_theme:
                t = True
                self.selected_theme_path = self.icon_db[item]
            r.append([item,self.icon_db[item],t])
        #print r
        return r
    
    def getStyleList(self):
        styleList = QStyleFactory.keys()
        rsj = str(self.settings.value('0-0-General/Theme/Style','').toString())
        #print rsj
        rsj_db = {}
        if rsj != '':
            try:
                rsj_p = json.loads(rsj)
                for item in rsj_p:
                    k = str(item[0])
                    rsj_db[k] = item[2]
                    #print k,len(k)
            except:
                pass        
        r = []
        use_default = True
        for item in styleList:
            t = False
            k = str(item)
            if k in rsj_db.keys() and rsj_db[k]:
                t = True
                use_default = False
                QApplication.setStyle(QStyleFactory.create(k))             
            item = str(item)
            r.append([item,item,t])
        default_style_key = self.getDefaultSystemStyle()    
        r.append(['System (%s)' % default_style_key,default_style_key,use_default])
        #print r
        return r    
    
    def setStyle(self,d):
        for item in d:
            if item[2]:
                try:
                    QApplication.setStyle(QStyleFactory.create(item[1]))
                except:
                    pass
                break
            
    def getDefaultSystemStyle(self):
        styleList = QStyleFactory.keys()
        style_keys = []
        if platform.system() == 'Darwin':
            style_keys = ['Mac']
        elif platform.system() == 'Linux':
            style_keys = ['GTK','CDE','Clean']
        elif platform.system() == 'Windows':
            style_keys = ['Vista','Win']
        
        for style_item in styleList:
            for style_key in style_keys:
                if re.match('.*' + style_key + '.*',str(style_item)):
                    return str(style_item)
    
if __name__ == '__main__':
    d = QDir(':/')
    for sd in d.entryList():
        print sd
    