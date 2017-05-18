"""
Serve webcam images (from a remote socket dictionary server)
using Tornado (to a WebSocket browser client.)

Usage:

   python server.py <host> <port>

"""

# Import standard modules.
from __future__ import division
import matplotlib
matplotlib.use('Agg', force=True)
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter, WeekdayLocator,\
	DayLocator, MONDAY,date2num,num2date,AutoDateLocator
from matplotlib.finance import quotes_historical_yahoo_ohlc, candlestick_ohlc,candlestick2_ochl
import datascience.models as dtscmd
import Queue
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
import numpy as np
# import coils
from io import BytesIO
import json
import webbrowser
import numpy as np
import zmq
import pickle as pkl
import zlib
import simplejson as sjson

import os

pd.set_option('max_colwidth', 150)



context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://*:5559")
websocketip=1820

def MakeChart(dF,T0,T,featcols):
	dF['datenum']=date2num(dF.index)
	df=dF[T0:T].copy()
	dfperf=dF[T:(T+pd.DateOffset(360)).date()].copy()
	
	autodate=AutoDateLocator()
	mondays = WeekdayLocator(MONDAY)        # major ticks on the mondays
	alldays = DayLocator()              # minor ticks on the days
	weekFormatter = DateFormatter('%Y\n %b %d')  # e.g., Jan 12
	dayFormatter = DateFormatter('%d')      # e.g., 12

	fig, ax = plt.subplots(1,2,figsize=(20,7))
	fig.subplots_adjust(bottom=0.2)
	ax[0].xaxis.set_major_locator(autodate)
	ax[0].xaxis.set_minor_locator(alldays)
	ax[0].xaxis.set_major_formatter(weekFormatter)
	
	

	quotes=[tuple(x) for x in df[['datenum','Open','High','Low','Close','Volume']].to_records(index=False)]
	ret=candlestick_ohlc(ax[0], quotes, width=0.6)
	ax[0].plot(df['datenum'],df['SMA20'],'g--',label='SMA20')
	ax[0].plot(df['datenum'],df['SMA50'],'r--',label='SMA50')
	
	L=df['High'].max()-df['Low'].min()
	mm=df['Volume'].max()
	ax[0].bar(df['datenum'],0.5*L*df['Volume']/mm,bottom=df['Low'].min()-1.5,color='y',alpha=0.5)
#     volume_overlay3(ax[0], quotes, colorup='k', colordown='r', width=4, alpha=1.0)
	
	for ff in  featcols:
		dp=df[df[ff]==True]
		ax[0].plot(dp['datenum'],dp['Close'],'y',marker='o',markersize=15,linestyle='',label=ff)
	
	ax[0].set_xlim(quotes[0][0],quotes[-1][0])
	ax[0].set_ylim(df['Low'].min()*0.9,df['High'].max()*1.1)
	ax[0].grid()
	
	ax2 = ax[0].twinx()
	ax2.set_ylim(df['Low'].min()*0.9,df['High'].max()*1.1)
#     ax2.set_yticks( )
	
	ax[0].xaxis_date()
	ax[0].autoscale_view()
	plt.setp(ax[0].get_xticklabels(), rotation=45, horizontalalignment='right')
	
	autodate=AutoDateLocator()
	mondays = WeekdayLocator(MONDAY)        # major ticks on the mondays
	alldays = DayLocator()              # minor ticks on the days
	weekFormatter = DateFormatter('%Y\n %b %d')  # e.g., Jan 12
	dayFormatter = DateFormatter('%d')      # e.g., 12

	ax[1].xaxis.set_major_locator(autodate)
	ax[1].xaxis.set_minor_locator(alldays)
	ax[1].xaxis.set_major_formatter(weekFormatter)
	
	ax[1].plot(dfperf['datenum'],dfperf['Close'],label='Close')
	ax[1].plot(dfperf['datenum'],dfperf['SMA20'],'g--',label='SMA20')
	ax[1].plot(dfperf['datenum'],dfperf['SMA50'],'r--',label='SMA50')
	
	L=dfperf['High'].max()-dfperf['Low'].min()
	mm=dfperf['Volume'].max()
	ax[1].bar(dfperf['datenum'],0.5*L*dfperf['Volume']/mm,bottom=dfperf['Low'].min()-1.5,color='y',alpha=0.5)

	
	ind3m=dfperf.index[dfperf.index<=(T+pd.DateOffset(90)).date()][-1]
	ind6m=dfperf.index[dfperf.index<=(T+pd.DateOffset(180)).date()][-1]
	ax[1].plot([dfperf.loc[ind3m,'datenum'],dfperf.loc[ind3m,'datenum']],[dfperf['Low'].min()*0.9,dfperf['High'].max()*1.1],label='Close')
	ax[1].plot([dfperf.loc[ind6m,'datenum'],dfperf.loc[ind6m,'datenum']],[dfperf['Low'].min()*0.9,dfperf['High'].max()*1.1],label='Close')
	
	ax[1].set_ylim(dfperf['Low'].min()*0.9,dfperf['High'].max()*1.1)
	ax[1].xaxis_date()
	ax[1].autoscale_view()
	ax[1].grid()
	
	plt.setp(ax[1].get_xticklabels(), rotation=45, horizontalalignment='right')
	
	plt.subplots_adjust(wspace=0.1, hspace=0)

	figfile = StringIO()
	fig.savefig(figfile,bbox_inches='tight',format='png')
	time.sleep(0.1)
	plt.close(fig)
	figfile.seek(0)
	image= base64.b64encode(figfile.getvalue())
	gc.collect()
	return image



def precomputecharts(df,featcols,evnt,imageQ,plotQ):
	while(1):
		try:
			plotpara=plotQ.get_nowait()
			TF=plotpara['TF']
			T0=plotpara['T0']
			image=MakeChart(df,T0,TF,featcols)
			imageQ.put({'T0':T0,'TF':TF,'image':image})
			time.sleep(0.1)

		except Queue.Empty:
			time.sleep(0.2)

		if evnt.is_set():
			print "event set"
			break

def webinterface(df,featcols,ip):
	
	server=None
	
	class IndexHandler(web.RequestHandler):
		def get(self):
			self.render('dfcharter.html',ip=ip)

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
			self.event=threading.Event()
			self.event.clear()
			self.thrd=threading.Thread(target=precomputecharts,args=(df,featcols,self.event,self.imageQ,self.plotQ))
			self.thrd.start()
			self.dir='right'
			self.chartsinQ=[]

			labelslist=list( set(dtscmd.Label.objects.all().values_list('label',flat=True)) )
			self.write_message(json.dumps({'labelslist':labelslist}))

			self.showlogs()

		def on_close(self):
			print 'connection closed'
			self.event.set()
			self.thrd.join()

			ioloop = tornado.ioloop.IOLoop.current().instance()
			# ioloop = tornado.ioloop.IOLoop.instance()
			ioloop.add_callback(server.stop)
			ioloop.add_callback(ioloop.stop)

		def check_origin(self, origin):
			return True

		def clearQs(self):
			with self.imageQ.mutex:
				self.imageQ.queue.clear()
			with self.plotQ.mutex:
				self.plotQ.queue.clear()
			print self.imageQ.empty(),self.plotQ.empty()
			self.chartsinQ=[]

		def showlogs(self):
			logs=pd.DataFrame( list( dtscmd.Label.objects.filter(Symbol=df['Symbol'].iloc[0],T__range=[self.T0,self.TF]).values('id','Symbol','window','T','label') ) )
			if not logs.empty:
				logs['idstr']=logs['id'].apply(lambda x: str(x))
				logs['delete']="<input type='submit' id='del_"+logs['idstr']+"' value='Delete' onclick=\"return deletelog('"+ logs['idstr'] +"');\" >"
				self.write_message(json.dumps({'logs': logs.to_html(escape=False,index=False,columns=['id','Symbol','window','T','label','delete']) }))
			else:
				self.write_message(json.dumps({'logs': '' }))
		def on_message(self, message):
			message=json.loads(message)
			print message

			if 'cmnd' in message:
				if message['cmnd']=='quit':
					# tornado.ioloop.IOLoop.make_current()
					# ioloop.add_callback(ioloop.close)
					self.close()
				if message['cmnd']=='moveright':
					if self.dir=='left':
						self.clearQs()

					self.dir='right'
					self.TF=(self.TF+pd.DateOffset(self.moveby)).date()
					self.T0=(self.TF-pd.DateOffset(self.window)).date()
				if message['cmnd']=='moveleft':
					if self.dir=='right':
						self.clearQs()

					self.dir='left'
					self.TF=(self.TF-pd.DateOffset(self.moveby)).date()
					self.T0=(self.TF-pd.DateOffset(self.window)).date()

			if message.get('para',None):
				if message['para'].get('moveby',None):
					self.moveby=int( message['para']['moveby'] )
					self.clearQs()
					self.write_message(json.dumps({'info':"moveby set"}))
					return 
					
				if message['para'].get('window',None):
					self.window=int( message['para']['window'] )
					self.clearQs()
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
				N=15
				T0=self.T0
				TF=self.TF

				for i in range(N):
					if (T0,TF) not in self.chartsinQ:
						print T0,TF
						self.plotQ.put({'T0':T0,'TF':TF})
						self.chartsinQ.append((T0,TF))
						time.sleep(0.1)

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

				print "getting img from queue"
				qimg=self.imageQ.get(block=True)
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

def RUN():
	i=0
	P=[]
	while (1):
		try:
			message = socket.recv(flags=zmq.NOBLOCK)
			flg=False
			try:
				z=zlib.decompress(message)
				message=pkl.loads(z)
				featcols=message['featcols']
				df=message['df']
				flg=True
			except:
				print "message not readable or has missing values"
				socket.send("error in message")
					
			if flg==True:
				print "---------%s----------------"%str(i) 
				ip=websocketip+i
				p=mp.Process(target=webinterface,args=(df,featcols,ip))   
				p.start()
				P.append([p,time.time()])
				i=i+1

				socket.send("received dataframe")

		except zmq.Again as e:
			print "#df charts = ",len(P),time.time(),"\r",
		
		delP=[]
		for p in P:
			p[0].join(0.2)
			if time.time()-p[1]>10000:
				p[0].terminate()
				time.sleep(0.5)

			
			if not p[0].is_alive():
				delP.append(p)

		P=[p for p in P if p not in delP]
		
		time.sleep(2)



if __name__ == '__main__':
	RUN()