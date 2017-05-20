# Create your tasks here
# from __future__ import absolute_import, unicode_literals
from celery import shared_task
import stockapp.models as stkmd
import queryapp.models as qrymd
import stockapp.models as stkmd
import dataapp.models as dtamd
import featureapp.models as ftmd

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
			q=Q.get_nowait()
		except Empty:
			print "Q done"
			break

		computequeries(*q)

def processqueries(rerun=False):
	stocks=stkmd.Stockmeta.objects.all()
	Fromdate=pd.datetime(2012,1,1)
	Todate=pd.datetime.today()
	Trange=pd.date_range(Fromdate,Todate)
	Trange=[T.date() for T in Trange if T.weekday()<=4]

	INQ=mp.Queue()
	for stk in stocks:
		INQ.put((stk.id,Trange))
	
	P=[]
	for i in range(5):
		P.append(mp.Process(target=processqryQ,args=(INQ,)) )
	
	for p in P:
		p.start()

	for p in P:
		p.join()

		

