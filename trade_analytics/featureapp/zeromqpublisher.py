import sys
import time
import zmq
import pandas as pd
context = zmq.Context()

# Socket to receive messages on
# receiver = context.socket(zmq.PULL)
# receiver.connect("tcp://localhost:5557")

# Socket to send messages to
sender = context.socket(zmq.PUSH)
sender.connect("tcp://localhost:5558")

# Process tasks forever
i=0
while True:
	print "sending ",i
	# Send results to sink
	sender.send(str(i))
	i=i+1
	time.sleep(1)
