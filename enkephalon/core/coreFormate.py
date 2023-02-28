'''
Created on 10 Dec 2022

@author: uschoen
'''
import logging


__version__='0.1.0'
__author__ = 'ullrich schoen'

LOG=logging.getLogger(__name__)
# Local application imports
from core.coreException import coreException




class coreFormater(object):
    '''
    classdocs
    '''
   

    def __init__(self):
        '''
        Constructor
        '''
        self.__funktion={
        "hexTOdec":self.__hexTOdec,
        "reverseValue":self.__reverseValue,
        "x1000":self.__x1000,
        "x100000":self.__x100000,
        "round2":self.__round2
        }
        LOG.info("__init %s finish, version %s"%(__name__,__version__))
    
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
                raise coreException("formater function %s is not in list"%(formating))
            return self.__funktion[formating](value)
        except (coreException) as e:
            LOG.error("error in formater")
            raise e
        except (Exception) as e:
            LOG.error("unknown error in formater")
            raise Exception("unknown error in formater %s"%(e))
    
    def __round2(self,value):
        '''
        formatted to a decimal number with 2 digits
        
        value => var input value as decimal
        
        Exmaple     
            dec=__round2("50.3232324242")
        
        return: a dezimal value with 2 digits
        '''
        try:
            return round(float(value),2)            
        except Exception as e:
            raise coreException("some error in __round2 value:%s, error:%s"%(value,e)) 
    
    def __reverseValue(self,value):
        '''
        reverse a value like 1/100
        
        value => var input value as decimal
        
        Exmaple:
            dec=__reverseValue("20")
        
        return: a decimal value
        '''
        try:
            return  1/value
        except Exception as e:
            raise coreException("some error in __reverseValue %s"%(e)) 
    
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
            raise coreException("some error in __x1000 %s"%(e))   
    
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
            raise coreException("some error in __x100000 %s"%(e))       
    
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
            raise coreException("some error in __hexTOdec %s"%(e))