'''
Created on Jan 16, 2012

@author: mxu, Anduril
@target: Provide logserver and basic logformat
'''
import logging, os, sys
class LogType:
    MockServer = "MockServer"
    Request = "Request"

class Formatter:
    Console = "%(levelname)s - %(message)s"
    MockServer = "%(asctime)s - %(name)s - {%(pathname)s:%(lineno)d} - %(levelname)s - %(message)s"
    Request = "-----------------\nREQUEST DETECTED - %(method)s - %(url)s \nREQUEST_HEADERS: %(requestheaders)s \nREQUEST_BODY: %(requestbody)s \
    \n\nRESPONSE_STATUS: %(status)s \nRESPONSE_HEADERS: %(responseheaders)s \nRESPONSE_BODY: %(responsebody)s \
    \n\nTEPLATE_NAME: %(request_filename)s \
    \n-----------------\n"
     
class Level:
    notset = logging.NOTSET
    debug = logging.DEBUG
    info = logging.INFO
    warning = logging.WARNING
    error = logging.ERROR
    critical = logging.CRITICAL
    
    @classmethod
    def get_number(self, level_name):
        if level_name in dir(self):
            return getattr(self, level_name)
        else:
            raise Exception("invalid log level %s" % level_name)
        

class LogServer:
    filehandler=[]
    def __init__(self,name=LogType.MockServer,level=Level.debug,
                formatter=Formatter.MockServer):
        rootlogger = logging.getLogger()
        rootlogger.setLevel(Level.notset)
        self.logger=logging.getLogger(name)
        self.logger.setLevel(Level.notset)
        self.add_consolehandler(level, formatter)

    def get_logger(self):
        return self.logger
    
    def add_consolehandler(self,level=Level.debug, formatter=Formatter.MockServer):
        self.consolehandler=logging.StreamHandler(stream = sys.stdout)
        self.consolehandler.setFormatter(logging.Formatter(formatter))
        self.consolehandler.setLevel(level)
        self.logger.addHandler(self.consolehandler)
    
    def add_filehandler(self,level=Level.debug,
                    formatter=Formatter.MockServer,
                    filepath=None,filename=None):
        if filename is None or filepath is None:
            raise Exception("Invalid Log file path %s and name %s" % (filepath,filename))
        logfile = os.path.join( filepath, filename)
        handler=logging.FileHandler(logfile)
        handler.setFormatter(logging.Formatter(formatter))
        handler.setLevel(level)
        self.logger.addHandler(handler)
        self.filehandler.append(handler)
        
    def close_logger(self):
        for handler in self.filehandler:
            handler.flush()
            self.logger.removeHandler(handler)
            handler.close()