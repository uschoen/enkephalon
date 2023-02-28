'''
Created on 1.01.2023

@author: uschoen
'''

__version__='0.1.0'
__filename__='onChangeEvent.py'
__author__ = 'uschoen'
__eventName__= "onrefresh"

# Standard library imports
import logging

# Local application imports
from core.events.defaultEvent import defaultEvent

LOG=logging.getLogger(__name__)

class onRefreshEvent(defaultEvent):
    '''
    classdocs
    '''
    eventName="onrefresh"