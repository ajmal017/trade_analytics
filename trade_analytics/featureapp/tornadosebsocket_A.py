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

import pandas as pd
import sys
import base64
import gc
import time, threading
from tornado.websocket import WebSocketClosedError
try:
    from cStringIO import StringIO
except:
    from StringIO import StringIO

import time
# Import 3rd-party modules.
import tornado
from tornado import web, ioloop, options, httpserver
from tornado import websocket, web, ioloop
import numpy
# import coils
from io import BytesIO
import json
import webbrowser
ip=9009
def RUN(df):
    server=None
    class IndexHandler(web.RequestHandler):
        def get(self):
            self.render('index_A.html',ip=ip)

    class SocketHandler(websocket.WebSocketHandler):
        def open(self):
            print 'new connection'
        def on_close(self):
            print 'connection closed'
     
        def check_origin(self, origin):
            return True

        def on_message(self, message):
            message=json.loads(message)
            print message
            if 'cmnd' in message:
                if message['cmnd']=='quit':
                    # self.close()
                    ioloop = tornado.ioloop.IOLoop.instance()
                    ioloop.add_callback(ioloop.stop)
                    self.close()
            try:
                fig,ax=plt.subplots(1,1,figsize=(10,7))
                ax.plot(df['A'],df['B'],'r')
                figfile = StringIO()
                fig.savefig(figfile,bbox_inches='tight',format='png')
                time.sleep(0.1)
                plt.close(fig)
                figfile.seek(0)
                image= base64.b64encode(figfile.getvalue())
                self.write_message(image)
                gc.collect()
            except WebSocketClosedError:
                print "closed websocket error "
                
    app = web.Application([
        (r'/', IndexHandler),
        (r'/ws', SocketHandler),
    ])
    server=httpserver.HTTPServer(app)

    server.listen(ip)
    webbrowser.open('http://localhost:%s'%str(ip),new=2)
    tornado.ioloop.IOLoop.instance().start()
    server.stop()
    # ioloop = tornado.ioloop.IOLoop.instance()
    # ioloop.add_callback(ioloop.close)



if __name__ == '__main__':
    df=pd.DataFrame({'A':[1,2,3,4],'B':[8,7,6,5]})
    thrd=threading.Thread(target=RUN,args=(df.copy(),))
    thrd.start()
    thrd.join()
    # print "Your web server will self destruct in 2 minutes"
    # time.sleep(100)
    # stopTornado()
    thrd.join()
