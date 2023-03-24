'''
Created on 01.01.2023

@author: uschoen
'''


__version__='0.0.1'
__author__ = 'ullrich schoen'

# Standard library imports

import logging


LOG=logging.getLogger(__name__)

class scriptException(Exception):
    '''
    
    '''
    def __init__(self, msg="unknown error occurred. ",tracback=True):
        super(scriptException, self).__init__(msg)
        self.msg = msg
        LOG.critical("%s"%(msg),exc_info=tracback)
  
class formatException(Exception):
    '''
    
    '''
    def __init__(self, msg="unknown error occurred. ",tracback=False):
        super(formatException, self).__init__(msg)
        self.msg = msg
        LOG.critical("%s"%(msg),exc_info=tracback)      
        
class configException(Exception):
    '''
    
    '''
    def __init__(self, msg="unknown error occurred. ",tracback=False):
        super(configException, self).__init__(msg)
        self.msg = msg
        LOG.critical("%s"%(msg),exc_info=tracback)             