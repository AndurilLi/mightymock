'''
Created on Jul 7, 2014

@author: pli, yuliu
'''
import web, time, copy, os, json, base64, urllib
import MockGlobals
from MockServer import MockServer, RequestMode
import traceback
import Utils

class ContentType:
    www_form = "application/x-www-form-urlencoded"
    multi_form = 'multipart/form-data; boundary='

class RequestHandler:
    '''
    Generic class handling all http request
    '''
    
    def GET(self):
        '''
        Handle request with get method
        '''
        return self._process_request()
        
    def POST(self):
        '''
        Handle request with post method
        '''
        return self._process_request()
    
    def PUT(self):
        '''
        Handle request with post method
        '''
        return self._process_request()
    
    def DELETE(self):
        '''
        Handle request with post method
        '''
        return self._process_request()
    
    def _parse_parameters(self):
        parameters = {}
        params = web.ctx.env["QUERY_STRING"]
        if params:
            for para in params.split("&"):
                key, value = para.split("=")
                parameters[key] = value
        return parameters
    
    def _parse_reqheaders(self):
        headers = {}
        for key, value in web.ctx.env.items():  # @UndefinedVariable
            if key.startswith("HTTP_"):
                real_key = key.split("HTTP_",2)[1].replace("_", "-")
                headers[real_key] = value.replace(MockServer.mock_address, MockServer.server)
            elif key.startswith("CONTENT_"):
                real_key = key.replace("_", "-")
                headers[real_key] = value.replace(MockServer.mock_address, MockServer.server)        
        headers = dict((k.encode('utf-8'),v.encode('utf-8')) for k,v in headers.items())
        return headers
                
    def _get_date(self):
        return time.strftime("%a, %d %b %Y %H:%M:%S GMT",time.gmtime())
    
    def _send_API(self):
        #TODO add credential balance
        self._recover_form_data_boundary()
        server = MockGlobals.get_server()
        opener = MockGlobals.get_opener()
        
        #urllib2 solution -- has Connection always close issue
#         import urllib2
#         request = urllib2.Request(url=server+self.request["url"], data=self.request["requestbody"], 
#                                   headers=self.request["requestheaders"])
#         request.get_method = lambda: self.request["method"]
#         try:
#             response = opener.open(request)
#         except urllib2.HTTPError as e:
#             response = e
#         except urllib2.URLError as e:
#             self.request["status"] = "500 Internal Server Error"
#             self.request["responseheaders"] = {"Date":self._get_date(), 
#                                        "Content-Type":"text/html; charset=utf-8",
#                                        "X-FW-Excpetion":str(e.reason)}
#             self.request["responsebody"] = "Internal Server Error"
#             return
#         except Exception, e:
#             self.request["status"] = "502 Bad Gateway"
#             self.request["responseheaders"] = {"Date":self._get_date(), 
#                                        "Content-Type":"text/html; charset=utf-8",
#                                        "X-FW-Excpetion":str(e)}
#             self.request["responsebody"] = "Bad Gateway"
#             return
#         self.request["status"] = str(response.code)
#         self.request["responseheaders"] = {}
#         for key, value in response.info().items():
#             realkey = '-'.join((ck.capitalize() for ck in key.split('-')))
#             self.request["responseheaders"][realkey] = value
#         if response.info().get('content-encoding', '').find('gzip') >= 0:
#             import zlib
#             d = zlib.decompressobj(16+zlib.MAX_WBITS)
#             self.request["responsebody"] = d.decompress(response.read())
#             try:
#                 del self.request["responseheaders"]["Content-Length"]
#             except:
#                 pass
#             del self.request["responseheaders"]["Content-Encoding"]
#         else:
#             self.request["responsebody"] = response.read()
#         if response.info().get('content-type','').find('text/html') >= 0:
#             self.request["responsebody"] = self.request["responsebody"].replace(MockServer.server, MockServer.mock_address)
#         for key in self.request["responseheaders"]:
#             self.request["responseheaders"][key] = self.request["responseheaders"][key].replace(MockServer.server, MockServer.mock_address)
#             self.request["responseheaders"][key] = self.request["responseheaders"][key].replace(urllib.quote(MockServer.server,''), urllib.quote(MockServer.mock_address,''))
#         #urllib issue
#         if self.request["requestheaders"].has_key("CONNECTION"):
#             if self.request["requestheaders"]["CONNECTION"].lower() == "keep-alive":
#                 if self.request["responseheaders"].has_key("Connection"):
#                     del self.request["responseheaders"]["Connection"]
        
        try:
            requester = copy.deepcopy(opener)
            resp, content = requester.request(server+self.request["url"], self.request["method"],
                                              headers = self.request["requestheaders"],
                                              body = self.request["requestbody"])
        except Exception, e:
            traceback.print_exc()
            self.request["status"] = "500 Internal Server Error"
            self.request["responseheaders"] = {"Date":self._get_date(), 
                                       "Content-Type":"text/html; charset=utf-8",
                                       "X-FW-Excpetion":str(e)}
            self.request["responsebody"] = "Internal Server Error"
            return
        self._filter_form_data_boundary()
        self.request["responsebody"] = content
        self.request["status"] = resp["status"] + " " + resp.reason
        self.request["responseheaders"] = {}
        if resp.get('content-type') and resp.get('content-type').find('text/html') >= 0:
            self.request["responsebody"] = self.request["responsebody"].replace(MockServer.server, MockServer.mock_address)
        for key in resp:
            realkey = '-'.join((ck.capitalize() for ck in key.split('-')))
            self.request["responseheaders"][realkey] = resp[key]
        
#             self.request["responseheaders"][realkey] = resp[key].replace(MockServer.server, MockServer.mock_address).replace(urllib.quote(MockServer.server,''), urllib.quote(MockServer.mock_address,''))
        if self.request["responseheaders"].get("Content-Location"):
            self.request["responseheaders"]["Content-Location"] = self.request["responseheaders"]["Content-Location"].replace(MockServer.server, MockServer.mock_address).replace(urllib.quote(MockServer.server,''), urllib.quote(MockServer.mock_address,''))
        if self.request["responseheaders"].get("Location"):
            self.request["responseheaders"]["Location"] = self.request["responseheaders"]["Location"].replace(MockServer.server, MockServer.mock_address).replace(urllib.quote(MockServer.server,''), urllib.quote(MockServer.mock_address,''))
        if self.request["responseheaders"].has_key("Content-Length"):
            del self.request["responseheaders"]["Content-Length"]
        
    def _parse_respheaders(self):
        headers = []
        for key, value in self.request["responseheaders"].items():
            header = (str(key).encode('utf-8'), str(value))
            headers.append(header)
        return headers         
    
    def _search_mapping(self):
        filename = False
        if self.strictname in MockServer.response_mapping:
            filename = copy.deepcopy(self.strictname)
        elif self.relaxname in MockServer.response_mapping:
            filename = copy.deepcopy(self.relaxname)
        if filename:
            response = MockServer.response_mapping.pop(filename)
            self.request["status"] = response["status"]
            self.request["responseheaders"] = response["headers"]
            self.request["responsebody"] = response["body"]
        return filename
    
    def _filter_form_data_boundary(self):
        #adjust request for special format
        if self.request["requestheaders"].has_key("CONTENT-TYPE"):
            if self.request["requestheaders"]["CONTENT-TYPE"].startswith("multipart/form-data; boundary="):
                self.boundary = self.request["requestheaders"]["CONTENT-TYPE"].split("multipart/form-data; boundary=")[1]
                self.request["requestbody"] = self.request["requestbody"].replace(self.boundary,"----MockServerBoundary")
                self.request["requestheaders"]["CONTENT-TYPE"] = "multipart/form-data; boundary=----MockServerBoundary"
    
    def _recover_form_data_boundary(self):
        if hasattr(self, "boundary"):
            self.request["requestbody"] = self.request["requestbody"].replace("----MockServerBoundary", self.boundary)
            self.request["requestheaders"]["CONTENT-TYPE"] = "multipart/form-data; boundary=%s" % self.boundary
            
    
    def _process_response(self):
        self.strictname = MockServer.get_strictname(self.request)
        self.relaxname = MockServer.get_relaxname(self.request)
        if MockServer.mode == "mock":
            filename = self._search_mapping()
            if not filename:
                filename = MockServer.search_request(self.strictname, self.relaxname)
                if filename:
                    MockServer.get_response(self.request, filename)
                    self.request["responseheaders"]["Date"] = self._get_date()
                else:
                    filename = copy.deepcopy(self.strictname)
                    if MockServer.auto_forward:
                        MockGlobals.get_mocklogger().info("API %s not found, use autoforward" % filename)
                        self._send_API()
                    else:
                        MockGlobals.get_mocklogger().info("API %s not found, return 404 since autoforward is forbidden" % filename)
                        self.request["status"] = '404 Not Found'
                        self.request["responseheaders"] = {}
                        self.request["responsebody"] = '404 Not Found'
        else:
            self._send_API()
            if MockServer.request_mode == RequestMode.strict:
                filename = self.strictname
            else:
                filename = self.relaxname
        self.request["request_filename"] = filename
        web.ctx.headers = copy.deepcopy(self._parse_respheaders())
        web.ctx.status = copy.deepcopy(self.request["status"])
        
    def _process_request(self):
        try:
            currenttime = time.time()
            
            #capture request
            self.request = {
                                "url": web.ctx.fullpath.encode('utf-8'),
                                "method": web.ctx.method.encode('utf-8'),
                                "requestheaders": self._parse_reqheaders(),
                                "requestbody": web.data(),
                                "path": str(web.ctx.path).encode('utf-8'),
                                "parameters": self._parse_parameters(),
                                "remote_address":":".join([web.ctx.env["REMOTE_ADDR"],web.ctx.env["REMOTE_PORT"]]), 
                                "request_filename":""
                            }
            self.request["requestbody"] = self.request["requestbody"] if not isinstance(self.request["requestbody"], unicode) else self.request["requestbody"].encode('utf-8')
            self._filter_form_data_boundary()
            #process response
            self._process_response()
            
            body = copy.deepcopy(self.request["responsebody"])
            
            #save records
            if MockServer.mode == "record":
                request = copy.copy(self.request)
                if request["responseheaders"].has_key("Date"):
                    del request["responseheaders"]["Date"]
                MockServer.save_request(request)
                
            self._save_log()
            
            #process delay   
            delay = self.request["delay"] if self.request.has_key("delay") else MockServer.get_delay()
            delay = delay + currenttime - time.time()
            if delay>0:
                time.sleep(delay)
            del self.request
            return body
        except Exception:
            traceback.print_exc()
            MockGlobals.get_mocklogger().exception("Mock Code Error, please report this issue")
            return "Mock Code Error, please report this issue"
    
    def _save_log(self):
        try:
            json.dumps(self.request["requestbody"])
        except:
            self.request["requestbody"] = base64.b64encode(self.request["requestbody"])
            MockGlobals.get_mocklogger().info("Request body is encoded with base64")
        
        try:
            json.dumps(self.request["responsebody"])
        except:
            self.request["responsebody"] = base64.b64encode(self.request["responsebody"])
            MockGlobals.get_mocklogger().info("Response body is encoded with base64")
        
        try:
            MockGlobals.get_requestlogger().info("", extra = self.request)
        except:
            traceback.print_exc()
            MockGlobals.get_mocklogger().error("Cannot save log for request %s" % self.request["request_filename"])
    
class SetMode(object):
    def GET(self):
        '''
        set mode or global mode 
        '''
        mock_logger = MockGlobals.get_mocklogger()
        try:
            data = web.input()       
            MockServer.set_mode(data.mode)
            mock_logger.info("Set mode to %s" % data.mode)
            return '{"status":"ok"}'
        except Exception, e:
            traceback.print_exc()
            mock_logger.exception("general server error: %s" % str(e))
            return '{"status":"failure","message":"general server error: %s"}' % str(e)

class SetDelay(object):
    def GET(self):
        '''
        set delay
        '''
        try:
            data = web.input()
            import string
            delaytime = string.atof(data.delay)
            MockServer.set_delay(delaytime)
            return '{"status":"ok"}'
        except Exception, e:
            traceback.print_exc()
            mock_logger = MockGlobals.get_mocklogger()
            mock_logger.exception("general server error: %s" % str(e))
            return '{"status":"failure","message":"general server error: %s"}' % str(e)
        
class SetNumber(object):
    def POST(self):
        '''
        set response number manually
        '''
        try:
            data = Utils.get_dict_from_json(web.data())
            assert data.has_key("filename")
            assert data.has_key("number")
            filename=Utils.check_filename(data["filename"])
            print os.path.join(MockServer.api_folder,filename)
            assert os.path.isfile(os.path.join(MockServer.api_folder,filename))
            MockServer.number_mapping[filename] = data["number"]
            return '{"status":"ok"}'
        except Exception, e:
            traceback.print_exc()
            mock_logger = MockGlobals.get_mocklogger()
            mock_logger.exception("general server error: %s" % str(e))
            return '{"status":"failure","message":"general server error: %s"}' % str(e)

class SearchRequest(object):
    def POST(self):
        '''
        search for request and return the corresponding serial number of the template file
        '''   
        try:
            data = Utils.get_dict_from_json(web.data())
            headers = {}
            for header in data["requestheaders"]:
                headers[header.upper()] = data["requestheaders"][header]
            headers = MockServer.filter_headers(headers)
            
            self.request = {
                                "method": data["method"],
                                "requestheaders": headers,
                                "requestbody": data["requestbody"],
                                "path": data["path"],
                                "parameters": data["parameters"],

                            }
            self.strictname = MockServer.get_strictname(self.request)
            self.relaxname = MockServer.get_relaxname(self.request)
            result = MockServer.search_request(self.strictname, self.relaxname)
            del self.request
            if result:
                return '{"status":"ok", "filename":%s}' % result
            else:
                mock_logger = MockGlobals.get_mocklogger()
                mock_logger.exception("template file %s not found. request is %s" % (self.strictname, 
                                                                                     str(web.data())))
                return '{"status":"failure","message":"template file %s not found"}' % self.strictname
        except Exception, e:
            traceback.print_exc()
            mock_logger = MockGlobals.get_mocklogger()
            mock_logger.exception("general server error: %s" % str(e))
            return '{"status":"failure","message":"general server error: %s"}' % str(e)

class SetResponseOnce:
    def POST(self):
        '''
        put new response in the mapping and only one time available
        '''
        try:
            data = Utils.get_dict_from_json(web.data())
            if data.has_key("filename"):
                resp = {"status":data["status"],"headers":data["responseheaders"],"body":data["responsebody"]}
                MockServer.response_mapping[Utils.check_filename(data['filename'])] = resp
                return '{"status":"ok"}'
            assert data.has_key("mode") and RequestMode.is_valid(data["mode"])
            if data["mode"] == RequestMode.relax:
                filename = MockServer.get_relaxname(data)
            else:
                filename = MockServer.get_strictname(data)
            resp = {"status":data["status"],"headers":data["responseheaders"],"body":data["responsebody"]}
            MockServer.response_mapping[filename] = resp
            return '{"status":"ok"}'
        except Exception, e:
            traceback.print_exc()
            mock_logger = MockGlobals.get_mocklogger()
            mock_logger.exception("general server error: %s" % str(e))
            return '{"status":"failure","message":"general server error: %s"}' % str(e)

class SetResponseCommon(object):
    def POST(self):
        '''
        modify the response of specified request forever
        '''     
        try:
            data = Utils.get_dict_from_json(web.data())
            self.request = {
                                "method": data["method"] if data.has_key["method"] else None,
                                "requestheaders": data["requestheaders"] if data.has_key["requestheaders"] else None,
                                "requestbody": data["requestbody"] if data.has_key["requestbody"] else None,
                                "path": data["path"] if data.has_key["path"] else None,
                                "parameters": data["parameters"] if data.has_key["parameters"] else None,
                                "number":0 if not data.has_key("number") else data["number"],
                                "responseheaders": data["responseheaders"],
                                "responsebody": data["responsebody"],
                                "status": data["status"]
                            }
            
            if data.has_key("filename"):
                if os.path.isfile(Utils.check_filename(data["filename"])):
                    MockServer.set_response(self.request, Utils.check_filename(data["filename"]))
                    return '{"status":"ok","message":"new response added"}'
                else:
                    return '''{"status":"failure","message":"filename doesn't exist"}'''
            self.strictname = MockServer.get_strictname(data)
            self.relaxname = MockServer.get_relaxname(data)
            filename = MockServer.search_request(self.strictname, self.relaxname)
            if filename:
                MockServer.set_response(self.request, filename)
                return '{"status":"ok","message":"new response added"}'
            else:
                assert data.has_key("mode") and RequestMode.is_valid(data["mode"])
                filename = self.strictname if data["mode"] != RequestMode.relax else self.relaxname
                MockServer.set_response(self.request, filename, data["mode"])
                return '{"status":"ok","message":"new request created"}'
        except Exception, e:
            traceback.print_exc()
            mock_logger = MockGlobals.get_mocklogger()
            mock_logger.exception("general server error: %s" % str(e))
            return '{"status":"failure","message":"general server error: %s"}' % str(e)

class ResetName(object):
    def GET(self):
        '''Check all file name, regenerate if not match'''
        try:
            MockServer.reset_name()
            return '{"status":"ok"}'
        except Exception, e:
            traceback.print_exc()
            mock_logger = MockGlobals.get_mocklogger()
            mock_logger.exception("general server error: %s" % str(e))
            return '{"status":"failure","message":"general server error: %s"}' % str(e)
    