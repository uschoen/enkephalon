#!/usr/bin/python3 -u

'''
File:hmcServer.py

Created on 01.01.2023
(C):2023
@author: ullrich schoen
@email: uschoen.hmc(@)johjoh.de
Requierment:python 3.2.3

Please use command to start:
python3 enkepahlon.py 
'''


__version__='0.1.0'
__author__ = 'ullrich schoen'
__PYTHONVERSION__=(3,2,3)
__LOGLEVEL__="INFO"


# Standard library imports
import sys
import signal
import argparse
import logging.config
logTyp="colored"
try:
    import coloredlogs                          #@UnresolvedImport 
    logTyp="colored"
except:
    logTyp="colored"
    print ("no cocloredlog install. Use: \"pip3 install coloredlogs\" to install. Use simple logging")
    logTyp="simple"

# local library import
from core.manager import manager



LOG=logging.getLogger(__name__)

def callSignalHandler(signum,frame):
    LOG.critical("Signal handler called with signal:%s frame:%s"%(signum,frame))
    sys.exit()

def addSignalHandler():
    '''
    addSignalHandler

    A list of signals and what they mean
    • These were all recorded from a Linux i386 system. Numbers may vary between platforms.
    • Linux uses signals 34-64 for its real-time system which we are not interested in.
    • “man 7 signal” gives the official manual page on signals.
    • This is a fairly exhaustive list of signals. Only some of them will arise in the context of the
    make program.
    No. Short name What it means
    1 SIGHUP 
    If a process is being run from terminal and that terminal suddenly goes
    away then the process receives this signal. “HUP” is short for “hang up”
    and refers to hanging up the telephone in the days of telephone modems.
    2 SIGINT 
    The process was “interrupted”. This happens when you press Control+C on
    the controlling terminal.
    3 SIGQUIT
    4 SIGILL 
    Illegal instruction. The program contained some machine code the CPU
    can't understand.
    5 SIGTRAP 
    This signal is used mainly from within debuggers and program tracers.
    6 SIGABRT 
    The program called the abort() function. This is an emergency stop.
    7 SIGBUS 
    An attempt was made to access memory incorrectly. This can be caused by
    alignment errors in memory access etc.
    8 SIGFPE 
    A floating point exception happened in the program.
    9 SIGKILL 
    The process was explicitly killed by somebody wielding the kill
    program.
    10 SIGUSR1 
    Left for the programmers to do whatever they want.
    11 SIGSEGV 
    An attempt was made to access memory not allocated to the process. This
    is often caused by reading off the end of arrays etc.
    12 SIGUSR2 
    Left for the programmers to do whatever they want.
    13 SIGPIPE 
    If a process is producing output that is being fed into another process that
    consume it via a pipe (“producer | consumer”) and the consumer
    dies then the producer is sent this signal.
    14 SIGALRM 
    A process can request a “wake up call” from the operating system at some
    time in the future by calling the alarm() function. When that time comes
    round the wake up call consists of this signal.
    15 SIGTERM 
    The process was explicitly killed by somebody wielding the kill
    program.
    16 unused
    17 SIGCHLD 
    The process had previously created one or more child processes with the
    fork() function. One or more of these processes has since died.
    18 SIGCONT 
    (To be read in conjunction with SIGSTOP.)
    If a process has been paused by sending it SIGSTOP then sending
    SIGCONT to the process wakes it up again (“continues” it).
    19 SIGSTOP 
    (To be read in conjunction with SIGCONT.)
    If a process is sent SIGSTOP it is paused by the operating system. All its
    No. Short name What it means
    state is preserved ready for it to be restarted (by SIGCONT) but it doesn't
    get any more CPU cycles until then.
    20 SIGTSTP 
    Essentially the same as SIGSTOP. This is the signal sent when the user hits
    Control+Z on the terminal. (SIGTSTP is short for “terminal stop”) The
    only difference between SIGTSTP and SIGSTOP is that pausing is
    only the default action for SIGTSTP but is the required action for
    SIGSTOP. The process can opt to handle SIGTSTP differently but gets no
    choice regarding SIGSTOP.
    21 SIGTTIN 
    The operating system sends this signal to a backgrounded process when it
    tries to read input from its terminal. The typical response is to pause (as per
    SIGSTOP and SIFTSTP) and wait for the SIGCONT that arrives when the
    process is brought back to the foreground.
    22 SIGTTOU 
    The operating system sends this signal to a backgrounded process when it
    tries to write output to its terminal. The typical response is as per
    SIGTTIN.
    23 SIGURG 
    The operating system sends this signal to a process using a network
    connection when “urgent” out of band data is sent to it.
    24 SIGXCPU 
    The operating system sends this signal to a process that has exceeded its
    CPU limit. You can cancel any CPU limit with the shell command
    “ulimit -t unlimited” prior to running make though it is more
    likely that something has gone wrong if you reach the CPU limit in make.
    25 SIGXFSZ 
    The operating system sends this signal to a process that has tried to create a
    file above the file size limit. You can cancel any file size limit with the
    shell command “ulimit -f unlimited” prior to running make though it is
    more likely that something has gone wrong if you reach the file size limit
    in make.
    26 SIGVTALRM 
    This is very similar to SIGALRM, but while SIGALRM is sent after a
    certain amount of real time has passed, SIGVTALRM is sent after a certain
    amount of time has been spent running the process.
    27 SIGPROF 
    This is also very similar to SIGALRM and SIGVTALRM, but while
    SIGALRM is sent after a certain amount of real time has passed, SIGPROF
    is sent after a certain amount of time has been spent running the process
    and running system code on behalf of the process.
    28 SIGWINCH 
    (Mostly unused these days.) A process used to be sent this signal when one
    of its windows was resized.
    29 SIGIO 
    (Also known as SIGPOLL.) A process can arrange to have this signal sent
    to it when there is some input ready for it to process or an output channel
    has become ready for writing.
    30 SIGPWR 
    A signal sent to processes by a power management service to indicate that
    power has switched to a short term emergency power supply. The process
    (especially long-running daemons) may care to shut down cleanlt before
    the emergency power fails.
    31 SIGSYS 
    Unuse
    '''
    
    LOG.info("set up signal handler ") 
    ignoreSIG=["SIGCONT","SIGWINCH"]
    for i in [x for x in dir(signal) if x.startswith("SIG")]:
        try:
            signum = getattr(signal,i)
            if i in ignoreSIG:
                LOG.debug("ignore signal handler signal. %s:%s"%(signum,i))
                continue
            signal.signal(signum,callSignalHandler)
            LOG.debug("add signal handler signal. %s:%s"%(signum,i))
        except:
            LOG.info("skip signal handler signal. %s:%s, not catchable"%(signum,i)) 
            
            
def getArgs():
    '''
    parse the argument from command line
    
    configfile
    daemon
    help
    
    return: (configfile,daemon)
    '''
    LOG.info("parse console arguments")
    try:
        parser = argparse.ArgumentParser(description='enkephalon help interface')
        parser.add_argument('--configfile','-c',help="full path of the configuration file",action="store", dest="configfile",default=None)
        parser.add_argument('--daemon','-d',help="start hmc as daemon, default true",action="store", dest="daemon",default=False) 
    except:
        print("you forget some start arguments. Use -h help option"%(sys.version_info))
        sys.exit(0)
    args = parser.parse_args()
    configFile=args.configfile
    daemon=args.daemon
    LOG.info("parse arguments for configFile:%s daemon:%s"%(configFile,daemon))
    return (configFile,daemon)

def enkephalon(logTyp):
    '''
    enkephalon
    
    main code
    '''
    LOG.info("start enkephalon(%s) on python version %s.%s.%s"%(__name__,sys.version_info[0],sys.version_info[1],sys.version_info[2],))
    
    #add signal handler
    addSignalHandler()
    
    #read command line arguments
    (configFile,daemon)=getArgs()
    
    #start up server
    try:
        LOG.info("start up enkephalon -c %s -d %s -l %s  version %s"%(configFile,daemon,logTyp,__version__)) 
        coreServer=manager(configFile,logTyp)
        coreServer.start() 
    except (SystemExit, KeyboardInterrupt):
        LOG.critical("get signal to kill enkephalon process! enkephalon going down !!") 
    except (Exception) as e:
        LOG.critical("unknown error in enkephlon. Shutting down server. Error:%s"%(e),exc_info=True) 
    finally:
        LOG.critical("enkephalon now in finally state and try to shut down !!")
        if coreServer:
            coreServer.shutdown() 
        LOG.critical("enkephalon is finally down !!")
        sys.exit()  

    
if __name__ == '__main__':
    '''
    call the enkephalon function
    '''
    print ("start up enkephalon")
    
    ''' 
    set up logging configuration
    '''
    if  logTyp=="colored": 
        coloredlogs.DEFAULT_FIELD_STYLES = {'asctime': {'color': 'green'}, 'hostname': {'color': 'magenta'}, 'levelname': {'color': 'black', 'bold': True}, 'name': {'color': 'blue'}, 'programname': {'color': 'cyan'}}
        coloredlogs.DEFAULT_LEVEL_STYLES = {'critical': {'color': 'red', 'bold': True}, 'debug': {'color': 'green'}, 'error': {'color': 'red'}, 'info': {}, 'notice': {'color': 'magenta'}, 'spam': {'color': 'green', 'faint': True}, 'success': {'color': 'green', 'bold': True}, 'verbose': {'color': 'blue'}, 'warning': {'color': 'yellow'}}
        coloredlogs.install(level=__LOGLEVEL__,milliseconds=True,fmt='%(msecs)03d %(name)30s[%(process)d] %(lineno)04d %(levelname)8s %(message)s')
    else:      
        logging.config.dictConfig({
            "version": 1,
            "disable_existing_LOGs": True,
            "formatters": {
                "simple": {
                    "format": "%(asctime)s %(levelname)s %(message)s"
                }
            },        
            "handlers": {
                
                "console": {
                    "class": "logging.StreamHandler",
                    "formatter": "simple",
                    "level": "DEBUG",
                    "stream": "ext://sys.stdout"
                }
            },   
            "root": {
                "level": "INFO",
                "handlers": ["console"]
            }
        })
    
    '''
    check python version 
    '''
    if sys.version_info <= __PYTHONVERSION__: 
        LOG.critical(__doc__)
        LOG.critical("This server have python version is %s.%s.%s,"%(sys.version_info[:3]))
        LOG.critical("please use python version %s.%s.%s or grader."%(__PYTHONVERSION__))
        sys.exit(0)
    
    enkephalon(logTyp)
        