from . import uiframework_web_demo_pb2_grpc as importStub

class UiFrameWorkHandWebActService(object):

    def __init__(self, router):
        self.connector = router.get_connection(UiFrameWorkHandWebActService, importStub.UiFrameWorkHandWebActStub)

    def register(self, request, timeout=None, properties=None):
        return self.connector.create_request('register', request, timeout, properties)

    def unregister(self, request, timeout=None, properties=None):
        return self.connector.create_request('unregister', request, timeout, properties)

    def sendNewOrderSingleGui(self, request, timeout=None, properties=None):
        return self.connector.create_request('sendNewOrderSingleGui', request, timeout, properties)

    def extractSentMessageGui(self, request, timeout=None, properties=None):
        return self.connector.create_request('extractSentMessageGui', request, timeout, properties)

    def findMessageGui(self, request, timeout=None, properties=None):
        return self.connector.create_request('findMessageGui', request, timeout, properties)