'''
Created on 01.01.2023

@author: uschoen
'''


__version__='0.1.0'
__author__ = 'ullrich schoen'

# Standard library imports

import logging
from core.coreException import coreException

LOG=logging.getLogger(__name__)

class defaultError(coreException):
    '''
    
    '''
    pass

class scriptProgrammError(coreException):
    '''
    
    '''
    pass

class scriptError(coreException):
    '''
    
    '''
    pass

class cmdError(coreException):
    '''
    
    '''
    pass

class testError(coreException):
    '''
    
    '''
    pass