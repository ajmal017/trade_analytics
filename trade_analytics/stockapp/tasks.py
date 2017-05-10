# Create your tasks here
# from __future__ import absolute_import, unicode_literals
from celery import shared_task
import stockapp.models as md
import dataapp.models as dtamd
import itertools as itt
import numpy as np
import multiprocessing as mp
from Queue import Empty
import time
import pandas as pd


def processQ_SyncPrice2Meta(inQ,BadStartQ,BadLastQ,NoDataQ,InActiveQ,DuplicatesQ):
	while True:
		try:
			id=inQ.get_nowait()
		except Empty:
			print "Queue Done"
			break

		stk=md.Stockmeta.objects.get(id=id)
		print stk.Symbol,stk.Lastdate,stk.Startdate,stk.LastPriceUpdate,stk.Status,stk.Derived

		stkprices=dtamd.Stockprice.objects.filter(Symbol_id=stk.id).order_by('Date')
		if len(stkprices)>0:
			if stk.Startdate!=stkprices.first().Date:
				BadStartQ.put((stk.id,stkprices.first().Date))
				time.sleep(np.abs(np.random.randint(3)+1)/10)
				print '\t',stk.Symbol," start dates are not synced"
			if stk.Lastdate!=stkprices.last().Date:
				BadLastQ.put((stk.id,stkprices.last().Date))
				time.sleep(np.abs(np.random.randint(3))/10)
				print '\t',stk.Symbol," last dates are not synced"

			# checking for duplicates
			df=pd.DataFrame(list(stkprices.values('id','Date','Symbol','Symbol_id')))
			df['Date']=df['Date'].apply(lambda x: x.strftime("%Y-%m-%d"))
			dp=df.drop_duplicates(subset=['Date','Symbol','Symbol_id'])
			if len(df)!=len(dp):
				dupid=list(set(df['id'].values)-set(dp['id'].values))
				print "--------------------DUPLICATES---------------------------"
				print len(dupid)," Duplicates detected for ",stk.Symbol
				print "---------------------------------------------------------"
				for d in dupid:
					DuplicatesQ.put(d)
				time.sleep(0.1)
				stkprices.filter(id__in=dupid).delete()

		else:
			NoDataQ.put((stk.id,None))
			time.sleep(np.abs(np.random.randint(3))/10)
			print '\t',stk.Symbol," has no data"

		if md.ComputeStatus_Stockdownload.objects.filter(Symbol=stk,Status='Fail').count()>=10:
			InActiveQ.put((stk.id,None))
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
	DuplicatesQ=mp.Queue()

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
	while not DuplicatesQ.empty():
		DuplicatesQ.get()

	for stk in md.Stockmeta.objects.all():
		inQ.put(stk.id) 
	time.sleep(1)

	P=[]
	from django import db
	db.connections.close_all()
	for i in range(mp.cpu_count()-1):
		P.append(mp.Process(target=processQ_SyncPrice2Meta,args=(inQ,BadStartQ,BadLastQ,NoDataQ,InActiveQ,DuplicatesQ)))
	for p in P:
		p.start()
		time.sleep(1)

	for p in P:
		p.join()
		time.sleep(1)

	print "DOne all jobs"

	BadStartstks=[]
	while not BadStartQ.empty():
		q=BadStartQ.get()
		BadStartstks.append( [md.Stockmeta.objects.get(id=q[0]),q[1] ] )
	BadLaststks=[]
	while not BadLastQ.empty():
		q=BadLastQ.get()
		BadLaststks.append( [md.Stockmeta.objects.get(id=q[0]),q[1] ] )
	NoDatastks=[]
	while not NoDataQ.empty():
		q=NoDataQ.get()
		NoDatastks.append( [md.Stockmeta.objects.get(id=q[0]),q[1] ] )
	InActivestks=[]
	while not InActiveQ.empty():
		q=InActiveQ.get()
		InActivestks.append( [md.Stockmeta.objects.get(id=q[0]),q[1] ] )

	Duplicatestkprc=[]
	while not DuplicatesQ.empty():
		q=DuplicatesQ.get()
		Duplicatestkprc.append( q )

	print "====================================================="
	print '		Summary'
	print "====================================================="
	print 'NoData = ',len(NoDatastks)
	print 'BadStartdates = ',len(BadStartstks)
	print 'BadLastdates = ',len(BadLaststks)
	print "InActive = ",len(InActivestks)
	print "Duplicates = ",len(Duplicatestkprc)
	print "====================================================="

	print "Setting activity status"
	for stk in  InActivestks:
		stk[0].Status='Inactive'
		stk[0].save()

	print "Setting start date"
	for stk in  BadStartstks:
		stk[0].Startdate=stk[1]
		stk[0].save()

	print "Setting last date"
	for stk in  BadLaststks:
		stk[0].Lastdate=stk[1]
		stk[0].save()