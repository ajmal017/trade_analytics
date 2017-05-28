"""
Serve webcam images (from a remote socket dictionary server)
using Tornado (to a WebSocket browser client.)

Usage:

   python server.py <host> <port>

"""

# Import standard modules.
from __future__ import division
import datascience.models as dtscmd
import utility.parallelcomputations as utprll
import charts.libs as chlibs

import Queue
import pandas as pd
import time, threading
from tornado.websocket import WebSocketClosedError
try:
	from cStringIO import StringIO
except:
	from StringIO import StringIO
import multiprocessing as mp

import numpy as np
import time
# Import 3rd-party modules.
import tornado
from tornado import web, ioloop, options, httpserver
from tornado import websocket, web, ioloop
import numpy as np
# import coils
from io import BytesIO
import json
import webbrowser
import numpy as np
import zmq
import pickle as pkl
import zlib

import os

pd.set_option('max_colwidth', 150)



context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://*:5562")
websocketip=1826







def webinterface(df,pricecols,querycols,featcols,ip):
	
	server=None
	
	class IndexHandler(web.RequestHandler):
		def get(self):
			self.render('df_charter.html',ip=ip)

	class SocketHandler(websocket.WebSocketHandler):
		def open(self):
			print 'new connection'
			self.window=360
			self.moveby=30
			self.T0=df.index[0]
			self.TF=(df.index[0]+pd.DateOffset(self.window) ).date()
			self.paras={'window':360,'moveby':30}
			self.imageQ=Queue.Queue()
			self.plotQ=Queue.Queue()
			# self.event=threading.Event()
			# self.event.clear()
			# self.thrd=threading.Thread(target=precomputecharts,args=(df,pricecols,querycols,featcols,self.event,self.imageQ,self.plotQ))
			# self.thrd.start()
			self.chartscompute=utprll.MPconsumer(3,chlibs.CurrentByFutureChart,usecache=True,constarg=(),constkwarg={'df':df,'pricecols':pricecols,'querycols':querycols,'featcols':featcols})
			self.chartscompute.start()

			self.dir='right'
			self.chartsinQ=[]

			labelslist=list( set(dtscmd.Label.objects.all().values_list('label',flat=True)) )
			self.write_message(json.dumps({'labelslist':labelslist}))

			self.savedplots={}
			
			self.showlogs()

		def on_close(self):
			print 'connection closed'
			# self.event.set()
			# self.thrd.join()
			self.chartscompute.stop()

			ioloop = tornado.ioloop.IOLoop.current().instance()
			# ioloop = tornado.ioloop.IOLoop.instance()
			ioloop.add_callback(server.stop)
			ioloop.add_callback(ioloop.stop)

		def check_origin(self, origin):
			return True

		# def clearQs(self):
		# 	with self.imageQ.mutex:
		# 		self.imageQ.queue.clear()
		# 	with self.plotQ.mutex:
		# 		self.plotQ.queue.clear()
		# 	print self.imageQ.empty(),self.plotQ.empty()
		# 	self.chartsinQ=[]

		def showlogs(self):
			logs=pd.DataFrame( list( dtscmd.Label.objects.filter(Symbol=df['Symbol'].iloc[0],T__range=[self.T0,self.TF]).values('id','Symbol','window','T','label') ) )
			if not logs.empty:
				logs['idstr']=logs['id'].apply(lambda x: str(x))
				logs['delete']="<input type='submit' id='del_"+logs['idstr']+"' value='Delete' onclick=\"return deletelog('"+ logs['idstr'] +"');\" >"
				self.write_message(json.dumps({'logs': logs.to_html(escape=False,index=False,columns=['id','Symbol','window','T','label','delete']) }))
			else:
				self.write_message(json.dumps({'logs': '' }))

		def AddChartSequence(self):
			N=30
			T0=self.T0
			TF=self.TF

			for i in range(N):
				print T0,TF
				self.chartscompute.append2Q({'args':(T0,TF)})

				# if (T0,TF) not in self.chartsinQ:
				# 	print T0,TF
				# 	self.plotQ.put({'T0':T0,'TF':TF})
				# 	self.chartsinQ.append((T0,TF))
				# 	time.sleep(0.1)

				if self.dir =='right':
					if TF>df.index[-1]:
						break
					TF=(TF+pd.DateOffset(self.moveby)).date()
					T0=(TF-pd.DateOffset(self.window)).date()
				if self.dir =='left':
					TF=(TF-pd.DateOffset(self.moveby)).date()
					T0=(TF-pd.DateOffset(self.window)).date()
					if T0<df.index[0]:
						break

		def on_message(self, message):
			message=json.loads(message)
			print message

			if 'cmnd' in message:
				if message['cmnd']=='quit':
					self.close()
				if message['cmnd']=='moveright':
					if self.dir=='left':
						self.chartscompute.clearQs()

					self.dir='right'
					self.TF=(self.TF+pd.DateOffset(self.moveby)).date()
					self.T0=(self.TF-pd.DateOffset(self.window)).date()

				if message['cmnd']=='moveleft':
					if self.dir=='right':
						self.chartscompute.clearQs()

					self.dir='left'
					self.TF=(self.TF-pd.DateOffset(self.moveby)).date()
					self.T0=(self.TF-pd.DateOffset(self.window)).date()

			if message.get('para',None):
				if message['para'].get('moveby',None):
					self.moveby=int( message['para']['moveby'] )
					self.chartscompute.clearQs()
					self.write_message(json.dumps({'info':"moveby set"}))
					return 
					
				if message['para'].get('window',None):
					self.window=int( message['para']['window'] )
					self.chartscompute.clearQs()
					self.T0=(self.TF-pd.DateOffset(self.window)).date()
					self.write_message(json.dumps({'info':"window set"}))

				if message['para'].get('newlabel',None):
					if dtscmd.Label.objects.filter(label=message['para']['newlabel']).exists()==False:
						labelslist=list(set( list( dtscmd.Label.objects.all().values_list('label',flat=True) )+[message['para']['newlabel']] ))
						self.write_message(json.dumps({'labelslist':labelslist}))
						return


				if message['para'].get('addlabel',None):
					if not dtscmd.Label.objects.filter(label=message['para']['addlabel']['label'],Symbol=df['Symbol'].iloc[0],T=message['para']['addlabel']['T'],window=self.window).exists():
						resp=dtscmd.Label(label=message['para']['addlabel']['label'],Symbol=df['Symbol'].iloc[0],T=message['para']['addlabel']['T'],window=self.window)	
						resp.save()
						self.write_message(json.dumps({'info': "recoreded "+message['para']['addlabel']['label'] }))                        
						self.showlogs()
					return

				if message['para'].get('deletelog',None):
					id=int(message['para']['deletelog']['logid'])
					dtscmd.Label.objects.filter(id=id).delete()
					self.write_message(json.dumps({'info': "log entry deleted" }))                        
					self.showlogs()
					return

			self.showlogs()

			try:
				# image=MakeChart(df,self.T0,self.TF,featcols)
				self.AddChartSequence()

				print "getting img from queue"
				qimg=self.chartscompute.getQ()
				self.TF=qimg['TF']
				self.T0=qimg['T0']
				print "got it from queue"
				st=json.dumps({'image':qimg['image'],'T':self.TF.strftime("%Y-%m-%d")})
				self.write_message(st)

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

def main():
	i=0
	P=[]
	while (1):
		try:
			message = socket.recv(flags=zmq.NOBLOCK)
			flg=False
			try:
				z=zlib.decompress(message)
				message=pkl.loads(z)
				print "recieved = ",message
				pricecols=message['pricecols']
				querycols=message['querycols']
				featcols=message['featcols']
				df=message['df']
				flg=True
			except:
				print "message not readable or has missing values"
				socket.send("error in message")
					
			if flg==True:
				print "---------%s----------------"%str(i) 
				ip=websocketip+i
				p=mp.Process(target=webinterface,args=(df,pricecols,querycols,featcols,ip))   
				p.start()
				P.append([p,time.time()])
				i=i+1

				socket.send("received dataframe")

		except zmq.Again as e:
			print e
			print "#df charts = ",len(P),time.time(),"\r",
		
		delP=[]
		for p in P:
			p[0].join(0.2)
			# if time.time()-p[1]>10000:
			# 	p[0].terminate()
			# 	time.sleep(0.5)

			
			if not p[0].is_alive():
				delP.append(p)

		P=[p for p in P if p not in delP]
		
		time.sleep(2)



if __name__ == '__main__':
	main()