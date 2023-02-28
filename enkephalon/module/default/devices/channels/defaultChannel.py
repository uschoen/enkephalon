'''
Created on 01.01.2023

@author: uschoen
'''
# Standard library imports
import logging
import os
import time
import sys
# Local application constant
from core.manager import manager as coreManager
from core.coreException import coreException
from core.events.eventManager import eventManager


__version__="0.1.0"
__author__="ullrich schoen"

DEFAULT_CONFIGURATION_FILE = lambda channelPckage, channelType : {'parameter':{},
                            'events':{},
                            'CFGVersion':__version__,
                            'date':int(time.time()),
                            'channelPackage': channelPckage,
                            'channelType': channelType,
                            'name':"",
                            "parameter": {}
                            }


DEVICE_BASE_PATH="module"

LOG=logging.getLogger(__name__)

class defaultChannel(eventManager,object):
    
    channel_package="default"             #default device package
    channel_type="defaultChannel"     #default device type
     
    
    def __init__(self,deviceID,channelCFG={},restore=False):
        '''
        deviceID       the device ID how is bound
        channelName    name of the channel
        channelCFG     channel Configuration:
                        channelCFG={
                            'parameter': ...
                            'attribute': ...
                            'events': ...
                            }
        restore          default=False, if ture only restore data
        
        
        '''
        self.deviceID=deviceID
        self.channelName=channelCFG.get('name','unknown')
        self.core=coreManager()
        '''
        absoloute path
        '''
        self.rootPath=("%s/%s"%(os.getcwd(),os.path.dirname(sys.argv[0])))
        '''
        confonfiuration file
        '''
        self.configFile=os.path.normpath("%s/%s/%s/devices/channels/%s.json"%(self.rootPath,DEVICE_BASE_PATH,self.channel_package.replace(".","/"),self.channel_type))
        
        self.__ifConfigLoad=False
        self.__currentCFG={}
        
        '''
        default device parameter
        '''
        self.parameter={
            'name':("%s.%s"%(self.channelName,self.deviceID)),
            'enable':False,
            'value':0,
            'channelPackage':self.channel_package,
            'channelType':self.channel_type,
            'CFGVersion':__version__
            }
        
        '''
        LOAD channel parameter
        #####################
        load json parameter
        '''
        self.parameter.update(self.loadConfiguration().get("parameter",{}))
        '''
        update customer parameter
        '''
        self.parameter.update(channelCFG.get('parameter',{}))
        
        '''
        overwrite the parameter
        '''
        self.parameter['CFGVersion']=__version__
        self.parameter['channelPackage']=self.channel_package
        self.parameter['channelType']=self.channel_type
        ''' 
        LOAD Events
        '''
        eventManager.__init__(self,channelCFG.get('events',{}),restore)    
        
        
        LOG.info("init defaultChannel %s finish, version %s, deviceID:%s"%(self.channelName,__version__,self.deviceID))
    
    
    def updateChannel(self,channelCFG={}):
        
        try:
            '''
            update customer parameter
            '''
            self.parameter.update(channelCFG.get('parameter',{}))
            '''
            overwrite the parameter
            '''
            self.parameter['CFGVersion']=__version__
            self.parameter['channelPackage']=self.channel_package
            self.parameter['channelType']=self.channel_type
            ''' 
            LOAD Events
            '''
            self.updateEvents(channelCFG.get('events',{}))    
        except (Exception) as e:
            raise coreException("unknown error in updateChannel: %s"%(e)) 
        
    def loadConfiguration(self,refresh=False):
        '''
        loading configuration file
        
        refresh= if true reload the file configuration
                 if false use old configuration
                 default false
        
        return a Dictionary
        
        exception: baseDevice
        '''
        try:
            if not self.__ifConfigLoad or refresh:
                if not self.core.ifPathExists(os.path.dirname(self.configFile)):
                    self.core.makeDir(os.path.dirname(self.configFile))
                if not self.core.ifFileExists(self.configFile):
                    self.core.writeJSON(self.configFile,DEFAULT_CONFIGURATION_FILE(self.channel_package,self.channel_type))
                LOG.debug("load device configuration file %s"%(self.configFile))
                self.__currentCFG = self.core.loadJSON(self.configFile)
            self.__ifConfigLoad=True
            return self.__currentCFG
        except IOError:
            raise coreException("can not find file: %s "%(self.configFile))
        except ValueError:
            raise coreException("error in json file: %s "%(self.configFile))
        except:
            raise coreException("unknown error to read json file %s"%(self.configFile)) 
           
    def getParameter(self,parameterName=None):
        """
        get one or all parameter back
        
        @var parameterName: string name of the parameter
        
        @return: dic/string return one[string] or all[dic] parameter
        """
        if parameterName==None:
            return self.parameter
        else:
            if parameterName not in self.parameter:
                raise coreException("can't find parameter name %s in device:%s channel:%s"%(parameterName,self.deviceID,self.channelName))
            return self.parameter.get(parameterName,{})
    
    def getChannelConfiguration(self):
        try:
            channelCFG={"channelPackage": self.channel_package,
                        "channelType": self.channel_type,
                        "events": self.getEventConfiguration(),
                        "parameter": self.getParameter()
                        }
            return channelCFG
        except:
            raise coreException("unknown error in getChannelConfiguration",True)       
        
    def getValue(self):
        return self.parameter['value']
    
    def setValue(self,
                 value):
        try:
            if value!=self.parameter['value']:
                self.parameter['value']=value
                self.events['onchange'].callCallers(self)
                self.events['onrefresh'].callCallers(self) 
            else:
                self.parameter['value']=value
                self.events['onrefresh'].callCallers(self) 
        except:
            raise coreException("unknown error in setValue",True)     
    
    def ifEnable(self):
        '''
        check if the channel enable
        
        enable=true
        disable=false
        
        '''
        try:
            return self.parameter['enable']
        except:
            raise coreException("unknown error ifChannelEnable")
    