#!/usr/bin/python

import subprocess
import platform
import sys
import re
import tempfile

def Platform():
    return platform.system()

if Platform() == 'Windows':
    from PyQt4.QtCore import *

def Uname():
    return platform.uname()

def isWindows():
    return Platform() == 'Windows'

def isMacOSX():
    return Platform() == 'Darwin'

def isLinux():
    return Platform() == 'Linux'

def Arch():
    for uname_item in Uname():
        if uname_item == 'x86_64' or uname_item == 'x86-64':
            return 'x86-64'

    for uname_item in Uname():
        if uname_item == 'i386' or uname_item == 'x86':
            return 'i386'   

    for uname_item in Uname():
        if re.match(r'^armv.*',uname_item):
            return uname_item

def PythonVersion():
    return [sys.version_info.major,sys.version_info.minor,sys.version_info.micro]

def _which(cmd):
    rtn = subprocess.check_output('which %s' % cmd,shell = True)
    return re.sub(r'[\n\r]','',rtn) 

def _rev2arr(rev):
    rev = re.sub(r'[\n\r]','',rev)
    return [int(x) for x in rev.split('.')]

def InstalledPythonPath(rev = 2):
    if rev == 2:
        rev = ''
        numrev = 2
    else:
        numrev = rev
    
    python_path = ''
    if Platform() == 'Linux' or Platform() == 'Darwin':
        python_path = _which('python' + str(rev))
    if Platform() == 'Windows':
        maxMinor = 0
        maxMinorPath = ''
        for rootKey in ['HKEY_LOCAL_MACHINE','HKEY_CURRENT_USER']:
            settings = QSettings('%s\SOFTWARE\Python\PythonCore' % rootKey,QSettings.NativeFormat)
            for group in settings.childGroups():
                matches = re.match(r'^(\d+)\.(\d+)$',group)
                if matches:
                    thisMajor = int(matches.group(1))
                    thisMinor = int(matches.group(2))
                    if thisMajor == numrev and thisMinor > maxMinor:
                        maxMinor = thisMinor
                        maxMinorPath = '%s\SOFTWARE\Python\PythonCore\%s\InstallPath' % (rootKey,group)                        
        if maxMinorPath != '':            
            settings = QSettings(maxMinorPath,QSettings.NativeFormat)
            python_path = '%spython.exe' % settings.value('.').toString()
            try:
                if subprocess.call(python_path + ' -V',stderr=subprocess.PIPE):
                    python_path = ''
            except:
                python_path = ''
    return python_path

def InstalledPythonVersion(rev = 2):

    python_path = InstalledPythonPath(rev)
    if python_path == '':
        return [0,0,0]
        
    f = tempfile.NamedTemporaryFile(delete=False)
    f.write("import sys\n")
    if rev == 2:
        f.write("print '%d.%d.%d' % (sys.version_info.major,sys.version_info.minor,sys.version_info.micro)")
    else:
        f.write("print ('%d.%d.%d' % (sys.version_info.major,sys.version_info.minor,sys.version_info.micro))")
    f.close()
    #print f.name
    try:
        ck = subprocess.check_output([python_path,f.name])
        return _rev2arr(ck)
    except:
        return [0,0,0]

def InstalledPyQtVersion(rev = 2,qtrev = 4):
    python_path = InstalledPythonPath(rev)
    if python_path == '':
        return [0,0,0]
        
    f = tempfile.NamedTemporaryFile(delete=False)
    f.write("try:\n")
    f.write("    from PyQt%d.QtCore import *\n" % qtrev)
    if rev == 2:
        f.write("    print QT_VERSION_STR\n")
        f.write("except:\n    print '0.0.0'")
    else:
        f.write("    print (QT_VERSION_STR)\n")
        f.write("except:\n    print ('0.0.0')")
    f.close()
    #print f.name
    try:
        ck = subprocess.check_output([python_path,f.name])
        return _rev2arr(ck)
    except:
        return [0,0,0]    
    
if __name__ == '__main__':
    print "Platform",Platform()
    print "Arch",Arch()
    print "Python",PythonVersion()
    print "Installed Python2",InstalledPythonPath(2),InstalledPythonVersion(2)
    print "Installed Python2 Qt4",InstalledPyQtVersion(2,4)
    print "Installed Python2 Qt5",InstalledPyQtVersion(2,5)
    print "Installed Python3",InstalledPythonPath(3),InstalledPythonVersion(3)
    print "Installed Python3 Qt4",InstalledPyQtVersion(3,4)
    print "Installed Python3 Qt5",InstalledPyQtVersion(3,5)