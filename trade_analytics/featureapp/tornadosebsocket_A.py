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
import multiprocessing as mp

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

import zmq
import pickle as pkl
import zlib

context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://*:5555")


def RUN(df,ip):
    server=None
    class IndexHandler(web.RequestHandler):
        def get(self):
            self.render('index_A.html',ip=ip)

    class SocketHandler(websocket.WebSocketHandler):
        def open(self):
            print 'new connection'
        def on_close(self):
            print 'connection closed'
            ioloop = tornado.ioloop.IOLoop.current().instance()
            # ioloop = tornado.ioloop.IOLoop.instance()
            ioloop.add_callback(server.stop)
            ioloop.add_callback(ioloop.stop)

        def check_origin(self, origin):
            return True

        def on_message(self, message):
            message=json.loads(message)
            print message
            if 'cmnd' in message:
                if message['cmnd']=='quit':
                    # self.close()
                    # tornado.ioloop.IOLoop.make_current()
                    
                    # time.sleep(1)
                    # ioloop.add_callback(ioloop.close)
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
    # tornado.ioloop.IOLoop.clear_instance()
    # tornado.ioloop.IOLoop.instance().install()
    tornado.ioloop.IOLoop.current().instance().start()
        

    server.stop()
    # ioloop = tornado.ioloop.IOLoop.instance()
    # ioloop.stop()
    # ioloop.close()
    # ioloop.add_callback(ioloop.close)

    print "stopped"

if __name__ == '__main__':
    i=0
    P=[]
    while (1):
        try:
            message = socket.recv(flags=zmq.NOBLOCK)
            z=zlib.decompress(message)
            df=pkl.loads(z)
            print "---------%s----------------"%str(i) 
            ip=3345+i
            p=mp.Process(target=RUN,args=(df,ip))   
            p.start()
            P.append([p,time.time()])
            i=i+1

            #  Send reply back to client
            socket.send("received dataframe")

        except zmq.Again as e:
            print "No messages"
        
        for p in P:
            p[0].join(0.2)
            if time.time()-p[1]>100:
                p[0].terminate()

        time.sleep(0.5)

    # # thrd1=threading.Thread(target=RUN,args=(df.copy(),ip))
    # # thrd1.start()
    
    # print "---------2----------------" 
    # ip=ip+1
    # p2=mp.Process(target=RUN,args=(df.copy(),ip))    
    # p2.start()
    # # thrd2=threading.Thread(target=RUN,args=(df.copy(),ip))
    # # thrd2.start()

    # p1.join()
    # p2.join()

    # thrd1.join()
    # thrd2.join()
    # print "Your web server will self destruct in 2 minutes"
    # time.sleep(100)
    # stopTornado()
    # thrd.join()
