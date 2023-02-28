'''
Created on 05.01.2023
@author: ullrich schoen

'''

__version__="0.1.0"
__author__="ullrich schoen"

# Standard library imports
import logging
# Local application imports
from module.default.devices.channels.defaultChannel import defaultChannel

LOG=logging.getLogger(__name__)

class powerL3(defaultChannel):

    channel_type="powerL3"
    channel_package="powermeter"

    def __init__(self,deviceID,channelCFG={},restore=False):

        defaultChannel.__init__(self,deviceID,channelCFG,restore)



        self.parameter['CFGVersion']=__version__

        LOG.info("init channel %s finish, version %s, deviceID:%s"%(self.channel_type,self.channelName,__version__))