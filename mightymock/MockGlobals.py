'''
Created on Jul 7, 2014

@author: pli
'''

def set_outputdir(path):
    '''Mark output folder as global'''
    global outputdir
    outputdir = path
    
def get_outputdir():
    '''Return output folder'''
    return outputdir

def set_mocklogger(loggerobj):
    '''Mark logger as global'''
    global mocklogger
    mocklogger=loggerobj
    
def get_mocklogger():
    '''Return logger'''
    return mocklogger

def set_requestlogger(loggerobj):
    '''Mark logger as global'''
    global requestlogger
    requestlogger=loggerobj
    
def get_requestlogger():
    '''Return logger'''
    return requestlogger

def set_configinfo(configinfo):
    '''Mark configinfo as global'''
    global config
    config = configinfo

def get_configinfo():
    '''Return configinfo'''
    return config

def set_delay(delay):
    '''Mark delay as global'''
    global delaytime
    delaytime = delay
    
def get_delay():
    '''Return delaytime'''
    return delaytime
    
def set_opener(opener):
    '''Mark opener as global'''
    global urllib_opener
    urllib_opener = opener
    
def get_opener():
    '''Return opener'''
    return urllib_opener
    
def set_server(server):
    '''Mark server as global'''
    global remote_server
    remote_server = server
    
def get_server():
    '''Return server'''
    return remote_server

def set_cookie(cookie):
    global cookiejar
    cookiejar = cookie
    
def get_cookie():
    return cookiejar