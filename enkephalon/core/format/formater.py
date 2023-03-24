'''
Created on 01.01.2023

@author: uschoen
'''
__version__="0.1.0"
__author__="ullrich schoen"


# Standard library imports
import logging
import sys,os

LOG=logging.getLogger(__name__)
sys.path.append("%s"%(os.getcwd()))

# Local application constant
from core.format.exception import scriptException,formatException,configException





class formater(object):
    
    def __init__(self):
        '''
        Constructor
        '''
        self.__FormatFunction={
        "round":self.__round,
        "hexTOdec":self.__hexTOdec,
        "reverseValue":self.__reverseValue,
        "multiply":self.__multiply
        }
        LOG.debug("__init formater finish with version:%s"%(__version__))
    
    def format(self,formatCMD={}, value=""):
        '''
        format values and give the value back
        
        format=> dictionary :{"command":{optional cfg}
        value=> value to format
        
        Exmaple:
        formaterClass=formater()
        
        format={"rnd":{2}}
        value=9.998
        
        decValue=formaterClass.format(format,value)
        
        return: return the formated value
        '''
        try:
            newVlaue=value
            for formatCommand in formatCMD:
                for fCommand,fCommandValue in formatCommand.items():
                    if fCommand not in self.__FormatFunction:
                        raise configException("format %s is not a format function [%s]"%(formatCMD,list(self.__FormatFunction.keys())))
                    newVlaue=self.__FormatFunction[fCommand](fCommandValue,newVlaue)
            return newVlaue
        except (formatException,configException) as e:
            raise e
        except (Exception) as e:
            raise scriptException("unknown error in formater %s"%(e))
    
    def __reverseValue(self,cfg="",value=""):
        '''
        reverse a value like 1/100
        
        value => var input value as dezimal
        
        Exmaple:
            dec=__reverseValue("20")
        
        return: a decimal value
        '''
        try:
            return  1/value
        except Exception as e:
            raise formatException("some error in __reverseValue %s"%(e)) 
    
    def __round(self,cfg=2,value=""):
        '''
        formatted to a decimal number with 2 digits
        
        value => var input value as decimal
        
        Exmaple     
            dec=__round2("50.3232324242")
        
        return: a dezimal value with 2 digits
        '''
        try:
            return round(float(value),cfg)            
        except Exception as e:
            raise scriptException("some error in __round2 cfg:%s , value:%s, error:%s"%(cfg,value,e)) 
        
    def __multiply(self,cfg=1,value=""):
        '''
        multiplication a value with x
        
        cfg => int for multiply
        value => var input value as dezimal
        
        Exmaple:
            dec=__multiply("3","20")
        
        return: a decimal value
        '''
        try:
            return  value*cfg
        except Exception as e:
            raise scriptException("some error in __multiply %s"%(e))   
       
    
    def __hexTOdec(self,cfg=16,value=""):
        '''
        format a hexadizimal value to  decimal value
        
        value => var input value as HEX
        
        Exmaple:
            dec=HEXtoDEC("09D1")
        
        return: a decimal value
        '''
        try:
            return  int(value,base=cfg)
        except Exception as e:
            raise scriptException("some error in __hexTOdec %s"%(e))    
        
        
if __name__ == '__main__':
    formatCMD=[{"round":3},{"round":2}]
    value=9.92773
    formaterOBJ=formater()
    print (formaterOBJ.format(formatCMD, value))