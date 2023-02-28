'''
Created on 01.01.2023

@author: uschoen
'''

'''
install python package xmltodict
use:
 pip3 install xmltodict
 
to retrive the iseID from the Homematic use:

Systemvariablen:
http://IpOfTheHomematic/addons/xmlapi/sysvarlist.cgi       
<systemVariable name="test" variable="0.000000" value="0.000000" value_list="" ise_id="44628" min="0" max="65000" unit="C" type="4" subtype="0" logged="false" visible="true" timestamp="1634145058" 
 

'''

__version__='0.1.0'
__author__ = 'ullrich schoen'

# Standard library imports
import urllib3                                       #@UnresolvedImport,@UnusedImport
import logging

# Local application imports
from module.modulException import modulException
from module.defaultModul import defaultModul

LOG=logging.getLogger(__name__)

try:
    import xmltodict                                     #@UnresolvedImport,@UnusedImport
except:
    raise modulException("xmltodict not install. use sudo pip3 install xmltodict",False)

class xml_api(defaultModul):
    '''
    classdocs
    '''
    def __init__(self,objectID,modulCFG={}):
        # confiuration 
        defaultCFG={
                "ccu3IP":"127.0.0.1",
                "https":False,
                
            }  
        defaultCFG.update(modulCFG)
        
        defaultModul.__init__(self,objectID,defaultCFG)
        LOG.info("build homematic xml_api modul, %s instance version: %s"%(__name__,__version__))               
        
    def setHMDevice(self,iseID,value):
        '''
        
        '''
        try:
            LOG.debug("update iseID %s with value %s"%(iseID,value))
            path=("/config/xmlapi/statechange.cgi?ise_id=%s&new_value=%s"%(iseID,value))
            response=self.__sendRequest(path)   
            HMresponse=xmltodict.parse(response.data)
            if "result" in HMresponse:
                if "changed" in HMresponse['result']: 
                    LOG.debug("value successful change")
                elif "not_found" in HMresponse['result']: 
                    LOG.error("can not found iseID %s"%(iseID))
                else:
                    LOG.warning("get some unknown answer %s"%(response.data))
            else:
                LOG.warning("get some unknown answer %s"%(response.data)) 
        except (modulException) as e:
            LOG.critical("error in update HMDevice %s"%(e))
        except:
            raise modulException("unknown error in updateHMDevices",True)
    
    def retrievedDevices(self):
        try:
            LOG.info("retrieved homematic devices from %s"%(self.config['ccu3IP'])) 
            response=self.__sendRequest("/config/xmlapi/devicelist.cgi")
            
            try:
                HMresponse=xmltodict.parse(response.data)
                return HMresponse
            except Exception as e:
                LOG.critical("error in response data: %s"%(e),exc_info=True)
                return {}
            return HMresponse
        except (modulException) as e:
            LOG.critical("error in retrievedDevices %s"%(e))
            return {}
        except Exception as e:
            LOG.critical("unknown error in retrievedDevices %s"%(e),exc_info=True)
            return {}
    
    def __sendRequest(self,urlPath):
        try:
            response=""
            if not self.config['https']:
                # use http
                url=("http://%s%s")%(self.config['ccu3IP'],urlPath)
                response=self.__sendHttp(url)
            else:
                # use https
                url=("https://%s%s")%(self.config['ccu3IP'],urlPath)
                response=self.__sendHttps(url)
            return response   
        except (modulException) as e:
            raise e       
        except:
            raise modulException("unknown error in __sendRequest",True) 
    
    def __sendHttp(self,url):
        try:
            LOG.debug("url is %s "%(url))
            http = urllib3.PoolManager()
            response = http.request('GET', url)
            if  response.status != 200:
                raise modulException("get http error back:%s"%(response.status))
            return response
        except (modulException) as e:
            raise e
        except:
            raise modulException("unknown error in __SendHTTP",True)    
    
    def __sendHttps(self,url):
        '''
        ' @todo: write HTTPS
        '''
        try:
            LOG.critical("__sendHttps not implemnted")
            return "<result><not_found/></result>"
        except:
            raise modulException("unknown error in __SendHTTPs",True)                
