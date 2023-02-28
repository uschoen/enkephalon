'''
Created on 01.01.2023

@author: uschoen
'''


__version__='0.1.0'
__author__ = 'ullrich schoen'

# Standard library imports

import logging

LOG=logging.getLogger(__name__)


class modulException(Exception):
    '''
    
    '''
    def __init__(self, msg="known error occurred, catch by coreException",tracback=False):
        super(modulException, self).__init__(msg)
        self.msg = msg
        LOG.critical("%s"%(msg),exc_info=tracback)
        
class modulError(Exception):
    '''
    
    '''
    def __init__(self, msg="known error occurred, catch by coreException",tracback=True):
        super(modulError, self).__init__(msg)
        self.msg = msg
        LOG.critical("%s"%(msg),exc_info=tracback)