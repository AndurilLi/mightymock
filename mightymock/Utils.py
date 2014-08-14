'''
Created on Jul 7, 2014

@author: pli
'''
import os, sys, stat, shutil, errno, json, traceback, ConfigParser

def handle_readonly(func, path, exc):
    '''Callable function for removing readonly access'''
    excvalue = exc[1]
    if func in (os.rmdir, os.remove) and excvalue.errno == errno.EACCES:
        os.chmod(path, stat.S_IRWXU| stat.S_IRWXG| stat.S_IRWXO) # 0777
        func(path)
    else:
        sys.stderr.write("Cannot handle read-only file, need to remove %s manually" % path)
        sys.exit(1)
        
def remove_path(path):
    '''Remove file or folder'''
    try:
        if os.path.isdir(path):
            shutil.rmtree(path, ignore_errors=False, onerror=handle_readonly)
        elif os.path.exists(path):
            os.remove(path)
        print "Remove Directory %s Successfully" % path
    except Exception:
        sys.stderr.write("Cannot remove the directory %s" % path)
        sys.exit(1)

def create_folder(folderpath, foldername, refreshflag=True):
    '''create a folder: 
       refreshflag=True: if folder exists, then delete it and re-create; else just create the folder
       refreshflag=False: if folder doesn't exist, then create the folder'''
    if folderpath=="" or os.path.isdir(folderpath):
        newfolder = os.path.join(folderpath,foldername)
        if os.path.isdir(newfolder):
            if refreshflag:
                serverlog = os.path.join(newfolder,"MockServer.log")
                requestlog = os.path.join(newfolder, "Request.log")
                if os.path.isfile(serverlog):
                    os.remove(serverlog)
                if os.path.isfile(requestlog):
                    os.remove(requestlog)
        else:
            os.makedirs(newfolder)
    else:
        sys.stderr.write("Cannot create folder %s" % folderpath)
        sys.exit(1)
    return newfolder

def _decode_list(lst):
    '''Written by Huangfu'''
    newlist = []
    for i in lst:
        if isinstance(i, unicode):
            i = i.encode('utf-8')
        elif isinstance(i, list):
            i = _decode_list(i)
        newlist.append(i)
    return newlist

def _decode_dict(dct):
    '''Written by Huangfu'''
    newdict = {}
    for k, v in dct.iteritems():
        if isinstance(k, unicode):
            k = k.encode('utf-8')
        if isinstance(v, unicode):
            v = v.encode('utf-8')
        elif isinstance(v, list):
            v = _decode_list(v)
        newdict[k] = v
    return newdict

def get_dict_from_json(data):
    jsonobj = json.loads(data,object_hook=_decode_dict)
    return jsonobj

def copy_folder(src, dst):
    """
    copy file from src to dst 
    also support recursively copy an entire directory tree rooted at src
    """
    shutil.rmtree(dst,ignore_errors=True)
    if not os.path.isdir(dst):   
        try:
            shutil.copytree(src, dst)
        except OSError as exc: 
            if exc.errno == errno.ENOTDIR:
                shutil.copy(src, dst)
            else: 
                traceback.print_exc()
                raise

def read_config(config_file):
    '''Read cfg file'''
    cfg = ConfigParser.RawConfigParser()
    cfg.optionxform = str
    cfg.read(config_file)
    if not cfg.sections():
        raise Exception("Cannot read config info from %s at %s, please check you configfile!" % config_file)
    else:
        print "Set config file to %s" % config_file
    return cfg

def check_filename(filename):
    if not filename.endswith(".py"):
        return filename + ".py"
    return filename