'''
Created on 01.01.2023

@author: uschoen
'''

__version__='0.1.0'
__author__ = 'ullrich schoen'

# Standard library imports
import logging
import os
import time
# Local application imports
from core.coreException import coreException

LOG=logging.getLogger(__name__)


class coreLogger():
    '''
    core events function
    '''
    def __init__(self,*args):
        self.loggerConf={}
        self.debugType="simple"
        LOG.info("__init core logger version: %s"%(__version__))
    
    
    def writeLoggerConfiguration(self,objectID=None,fileNameABS=None,forceUpdate=False):
        '''
        internal function to write the logger configuration 
        
        objectID= host id to save
        fileNameABS=None
        
        exception: coreException,coreException
        '''
        try:
            if fileNameABS==None:
                raise coreException("no filename given to write logger file")
            if objectID==None:
                objectID="logger@%s"%(self.host)
            if self.ifonThisHost(objectID):
                self._writeLoggerConfiguration(fileNameABS)
            else:
                self.updateRemoteCore(forceUpdate,objectID,'writeLoggerConfiguration',objectID,fileNameABS)
        except:
            raise coreException("can't write logging configuration")
    
    def _writeLoggerConfiguration(self,fileNameABS):
        '''
        internal function to write the logger configuration 
        
        fileNameABS: the absolut path of the file
        
        exception: coreException,coreException
        
        '''
        try:
            if len(self.loggerConf)==0:
                LOG.info("can't write logger configuration, is empty")
                return
            if not self.ifFileExists(fileNameABS):
                if not self.ifPathExists(os.path.dirname(fileNameABS)):
                    self.makeDir(os.path.dirname(fileNameABS))
            LOG.info("save logger configuration %s"%(fileNameABS))
            loggerCFG={
                    "version":__version__,
                    "from":int(time.time()),
                    "config":self.loggerConf
                    }
            self.writeJSON(fileNameABS,loggerCFG)
        except:
            LOG.critical("can't write logging configuration",True)
            raise coreException("can't write logging configuration")
    
    def loadLoggerConfiguration(self,objectID=None,fileNameABS=None,forceUpdate=False):
        '''
        internal function to load the logger configuration 
        
        fileNameABS=None
        
        exception:
        
        if none fileNameABS raise exception
        if fileNameABS file not exist rasie exception
        '''
        try:
            if fileNameABS==None:
                raise coreException("no filename given to load core file")
            if objectID==None:
                objectID="logger@%s"%(self.host)
            if self.ifonThisHost(objectID):
                self._loadLoggerConfiguration(fileNameABS)
            else:
                self.updateRemoteCore(forceUpdate,objectID,'loadLoggerConfiguration',objectID,fileNameABS)
        except:
            raise coreException("can't read logging configuration")
    
    def _loadLoggerConfiguration(self,fileNameABS):
        '''
        internal function to load the logger configuration 
        
        fileNameABS: the absolute path of the file
        
        exception: coreException,coreException
        
        '''
        try:
            if not self.ifFileExists(fileNameABS):
                if not self.ifPathExists(os.path.dirname(fileNameABS)):
                    LOG.info("create new directory %s"%(os.path.dirname(fileNameABS)))
                    self.makeDir(os.path.dirname(fileNameABS))
                    
                LOG.info("create new file %s"%(fileNameABS))
                loggerCFG={
                    "version":__version__,
                    "from":int(time.time()),
                    "config":self.getLoggerDefaults()
                    }
                self.writeJSON(fileNameABS,loggerCFG)
                
            LOG.info("load logger configuration %s"%(fileNameABS))
            loggerCFG=self.loadJSON(fileNameABS)
            if len(loggerCFG['config'])==0:
                LOG.info("logger configuration file is empty")
                return
            self.__applyLoggerConfiguration(loggerCFG['config'],self.debugType)
            self.loggerConf=loggerCFG['config']
        except (Exception) as e:
            raise coreException("can't read logging configuration: %s"%(format(e)))
    
    def __applyLoggerConfiguration(self,loggerConf,logTyp="simple"):
        try:
            LOG.info("apply new logger configuration type: %s"%(logTyp))
            if loggerConf['logTyp']=="colored":
                import coloredlogs      #@UnresolvedImport
                conf=loggerConf.get("colored")
                coloredlogs.DEFAULT_FIELD_STYLES = conf.get("FIELD_STYLES")
                coloredlogs.DEFAULT_LEVEL_STYLES = conf.get("LEVEL_STYLES")
                coloredlogs.DEFAULT_LOG_FORMAT='%s'%(conf.get("fmt"))
                coloredlogs.DEFAULT_LOG_LEVEL=conf.get("level","DEBUG")
                coloredlogs.install(milliseconds=conf.get("milliseconds",True))
            else:
                logging.config.dictConfig(loggerConf['simple'])
        except:
            raise coreException("can not add logging instances")