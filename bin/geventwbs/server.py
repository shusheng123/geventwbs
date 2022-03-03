import logging
from gevent.pywsgi import WSGIServer
from .handler import WebSocketHandler

log = logging.getLogger()

class WebSocketServer(WSGIServer):
    handler_class = WebSocketHandler

    def __init__(self, *args, **kwargs):
        self.clients = {}

        super(WebSocketServer, self).__init__(*args, **kwargs)

    def handle(self, socket, address):
        handler = self.handler_class(socket, address, self)
        handler.handle()
    
    def serve_forever(self):
        log.info('%s server started at:%d', self.address[0], self.address[1])
        super().serve_forever()