from gevent.pywsgi import WSGIServer
from .handler import WebSocketHandler

class WebSocketServer(WSGIServer):
    handler_class = WebSocketHandler

    def __init__(self, *args, **kwargs):
        self.clients = {}

        super(WebSocketServer, self).__init__(*args, **kwargs)

    def handle(self, socket, address):
        handler = self.handler_class(socket, address, self)
        handler.handle()
