'''
Created on 01.01.2023

@author: uschoen
'''



__version__="0.1.0"
__author__="ullrich schoen"


# Standard library imports
import logging

# Local application constant
from .exception import formatException


LOG=logging.getLogger(__name__)

class formater(object):
    
    def __init__(self):
        '''
        Constructor
        '''
        self.__funktion={
        "hexTOdec":self.__hexTOdec,
        "reverseValue":self.__reverseValue,
        "x1000":self.__x1000,
        "x100000":self.__x100000
        }
        LOG.debug("__init formater finish with version:%s"%(__version__))
    
    def format(self,formating, value):
        '''
        format values
        
        formater=> name to format
        value=> value to format
        
        Exmaple:
        formaterClass=formater()
        decValue=formaterClass.format("hexTOdec","09D1")
        
        return: return the formated value
        '''
        try:
            if formating not in self.__funktion:
                raise formatException("formater function %s is not in list"%(formating))
            return self.__funktion[formating](value)
        except (formatException) as e:
            LOG.error("error in formater")
            raise e
        except (Exception) as e:
            LOG.error("unknown error in formater")
            raise Exception("unknown error in formater %s"%(e))
    
    def __reverseValue(self,value):
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
    
    def __x1000(self,value):
        '''
        multiplication a value with 1000
        
        value => var input value as dezimal
        
        Exmaple:
            dec=__x1000("20")
        
        return: a decimal value
        '''
        try:
            return  value*1000
        except Exception as e:
            raise formatException("some error in __x1000 %s"%(e))   
    
    def __x100000(self,value):
        '''
        multiplication a value with 100000
        
        value => var input value as dezimal
        
        Exmaple:
            dec=__x100000("20")
        
        return: a decimal value
        '''
        try:
            return  value*100000
        except Exception as e:
            raise formatException("some error in __x100000 %s"%(e))       
    
    def __hexTOdec(self,value):
        '''
        format a hexadizimal value to  decimal value
        
        value => var input value as HEX
        
        Exmaple:
            dec=HEXtoDEC("09D1")
        
        return: a decimal value
        '''
        try:
            return  int(value,base=16)
        except Exception as e:
            raise formatException("some error in __hexTOdec %s"%(e))    