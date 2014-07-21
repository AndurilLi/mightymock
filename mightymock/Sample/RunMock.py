'''
Created on Jul 3, 2014

@author: pli, yuliu
'''
import sys

# from mightymock.MockConfiguration import MockConfiguration
# from mightymock.MockServer import MockServer
# import web
# def main(argv = sys.argv):
#     urls = (
#         '/set/response_once', "SetResponseOnce",
#         '/set/response_common',"SetResponseCommon",
#         '/search/request',"SearchRequest",
#         '/set/number', "SetNumber",
#         '/set/delay', "SetDelay",
#         '/set/mode', "SetMode",
#         '/set/reset_name',"ResetName",
#         '^.*', 'RequestHandler'
#         ) 
#     mock_config = MockConfiguration()
#     mock_config.setup(argv)
#     MockServer.set_config_info()
#     app = web.application(urls, globals())
#     sys.argv[1:] = ["%s:%s" % (mock_config.baseurl, str(mock_config.port))]
#     app.run()

from mightymock import RunMock
RunMock.main(sys.argv)