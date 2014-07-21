'''
Created on Jul 7, 2014

@author: pli, yuliu
'''
import os, urllib2, hashlib
import MockGlobals, Utils
from FileHandler import FileHandler

class Mode:
    @classmethod
    def is_valid(cls, mode):
        for attr in dir(cls):
            if mode == getattr(cls, attr):
                return True
        return False

class MockMode(Mode):
    mock = "mock"
    record = "record"
    proxy = "proxy"

class RequestMode(Mode):
    strict = "strict"
    relax = "relax"

class MockServer:
    url_mapping = {}
    number_mapping = {}
    global_delay = 0
    delay = 0
    mapping_changes = {}
    record_prefix = "API"
    baseurl = "0.0.0.0"
    port = 8080
    request_mode = "relax"
    auto_forward = True
    TEMPLATE = "APITemplates"
    mode = "record"
    record_number = 0
    api_folder = None
    server = None
    mock_address = None
              
    @classmethod
    def _parse_config(cls):
        cls.global_delay = cls.config["delay"] if cls.config.has_key("delay") else 0
        MockGlobals.set_delay(cls.global_delay)
        cls.server = cls.config["server"] if cls.config.has_key("server") else None  
        cls.baseurl = cls.config["baseurl"]
        cls.port = int(cls.config["port"])
        cls.set_mode(cls.config["mode"])
        cls.get_omit_headers()
        if cls.mode == "record" or cls.mode == "mock":
            api_foldername = cls.config["apitemplatepath"] if cls.config.has_key("apitemplatepath") else cls.TEMPLATE
            cls.request_mode = cls.config["request_mode"] if cls.config.has_key("request_mode") else "relax"
            api_folderpath = os.getcwd()
            cls.api_folder = os.path.join(api_folderpath, api_foldername)
            MockGlobals.get_mocklogger().info("APITemplate path is set to %s" % cls.api_folder)
            Utils.create_folder(api_folderpath, api_foldername, False)
            cls.auto_forward = True if not cls.config.has_key("mockforward") or cls.config["mockforward"].lower() == "true" else False
            cls.filehandler = FileHandler(cls.api_folder)
            cls.reset_name()
            
    @classmethod    
    def _check_config(cls):
        assert MockMode.is_valid(cls.mode)
        assert cls.baseurl
        assert cls.port
        if cls.mode != "mock" or (cls.mode == "mock" and cls.auto_forward):
            assert cls.server!=None
            if cls.server.endswith("/"):
                cls.server = cls.server[:-1]
        if cls.mode == "record" or cls.mode == "mock":
            assert RequestMode.is_valid(cls.request_mode)
    
#     @classmethod
#     def common_opener(cls):
#         '''urllib2 solution'''
#         if cls.config.has_key("proxy"):
#             handler = urllib2.ProxyHandler({"http": cls.config["proxy"],
#                                             "https": cls.config["proxy"]})
#         else:
#             handler = urllib2.BaseHandler()
#         class NoRedirection(urllib2.HTTPErrorProcessor):
#  
#             def http_response(self, request, response):
#                 return response
#          
#             https_response = http_response
#         from cookielib import CookieJar
#         cj = CookieJar()
#         MockGlobals.set_cookie(cj)
#         opener = urllib2.build_opener(NoRedirection,urllib2.HTTPCookieProcessor(cj),handler)
#         return opener
    
    @classmethod
    def common_opener(cls):
        '''httplib2 solution'''
        import httplib2
        if cls.config.has_key("proxy"):
            proxy = httplib2.proxy_info_from_url("http://" + cls.config["proxy"])
            http = httplib2.Http(proxy_info = proxy)
        else:
            http = httplib2.Http()
        http.disable_ssl_certificate_validation = True
        http.follow_redirects = False
        return http
            
    @classmethod
    def save_request(cls, request):
        if cls.request_mode == "relax":
            filename = "%s-%s.py" % (request ['method'], request['path'].replace("/","-").replace(".","_"))
        else:
            key_content = str(sorted(request['requestheaders'].items())) + request['requestbody'] + str(sorted(request['parameters'].items()))
            key = hashlib.sha224(key_content.replace('\n','').replace('\r','').replace('\t','')).hexdigest()
            filename = "%s-%s-%s.py" % (request ['method'], request['path'].replace("/","-").replace(".","_"), key[-5:])
        if os.path.isfile(os.path.join(cls.api_folder, filename)):
            cls.filehandler.add_request(request, filename, cls.request_mode)
        else:
            cls.filehandler.create_request(request, filename, cls.request_mode)    
        return filename
        
    @classmethod
    def search_request(cls, request):
        key_content = str(sorted(request['requestheaders'].items())) + request['requestbody'] + str(sorted(request['parameters'].items())).rstrip()
        key = hashlib.sha224(key_content.replace('\n','').replace('\r','').replace('\t','')).hexdigest()
        filename = "%s-%s-%s.py" % (request ['method'], request['path'].replace("/","-").replace(".","_"), key[-5:])
        if os.path.isfile(os.path.join(cls.api_folder, filename)):
            return filename
        else:
            filename = "%s-%s.py" % (request ['method'], request['path'].replace("/","-").replace(".","_"))
            if os.path.isfile(os.path.join(cls.api_folder, filename)):
                return filename
            else:
                return False

    
    @classmethod
    def get_response(cls, request, filename, number=None):
        response = cls.filehandler.read_response(filename, number)
        if response:
            request["responseheaders"] = response["headers"]
            request["responsebody"] = response["body"]
            request["status"] = response["status"]
            if response.has_key("delay"):
                request["delay"] = response["delay"]
    
    @classmethod
    def set_response(cls, request, filename, mode=None):
        if not mode:
            cls.filehandler.set_response_common(filename, request, request["number"])
        else:
            cls.filehandler.create_request(request, filename, mode)
    
    @classmethod
    def set_mode(cls, mode):
        cls.mode = mode
    
    @property
    def get_mode(self):
        return self.mode
    
    @classmethod
    def set_delay(cls, delay):
        cls.delay = delay
    
    @classmethod
    def get_delay(cls):
        return cls.delay
    
    @classmethod
    def get_mock_address(cls):
        import socket
        local_name = socket.gethostname()
        local_ip = socket.gethostbyname(local_name)
        if cls.server.endswith("/"):
            cls.mock_address = cls.prefix + local_ip + ":"+ str(cls.port) + "/"
        else:
            cls.mock_address = cls.prefix + local_ip + ":"+ str(cls.port)
    
    @classmethod
    def set_config_info(cls):
        cls.mocklogger = MockGlobals.get_mocklogger()
        cls.config = MockGlobals.get_configinfo()
        cls._parse_config()
        cls._check_config()
        cls.set_ssl()
        cls.get_mock_address()
        
        cls.opener = cls.common_opener()
        MockGlobals.set_opener(cls.opener)
        MockGlobals.set_server(cls.server)
    
    @classmethod
    def set_ssl(cls):
        if cls.config.has_key("ssl") and cls.config["ssl"].lower() == "true":
            from web.wsgiserver import CherryPyWSGIServer
            cls.prefix = "https://"
            assert cls.config.has_key("sslkeypath") and os.path.isfile(cls.config["sslkeypath"])
            assert cls.config.has_key("sslcerpath") and os.path.isfile(cls.config["sslcerpath"])
            CherryPyWSGIServer.ssl_certificate = cls.config["sslcerpath"]
            CherryPyWSGIServer.ssl_private_key = cls.config["sslkeypath"]
        else:
            cls.prefix = "http://"
    
    @classmethod
    def get_omit_headers(cls):
        cls.omit_headers = []
        if cls.config.has_key("omitheaders"):
            temp = cls.config["omitheaders"].split(",")
            for key in temp:
                cls.omit_headers.append(key.strip().upper())
    
    @classmethod
    def filter_headers(cls, headers):
        for header in cls.omit_headers:
            if header in headers:
                del headers[header]
        return headers
    
    @classmethod
    def reset_name(cls):
        cls.filehandler.reset_name()