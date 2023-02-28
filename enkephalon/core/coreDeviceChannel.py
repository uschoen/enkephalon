'''
Created on 01.01.2023

@author: uschoen
'''


__version__='0.1.0'
__author__ = 'ullrich schoen'

# Standard library imports
import logging
from threading import Thread

# Local application imports
from core.coreException import coreException


DEVICE_BASE_PATH="module"      #device base path
DEFAULT_DEVICE_PACKGAE="default"             #default device packgae
DEFAULT_DEVICE_TYPE="defaultDevice"      #default device type
LOG=logging.getLogger(__name__)

class coreDeviceChannel():
    '''
    core events function
    '''
    def __init__(self,*args):
        
        LOG.info("__init core channels finish, version %s"%(__version__))
    
    def setDeviceChannelValue(self,
                              objectID,
                              channelName,
                              value):
        if not self.ifDeviceIDExists(objectID):
            raise coreException("deviceID %s is not exist"%(objectID),False)
        try: 
            self.startThread(target=self.devices[objectID].setChannelValue, args=(channelName, value))
        except:
            raise coreException("can't setDeviceChannelValue  deviceID %s"%(objectID))
    
    def getDeviceChannelValue(self,
                              objectID,
                              channelName):
        if not self.ifDeviceIDExists(objectID):
            raise coreException("deviceID %s is not exist"%(objectID),False)
        try: 
            return self.devices[objectID].getChannelValue(channelName)
        except:
            raise coreException("can't getDeviceChannelValue  deviceID %s"%(objectID))
        
    def addDeviceChannel(self,
                         objectID,
                         channelName,
                         channelCFG={}
                         ):
        
        if not self.ifDeviceIDExists(objectID):
            raise coreException("deviceID %s is not exist"%(objectID),False)
        if self.devices[objectID].ifDeviceChannelExist(channelName):
            raise coreException("channel name %s in deviceID %s is  exist"%(channelName,objectID),True)
        try:
            restore=False
            self.devices[objectID].addChannel(channelName,channelCFG,restore)
        except (Exception) as e:
            raise Exception("can't add channel %s msg:%s"%(channelName,e))   
    
    def ifDeviceChannelExist(self,
                                 objectID,
                                 channelName
                                 ):
        '''
            check if a channel exists for this device 
            
            objectID: the device id to check if enable
            channelName: Channel Name
            
            return: 
                true if device enable
                false if no device disable
            
            exception:
                coreDeviceExecption
        '''
            
        if not self.ifDeviceIDExists(objectID):
            raise coreException("deviceID %s is not exist"%(objectID),False)
        try: 
            return self.devices[objectID].ifDeviceChannelExist(channelName)
        except:
            raise coreException("some errer in ifDeviceChannelExist for deviceID %s"%(objectID))