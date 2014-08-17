#!/usr/bin/python

from PyQt4.QtCore import *
from PyQt4.QtGui import *
import platform
import sys
import re
import json

_mime_type = 'application/x-qt-windows-mime;value="qspreadsheet_blocks"'

class QXTableView(QTableView):

    beginRemove = pyqtSignal(bool)
    endRemove = pyqtSignal(bool)
    dataChangeMulti = pyqtSignal(list)
    
    def __init__(self,*kargs):
        QTableView.__init__(self,*kargs)
    
       
    def copySelection(self,doCut = False,mode = QClipboard.Clipboard):
        if self.model() is None:
            return
        selction = self.selectionModel()
        indexes = selction.selectedIndexes()
        
        logData = []
        values = []
        clipData = []
        for index in indexes:
            value = self.model().data(index)
            key = "%d,%d" % (index.row(),index.column())
            logData.append({
                'dataSource' : self.model(),
                'key' : key,
                'prev' : value,
                'curv' : ''
            })
            values.append(value)
            clipData.append({
                'r' : index.row(),
                'c' : index.column(),
                'v' : value
            })

        clipBoard = QApplication.clipboard()
        
        mimeData = QMimeData()
        mimeData.setText(",".join(values))
        mimeData.setData(_mime_type,json.dumps(clipData))
        clipBoard.setMimeData(mimeData,mode)
        
        if doCut:
            self.beginRemove.emit(False)
            for index in indexes:
                self.model().setData(index,"")
                self.endRemove.emit(True)
            self.dataChangeMulti.emit(logData)
            
    def cutSelection(self):
        self.copySelection(True)
        
    def pasteSelection(self,mode = QClipboard.Clipboard):
        if self.model() is None:
            return
        selction = self.selectionModel()
        indexes = selction.selectedIndexes()
        
        #start point
        d = -1
        p_r = -1
        p_c = -1
        
        for index in indexes:
            this_d = index.row() + index.column()
            if d == -1 or this_d < d:
                d = this_d
                p_r = index.row()
                p_c = index.column()
            selction.select(index,QItemSelectionModel.Clear)
        
        if d == -1:
            index = selction.currentIndex()
            if not index is None:
                p_r = index.row()
                p_c = index.column()
                d = p_r + p_c
                selction.select(selction.currentIndex(),QItemSelectionModel.Clear)
        
        if d == -1:
            p_r = 0
            p_c = 0
            d = 0
        
        clipBoard = QApplication.clipboard()
        mimeData = QMimeData()
        clipData = []
        
        if mode == QClipboard.Clipboard:
            firstTryMode = QClipboard.Clipboard
            secondTryMode = QClipboard.Selection
        elif mode == QClipboard.Selection:
            firstTryMode = QClipboard.Selection
            secondTryMode = QClipboard.Clipboard            
            
        mimeData = clipBoard.mimeData(firstTryMode)
        if (not mimeData is None) and mimeData.hasFormat(_mime_type):
            clipData = json.loads(str(mimeData.data(_mime_type)))
        else:
            mimeData = clipBoard.mimeData(secondTryMode)
            if (not mimeData is None) and mimeData.hasFormat(_mime_type):
                clipData = json.loads(str(mimeData.data(_mime_type)))
            else:
                mimeData = clipBoard.mimeData(firstTryMode)
                if (not mimeData is None) and mimeData.hasText():
                    clipData = [{
                        'r' : 0,
                        'c' : 0,
                        'v' : mimeData.text()
                    }]
                else:
                    mimeData = clipBoard.mimeData(secondTryMode)
                    if (not mimeData is None) and mimeData.hasText():
                        clipData = [{
                            'r' : 0,
                            'c' : 0,
                            'v' : mimeData.text()
                        }]        
                    else:
                        clipData = []
                    
        

        m_r = -1
        m_c = -1
        
        for item in clipData:
            if m_r == -1 or item['r'] < m_r:
                m_r = item['r']
            if m_c == -1 or item['c'] < m_c:
                m_c = item['c']                
        
        dif_r = p_r - m_r
        dif_c = p_c - m_c
        
        logData = []
        self.beginRemove.emit(False)
        
        
        
        for item in clipData:
            index = self.model().index(item['r'] + dif_r,item['c'] + dif_c,QModelIndex())
            selction.select(index,QItemSelectionModel.Select)
            key = "%d,%d" % (index.row(),index.column())
            logData.append({
                'dataSource' : self.model(),
                'key' : key,
                'prev' : self.model().data(index),
                'curv' : item['v']
            })            
            self.model().setData(index,item['v'])
            self.endRemove.emit(True)
        self.dataChangeMulti.emit(logData)   
        
    def mousePressEvent(self,e):
        if e.button() == Qt.MiddleButton:
            self.pasteSelection(QClipboard.Selection)
        QTableView.mousePressEvent(self,e)
    
    def mouseReleaseEvent(self,e):
        QTableView.mouseReleaseEvent(self,e)
        if e.button() == Qt.LeftButton:
            self.copySelection(False,QClipboard.Selection)
        