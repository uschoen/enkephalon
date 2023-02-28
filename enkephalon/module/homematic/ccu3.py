'''
Created on 01.01.2023

@author: ullrich schoen
'''







'''
configuration file

        
'''

__version__='0.1.0'
__author__ = 'ullrich schoen'

# Standard library imports
import time
import re
import datetime
import logging
LOG=logging.getLogger(__name__)


# Local application imports
from module.defaultModul import defaultModul
from module.modulException import modulException
from module.homematic.xml_api import xml_api




DEFAULT_DEVICE_PACKAGE="homematic"
DEFAULT_CHANNEL_PACKAGE="homematic"
DEFAULT_CFG={
    "ccu3IP":"10.90.12.90",
    "xmlAPI":{
        "https":False,
    }
}
HMC_DEVICE_MAPPING={"device_type":"deviceType"
                    }

class ccu3(defaultModul):
    '''
    classdocs
    '''
    def __init__(self,objectID,modulCFG):
        # configuration 
        defaultCFG=DEFAULT_CFG
        defaultCFG.update(modulCFG)
        defaultModul.__init__(self,objectID,defaultCFG)   
        
        
        self.__xmlAPI=xml_api("ccu3Intance",{"ccu3IP":self.config['ccu3IP'],
                    "https":self.config['xmlAPI']["https"]
                    })
        
        LOG.info("build homematic.ccu3 modul, %s instance version: %s"%(__name__,__version__))
    
    
    def run(self):
        '''
        '
        '    client loop
        '
        '    exception:    none
        '
        '''
        try:
            LOG.info("%s start"%(self.config['objectID']))
            while not self.ifShutdown:
                ''' running or stop '''
                while self.running:
                    try:
                        '''
                        modul is start
                        '''
                        self.__updateDevices()
                        while (1):
                            '''
                            modul ist starting loop
                            '''
                            if not self.running:
                                ''' 
                                modul ist stop
                                '''
                                break 
                      
                        time.sleep(1)   
                    except(Exception) as e:
                        LOG.critical("unknown error in ccu3 %s"%(e),exc_info=True)
                        self.stopModul()
                    
                ''' shutdown '''    
                time.sleep(0.5)
            LOG.info("%s is shutdown"%(self.config['objectID']))
        except (Exception) as e:
            LOG.error("modul %s is stop with error %s"%(self.config['objectID'],e))
            
    def __updateDevices(self):
        try:
            LOG.info("retrieved devices from HM ")
            deviceList=self.__xmlAPI.retrievedDevices()
            devices={}  #all devices
            for device in deviceList['deviceList']['device']:
                deviceParameter={}
                deviceCFG={}
                channelData=[]
                for deviceKey,deviceValue in device.items():
                    '''
                    channels
                    '''
                    if deviceKey=="channel":
                        channelData=deviceValue
                        #LOG.debug("store channel parameter in temp channelData")
                    else:
                        '''
                        retrieved all device parameter
                        '''
                        deviceParameter[deviceKey.replace("@","")]=deviceValue
                        #LOG.debug("get device parameter %s:%s"%(deviceKey.replace("@",""),deviceValue))
                deviceParameter['devicePackage']=DEFAULT_DEVICE_PACKAGE
                deviceParameter['deviceType']= deviceParameter['device_type'].replace("-","_")
                deviceParameter['enable']=True
                '''
                build channels
                '''
                channelParameter={}
                channelsCFG={}
                if isinstance(channelData, dict):
                    
                    for channelKey,channelvalue in channelData.items():
                        '''
                        retrieved all channel parameter
                        '''
                        channelParameter[channelKey.replace("@","")]=channelvalue
                        #LOG.debug("get channel parameter %s:%s"%(channelKey.replace("@",""),channelvalue))
                    channelsCFG[channelParameter['address']]={
                            "channelPackage": DEFAULT_CHANNEL_PACKAGE,
                            "channelType": "%s_%s"%(deviceParameter['device_type'].replace("-","_"),channelParameter['type']),
                            "parameter":channelParameter
                    }
                    #LOG.debug("retrieved channel:%s type: %s"%(channelParameter['address'],channelsCFG[channelParameter['address']]))
                
                else:
                    for channels in channelData:
                        channelParameter={ }
                        
                        for channelKey,channelvalue in channels.items():
                            '''
                            retrieved all channel parameter
                            '''
                            channelParameter[channelKey.replace("@","")]=channelvalue
                            #LOG.debug("get channel parameter %s:%s"%(channelKey.replace("@",""),channelvalue))
                        channelsCFG[channelParameter['address']]={
                            "channelPackage": DEFAULT_CHANNEL_PACKAGE,
                            "channelType": "%s_%s"%(deviceParameter['device_type'].replace("-","_"),channelParameter['type']),
                            "parameter":channelParameter
                        }
                        #LOG.debug("retrieved channel:%s type: %s"%(channelParameter['address'],channelsCFG[channelParameter['address']]))
                
                deviceCFG={
                    "parameter":deviceParameter,
                    "channels":channelsCFG
                    }  
                objectID="%s@%s"%(deviceCFG['parameter']['address'],self.config['gatewayID'])
                LOG.debug("retrieved deviceID:%s deviceType:%s"%(objectID,deviceParameter['deviceType']))
                
                try:
                    self.core.addDevice(objectID, DEFAULT_DEVICE_PACKAGE, deviceParameter['deviceType'], deviceCFG, False)
                except (Exception) as e:
                    LOG.critical("can't add device %s error:%s"%(objectID,e), exc_info=True)
   
        except (Exception) as e:
            raise modulException("unknown error in __updateDevices %s"%(e),True)
        
        
        