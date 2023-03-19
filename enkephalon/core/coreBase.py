'''
Created on 01.01.2023

@author: uschoen
'''
__version__ = '0.1.0'
__author__ = 'ullrich schoen'


# Standard library imports
import json
import os
import importlib
import logging
import sys
import re
import socket
from threading import Thread

LOG=logging.getLogger(__name__)

try:
    import psutil                   #@UnresolvedImport 
    GETSTATISTICPROCESS=True
except:
    LOG.error("psutil not installed. Use pip3 install psutil to install. Function getStatisticProcess not working")
    GETSTATISTICPROCESS=False
# Local application imports
from core.coreException import coreException
from module.modulException import modulException



class coreBase():
    
    def __init__(self):
        '''
        coreBase 
        
        Global variable:
        self.path:          absolute path of the script
        self.rootPath:      root path of the script
        self.host:          host name
        self.threads:       all running thread objects
        
        
        '''
        
        '''
        self.path: the absolute path of the script
        '''
        self.runPath='' if not os.path.dirname(sys.argv[0]) else '%s/'%(os.path.dirname(sys.argv[0]))
        
        '''
        script absolute root path
        '''
        self.rootPath=("%s/%s"%(os.getcwd(),os.path.dirname(sys.argv[0])))
         
        '''
        self.host: the self host name
        '''
        self.host=socket.gethostbyaddr(socket.gethostname())[0].split(".")[0]
        
        
        '''
        thread queue
        '''
        self.threads=[]
        
        LOG.info("__init core base finish, version %s"%(__version__))
    
    def clearUpThreads(self):
        '''
        clear up death or old thread
        '''
        try:
            for thread in self.threads:
                if not thread.is_alive():
                    self.threads.remove(thread)
        except (Exception) as e:
            raise coreException("unknown error in clearUpThreads. error: %e"%(e))
        
    def getStatisticProcess(self):
        '''
        return a dic with statis data
        
        return: {  'cpu': cpu usage in percent
                   'mem' : memory in percent
                   'threads' running threads
                }
        '''
        try: 
            statisticValues={
                    'mem':0,
                    'cpu':0,
                    'threads':0
                    }
            if GETSTATISTICPROCESS:
                python_process = psutil.Process(os.getpid())
                statisticValues={
                    'mem':round(python_process.memory_percent(),2),
                    'cpu':python_process.cpu_percent(interval=1),
                    'threads':len(self.threads)
                    }
            return statisticValues
        except (Exception) as e:
            raise coreException("some error in getStatisticProcess. error:%s"%(e),True)
        
    def startThread(self,target,args):
        '''
        start an the funktion in the new thread and add it to
        the thread queue
        
        target=function or object to start
        args= argument
        '''
        try:
            thread=Thread(target=target, args=args,daemon=True)
            self.threads.append(thread)
            thread.start()
        except (Exception) as e:
            raise coreException("can't start new thread. error:%s"%(e))
    
    def thisMethode(self):
        '''
        return the actule methode
        '''
        try:
            return sys._getframe(1).f_code.co_name 
        except:
            LOG.critical("some error in thisMethode",True)
    
    def checkModulVersion(self,package,classModul,modulVersion=__version__):
        '''
        check if a load package have the right module version
        
        package:    the load package
        classModul:    the load class
        modulVersion:    min version , default=core Version
        
        return: object  from the Class
        
        exception: defaultEXC
         
        '''
        try:
            if hasattr(classModul, '__version__'):
                if classModul.__version__<modulVersion:
                    LOG.warning("version of %s is %s and can by to low"%(package,classModul.__version__))
                else:
                    LOG.debug( "version of %s is %s"%(package,classModul.__version__))
            else:
                LOG.warning("modul %s has no version Info"%(package))
        except:
            LOG.critical("can't check modul version")  
    
    def makeDir(self,pathABS=None):
        '''
        add a direktor to the filesystem
        
        pathABS: absolute file path to add
            
        Exception: coreException
        '''
        if pathABS==None:
            raise coreException("no path  given")
        try:
            path=os.path.normpath(pathABS)
            LOG.debug("add directory %s"%(path))
            os.makedirs(path)
        except coreException as e:
            raise e
        except:
            raise coreException("can not add directory %s"%(path))
    
    def ifPathExists(self,pathABS=None):
        '''
        check if a file Path exits
        
        pathABS: absolute file path to check
            
        Exception: coreException
        '''
        if pathABS==None:
            raise coreException("no path given")
        try:
            return os.path.isdir(os.path.normpath(pathABS))
        except:
            raise coreException("ifPathExists have a problem")
    
    def ifFileExists(self,fileNameABS=None):
        '''
        check if a file  exits
        
        fileNameABS: absolute file to check
            
        return: true if exists
        
        Exception: coreException
        '''
        if fileNameABS==None:
            raise coreException("no file name given")
        try:
            filename=os.path.normpath(fileNameABS)          
            return os.path.isfile(filename)
        except:
            raise coreException("ifFileExists have a problem")
    
    def loadJSON(self,fileNameABS=None):
        '''
        load a file with json data
        
        fileNameABS: absolute filename to load
        
        return: Dict 
        
        Exception: coreException
        '''
        if fileNameABS==None:
            raise coreException("no fileNameABS given")
        try:
            with open(os.path.normpath(fileNameABS)) as jsonDataFile:
                dateFile = json.load(jsonDataFile)
            return dateFile 
        except IOError:
            raise coreException("can't find file: %s "%(os.path.normpath(fileNameABS)),False)
        except ValueError:
            raise coreException("error in json file: %s "%(os.path.normpath(fileNameABS)))
        except:
            raise coreException("unkown error to read json file %s"%(os.path.normpath(fileNameABS)))
    
    def writeJSON(self,fileNameABS=None,jsonData={}):
        '''
        write a file with json data
        
        fileNameABS: absolute filename to write
        fileData= data to write
        
        Exception: coreException
        '''
        if fileNameABS==None:
            raise coreException("no fileNameABS given")
        try:
            LOG.debug("write json file to %s"%(fileNameABS))
            with open(os.path.normpath(fileNameABS),'w') as outfile:
                json.dump(jsonData, outfile,sort_keys=True, indent=4)
                outfile.close()
        except IOError:
            raise coreException("can not find file: %s "%(os.path.normpath(fileNameABS)))
        except ValueError:
            raise coreException("error in json find file: %s "%(os.path.normpath(fileNameABS)))
        except:
            raise coreException("unkown error in json file to write: %s"%(os.path.normpath(fileNameABS)))
    
    def writeFile(self,fileNameABS=None,fileData=None,parm="w"):
        '''
        write a file 
        
        fileNameABS: absolute filename to write
        fileData= data to write
        
        Exception: defaultEXC
        '''
        if fileNameABS==None:
            raise coreException("no fileNameABS given")
        try:
            LOG.debug("write json file to %s"%(fileNameABS))
            pythonFile = open(os.path.normpath(fileNameABS),parm) 
            pythonFile.write(fileData)
            pythonFile.close()
        except IOError:
            raise coreException("can not find file: %s "%(os.path.normpath(fileNameABS)))
        except ValueError:
            raise coreException("error  find file: %s "%(os.path.normpath(fileNameABS)))
        except:
            raise coreException("unkown error in  file to write: %s"%(os.path.normpath(fileNameABS)))       
    
    def loadModul(self,objectID,packageName,className,classCFG):
        '''
        load python pakage/module
        
        Keyword arguments:
        packageName -- pakage name 
        className -- the name of the gateway typ:strg
        modulCFG -- configuration of the gateway typ:direcorty as dic.
                    ['pakage'] -- pakage name
                    ['modul'] -- modul name
                    ['class'] -- class name
        
        return: class Object
        exception: yes 
        '''           
        try:
            package="%s.%s"%(packageName,className)
            LOG.debug("for %s, try to build package: %s  with class: %s"%(objectID,package,className))
            CLASS_NAME = className
            module = self.loadPackage(package)
            self.checkModulVersion(package,module)
            return getattr(module, CLASS_NAME)(**classCFG)
        except (modulException) as e:
            raise e
        except Exception as e:
            raise coreException("can't no load package: %s class: %s %s"%(package,className,e))  
    
    def loadPackage(self,package):
        '''
        load a python package
        
        return: object  from the Class
        
        exception: defaultEXC
         
        '''
        try:
            classModul = importlib.import_module(package)
            LOG.info("load package %s"%(package))
            return classModul
        except (modulException) as e:
            raise e
        except:
            raise coreException("can't not loadPackage %s"%(package))
    
    def ifonThisHost(self,objectID):
        '''
        #################################################
        check is objectID on this host
        
        check to parts of pattern
        
        1:
        *@*.*  deviceID@gateway.host
        2:
        *@*    name@host
        
        return true is host on this host, else false
        ##################################################
        '''
        try:
            if re.match('.*@.*\..*',objectID):
                ''' device id  device@gateway.host '''
                host=objectID.split("@")[1].split(".")[1]
                if host == self.host:
                    #LOG.debug("objectID %s is on this host: %s"%(objectID,self.host))
                    return True
                else:
                    #LOG.debug("objectID %s is not on host: %s"%(objectID,self.host))
                    return False
            
            if re.match('.*@.*',objectID):
                ''' object patter test@host '''
                host=objectID.split("@")[1]
                if host == self.host:
                    #LOG.debug("objectID %s  is on host: %s"%(objectID,self.host))
                    return True
                else:
                    #LOG.debug("objectID %s is not on host: %s"%(objectID,self.host))
                    return False
            LOG.error("unkown objectID pattern:%s"%(objectID))       
            return False
        except:
            LOG.error("can't format pattern %s"%(objectID),exc_info=True)
            return False