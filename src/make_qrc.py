#!/usr/bin/python

from PyQt4.QtCore import *

import sys,os,re

try:
    res_path = sys.argv[1]
    output_file = sys.argv[2]
except:
    print "Usage: %s [res_path] [output_file]" % sys.argv[0]
    exit()

iconRoot = QDir(res_path + '/usr/share/icons/')
FilterDir = QDir.AllDirs | QDir.NoDotAndDotDot | QDir.Readable

fout = QFile(output_file)
if not fout.open(QIODevice.WriteOnly):
    print "Cannot open %s for write" % output_file
    exit()

fout.write("<!DOCTYPE RCC><RCC version=\"1.0\">\n<qresource>\n")

compatibility_items = {}

for themeEntry in iconRoot.entryInfoList(FilterDir):
    theme_name = themeEntry.fileName()
    theme_qrc_path = themeEntry.filePath()
    # print theme_name,theme_qrc_path
    themeRoot = QDir(themeEntry.filePath())
    default_size_name = ''
    default_size_qrc_path = ''
    size_max = 1024
    # default rule 1 : smallest size become default
    for sizeEntry in themeRoot.entryInfoList(FilterDir):
        size_name = sizeEntry.fileName()
        size = str(size_name).split('x')
        if len(size) == 2 and int(size[0]) < size_max:
            default_size_qrc_path = sizeEntry.filePath() 
            default_size_name = size_name   
    # default rule 2 : 32x32 or default size become default
    for sizeEntry in themeRoot.entryInfoList(FilterDir):
        size_name = sizeEntry.fileName()
        size_qrc_path = sizeEntry.filePath()
        if size_name == '32x32' or size_name == 'default':
            default_size_name = size_name
            default_size_qrc_path = size_qrc_path

    for sizeEntry in themeRoot.entryInfoList(FilterDir):
        size_name = sizeEntry.fileName()
        size_qrc_path = sizeEntry.filePath()
        print " ",size_name,size_qrc_path
        
        sizeRoot = QDir(sizeEntry.filePath())
        
        for categoryEntry in sizeRoot.entryInfoList(FilterDir):
            category_name = categoryEntry.fileName()
            categoryRoot = QDir(categoryEntry.filePath())
            for fileEntry in categoryRoot.entryList(['*.png'],QDir.Files):
                file_full_name = size_qrc_path + '/' + category_name + '/' + fileEntry
                # compatibility
                if default_size_name == size_name:
                    if fileEntry == 'configure.png':
                        compatibility_items['preferences.png'] = file_full_name
                    compatibility_entry = re.sub(r'^[^\-]+\-','',str(fileEntry))
                    compatibility_items[compatibility_entry] = file_full_name
                    
                # default
                if default_size_name == size_name:
                    fout.write("    <file alias=\"%s/%s/%s\">%s</file>\n" % (theme_name,'default',fileEntry,file_full_name))                      
                
                fout.write("    <file alias=\"%s/%s/%s\">%s</file>\n" % (theme_name,size_name,fileEntry,file_full_name)) 
                
#print compatibility_items    
for key in compatibility_items:
    fout.write("    <file alias=\"%s\">%s</file>\n" % (key,compatibility_items[key]))
    
fout.write("</qresource>\n</RCC>\n")
fout.close()