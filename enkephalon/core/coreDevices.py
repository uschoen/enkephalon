'''
Created on 01.01.2023

@author: uschoen
'''

__version__='0.1.0'
__author__ = 'ullrich schoen'

# Standard library imports
import logging
import os
from copy import deepcopy
import py_compile
import time
from datetime import datetime

# Local application imports
from core.coreException import coreException

DEVICE_BASE_PATH="module"                 #device base path
DEFAULT_DEVICE_PACKGAE="default"             #default device package
DEFAULT_DEVICE_TYPE="defaultDevice"      #default device type
LOG=logging.getLogger(__name__)

class coreDevices():
    '''
    core events function
    '''
    def __init__(self):
        
        self.devices={}
        
        LOG.info("__init core devices finish, version %s"%(__version__))
    
    def ifDeviceIDExists(self,
                         objectID):
        '''
            check if device exist
            
            objectID: the device id to check if exists
            
            return: 
                true if device exists
                false if no device exists
            
            exception:
                hmc.coreExecption
        ''' 
        try: 
            if objectID in self.devices:
                return True
            return False  
        except:
            raise coreException("can't not check ifDeviceExists deviceID %s"%(objectID)) 
    
    def restoreDevice(self,objectID,deviceCFG={},forceUpdate=False):
        
        try:
            restore=True
            devicePackage=deviceCFG.get("devicePackage",DEFAULT_DEVICE_PACKGAE)
            deviceType=deviceCFG.get("deviceType",DEFAULT_DEVICE_TYPE)
            if self.ifDeviceIDExists(objectID):
                self._deleteDevice(objectID)
            self.__buildDevice(objectID,
                               devicePackage,
                               deviceType,
                               deviceCFG,
                               restore
                               )
            self.updateRemoteCore(forceUpdate,
                                  objectID,
                                  self.thisMethode(),
                                  objectID,
                                  deviceCFG
                                  )
        
        except:
            raise coreException("can't restore deviceID %s with package %s and type: %s"%(objectID))
            
            
    def addDevice(self,
                  objectID,
                  devicePackage=DEFAULT_DEVICE_PACKGAE,      #default value default
                  deviceType=DEFAULT_DEVICE_TYPE,            #default value defaultDevice
                  deviceCFG={},
                  forceUpdate=False):
        ''' 
        add a new device to core
        
        objectID: device id from the device
        deviceCFG: configuration of the device
        
        deviceCFG:{
                    'type': "example",
                    ...
                  }
        '''
        if self.ifDeviceIDExists(objectID):
            raise coreException("objectID %s is exists"%(objectID),False)
        try:
            restore=False
            
            self.__buildDevice(objectID,
                               devicePackage,
                               deviceType,
                               deviceCFG,
                               restore
                               )
            self.updateRemoteCore(forceUpdate,
                                  objectID,
                                  self.thisMethode(),
                                  objectID,
                                  devicePackage,
                                  deviceType,
                                  deviceCFG
                                  )
        except (Exception) as e:
            raise coreException("can't not add objectID %s: %s"%(objectID,e))    
    
    def _loadDeviceConfiguration(self,fileNameABS):
        '''
        internal function to load the device configuration 
        
        fileNameABS: the absolute path of the file
        
        exception: deviceException,defaultEXC
        
        '''
        try:
            if not self.ifFileExists(fileNameABS):
                if not self.ifPathExists(os.path.dirname(fileNameABS)):
                    self.makeDir(os.path.dirname(fileNameABS))
                LOG.info("create new file %s"%(fileNameABS))
                self.writeJSON(fileNameABS,{"devices":{},"version": __version__,"from":int(time.time())})
            LOG.info("load device configuration %s"%(fileNameABS))
            CFGFile={
                "version":"unknown",
                "from":0,
                "devices":{}
                }
            CFGFile.update(self.loadJSON(fileNameABS))
            LOG.info("device configuration file has version: %s from %s"%(CFGFile['version'],datetime.fromtimestamp(CFGFile['from'])))
            
            if len(CFGFile["devices"])==0:
                LOG.info("device configuration file is empty")
                return
            for objectID in CFGFile["devices"]:
                try:
                    self.restoreDevice(objectID,CFGFile["devices"][objectID])
                except (coreException) as e:
                    LOG.error("some error at restoreDevice: %s"%(e.msg))
                except:
                    LOG.critical("unknown error at loadDeviceConfiguration",True)
        except:
            raise coreException("can't read device configuration")
    
    def _writeDeviceConfiguration(self,fileNameABS):
        '''
        internal function to write the devices configuration 
        
        fileNameABS: the absolute path of the file
        
        exception: deviceException,defaultEXC
        
        '''
        try:
            if len(self.devices)==0:
                LOG.warning("can't write device configuration, devices are empty")
                return
            if not self.ifFileExists(fileNameABS):
                if not self.ifPathExists(os.path.dirname(fileNameABS)):
                    self.makeDir(os.path.dirname(fileNameABS))
            LOG.info("save devices configuration %s"%(fileNameABS))
            deviceCFG={
                "version":__version__,
                "from":int(time.time()),
                "devices":{}
            }
            for deviceID in self.devices:
                deviceCFG["devices"][deviceID]=self.devices[deviceID].getConfiguration()
            self.writeJSON(fileNameABS,deviceCFG)
        except:
            raise coreException("can't write device configuration: %s"%(deviceCFG),True) 
        
    def __buildDevice(self,
                      objectID,
                      devicePackage=DEFAULT_DEVICE_PACKGAE,
                      deviceType=DEFAULT_DEVICE_TYPE,
                      deviceCFG={},
                      restore=False):
        try:
            
            ''' 
            check if channel package exists. if do not exits build this channel
            '''
            devicePackageFileName=os.path.normpath("%s/%s/%s/devices/%s.py"%(self.rootPath,DEVICE_BASE_PATH,devicePackage.replace(".","/"),deviceType))
            self.__checkIfDevicePackageExist(devicePackageFileName, devicePackage, deviceType)
            
            '''
            import & build package
            '''
            classCFG={
                "deviceID":objectID,
                "deviceCFG":deepcopy(deviceCFG),
                "restore":restore
                }
            fullDevicePackage="%s.%s.devices"%(DEVICE_BASE_PATH,devicePackage)
            self.devices[objectID]=self.loadModul(objectID,fullDevicePackage,deviceType,classCFG)
            
            
        except:
            raise coreException("can't build device %s package %s typ:%s"%(objectID,devicePackage,deviceType))
    
    def __checkIfDevicePackageExist(self,devicefileName,devicePackage,deviceType):
        try:
            if self.ifFileExists(devicefileName):
                return
            fileData="\'\'\'\nCreated on %s\n"%(time.strftime("%d.%m.%Y"))
            fileData+="@author: %s\n\n"%(__author__)
            fileData+="\'\'\'\n\n"
            fileData+="__version__=\"%s\"\n"%(__version__)
            fileData+="__author__=\"%s\"\n"%(__author__)
            fileData+="__DEVICETYPE__=\"%s\"\n"%(deviceType)
            fileData+="__DEVICEPACKAGE__=\"%s\"\n"%(devicePackage)
            fileData+="\n"
            fileData+="# Standard library imports\n"
            fileData+="import logging\n"
            fileData+="# Local application imports\n"
            fileData+="from %s.%s.devices.%s import %s\n\n"%(DEVICE_BASE_PATH,DEFAULT_DEVICE_PACKGAE,DEFAULT_DEVICE_TYPE,DEFAULT_DEVICE_TYPE)
            fileData+="LOG=logging.getLogger(__name__)\n"
            fileData+="\n"
            fileData+="class %s(defaultDevice):\n"%(deviceType)
            fileData+="\n"
            fileData+="    deviceType=\"%s\"\n"%(deviceType)
            fileData+="    devicePackage=\"%s\"\n"%(devicePackage)
            fileData+="        \n"
            fileData+="    def __init__(self,deviceID,deviceCFG={},restore=False):\n"
            fileData+="        \n"
            fileData+="        \n"
            fileData+="        defaultDevice.__init__(self,deviceID,deviceCFG,restore)\n"
            fileData+="        LOG.info(\"init %s finish, version %s, deviceID:%s\"%(__DEVICETYPE__,__version__,self.deviceID))"
            self.writeFile(devicefileName,fileData)
            py_compile.compile(os.path.normpath(devicefileName))
        except:
            raise coreException("can't not check if device file %s exists"%(devicefileName))
        