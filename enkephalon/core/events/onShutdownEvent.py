'''
Created on 01.01.2023

@author: uschoen
'''

__version__='0.1.0'
__filename__='onShutdownEvent.py'
__author__ = 'uschoen'
__eventName__= "onshutdown"

# Standard library imports
import logging

# Local application imports
from core.events.defaultEvent import defaultEvent

LOG=logging.getLogger(__name__)

class onShutdownEvent(defaultEvent):
    '''
    classdocs
    '''
    
    eventName="onshutdown"