'''
Created on Jul 20, 2014

@author: pli, yuliu
'''
import httplib2, traceback, json, time
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
    
    def sendAPI(self, path, method, paras="", body="", times = 0):
        http = httplib2.Http(disable_ssl_certificate_validation = True)
        url = self.baseurl + path + paras
        print url
        try:
            resp, content = http.request(url, method, body)
        except httplib2.SSLHandshakeError:
            time.sleep(3)
            if times > 5:
                print "Mock Server meet SSLHandShakeError"
                traceback.print_exc()
                return None
            return self.sendAPI(path, method, paras, body, times+1)
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
        resp = self.sendAPI(path, "POST", body = json.dumps(body))
        return True if resp == '{"status":"ok"}' else False
    
    def ResetName(self, path="/set/reset_name"):
        resp = self.sendAPI(path, "GET")
        return True if resp == '{"status":"ok"}' else False
    
    def SearchRequest(self, request, path="/search/request"):
        body = {
                    "method": request.method,
                    "requestheaders": request.requestheaders,
                    "requestbody": request.requestbody,
                    "path": request.path,
                    "parameters": request.parameters
                }
        resp = self.sendAPI(path, "POST", body = json.dumps(body))
        if resp.startswith('{"status":"ok",'):
            data = Utils.get_dict_from_json(resp)
            return data["filename"]
        else:
            return None
    
    def SetResponseOnce(self, request, path="/set/response_once"):
        body = {
                    "method": request.method,
                    "requestheaders": request.requestheaders,
                    "requestbody": request.requestbody,
                    "path": request.path,
                    "parameters": request.parameters,
                    "status":request.status,
                    "responseheaders":request.responseheaders,
                    "responsebody":request.responsebody
                }
        if request.filename:
            body["filename"] = request.filename
        resp = self.sendAPI(path, "POST", body = json.dumps(body))
        return True if resp == '{"status":"ok"}' else False
    
    def SetResponseCommon(self, request, path="/set/response_common"):
        body = {
                    "method": request.method,
                    "requestheaders": request.requestheaders,
                    "requestbody": request.requestbody,
                    "path": request.path,
                    "parameters": request.parameters,
                    "status":request.status,
                    "responseheaders":request.responseheaders,
                    "responsebody":request.responsebody,
                    "number":request.number
                }
        if request.filename:
            body["filename"] = request.filename
        resp = self.sendAPI(path, "POST", body = json.dumps(body))
        return True if resp == '{"status":"ok"}' else False