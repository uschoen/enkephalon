'''
Created on 01.01.2023

@author: ullrich schoen
'''

from core.coreException import coreException
from core.coreException import modulException



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

try:
    import serial       #@UnresolvedImport 
except:
    LOG.critical('no serial modul installed. use: "sudo pip3 install pyserial" to install')
    raise modulException

# Local application imports
from module.defaultModul import defaultModul




DEFAULT_CFG={
    "costs":0.35,
    "consum":{
                "hour":{
                    "counter":0,
                    "actualTime":0
                    },
                "day":{
                    "counter":0,
                    "actualTime":0
                    },
                "week":{
                    "counter":0,
                    "actualTime":0
                    },
                "month":{
                    "counter":0,
                    "actualTime":0
                    },
                "year":{
                    "counter":0,
                    "actualTime":0
                    }             
                },
    "dataMapping":{},
    "serial":{
        "port":'/dev/ttyUSB0',
        "baudrate":9600,
        "parity":'E',
        "stopbits":1,
        "bytesize":7,
        "timeout":2, 
        "xonxoff":False, 
        "rtscts":False, 
        "dsrdtr":False
                }
            }
STARTMARKER='/'
STOPMARKER='!'
DEFAULT_DEVICE_PACKAGE="powermeter"
DEFAULT_DEVICE_TYP="meter"
DEFAULT_CHANNEL_PACKAGE="powermeter"

INTERNAL_MEASURING_POINTS=["voltageAll",
                           "powerAll",
                           "powerAvg",
                           "powerMax",
                           "consumActualDay",
                           "consumActualHour",
                           "consumActualWeek",
                           "consumActualMonth",
                           "consumActualYear"
                          ]

class meter(defaultModul):
    '''
    classdocs
    '''
    def __init__(self,objectID,modulCFG):
        # configuration 
        defaultCFG=DEFAULT_CFG
        defaultCFG.update(modulCFG)
        defaultModul.__init__(self,objectID,defaultCFG)
        
        self.__buildSerial(self.config['serial'])
        self.deviceID="powermeter@%s"%(self.config["gatewayID"])
        '''
        internal measuring points
        
        
        '''
        self.__measuringPoints={}
        self.__buildInternalMeasuringPoints()
        
        self.__searchStrings=[]
        self.__buildSearchStringFromdataMapping()
        
        LOG.info("build powermeter.meter modul, %s instance"%(__name__))    
    
    def __buildInternalMeasuringPoints(self):
        try:
            for internalPoint in INTERNAL_MEASURING_POINTS:
                self.__measuringPoints[internalPoint]={
                    "lastValue":0,
                    "coreValue":0
                }
        except Exception as e:
            raise e
    
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
                data_raw=b''
                start=True
                while self.running:
                    try:   
                        self.__findStart()
                        start=True
                        LOG.info("get data from powermeter")
                        while (1):
                            if not self.running:
                                break
                            data_raw = self.__serial.readline()
                            data_raw=data_raw[:-2]
                            data_str=data_raw.decode("utf-8") 
                            if start:
                                LOG.debug("ehzName: %s"%(data_str))
                                self.deviceID="%s@%s"%(data_str,self.config["gatewayID"])
                                self.__updateDeviceChannel("ehzName",data_str)
                                start=False
                                continue
                            elif data_str=="":
                                '''
                                empty string or lf /rt
                                '''
                                continue
                            elif data_str==STOPMARKER:
                                '''
                                stop marker found
                                '''
                                LOG.debug("find end data: %s"%(STOPMARKER))
                                break
                            '''
                            search after data points
                            '''
                            dataPointItem=False
                            dataPointKey=False
                            for dataPointKey,dataPointItem in self.config['dataMapping'].items():
                                if dataPointItem['find'] in data_str:     
                                    '''
                                    Example:
                                    dataPointItem:{
                                        "find":"1-0:61.7.255*255",
                                        "format":["round2"],
                                        "unit":"A"
                                        }
                                    
                                        or
                                        FLASE
                                    '''
                                    
                                    '''
                                    delete find data and control strings
                                    '''
                                    data=data_str.replace(dataPointItem['find'],"")
                                    data=(re.sub("\(|\)|:|\*|[AVW]|L[123]", "", data))
                                    '''
                                    format data if need
                                    '''
                                    try:
                                        for formatCMD in dataPointItem["format"]:
                                            data=self.core.format(formatCMD,data)
                                        
                                        LOG.debug("find  data: %s=>%s original:%s"%(dataPointKey,data,data_str))
                                        self.__updateDeviceChannel(dataPointKey,data)
                                    except Exception as e:
                                        LOG.critical("error for data Point %s in formater :%s"%(dataPointKey,e))
                        self.__calcData()
                        LOG.debug("End of telegram, wait for next data")
                    except(Exception) as e:
                        LOG.critical("unknown error in powermeter %s"%(e),exc_info=True)
                        self.stopModul()
                    
                ''' shutdown '''    
                time.sleep(0.5)
            LOG.info("%s is shutdown"%(self.config['objectID']))
        except (Exception) as e:
            LOG.error("modul %s is stop with error %s"%(self.config['objectID'],e))
    
    def __buildSearchStringFromdataMapping(self):
        try:
            LOG.info("build search String")
            for measuringPointsKeys in self.config['dataMapping']:
                self.__searchStrings.append(self.config['dataMapping'][measuringPointsKeys]['find'])   
        except Exception as e:
            raise modulException("unknown error in buildInternalMeasuringPoints %s"%(e),True)
        
    def __calcData(self):
        '''
        calculation from 
        voltageAll: voltage1+voltage2+voltage3 (A)
        powerAll: power1+power2+power3 (W)
        
        '''
        try:
            try:
                #voltageAll (A)
                voltageAll=round(self.__measuringPoints["voltageL1"]["lastValue"]+self.__measuringPoints["voltageL2"]["lastValue"]+self.__measuringPoints["voltageL3"]["lastValue"],2)
                LOG.debug("find  data: voltageAll=>%s "%(voltageAll))
                self.__updateDeviceChannel("voltageAll",voltageAll)
            except (Exception) as e:
                LOG.critical("some unknown error in calc voltageAll msg:%s"%(e),exc_info=True)                    
            if not self.running:
                return
            try:
                #powerAll (W)
                powerAll= round(self.__measuringPoints["powerL1"]["lastValue"]+self.__measuringPoints["powerL2"]["lastValue"]+self.__measuringPoints["powerL3"]["lastValue"],2)
                LOG.debug("find  data: powerAll=>%s "%(powerAll))
                self.__updateDeviceChannel("powerAll",powerAll)
            except (Exception) as e:
                LOG.critical("some unknown error in calc voltageAll msg:%s"%(e),exc_info=True)
            
            try:
                #powerMax
                if self.__measuringPoints["powerMax"]["lastValue"]<self.__measuringPoints["powerAll"]["lastValue"]:
                    self.__measuringPoints["powerMax"]["lastValue"]=round(self.__measuringPoints["powerAll"]["lastValue"],2)
                    LOG.debug("find  data: powerMax=>%s "%(self.__measuringPoints["powerMax"]["lastValue"]))
                    self.__updateDeviceChannel("powerMax",self.__measuringPoints["powerMax"]["lastValue"])
            except (Exception) as e:
                LOG.critical("some unknown error in calc powerMax msg:%s"%(e),exc_info=True)  
            
            try:
                #powerAvg
                self.__measuringPoints["powerAvg"]["lastValue"]=round((self.__measuringPoints["powerAll"]["lastValue"]+self.__measuringPoints["powerAvg"]["lastValue"])/2,2)
                LOG.debug("find  data: powerAvg=>%s "%(self.__measuringPoints["powerAvg"]["lastValue"]))
                self.__updateDeviceChannel("powerAvg",self.__measuringPoints["powerAvg"]["lastValue"])
            except (Exception) as e:
                LOG.critical("some unknown error in calc powerAvg msg:%s"%(e),exc_info=True)   
            '''
            first start set the actual consum for all points
            '''
            now = datetime.datetime.now()
            year, week_num, day_of_week=datetime.date.today().isocalendar()
            actualConsumCounter=self.__measuringPoints["consum"]["lastValue"]
            if self.config["consum"]["hour"]["counter"]==0:
                LOG.info("set initial value for consum last and actual value")
                self.config["consum"]={
                    "hour":{
                        "counter":actualConsumCounter,
                        "actualTime":now.hour
                        },
                    "day":{
                        "counter":actualConsumCounter,
                        "actualTime":now.day
                        },
                    "week":{
                        "counter":actualConsumCounter,
                        "actualTime":week_num
                        },
                    "month":{
                        "counter":actualConsumCounter,
                        "actualTime":now.month
                        },
                    "year":{
                        "counter":actualConsumCounter,
                        "actualTime":year
                        }             
                    }
            
            consumInterval=self.config['consum']
            '''
            consum hour
            '''
            interval="hour"
            channelIDNow="consumActualHour"
            channelIDLast="consumLastHour"
            value=round(float(actualConsumCounter)-float(consumInterval[interval]["counter"]),2)
            LOG.debug("find  data: %s=>%s "%(channelIDNow,value))
            self.__updateDeviceChannel(channelIDNow, value, True)
            if not consumInterval[interval]["actualTime"]==now.hour:
                '''
                new hour interval
                '''
                #copy actual count to Last
                LOG.debug("find  data: %s=>%s "%(channelIDLast,value))
                self.__updateDeviceChannel(channelIDLast, value, True)
                #start new Interval
                consumInterval[interval]={
                    "counter":actualConsumCounter,
                    "actualTime":now.hour
                    }
                LOG.debug("find  data: %s=>%s "%(channelIDNow,0))
                self.__updateDeviceChannel(channelIDNow, 0, True)
            if not self.running:
                return   
            '''
            consum day
            '''
            interval="day"
            channelIDNow="consumActualDay"
            channelIDLast="consumLastDay"
            value=round(float(actualConsumCounter)-float(consumInterval[interval]["counter"]),2)
            LOG.debug("find  data: %s=>%s "%(channelIDNow,value))
            self.__updateDeviceChannel(channelIDNow, value, True)
            if not consumInterval[interval]["actualTime"]==now.day:
                '''
                new hour interval
                '''
                #copy actual count to Last
                LOG.debug("find  data: %s=>%s "%(channelIDLast,value))
                self.__updateDeviceChannel(channelIDLast, value, True)
                #start new Interval
                consumInterval[interval]={
                    "counter":actualConsumCounter,
                    "actualTime":now.day
                    }
                LOG.debug("find  data: %s=>%s "%(channelIDNow,0))
                self.__updateDeviceChannel(channelIDNow, 0, True)
            if not self.running:
                return
            '''
            consum week
            '''
            interval="week"
            channelIDNow="consumActualWeek"
            channelIDLast="consumLastWeek"
            value=round(float(actualConsumCounter)-float(consumInterval[interval]["counter"]),2)
            LOG.debug("find  data: %s=>%s "%(channelIDNow,value))
            self.__updateDeviceChannel(channelIDNow, value, True)
            if not consumInterval[interval]["actualTime"]==week_num:
                '''
                new hour interval
                '''
                #copy actual count to Last
                LOG.debug("find  data: %s=>%s "%(channelIDLast,value))
                self.__updateDeviceChannel(channelIDLast, value, True)
                #start new Interval
                consumInterval[interval]={
                    "counter":actualConsumCounter,
                    "actualTime":week_num
                    }
                LOG.debug("find  data: %s=>%s "%(channelIDNow,0))
                self.__updateDeviceChannel(channelIDNow, 0, True)
            if not self.running:
                return
            '''
            consum month
            '''
            interval="month"
            channelIDNow="consumActualMonth"
            channelIDLast="consumLastMonth"
            value=round(float(actualConsumCounter)-float(consumInterval[interval]["counter"]),2)
            LOG.debug("find  data: %s=>%s "%(channelIDNow,value))
            self.__updateDeviceChannel(channelIDNow, value, True)
            if not consumInterval[interval]["actualTime"]==now.month:
                '''
                new hour interval
                '''
                #copy actual count to Last
                LOG.debug("find  data: %s=>%s "%(channelIDLast,value))
                self.__updateDeviceChannel(channelIDLast, value, True)
                #start new Interval
                consumInterval[interval]={
                    "counter":actualConsumCounter,
                    "actualTime":now.month
                    }
                LOG.debug("find  data: %s=>%s "%(channelIDNow,0))
                self.__updateDeviceChannel(channelIDNow, 0, True)
            if not self.running:
                return
            '''
            consum year
            '''
            interval="year"
            channelIDNow="consumActualYear"
            channelIDLast="consumLastYear"
            value=round(float(actualConsumCounter)-float(consumInterval[interval]["counter"]),2)
            LOG.debug("find  data: %s=>%s "%(channelIDNow,value))
            self.__updateDeviceChannel(channelIDNow, value, True)
            if not consumInterval[interval]["actualTime"]==year:
                '''
                new hour interval
                '''
                #copy actual count to Last
                LOG.debug("find  data: %s=>%s "%(channelIDLast,value))
                self.__updateDeviceChannel(channelIDLast, value, True)
                #start new Interval
                consumInterval[interval]={
                    "counter":actualConsumCounter,
                    "actualTime":year
                    }
                LOG.debug("find  data: %s=>%s "%(channelIDNow,0))
                self.__updateDeviceChannel(channelIDNow, 0, True)    
        
        except Exception as e:
            LOG.critical("unknown error in __calcData %s"%(e),True)
            
    def __findStart(self):
        while (1):
            if not self.running:
                break
            data_bin = self.__serial.read(1)
            data_str=data_bin.decode("utf-8") 
            if data_str==STARTMARKER:
                LOG.debug("find start data :%s"%(STARTMARKER))
                break
        return    
    
    def __createMeasuringPoint(self,measuringPoint):
        '''
        create measuring points internal and in core devices
        '''
        try:
            '''
            check if device  exist
            '''
            if not self.core.ifDeviceIDExists(self.deviceID):
                self.__addDevice()
            '''
            check if channel  exist
            '''
            if not self.core.ifDeviceChannelExist(self.deviceID,measuringPoint):
                self.__addChannel(measuringPoint)
            '''
            check if internal  exist
            '''
            if not measuringPoint in self.__measuringPoints:
                self.__measuringPoints[measuringPoint]={
                    "lastValue":0,
                    "coreValue":self.core.getDeviceChannelValue(self.deviceID,measuringPoint)
                }
        except:
            raise modulException("unknown error in createMeasuringPoint")
    
    
    def __updateDeviceChannel(self,channelID,value,forceupdate=False):
        try:
            self.__createMeasuringPoint(channelID)
            '''
            check if value have change
            '''
            self.__measuringPoints[channelID]['lastValue']=value
            LOG.debug("%s: new value %s = old value %s"%(channelID,value,self.__measuringPoints[channelID]['coreValue']))
            if not value==self.__measuringPoints[channelID]['coreValue'] or forceupdate :
                self.core.setDeviceChannelValue(self.deviceID,channelID,value)
                self.__measuringPoints[channelID]['coreValue']=value
                
        except Exception as e:
            LOG.critical("unknown error in updateDeviceChannel %s"%(e),True)
    
    def __addChannel(self,channelID):
        try:
            channelCFG={"channelPackage":DEFAULT_CHANNEL_PACKAGE,
                        "channelType":channelID}
            self.core.addDeviceChannel(self.deviceID,channelID,channelCFG)
        except Exception as e:
            raise coreException ("unknown error in addChannel %s"%(e))
    
    def __addDevice(self):
        try:
            deviceCFG={}
            self.core.addDevice(self.deviceID, DEFAULT_DEVICE_PACKAGE, DEFAULT_DEVICE_TYP, deviceCFG)
        except Exception as e:
            raise coreException("unknown error in addDevice %s"%(e))
   
    def __buildSerial(self,serialCFG):
        try:
            self.__serial = serial.Serial(
                port=serialCFG['port'],
                baudrate=serialCFG['baudrate'],
                parity=serialCFG['parity'],
                stopbits=serialCFG['stopbits'],
                bytesize=serialCFG['bytesize'],
                timeout=serialCFG['timeout'],
                xonxoff=serialCFG['xonxoff'],
                rtscts=serialCFG['rtscts'],
                dsrdtr=serialCFG['dsrdtr']
                )
            self.__serial.flushInput()
            self.__serial.flushOutput()
        except serial.serialutil.SerialException as e:
            LOG.error("Error reading serial port: %s" % (e,))
            raise Exception
        except:
            LOG.critical("unknown error in power meter",True)
            