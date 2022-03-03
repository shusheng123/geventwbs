# vim: set ts=4 et sw=4 sts=4 fileencoding=utf-8 :
import logging
from zbase3.base.logger import install
log = install('stdout')


from geventwbs import WebSocketServer, WebSocketApplication, Resource

class EchoApplication(WebSocketApplication):
    def on_open(self):
        print("Connection opened")

    def on_message(self, message):

        return message

    def on_close(self, reason):
        print(reason)

WebSocketServer(
    ('0.0.0.0', 8000),
    application=Resource([('/con/msg', EchoApplication)])
).serve_forever()
