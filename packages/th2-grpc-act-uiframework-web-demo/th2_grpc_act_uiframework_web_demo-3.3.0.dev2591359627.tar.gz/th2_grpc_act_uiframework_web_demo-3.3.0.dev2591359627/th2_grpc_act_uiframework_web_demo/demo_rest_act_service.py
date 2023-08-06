from . import uiframework_web_demo_pb2_grpc as importStub

class DemoRestActService(object):

    def __init__(self, router):
        self.connector = router.get_connection(DemoRestActService, importStub.DemoRestActStub)

    def getLastMessageFromProvider(self, request, timeout=None, properties=None):
        return self.connector.create_request('getLastMessageFromProvider', request, timeout, properties)