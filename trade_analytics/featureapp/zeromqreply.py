import time
import zmq
import pandas as pd
import pickle as pkl
import zlib
context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://*:5555")

while True:
    #  Wait for next request from client
    try:
	    message = socket.recv(flags=zmq.NOBLOCK)
	    z=zlib.decompress(message)
	    df=pkl.loads(z)
	    print df.mean().values
	    # print("Received request: %s" % message)

	    #  Do some 'work'
	    # time.sleep(1)

	    #  Send reply back to client
	    socket.send(df.mean().to_json())
    except zmq.Again as e:
    	print "No msg recieved "

    time.sleep(0.2)
