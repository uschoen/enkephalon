'''
Created on 01.01.2023

@author: uschoen
'''

__version__ = '0.1.0'

# Standard library imports
import logging
import os
from datetime import datetime
import time

# Local library imports
from core.script.exception import defaultError,cmdError,testError,scriptProgrammError
from core.script.praraphser import praraphser

# defaults
LOG=logging.getLogger(__name__)

class scriptManager():
    """
    script Manager to manage Scripts
    
       
    """
    def __init__(self,*args):
        
        self.scripts={}
        LOG.info("__init core scriptManager finish, version %s"%(__version__))
        
    def addScript(self,scriptName,script,forecUpdate=False):
        '''
        add a Script
        '''  
        try:
            self.__addScript(scriptName, script)
            self.updateRemoteCore(forecUpdate,scriptName,'addScript',scriptName,script)
        except:
            raise scriptProgrammError("unknown error in addScript",True)
    
    def __addScript(self,scriptName,script,test=False):
        try:
            LOG.debug("add script  %s"%(scriptName))
            self.scripts[scriptName]=script
        except:
            raise scriptProgrammError("unknown error in __addScript",True)
    
    def updateScript(self,scriptName,script,forecUpdate=False):
        '''
        update a script
        '''
        try:
            pass
            self.updateRemoteCore(forecUpdate,scriptName,'updateScript',scriptName,script)
        except:
            raise scriptProgrammError("unknown error in updateScript",True)
    
    def __restoreScript(self,scriptName,script):
        '''
        restore a program, only for restart/start
        '''
        try:
            LOG.debug("restore script %s"%(scriptName))
            if scriptName in self.scripts:
                self.__deleteScript(scriptName)
            self.__addScript(scriptName,script)
        except:
            raise scriptProgrammError("unknown error in __restoreScript",True)
        
    def restoreScript(self,scriptName,script,forceUpdate=False):
        '''
        restore a script
        '''
        try:
            self.__restoreScript(
                scriptName,
                script
                )
            self.updateRemoteCore(
                forceUpdate,
                scriptName,
                self.thisMethode(),
                scriptName,
                script)
        except:
            raise scriptProgrammError("unknown error in restoreScript",True)
        
    def _writeScriptConfiguration(self,fileNameABS):
        '''
        internal function to write the devices configuration 
        
        fileNameABS: the absolute path of the file
        
        exception: deviceException,defaultEXC
        
        '''
        try:
            if len(self.scripts)==0:
                LOG.warning("can't write script configuration, scripts are empty")
                return
            if not self.ifFileExists(fileNameABS):
                if not self.ifPathExists(os.path.dirname(fileNameABS)):
                    self.makeDir(os.path.dirname(fileNameABS))
            LOG.info("save script configuration %s"%(fileNameABS))
            scriptCFG={
                "version":__version__,
                "from":int(time.time()),
                "scripts":{}
            }
            for scriptID in self.scripts:
                scriptCFG['scripts'][scriptID]=self.scripts[scriptID]
            self.writeJSON(fileNameABS,scriptCFG)
        except:
            raise scriptProgrammError("can't write script configuration",True) 
    
    def _loadScriptConfiguration(self,fileNameABS):
        '''
        internal function to load the script configuration 
        
        fileNameABS: the absolute path of the file
        
        exception: deviceException,defaultEXC
        
        '''
        try:
            if not self.ifFileExists(fileNameABS):
                if not self.ifPathExists(os.path.dirname(fileNameABS)):
                    self.makeDir(os.path.dirname(fileNameABS))
                LOG.info("create new file %s"%(fileNameABS))
                self.writeJSON(fileNameABS,{"scripts":{},"version": __version__,"from":int(time.time())})
            LOG.info("load script configuration %s"%(fileNameABS))
            CFGFile={
                "version":"unknown",
                "from":0,
                "scripts":{}
                }
            CFGFile.update(self.loadJSON(fileNameABS))
            LOG.info("script configuration file has version: %s from %s"%(CFGFile['version'],datetime.fromtimestamp(CFGFile['from'])))
            
            if len(CFGFile['scripts'])==0:
                LOG.info("script configuration file is empty")
                return
            for scriptName in CFGFile['scripts']:
                try:
                    self.__restoreScript(scriptName,CFGFile['scripts'][scriptName])
                except (defaultError) as e:
                    LOG.error("some error at restoreScript: %s"%(e.msg))
                except:
                    LOG.critical("unknown error at restoreScript",exc_info=True)
        except:
            raise scriptProgrammError("can't read script configuration",True)
        
    def runScript(self,scriptName,script=None,callerObject=None,callerVars={},programDeep=0):
        try:
            if self.ifonThisHost(scriptName):
                LOG.debug("run script name: %s , with script: %s"%(scriptName,script))
                if script==None:
                    LOG.debug("no script was given, load script %s"%(scriptName))
                    if scriptName in self.scripts:
                        script=self.scripts[scriptName]
                    else:
                        LOG.error("can't not find script %s"%(scriptName))
                        raise defaultError("can't not find script %s"%(scriptName), False)
                
                p=praraphser(core=self,
                             callerObject=callerObject,
                             callerVars=callerVars)
                
                presult=p.runScript(script=script,
                            programDeep=programDeep)
                return presult
            else:
                LOG.debug("script %s is not at this host %s"%(scriptName.self.host))
        except (defaultError,cmdError,testError) as e:
            raise e
        except:
            raise scriptProgrammError("unknown error in runScript",True)
   
    def deleteScript(self,scriptName,forecUpdate=False):
        try:
            if scriptName in self.scripts:
                self.__deleteScript(scriptName)
                
            self.updateRemoteCore(
                forecUpdate,
                scriptName,
                self.thisMethode(),
                scriptName
            )
        except:
            raise scriptProgrammError("unknown error in deleteScript",True)
    
    def __deleteScript(self,scriptName):
        try:
            if not scriptName in self.scripts:
                return
            LOG.info("delete script %s"%(scriptName))
            del self.scripts[scriptName]
        except:
            raise scriptProgrammError("unknown error in __deleteScript",True)

    
    