# Create your tasks here
# from __future__ import absolute_import, unicode_literals
from celery import shared_task
import stockapp.models as md
import dataapp.models as dtamd
import itertools as itt
import numpy as np
import multiprocessing as mp
import time



def processQ_SyncPrice2Meta(inQ,BadStartQ,BadLastQ,NoDataQ,InActiveQ):
	while True:
		try:
			id=inQ.get()
		except mp.Queue.Empty:
			print "Queue Done"
			break

		stk=md.Stockmeta.objects.get(id=id)
		print stk.Symbol,stk.Lastdate,stk.Startdate,stk.LastPriceUpdate,stk.Status,stk.Derived

		stkprices=dtamd.Stockprice.objects.filter(Symbol_id=stk.id).order_by('Date')
		if len(stkprices)>0:
			if stk.Startdate!=stkprices.first().Date:
				BadStartQ.put(stk.id)
				time.sleep(np.abs(np.random.randint(3)+1)/10)
				print '\t',stk.Symbol," start dates are not synced"
			if stk.Lastdate!=stkprices.last().Date:
				BadLastQ.put(stk.id)
				time.sleep(np.abs(np.random.randint(3))/10)
				print '\t',stk.Symbol," last dates are not synced"
		else:
			NoDataQ.put(stk.id)
			time.sleep(np.abs(np.random.randint(3))/10)
			print '\t',stk.Symbol," has no data"

		if md.ComputeStatus_Stockdownload.objects.filter(Symbol=stk,Status='Fail').count()>=10:
			InActiveQ.put(stk.id)
			time.sleep(np.abs(np.random.randint(3))/10)
			print stk.Symbol," failed 10 times will be made inactive"

def SyncPrice2Meta():
	"""
	sync all the price data to meta data
	"""
	inQ=mp.Queue()
	BadStartQ=mp.Queue()
	BadLastQ=mp.Queue()
	NoDataQ=mp.Queue()
	InActiveQ=mp.Queue()

	while not inQ.empty():
		inQ.get()
	while not BadStartQ.empty():
		BadStartQ.get()
	while not BadLastQ.empty():
		BadLastQ.get()
	while not NoDataQ.empty():
		NoDataQ.get()
	while not InActiveQ.empty():
		InActiveQ.get()

	for stk in md.Stockmeta.objects.all():
		inQ.put(stk.id) 
	time.sleep(1)

	P=[]
	for i in range(mp.cpu_count()-1):
		P.append(mp.Process(target=processQ_SyncPrice2Meta,args=(inQ,BadStartQ,BadLastQ,NoDataQ,InActiveQ)))
	for p in P:
		p.start()
		time.sleep(1)

	for p in P:
		p.join()
		time.sleep(1)

	BadStartstks=[]
	while not BadStartQ.empty():
		BadStartstks.append( md.Stockmeta.objects.get(id=BadStartQ.get()) )
	BadLaststks=[]
	while not BadLastQ.empty():
		BadLaststks.append( md.Stockmeta.objects.get(id=BadLastQ.get()) )
	NoDatastks=[]
	while not NoDataQ.empty():
		NoDatastks.append( md.Stockmeta.objects.get(id=NoDataQ.get()) )
	InActivestks=[]
	while not InActiveQ.empty():
		InActivestks.append( md.Stockmeta.objects.get(id=InActiveQ.get()) )

	print 'Summary'
	print 'NoData = ',len(NoDatastks)
	print 'BadStartdates = ',len(BadStartstks)
	print 'BadLastdates = ',len(BadLaststks)
	print "InActive = ",len(InActivestks)


