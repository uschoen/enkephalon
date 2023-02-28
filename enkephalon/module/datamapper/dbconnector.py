'''
Created on 01.01.2023

@author: ullrich schoen
'''

from core.coreException import coreException, modulException
import threading
'''
configuration file

        
'''

__version__='0.1.0'
__author__ = 'ullrich schoen'

# Standard library imports
import logging
LOG=logging.getLogger(__name__)

dbDriver=[]
try:
    import pymysql          #@UnresolvedImport 
    dbDriver.append("pymysql")
    LOG.info("probe to import pymysql, success")
except:
    LOG.warning("probe to import pymysql, failed, try next driver")
try:
    import mysql.connector  #@UnresolvedImport
    dbDriver.append("mysql")
    LOG.info("probe to import mysql, success")
except:
    LOG.warning("probe to import mysql.connector, failed, try next driver")

try:
    import mariadb  #@UnresolvedImport
    dbDriver.append("mariadb")
    LOG.info("probe to import mariadb, success")
except:
    LOG.warning("probe to mariadb, failed, try next driver")
    
if len(dbDriver)==0:
    LOG.critical("no mysql driver found. install pymsql or mysql.connector")
    raise coreException("no mysql driver found")


# Local application imports
from module.defaultModul import defaultModul




DEFAULT_CFG={
    "database":{
        "user":"enkephalon",
        "password":"lP6!hyV@wc",
        "host":"10.90.12.100",
        "database":"enkephalon"},
    "dbTyp":"mariadb"
    }


class dbconnector(defaultModul):
    '''
    classdocs
    '''
    def __init__(self,objectID,modulCFG):
        # configuration 
        defaultCFG=DEFAULT_CFG
        defaultCFG.update(modulCFG)
        defaultModul.__init__(self,objectID,defaultCFG)
        self.__callerARGS={}
        self.dbInstance=False
        
        self.__database={
            "mysql":{
                "connect":self.__connect_mysql_DB,
                "execute":self.__mysql_DB_execute,
                "close":self.__mysql_DB_close
                },
            "pymysql":{
                "connect":self.__connect_pymysql_DB,
                "execute":self.__pymysql_DB_execute,
                "close":self.__pymysql_DB_close
                },
            "mariadb":{
                "connect":self.__connect_mariadb_DB,
                "execute":self.__mariadb_DB_execute,
                "close":self.__mariadb_DB_close
                }
            }
        self.__mappers={
               "callerValues":self.__callerValues
            }
        if self.config["dbTyp"] not in dbDriver:
            raise coreException("use %s dbDriver,available dbDrivers are %s"%(self.config["dbTyp"],dbDriver))
        self.__database[self.config["dbTyp"]]['connect'](self.config['database'])
        
        self.lock = threading.Lock()
        
        LOG.info("build DB connector modul, %s instance"%(__name__))    
    
    def shutDownModul(self):
        '''
        shutdown Modul
        '''
        defaultModul.shutDownModul()
        self.__database[self.config["dbTyp"]]['close']()
        
    def update(self,values={}):
        '''
        update the database
        
        values:{        }
        
        exception: NONE
        '''
        try:
            LOG.debug("call update from MysqlMapper with args %s"%(values))          
            self.__callerARGS.update(values)
            sql=""
            sql=self.__buildSQL(self.config["mapping"])
            self.lock.acquire()
            self.__database[self.config["dbTyp"]]['execute'](sql)
        except (coreException,modulException) as e:
            LOG.critical("error in mysqlMapper: %s with error:%s"%(self.config['objectID'],e))
            self.__mariadb_DB_close()
        except:
            LOG.critical("unknown error in modul %s"%(self.config['objectID']),True)
            self.__mariadb_DB_close()
        finally:
            self.lock.release()
            
    def __callerValues(self,value):
        '''
        give back the Value from caller
        
        give the value from self.callerArgs back. This variable have be
        set by the update(self,vars={}) 
        
        return: the value from 
                
        exception: defaultEXC
        '''
        try:
            if value not in self.__callerARGS:
                raise coreException ("can't find % in callerVars"%(value))
            return self.__callerARGS[value]
        except (coreException) as e:
            raise e
        except:
            raise coreException("unknown err in getValue",True)
    
    def __buildSQL(self,mapping):
        '''
        build the sql string
        '''
        try:
            field=mapping["fields"]
            
            tableString=""
            valueString=""
            secound=False
            for tableEntry in field:
                if secound:
                    tableString+=","
                    valueString+=","
                secound=True
                tableString+=("`%s`"%(tableEntry))
                
                (command,commandValue)=(*field[tableEntry].keys(),*field[tableEntry].values())
                if command not in self.__mappers:
                    raise coreException("can't find %s in db Mapper")
                valueString+=("'%s'"%(self.__mappers[command](commandValue)))
            
            sql=("INSERT INTO %s (%s) VALUES (%s);"%(mapping['table'],tableString,valueString))
            LOG.debug("build sql string:%s"%(sql))
            return sql
        except coreException as e: 
            raise e
        except:
            raise coreException("error in modul %s: buildSQL"%(self.config['objectID']),True)  
    
    '''
    pymysql driver
    '''
    def __connect_pymysql_DB(self,cfg={}):
        try:
            self.dbInstance=pymysql.connect(cfg["host"],cfg["user"],cfg["password"],cfg["database"])
            LOG.info("connect to pymsql host:%s"%(cfg["host"])) 
        except (Exception) as e:
            LOG.critical("unknown error for connect db msg:%s"%(e),True)
            raise coreException
    
    def __pymysql_DB_execute(self,sql):
        LOG.error("not implemented")
    def __pymysql_DB_close(self):
        LOG.error("not implemented")
    
    '''
    mysql driver
    '''   
    def __connect_mysql_DB(self,cfg={}):
        try:
            self.dbInstance=mysql.connector.connect(
                                                     host=cfg["host"],
                                                     user=cfg["user"],
                                                     password=cfg["password"]
                                                    )
            LOG.info("connect to mysql host:%s"%(cfg["host"]))                                       
        except (Exception) as e:
            LOG.critical("unknown error for connect db msg:%s"%(e),True)
            raise coreException
    
    def __mysql_DB_execute(self,sql):
        LOG.error("not implemented")
    def __mysql_DB_close(self):
        LOG.error("not implemented")
    
    '''
    maria db driver
    '''
    def __connect_mariadb_DB(self,cfg={}):
        try:
            self.dbInstance=mariadb.connect(
                                                     host=cfg["host"],
                                                     user=cfg["user"],
                                                     password=cfg["password"],
                                                     database=cfg["database"]
                                                    )
            LOG.info("connect to mariadb host:%s database:%s"%(cfg["host"],cfg["database"])) 
            self.dbInstance.autocommit = True
            
        except mariadb.Error as e:
            self.__mariadb_DB_close()
            raise coreException("error for connect mariadb host:%s database:%s db msg:%s"%(cfg["host"],cfg["database"],e))
        except (Exception) as e:
            self.__mariadb_DB_close()
            raise coreException("unknown error for connect db msg:%s"%(e))
    
    def __mariadb_DB_execute(self,sql):
        """
        excecute a sql statment
         
        @var: sql , a well form sql statment.
        
        exception: defaultEXC 
         
        """
        try:
            LOG.info("sqlExecute: %s"%(sql))
            # check if DB connection ready
            if not self.dbInstance:
                self.__database[self.config["dbTyp"]]['connect'](self.config['database'])
            dbCursor =self.dbInstance.cursor()  
            dbCursor.execute(sql) 
            self.dbInstance.commit()
            dbCursor.close()
        except (mariadb.Error) as e:
            raise modulException("mysql error %s"%(e))
        except :
            raise coreException("unknown error sql:%s"%(sql),True)  
        
    def __mariadb_DB_close(self):  
        '''
        close mariad db connection
        '''
        try:
            LOG.info("close mariadb database connection")
            self.dbInstance.close()
            self.dbInstance=False
        except:
            self.dbInstance=False
            LOG.warning("can't close db connection. delete db instance")
    