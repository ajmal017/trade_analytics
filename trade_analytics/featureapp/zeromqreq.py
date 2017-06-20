

#
#   Hello World client in Python
#   Connects REQ socket to tcp://localhost:5555
#   Sends "Hello" to server, expects "World" back
#

import zmq
import pandas as pd
import numpy as np
import time
import zlib
import pickle as pkl

context = zmq.Context()

#  Socket to talk to server
print("Connecting to hello world server")
socket = context.socket(zmq.REQ)
socket.connect("tcp://localhost:5555")

#  Do 10 requests, waiting each time for a response
for request in range(2):
    print("Sending request %s" % request)
    df=pd.DataFrame({'A':np.random.randn(100),'B':np.random.randn(100)})
    p=pkl.dumps(df)
    z = zlib.compress(p)
    print len(p),len(z)
    socket.send(z)

    #  Get the reply.
    message = socket.recv()
    print message
    print("sent/Received reply %s [ %s ]" % (str(df.mean().values), message) )
    time.sleep(1)


