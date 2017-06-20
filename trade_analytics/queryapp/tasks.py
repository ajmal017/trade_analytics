# Create your tasks here
# from __future__ import absolute_import, unicode_literals
from celery import shared_task
import stockapp.models as stkmd
import queryapp.models as qrymd
import stockapp.models as stkmd
import dataapp.models as dtamd


import itertools as itt
import numpy as np
import multiprocessing as mp
from Queue import Empty
import time
import pandas as pd
from django import db

import pandas as pd

def computequeries(stkid,Trange):
	querycodes=qrymd.QueryComputeCode.objects.all()
	for computecode in querycodes:
		computeclass=computecode.importcomputeclass()
		CC=computeclass(stkid,Trange)
		CC.computeall(skipdone=True)
		CC.saveall()

def processqryQ(Q):
	while True:
		try:
			q=Q.get(block=True)
		except Empty:
			print "Q done"
			break


		print "Working on ",q[0]


		try:
			comstat=qrymd.ComputeStatus_Query.objects.get(Status='ToDo',Symbol__id=q[0])
			comstat.Status='Run'
			comstat.save()

			computequeries(*q)

			comstat=qrymd.ComputeStatus_Query.objects.get(Status='Run',Symbol__id=q[0])
			comstat.Status='Success'
			comstat.save()

		except:
			comstat=qrymd.ComputeStatus_Query.objects.get(Status='Run',Symbol__id=q[0])
			comstat.Status='Fail'
			comstat.save()

def processqueries(rerun=False):
	stocks=stkmd.Stockmeta.objects.all()
	Fromdate=pd.datetime(2012,1,1)
	Todate=pd.datetime.today()
	Trange=pd.date_range(Fromdate,Todate)
	Trange=[T.date() for T in Trange if T.weekday()<=4]


	qrymd.ComputeStatus_Query.objects.filter(Status='Success').delete()
	qrymd.ComputeStatus_Query.objects.filter(Status='Run').delete()
	qrymd.ComputeStatus_Query.objects.filter(Status='ToDo').delete()

	objs=[]
	for stk in stkmd.Stockmeta.objects.all():
		objs.append( qrymd.ComputeStatus_Query(Status='ToDo',Symbol=stk) )
	qrymd.ComputeStatus_Query.objects.bulk_create(objs)


	INQ=mp.Queue()
	for stk in stocks:
		INQ.put((stk.id,Trange))
		time.sleep(0.01)

	db.connections.close_all()
	
	P=[]
	for i in range(6):
		P.append(mp.Process(target=processqryQ,args=(INQ,)) )
	
	for p in P:
		p.start()

	for p in P:
		p.join()

		

