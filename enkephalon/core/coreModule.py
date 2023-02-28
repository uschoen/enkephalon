'''
Created on 01.01.2023

@author: uschoen
'''

DEFAULT_MODUL_PATH="module"

__version__='0.1.0'
__author__ = 'ullrich schoen'

# Standard library imports
import logging
import os
from datetime import datetime
import time


# Local application imports
from core.coreException import coreException
from module.modulException import modulException

LOG=logging.getLogger(__name__)


class coreModule():
    '''
    core modul function
    '''
    def __init__(self,*args):
        self.module={}
        
        LOG.info("__init core module finish, version %s"%(__version__))
    
    def shutDownAllModule(self,hostID=None,forceUpdate=False):
        '''
        shutdown all module for the host ID
        '''
        try:
            if (hostID==None):
                hostID="core@%s"%(self.host)
            
            if self.ifonThisHost(hostID):
                LOG.warning("shutdown all module for core %s"%(hostID))
                for moduleName in self.module:
                    self.__shutDownModul(moduleName)
            else:
                self.updateRemoteCore(forceUpdate,hostID,self.thisMethode(),hostID)
        except:
            raise coreException("some error in shutdownAllModule",True)  
    
    def __shutDownModul(self,objectID):
        try:
            if (self.module[objectID]['running']):
                self.__stopModul(objectID)
            LOG.warning("shutdown modul %s "%(objectID))
            if not self.module[objectID]['shutdown']:
                self.module[objectID]['instance'].shutDownModul()
            self.module[objectID]['shutdown']=True
        except:
            raise coreException("some error __shutdownModul modul %s"%(objectID),True) 
    
    def _writeModulConfiguration(self,fileNameABS):
        try:
            if len(self.module)==0:
                LOG.warning("can't write modul configuration, is empty")
                return
            if not self.ifFileExists(fileNameABS):
                if not self.ifPathExists(os.path.dirname(fileNameABS)):
                    self.makeDir(os.path.dirname(fileNameABS))
            LOG.info("save connector configuration %s"%(fileNameABS))
            modulCFG={
                "version":__version__,
                "from":int(time.time()),
                "module":{}
            }
            for modulName in self.module:
                modulCFG["module"][modulName]=self.module[modulName]
                '''
                get module configuration
                '''
                if hasattr(self.module[modulName]['instance'], 'getConfiguration'):
                    modulCFG["module"][modulName]['config']=self.module[modulName]['instance'].getConfiguration()
                else:
                    LOG.warning("modul %s is not build, use configuration in core"%(modulName))
                    modulCFG["module"][modulName]['config']=self.module[modulName]['config']
                '''
                delete object from json file
                '''    
                del(modulCFG["module"][modulName]['instance'])
                
            self.writeJSON(fileNameABS,modulCFG)
        except (Exception) as e:
            raise coreException("can't _writeModulConfiguration: %s"%(e)) 
    
    def _loadModulConfiguration(self,fileNameABS):
        '''
        internal function to load the device configuration 
        
        fileNameABS: the absolut path of the file
        
        exception: deviceException
        
        '''
        try:
            if not self.ifFileExists(fileNameABS):
                if not self.ifPathExists(os.path.dirname(fileNameABS)):
                    self.makeDir(os.path.dirname(fileNameABS))
                LOG.info("create new file %s"%(fileNameABS))
                self.writeJSON(fileNameABS,{"version": __version__,"from":int(time.time()),"module":{}})
            LOG.info("load modul configuration %s"%(fileNameABS))
            CFGFile={
                "version":"UNKOWN",
                "from":0,
                "module":{}
                }
            CFGFile.update(self.loadJSON(fileNameABS))
            LOG.info("modul configuration file has version: %s from %s"%(CFGFile['version'],datetime.fromtimestamp(CFGFile['from'])))
            if len(CFGFile["module"])==0:
                LOG.info("modul configuration file is empty")
                return
            for objectID in CFGFile["module"]:
                try:
                    LOG.info("try to restore %s"%(objectID))
                    self.__restoreModul(objectID, CFGFile["module"][objectID])
                except (coreException,modulException) as e:
                    LOG.error("some error at __restoreModul objectID %s"%(e.msg))
                except (Exception) as e:
                    LOG.error("unknown error _loadModulConfiguration %s"%(e),True)
        except (Exception) as e:
            raise coreException("unknown error, can't read modul configuration: %s"%(e),True)
    
    def __restoreModul(self,objectID,modulCFG):
            '''
            restore a Module,only for internal access
            
            objectID: Module ID
            
            exception: defaultEXC
            '''
            try:
                if objectID in self.module:
                    LOG.critical("not implementet delete module")
                    #self.__deleteModul(objectID )
                self.__buildModul(objectID,modulCFG)
                if self.ifonThisHost(objectID):
                    if self.module[objectID]['enable'] and self.module[objectID]['startable']:
                        self.__startModul(objectID)
                    elif not self.module[objectID]['enable']:
                        LOG.warning("modul %s is not enable"%(objectID))
            except (modulException) as e:
                raise e
            except:
                raise coreException("some error in restoreModule",True)
            
    def __stopModul(self,objectID):
        '''
        stop a modul
        '''
        try:
            LOG.warning("stop modul %s"%(objectID))
            self.module[objectID]['running']=False
            self.module[objectID]['instance'].stopModul()
        except:
            raise coreException("some error _stopModul modul %s"%(objectID),True) 
        
    def __startModul(self,objectID):
        '''
        start a modul
         
        objectID: connector obectID
        
        exception: connectorException
        '''
        try:
            LOG.debug("try to start modul %s"%(objectID))
            self.module[objectID]['instance'].runModul()
            self.module[objectID]['instance'].start() 
            self.module[objectID]['running']=True
            self.module[objectID]['shutdown']=False
        except (modulException) as e:
            self.module[objectID]['enable']=False
            self.module[objectID]['running']=False
            self.module[objectID]['shutdown']=True
            raise e
        except (Exception) as e:
            self.module[objectID]['enable']=False
            self.module[objectID]['running']=False
            self.module[objectID]['shutdown']=True
            raise coreException("can't start modul %s error:%s"%(objectID,e),True)
        
    def __buildModul(self,  
                      objectID,
                      modulCFG
                      ):
        '''
        add a core connector as server or client
        objectID:    the core name of the client (name@hostname)
        modulCFG:    Configuration of the modul
        syncStatus true/false if true it set the status to the core to is sync
        
        Exception: clusterException
        '''
        try:
            LOG.info("try to build modul %s"%(objectID))
            self.module[objectID]={
                "startable":False,
                "enable":False,
                "modulPackage":"unkown",
                "modulClass":"unkown",
                "config":{},
                "instance":False,
                "running":False,
                "shutdown":True
                }
            '''
            #    add modul Parameter
            '''
            self.module[objectID].update(modulCFG)
            self.module[objectID]['config']["objectID"]=objectID
            self.module[objectID]['config']["enable"]=self.module[objectID]["enable"]
            self.module[objectID]['config']["objectID"]=objectID
            self.module[objectID]['config']["gatewayID"]="%s"%(objectID.replace("@","."))
            
            if self.ifonThisHost(objectID):
                '''
                build local module
                '''
                classCFG={
                "objectID":objectID,
                "modulCFG":self.module[objectID]["config"],
                }
                LOG.info("modul is build  %s"%(objectID))
                package="%s.%s"%(DEFAULT_MODUL_PATH,self.module[objectID]['modulPackage'])
                self.module[objectID]['instance']=self.loadModul(objectID,package,self.module[objectID]['modulClass'],classCFG)
                if self.module[objectID]['startable']:
                    self.module[objectID]['instance'].daemon=True   
        except (modulException) as e:
            self.module[objectID]['enable']=False
            self.module[objectID]['instance']=False
            self.module[objectID]['running']=False
            self.module[objectID]['shutdown']=True
            raise e
        except:
            self.module[objectID]['enable']=False
            self.module[objectID]['instance']=False
            self.module[objectID]['running']=False
            self.module[objectID]['shutdown']=True
            raise modulException ("can not build modul %s"%(objectID),True)       
            
            