'''
Created on 01.01.2023

@author: uschoen
'''



__version__='0.1.1'
__author__ = 'ullrich schoen'

# Standard library imports
import threading
import logging


# Local application constant
from core.coreException import coreException
from core.manager import manager as coreManager

LOG=logging.getLogger(__name__)

class defaultModul(threading.Thread):
    '''
    
    '''
    
    def __init__(self,objectID,modulCFG):
        '''
        Constructor
        '''
        threading.Thread.__init__(self)
        self.core=coreManager()
        self.config={
                        'enable':False,
                        'objectID':objectID
                      }
        self.config.update(modulCFG)
        ''' gateway running '''
        self.running=False
        
        self.ifShutdown=False
        ''' core instance '''
        LOG.debug("__init default modul %s instance, version %s"%(__name__,__version__))
        
    def run(self):
        LOG.warning("modul %s have no run function"%(self.config['objectID']))
    
    def getConfiguration(self):#
        return self.config
       
    def stopModul(self):
        '''
        '
        '    stop modul
        '
        '    exception: none
        '
        '''
        LOG.critical("stop modul %s"%(self.config['objectID']))
        self.running=False
    
    def runModul(self):
        '''
        '
        '    start modul
        '
        '    exception: none
        '
        '''
        if self.ifShutdown:
            LOG.error("modul is shutdown and can*t start")
            return
        LOG.info("set running=true. starting modul %s"%(self.config['objectID']))
        self.running=True
    
    def shutDownModul(self):
        '''
        
        shutdown modul
        
        exception: gatewayException
        
        '''
        try:
            if self.running:
                self.stopModul()
            LOG.critical("shutdown modul %s"%(self.config['objectID']))
            self.ifShutdown=True
        except:
            raise coreException("can't shutdown modul %s"%(self.config['objectID']))