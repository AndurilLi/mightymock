'''
Created on Jul 20, 2014

@author: pli, yuliu
'''
import httplib2, traceback, json
import Utils

class Request:
    def __init__(self, filename=None, method=None, path=None, 
                 requestheaders={}, requestbody="", parameters={}, 
                 responseheaders={}, responsebody="", status=None,
                 number = 0):
        self.filename = filename
        self.method = method
        self.path = path
        if path and not path.startswith("/"):
            self.path = "/" + self.path
        self.requestheaders = requestheaders
        self.requestbody = requestbody
        self.parameters = parameters
        self.responseheaders = responseheaders
        self.responsebody = responsebody
        self.status = status
        self.number = number

class ClientAPI:
    def __init__(self, serveraddr, port, ssl = False):
        if ssl:
            prefix = "https://"
        else:
            prefix = "http://"
        self.baseurl = "%s%s:%s" % (prefix, serveraddr, port)
        if self.baseurl.endswith("/"):
            self.baseurl = self.baseurl[:-1]
    
    def sendAPI(self, path, method, paras="", body=""):
        http = httplib2.Http()
        http.disable_ssl_certificate_validation = True
        url = self.baseurl + path + paras
        print url
        try:
            resp, content = http.request(url, method, body)
        except Exception, e:
            traceback.print_exc()
            print "Mock Server response error %s" % str(e)
            return None
        del resp
        return content
    
    def SetMode(self, mode, path="/set/mode"):
        resp = self.sendAPI(path, "GET", "?mode="+mode)
        return True if resp == '{"status":"ok"}' else False
    
    def SetDelay(self, delay, path="/set/delay"):
        resp = self.sendAPI(path, "GET", "?delay="+delay)
        return True if resp == '{"status":"ok"}' else False
        
    def SetNumber(self, filename, number, path="/set/number"):
        body = {
                    "filename": filename,
                    "number": number
                }
        resp = self.sendAPI(path, "POST", {}, json.dumps(body))
        return True if resp == '{"status":"ok"}' else False
    
    def ResetName(self, path="/set/reset_name"):
        resp = self.sendAPI(path, "GET")
        return True if resp == '{"status":"ok"}' else False
    
    def SearchRequest(self, request, path="/search/request"):
        body = {
                    "method": request.method,
                    "requestheaders": request.headers,
                    "requestbody": request.body,
                    "path": request.path,
                    "parameters": request.parameters
                }
        resp = self.sendAPI(path, "POST", {}, json.dumps(body))
        if resp.startswith('{"status":"ok",'):
            data = Utils.get_dict_from_json(resp)
            return data["filename"]
        else:
            return None
    
    def SetResponseOnce(self, request, path="/set/response_once"):
        body = {
                    "method": request.method,
                    "requestheaders": request.headers,
                    "requestbody": request.body,
                    "path": request.path,
                    "parameters": request.parameters,
                    "status":request.status,
                    "responseheaders":request.responseheaders,
                    "responsebody":request.responsebody
                }
        if request.filename:
            body["filename"] = request.filename
        resp = self.sendAPI(path, "POST", {}, json.dumps(body))
        return True if resp == '{"status":"ok"}' else False
    
    def SetResponseCommon(self, request, path="/set/response_common"):
        body = {
                    "method": request.method,
                    "requestheaders": request.headers,
                    "requestbody": request.body,
                    "path": request.path,
                    "parameters": request.parameters,
                    "status":request.status,
                    "responseheaders":request.responseheaders,
                    "responsebody":request.responsebody,
                    "number":request.number
                }
        resp = self.sendAPI(path, "POST", {}, json.dumps(body))
        return True if resp == '{"status":"ok"}' else False