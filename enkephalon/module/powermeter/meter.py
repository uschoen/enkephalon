'''
Created on 01.01.2023

@author: ullrich schoen
'''
__version__='0.1.8'
__author__ = 'Ullrich Schoen'

# Local application imports
from module.powermeter.exception import errorException,cfgException
from module.defaultModul import defaultModul
from module.powermeter import ehzPotocol
from module.powermeter.datapoint import dataPoint

# Standard library imports
import time
import logging
LOG=logging.getLogger(__name__)



'''
default configuration for the modul. This 
value can be overwrite with the modulCFG parameter
'''
DEFAULT_CFG={
    "protocol":{},
    "serial":{}
}


'''
ehz protocol class
'''
EHZ_PROTOCOL={
    "D0":ehzPotocol.d0,
    "SML":ehzPotocol.sml
}            

'''
data Points json File name from script base
'''
DATA_POINTS_FILE="module/powermeter/datapoints.json"


class meter(defaultModul):
    '''
    classdocs
    '''
    def __init__(self,objectID,modulCFG):
        '''
        
        meter class to measure powermeter
        
        global variable:
        self.__dataPoints        store the data point
        self.__Serial            serial object
        
        '''
        try:
            # configuration 
            defaultCFG=DEFAULT_CFG
            defaultCFG.update(modulCFG)
            defaultModul.__init__(self,objectID,defaultCFG)
            
            self.deviceID="powermeter@%s"%(self.config["gatewayID"])
                      
            # data points objects
            self.__dataPoints={}
            
            # input protocol
            self.__ehzProtocolType=modulCFG["protocol"].get("type",None)
            if  self.__ehzProtocolType not in EHZ_PROTOCOL:
                raise cfgException("configuration error in protokcol.type:%s . possible value are %s"%(self.__ehzProtocolType,EHZ_PROTOCOL.keys())) 
            self.__ehzProtocol=EHZ_PROTOCOL[self.__ehzProtocolType](modulCFG["protocol"].get("cfg",{}))
                        
            LOG.info("build powermeter.meter modul, %s instance"%(__name__))   
        except (Exception) as e:
            raise errorException("unknown error in __init__ for %s. error:%s"%(__name__,e))
    
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
                    '''
                    start up the modul
                    '''
                    try:   
                        ehzData=self.__ehzProtocol.getData(self.running)
                        if ehzData:
                            pass
                    except (Exception) as e:
                        LOG.critical("modul %s is stop with error %s"%(self.config['objectID'],e))
                    finally:
                        self.__closeSerial()    
                # modul is stopped
                time.sleep(0.5)
            
            # modul is shutdown
            LOG.info("%s is shutdown"%(self.config['objectID']))
        except (Exception) as e:
            LOG.critical("modul %s is shutdown with error %s"%(self.config['objectID'],e))  
              
    def runModul(self):
        '''
        '
        '    start modul
        '
        '    exception: none
        '
        '''
        try:
            self.__buildDataPoints()
            defaultModul.runModul()
        except (Exception) as e:
            raise errorException("unknown error in modul %s runModul. Error %s"%(self.config['objectID'],e))
    
    def stopModul(self):
        '''
        '
        '    stop modul
        '
        '    exception: none
        '
        '''
        try:
            self.__closeSerial() 
            defaultModul.stopModul()
        except (Exception) as e:
            LOG.critical("unknown error in modul %s stopModul. Error:%s"%(self.config['objectID'],e))
    
     
    
    def __buildDataPoints(self):
        '''
        build the data point object
        
        build the data point object from the datapoints.json file in
        .powermeter/datapoints.json ad store the objects in self.__dataPoints.
        
        exception: powermeter.errorException
        '''
        try:
            # delete all old data points
            self.__dataPoints={}
            # load data point configuration file 
            datapoints=self.core.loadJSON(self.core.rootPath+"/"+DATA_POINTS_FILE) 
            LOG.debug("read data point file %s for modul %s"%(self.core.rootPath+"/"+DATA_POINTS_FILE,self.config['objectID']))  
            # build data points
            for (dataPointName,dataPointCFG) in datapoints.item():
                LOG.debug("add data point  %s for modul %s"%(dataPointName,self.config['objectID']))
                self.__dataPoints[dataPointName]=dataPoint(dataPointName,dataPointCFG)
        except (Exception) as e:
            raise errorException("unknown error in modul %s__buildDataPoints. error: %s"%(self.config['objectID'],e))  
   