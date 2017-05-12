"""
Serve webcam images (from a remote socket dictionary server)
using Tornado (to a WebSocket browser client.)

Usage:

   python server.py <host> <port>

"""

# Import standard modules.

import matplotlib
matplotlib.use('Agg', force=True)
import matplotlib.pyplot as plt


import sys
import base64
import gc

try:
    from cStringIO import StringIO
except:
    from StringIO import StringIO

import time
# Import 3rd-party modules.
from tornado import websocket, web, ioloop
import numpy
# import coils
from io import BytesIO


class IndexHandler(web.RequestHandler):
    def get(self):
        self.render('index_A.html')

class SocketHandler(websocket.WebSocketHandler):
    def open(self):
        print 'new connection'
    def on_close(self):
        print 'connection closed'
 
    def check_origin(self, origin):
        return True

    def on_message(self, message):

        fig,ax=plt.subplots(1,1,figsize=(10,7))
        ax.plot([0,10],[1,10],'r')
        figfile = StringIO()
        fig.savefig(figfile,bbox_inches='tight',format='png')
        time.sleep(0.1)
        plt.close(fig)
        figfile.seek(0)
        image= base64.b64encode(figfile.getvalue())
        self.write_message(image)
        gc.collect()

app = web.Application([
    (r'/', IndexHandler),
    (r'/ws', SocketHandler),
])

if __name__ == '__main__':
    app.listen(9000)
    ioloop.IOLoop.instance().start()
