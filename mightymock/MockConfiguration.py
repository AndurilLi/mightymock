'''
Created on Jul 3, 2014

@author: pli
'''

import os, sys, optparse
import MockGlobals, Utils
from LogServer import LogServer, LogType, Level, Formatter

class ConstantValue:
    MockServerKey = "MockServer"
    ConfigFolder = "Config"
    
class MockConfiguration:
    
    def init_options(self):
        self.parser = optparse.OptionParser()
        self.parser.add_option("-d","--directory", dest="directory",
                               help="Current working directory full path, which contains the Config/Testsuite/Baseline folder, if you are in the default directory, you can omit this option")
        self.parser.add_option("-m","--mode", dest="mode", default=None,
                               help="Start Mode, e.g: Proxy, Record, Mock")
        self.parser.add_option("-o","--output",dest="outputpath",
                               default="",
                               help="output file path, default: Output/, e.g: Output")
        self.parser.add_option("-c", "--config", dest="config",
                               default="default.cfg", help="specify config filepath")
        self.parser.add_option("-p","--path",dest="configpath",
                               default="",
                               help="config file relative path under Config folder, default: Config/, e.g. test")
        
    def setup(self, argv=[]):
        if not hasattr(self,"parser"):
            self.init_options()
        self.options, argv = self.parser.parse_args(list(argv))
        self.set_working_directory()
        self.set_output_folder()
        self.set_configfile()
        self.set_logserver()

    def set_working_directory(self):
        if self.options.directory:
            if os.path.isdir(self.options.directory):
                os.chdir(self.options.directory)
            else:
                sys.stderr.write("Invalid directory %s" % self.options.directory)
                sys.exit(1)
        current_dir_abs = os.getcwd()
        sys.path.append(current_dir_abs)
        
    def set_output_folder(self):
        '''Set output folder
           Input: options.outputpath
           Output: self.outputdir, ChorusGlobals.outputdir'''
        self.outputdir = Utils.create_folder(self.options.outputpath, "Output", True)
        MockGlobals.set_outputdir(self.outputdir)
        print "Set output directory to %s" % self.outputdir
    
    def set_configfile(self):
        self.config = {}
        if self.options.config:
            config_folder = ConstantValue.ConfigFolder if self.options.configpath=="" else os.path.join(ConstantValue.ConfigFolder, self.options.configpath)
            config_filepath = os.path.join(config_folder, self.options.config)
            assert os.path.isfile(config_filepath)
            cfg = Utils.read_config(config_filepath)
            section = ConstantValue.MockServerKey
            for option in cfg.options(section):
                self.config[option.lower()]=cfg.get(section, option)
        if self.options.mode:
            self.config["mode"] = self.options.mode.lower()
        if "mode" not in self.config:
            sys.stderr.write("Please set mode in either options or configfile")
            sys.exit(1)
        if "baseurl" not in self.config:
            self.config["baseurl"] = "0.0.0.0"
        MockGlobals.set_configinfo(self.config)
    
    @property
    def port(self):
        return self.config["port"]
    
    @property
    def baseurl(self):
        return self.config["baseurl"]
    
    def set_logserver(self):
        if self.config.has_key("loglevel"):
            level = Level.get_number(self.config["loglevel"].lower())
        else:
            level = Level.debug
        mocklog=LogServer(LogType.MockServer, level, Formatter.Console)
        mocklog.add_filehandler(level, Formatter.MockServer, self.outputdir, LogType.MockServer+".log")
        MockGlobals.set_mocklogger(mocklog.get_logger())
        requestlog = LogServer(LogType.Request, level, Formatter.Request)
        requestlog.add_filehandler(level, Formatter.Request, self.outputdir, LogType.Request+".log")
        MockGlobals.set_requestlogger(requestlog.get_logger())
        