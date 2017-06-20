# Create your tasks here
# from __future__ import absolute_import, unicode_literals
from celery import shared_task
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

import logging
logger = logging.getLogger('debug')

def computefeatuers(stkid,Trange):
	featurecodes=ftmd.FeatureComputeCode.objects.all()
	for computecode in featurecodes:
		computeclass=computecode.importcomputeclass()
		CC=computeclass(stkid,Trange)
		CC.computeall(skipdone=True)
		CC.saveall()
		del CC



def processfeatQ(Q):
	while True:
		try:
			q=Q.get(block=True)
		except Empty:
			print "Q done"
			break


		print "Working on ",q[0]


		try:
			comstat=ftmd.ComputeStatus_Feature.objects.get(Status='ToDo',Symbol__id=q[0])
			comstat.Status='Run'
			comstat.save()

			computefeatuers(*q)

			comstat=ftmd.ComputeStatus_Feature.objects.get(Status='Run',Symbol__id=q[0])
			comstat.Status='Success'
			comstat.save()

			print "Done on ",q[0]

		except Exception as e:
			comstat=ftmd.ComputeStatus_Feature.objects.get(Status='Run',Symbol__id=q[0])
			comstat.Status='Fail'
			comstat.save()

			logger.error("Failed Computation of "+str(q[0])+" "+str(e)  )

			print "Failed on ",q[0],e


def processfeatures(rerun=False):
	stocks=stkmd.Stockmeta.objects.all()
	Fromdate=pd.datetime(2012,1,1)
	Todate=pd.datetime.today()
	Trange=pd.date_range(Fromdate,Todate)
	Trange=[T.date() for T in Trange if T.weekday()<=4]

	ftmd.ComputeStatus_Feature.objects.filter(Status='Success').delete()
	ftmd.ComputeStatus_Feature.objects.filter(Status='Run').delete()
	ftmd.ComputeStatus_Feature.objects.filter(Status='ToDo').delete()

	objs=[]
	for stk in stkmd.Stockmeta.objects.all():
		objs.append( ftmd.ComputeStatus_Feature(Status='ToDo',Symbol=stk) )
	ftmd.ComputeStatus_Feature.objects.bulk_create(objs)

	print "Buildoing compute Q"
	INQ=mp.Queue()
	for stk in stocks:
		print " adding to Q ",stk.id,"\r,"
		INQ.put((stk.id,Trange))
		time.sleep(0.01)
	
	print "Starting up processors"

	db.connections.close_all()
	
	P=[]
	for i in range(7):
		P.append(mp.Process(target=processfeatQ,args=(INQ,)) )
	
	for p in P:
		p.start()

	for p in P:
		p.join()



