'''
Created on Jul 3, 2014

@author: pli, yuliu
'''
import sys, os
import web
from web.wsgiserver.ssl_pyopenssl import SSL_fileobject
from MockConfiguration import MockConfiguration
from HttpHandler import SetResponseOnce, SetResponseCommon, SearchRequest, SetNumber, SetDelay, SetMode, RequestHandler, ResetName
from MockServer import MockServer
import Utils

def copy_sample_folder(foldername):
    current_dir_abs = os.path.abspath(os.path.dirname(__file__))
    sampler_folder = os.path.join(current_dir_abs, "Sample")
    output_dir_abs = os.getcwd()
    output_folder = os.path.join(output_dir_abs, foldername)
    Utils.copy_folder(sampler_folder, output_folder)

def main(argv = sys.argv):
    urls = (
        '/set/response_once', "SetResponseOnce",
        '/set/response_common',"SetResponseCommon",
        '/search/request',"SearchRequest",
        '/set/number', "SetNumber",
        '/set/delay', "SetDelay",
        '/set/mode', "SetMode",
        '/set/reset_name',"ResetName",
        '^.*', 'RequestHandler'
        ) 
    mock_config = MockConfiguration()
    mock_config.setup(argv)
    SSL_fileobject.ssl_timeout = 60
    MockServer.set_config_info()
    app = web.application(urls, globals())
    sys.argv[1:] = ["%s:%s" % (mock_config.baseurl, str(mock_config.port))]
    app.run()
    
def setup(argv = sys.argv):
    current_dir_abs = os.getcwd()
    sys.path.append(current_dir_abs)
    if len(sys.argv)==1:
        foldername = "mock_project"
    elif len(sys.argv)==2 and not sys.argv[1].startswith("-") and sys.argv[1].find("help")==-1:
        foldername = sys.argv[1]
    else:
        print "please enter the folder name after mocksetup. E.g. mocksetup <foldername>."
        print "It will generate a mock_project folder by default."
        sys.exit(2)
    copy_sample_folder(foldername)
    print "Generate a <%s> folder for sample mock project successfully." % foldername

def modify(argv = sys.argv):
    import optparse
    parser = optparse.OptionParser()
    parser.add_option("-c","--config",dest="configfile",
                      default="default.cfg",
                      help="config file name, e.g: test.cfg")
    parser.add_option("-p","--path",dest="configpath",
                      default="",
                      help="config file path, default: Config, e.g. test")
    parser.add_option("-s", dest="section", default="MockServer",
                      help="section name, e.g: DEFAULTENV")
    parser.add_option("-k", dest="keyname",
                      help="key name, e.g: Scope")
    parser.add_option("-v", dest="value",
                      help="key value, e.g: All")
    parser.add_option("-d","--directory", dest="directory",
                      default=None,
                      help="Current working directory full path, which contains the Config/Testsuite/Baseline folder, if you are in the default directory, you can omit this option")
    options, argv = parser.parse_args(list(argv))
    if options.directory:
        if os.path.isdir(options.directory):
            os.chdir(options.directory)
    current_dir_abs = os.getcwd()
    sys.path.append(current_dir_abs)
    if not hasattr(options,"section") or not hasattr(options,"keyname") or not hasattr(options,"value"):
        print "please enter section name, key name and key value by the correct format"
        sys.exit()
    else:
        if options.configpath=="":
            config_filepath = "Config"
        else:
            config_filepath = os.path.join("Config",options.configpath)
        configfile = os.path.join(config_filepath, options.configfile)
        configdata = Utils.read_config(configfile)
        if configdata.has_section(options.section):
            configdata.set(options.section, options.keyname, options.value)
        else:
            configdata.add_section(options.section)
            print "add new section %s" % options.section
            configdata.set(options.section, options.keyname, options.value)
        configfile.write_config()
        print "set section %s key %s with value %s successful" % (options.section, options.keyname, options.value)