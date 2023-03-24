'''
Created on 01.01.2023

@author: uschoen
'''
__version__ = '0.1.0'
# Local library imports
from core.coreBase import coreBase
from core.coreException import coreException
from core.coreDefaults import coreDefaults
from core.coreEvents import coreEvents
from core.coreConfiguration import coreConfiguration
from core.coreLogger import coreLogger
from core.coreModule import coreModule
from core.format.formater import formater
from core.coreDevices import coreDevices
from core.coreDeviceChannel import coreDeviceChannel
from core.coreCluster import coreCluster
from core.script.scriptManager import scriptManager

__author__ = 'ullrich schoen'

# Standard library imports
import threading
import logging
import logging.config
import time

# defaults
LOG=logging.getLogger(__name__)
CORELOOP=2

class manager(coreBase,
              coreDefaults,
              coreEvents,
              coreConfiguration,
              coreLogger,
              coreModule,
              formater,
              coreDevices,
              coreDeviceChannel,
              coreCluster,
              scriptManager):
    
    """A thread-safe class acting like a singleton"""
    _instance = None
    _lock = threading.Lock()

    def __new__(cls,configFile=None,debugType=None):
        '''
        #####################################################
        new 
        #####################################################
        ''' 
        if not cls._instance:
            with cls._lock:
                cls._instance = object.__new__(cls)
        return cls._instance
    
    def __init__(self,configFile=None,debugType=None):
        '''
        #####################################################
        init 
        #####################################################
        '''
        if hasattr(self, 'firstrun'):
            return
        self.__initFirstRun(configFile,debugType)
       
    def __initFirstRun(self,configFile=None,debugType=None):    
        '''
        #####################################################
        default args
        #####################################################
        ''' 
        self.firstrun=True
        self.coreShutdown=False
        self.debugType=debugType
        
        '''
        #####################################################
        start up CoreBase information and function
        #####################################################
        '''
        coreBase.__init__(self)
        
        LOG.info("starting core on host %s in root path %s run at /%s"%(self.host,self.rootPath,self.runPath))
        
        '''
        #####################################################
        load configuration 
        #####################################################
        '''
        coreDefaults.__init__(self)
        coreLogger.__init__(self)
        coreCluster.__init__(self)
        coreModule.__init__(self)
        
        '''
        self.args: configuration of the core 
        '''
        self.args={}
        
        
        self.args=self.getCoreDefaults()['config']
        try:
            if not configFile == None:
                self.args.update(self.loadJSON(configFile))
        except:
            LOG.warning("can't load config file %s, use default config"%(configFile))
        
        '''
        #####################################################
        load core module
        #####################################################
        '''
        coreEvents.__init__(self)  
        coreConfiguration.__init__(self)  
        coreDevices.__init__(self)
        coreDeviceChannel.__init__(self)
        scriptManager.__init__(self)
        formater.__init__(self)
        
        LOG.info("__init core manager finish, version %s"%(__version__))  
        
    def start(self):
        '''
        #####################################################
        coreloop
        #####################################################
        '''
        try:
            LOG.info("start up core")
            try:
                self._onboot()
            except (coreException):
                LOG.error("can't call the onboot event")
            while 1:
                LOG.debug("coreLoop is running")
                self.clearUpThreads()
                statistic=self.getStatisticProcess()
                LOG.info("core statistic mem:%s cpu:%s threads:%s"%(statistic['mem'],statistic['cpu'],statistic['threads']))
                time.sleep(CORELOOP)
        except (SystemExit, KeyboardInterrupt) as e:
            LOG.critical("get signal to kill coreManager process! coreManager going down !!")
            raise e
        except:
            raise coreException("unknown error in coreLoop",True)
        finally:
            LOG.critical("stop core %s"%(self.host))
            self.shutdown()
    
    def shutdown(self,hostID=None,forceUpdate=False):
        '''
        ################################################################
        shutdown the corserver
        
        objectID: CoreID (format core@hostename)
        forceUpdate: send request du other core
        ################################################################
        '''
        try:
            if hostID==None:
                hostID="core@%s"%(self.host)
            if self.ifonThisHost(hostID):
                self._shutdown()
            else:
                LOG.critical("todo .. updateRemoteCore")
                #self.updateRemoteCore(forceUpdate,hostID,'shutdown',hostID)
        except:
            LOG.error("some error in shutdown coreServer", exc_info=True)
    
    def _shutdown(self):
        '''
        ################################################################
        internal function to shutdown this coreServer
        
        exception: 
        ################################################################
        '''
        try:
            if self.coreShutdown:
                return
            self.coreShutdown=True
            LOG.warning("shutdown core %s"%(self.host))
            try:
                self._onshutdown()
            except (coreException):
                LOG.error("can't call the onshutdown event")
                
            LOG.warning("wait 5 sec, to shutdown core %s finaly"%(self.host))
            time.sleep(5)
        except:
            LOG.error("some error in _shutdown coreServer",exc_info=True)