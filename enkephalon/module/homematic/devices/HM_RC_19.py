'''
Created on 13.01.2023
@author: ullrich schoen

'''

__version__="0.1.0"
__author__="ullrich schoen"
__DEVICETYPE__="HM_RC_19"
__DEVICEPACKAGE__="homematic"

# Standard library imports
import logging
# Local application imports
from module.default.devices.defaultDevice import defaultDevice

LOG=logging.getLogger(__name__)

class HM_RC_19(defaultDevice):

    deviceType="HM_RC_19"
    devicePackage="homematic"
        
    def __init__(self,deviceID,deviceCFG={},restore=False):
        
        
        defaultDevice.__init__(self,deviceID,deviceCFG,restore)
        LOG.info("init %s finish, version %s, deviceID:%s"%(__DEVICETYPE__,__version__,self.deviceID))