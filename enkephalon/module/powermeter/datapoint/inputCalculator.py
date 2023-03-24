'''
Created on 01.01.2023

@author: ullrich schoen
'''
__version__='0.1.0'
__author__ = 'ullrich schoen'

# Standard library imports
import logging
LOG=logging.getLogger(__name__)


# Local application imports
from module.powermeter.datapoint.exception import errorException,valueError
from core.manager import manager


class tendencyValue(object):
    def __init__(self,dataPoint,cfg={}):
        try:
            self.core=manager()
            LOG.info("__init  package %s instance"%(__name__))
        except (Exception) as e:
            raise errorException("unknown error in __init__ for %s. error:%s"%(__name__,e))
    
    def calculate(self):
        '''
        ----
        calculate tendency between 2 or more values
                
        return value
        '''    
            
        try:
            if self.__readValue==None:
                self.__missingTendency+=1
            elif len(self.__dataqueue)==0:
                self.__missingTendency=0
                LOG.debug("calculation data type __calcTendency for data point %s. Given value:%s"%(self.__name,self.__readValue))
                self.__addValueToQueue(self.__readValue)
            else:
                start=self.__dataqueue[-1]
                end=self.__readValue
                for missingTendency in range(1,self.__missingTendency+1):
                    if start>end:
                        newValue=start-((abs(end-start))/(missingTendency+1))*missingTendency
                    else:
                        newValue=start+((abs(end-start))/(missingTendency+1))*missingTendency
                    LOG.debug("##calculation data type __calcTendency for data point %s. Given value:%s calc value:%s calcEntry:%s"%(self.__name,self.__readValue,newValue,missingTendency))
                    self.__addValueToQueue(newValue)
                self.__missingTendency=0
                LOG.debug("calculation data type __calcTendency for data point %s. Given value:%s"%(self.__name,self.__readValue))
                self.__addValueToQueue(self.__readValue)   
            self.__readValue=None
        except (Exception) as e:
            raise errorException("unknown error in __calcDUMMY from data point %s. error %s"%(self.__name,e))


class lastValue(object):
    def __init__(self,dataPoint,cfg={}):
        try:
            self.core=manager()
            LOG.info("__init  package %s instance"%(__name__))
        except (Exception) as e:
            raise errorException("unknown error in __init__ for %s. error:%s"%(__name__,e))
    
    def calculate(self):       
        try:
            newValue=self.__readValue
            if newValue==None:
                if len(self.__dataqueue)==0:
                    newValue=0
                else:
                    newValue=self.__dataqueue[-1]
            
            LOG.debug("calculation data type calcLastValue for data point %s. Given value:%s calc value:%s"%(self.__name,self.__readValue,newValue))
            self.__addValueToQueue(newValue)
            self.__readValue=None
        except (Exception) as e:
            raise errorException("unknown error in __calcLastValue from data point %s. error %s"%(self.__name,e))
        
class  averageValue(object): 
    def __init__(self,dataPoint,cfg={}):
        try:
            self.__intervall=cfg.get('interval', 10)
            self.core=manager()
            LOG.info("__init  package %s instance"%(__name__))
        except (Exception) as e:
            raise errorException("unknown error in __init__ for %s. error:%s"%(__name__,e))
    def calculate(self):
        '''
        calculation of the last 5 values the average     
        
        
        return value
        '''    
        try:
            newValue=self.__readValue
            if newValue==None:
                if len(self.__dataqueue)==0:
                    newValue=0  
                else:
                    newValue=sum(self.__dataqueue[-self.__intervall:]) / self.__intervall
            
            LOG.debug("calculation data type calcAverage (%s) for data point %s. Given value:%s calc value:%s"%(self.__intervall,self.__name,self.__readValue,newValue))
            self.__addValueToQueue(newValue)
            self.__readValue=None
        except (Exception) as e:
            raise errorException("unknown error in calcAverage (%s) from data point %s. error %s"%(self.__intervall,self.__name,e))