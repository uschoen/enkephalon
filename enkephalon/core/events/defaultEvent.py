'''
Created on 01.01.2023

@author: uschoen
'''

__version__='0.1.0'
__filename__='events/defaultEvent.py'
__author__ = 'uschoen'




# Standard library imports
import logging
import time
from copy import deepcopy

# Local application imports
from core.events.exception import eventError
from core.manager import manager

DEFAULT_CALLER={
    "caller":None,
    "parameter":None
    }

LOG=logging.getLogger(__name__)


class defaultEvent(object):
    '''
    classdocs

    eventCFG={
        'parameter':{....}
        'callers':{...}
        
    
        parameter:{
            CFGVersion= int    default  __version__ from script, can't change
            eventName= var     default name from event, can't change
            timestamp= int     default time at __init__ can't change
        }   
        callers:{
        
        }
    restore= true/false    default false
    '''
    eventName="defaultEvent"
    
    def __init__(self,eventCFG={},restore=False):
        
        self.callers={}
        self.parameter={}
        self.core=manager()
        
        ### Parameter ###
        ''' 
        update parameter from eventCFG{'parameter'}
        '''
        self.parameter.update(eventCFG.get('parameter',{}))
        '''
        fixed parameter
        '''
        self.parameter["CFGVersion"]=__version__,
        self.parameter["eventName"]=self.eventName,
        self.parameter["timestamp"]=int(time.time())
        
        self.callers.update(eventCFG.get('callers',{}))
        
        LOG.debug("init %s finish, version %s"%(self.eventName,__version__))
    
    def getParameter(self):
        '''
        return the Parameter
        
        return dic
        '''
        return self.parameter 
    
    def getCallers(self):
        '''
        return the callers
        
        return: dic
        '''
        return self.callers
    
    def updateParameter(self,eventParameter):
        '''
        update the parameter of the event
        
        update existing parameter and add new one if they not exists
        
        parameter: dic            a list of parameter
                                  {
                                  'name':"unknown",
                                  'objectID':"unknown",
                                  'lastcall':0
                                  }
        
        exception: eventError
        '''
        try:
            self.parameter.update(eventParameter)
            LOG.debug("update event %s parameter"%(self.eventName))
        except:
            raise eventError("some error in updateParameter",True)
        
    def updateCallers(self,callers):
        '''
        update one or mor caller 
        
        update one or more caller. Error for one caller was ignored
        
        callers = dic            Caller an parameters
                                 "mysql"{
                                        "caller":None,
                                        "parameter":None
                                        }
        exception: eventError
        '''
        try:  
            for callerName in callers:
                try:
                    self.updateCaller(callerName, callers[callerName])
                except eventError as e:
                    LOG.error("updateCaller %s have an error : %s"%(callerName,e.msg))
        except:
            raise eventError("some error in updateCallers",True) 
            
    def updateCaller(self,callerName,callerCFG):
        '''
        update a event caller configuration
        
        if the callerName exists, overwirte the old configration
        
        callerName = string        name of the caller
                                   "mysql"
        callerCFG = dic            configurtion of the caller
                                   {
                                    "caller":None,
                                    "parameter":None
                                   }
        
        exception: eventError
        '''
        try:
            if callerName not in self.callers:
                self.callers[callerName]=DEFAULT_CALLER
            self.callers[callerName]=callerCFG
            LOG.debug("update event %s caller: %s"%(self.eventName,callerName))
        except:
            raise eventError("some error in updateCaller",True)
    
    def ifCallerExists(self,callerName):
        '''
        check if the caller name exists
        
        modulName: the modul to check
        
        return: true/false
        
        exception: eventError
    
        '''
        try:
            if callerName in self.callers:
                return True
            return False 
        except:
            raise eventError("some error in ifModulExitst",True)
    
    def callCallers(self,callerObject={}):
        '''
        
        callerObject is the object that have request the function.
        most a device object
        
        callerObjects: object 
        
        '''
        LOG.debug("event %s check callers"%(self.eventName))
        try:
            for caller in self.callers:
                try:
                    callerArgs=self.callers[caller]
                    LOG.debug("executeCaller %s with args: %s"%(caller,callerArgs))
                    self.executeCaller(callerArgs,callerObject)
                except:
                    LOG.error("can't execute caller %s"%(caller))
        except:
            raise eventError("some error in callCallers",True)    
    
    def executeCaller(self,args,callerObject={}):
        '''
        args are the arguments to call a function and the args for the function
        callerObject is the object that have request the function.
        most a device object
        
        "args":{
            "callfunktion": "some funktion",   function to call
            "args": {...}                      argument for the function
            
        callerObject: object       
        
        '''
        try:
            LOG.debug("call function %s"%(args.get('callFunction',"unknown")))
            methodToCall = getattr(self.core,args['callFunction'])
        except:
            raise eventError("call function %s not found"%(args.get('callFunction',"unknown")))
        arguments={}
        arguments=deepcopy(args.get('args',{}))
        arguments["callerObject"]=callerObject
        
        try:
            '''
            call the function with argument
            a#
            arguments:{
                "callerObject": object
                "..." all other arguments from args
            
            '''
            methodToCall(**arguments)
        except (Exception) as e:
            raise eventError("can't call function %s: (%s) error: %s"%(args.get('callFunction',"unknown"),arguments,e.msg))
    
    
    def getConfiguration(self):
        '''
        return the event configuration
        
        return: dic
        '''
        cfg={
            "parameter":self.getParameter(),
            "callers":self.getCallers()
            } 
        return cfg 