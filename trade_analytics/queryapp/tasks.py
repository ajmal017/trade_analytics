# Create your tasks here
# from __future__ import absolute_import, unicode_literals
from celery import shared_task
import stockapp.models as stkmd
import queryapp.models as qrymd

import pandas as pd

def computequeries(stkid,Trange):
	querycodes=qrymd.QueryComputeCode.objects.all()
	for computecode in querycodes:
		computeclass=computecode.importcomputeclass()
		CC=computeclass(stkid,Trange)
		CC.computeall(skipdone=True)
		CC.saveall()

def processfeatures(rerun=False):
	stocks=stkmd.Stockmeta.objects.all()
	Fromdate=pd.datetime(2008,1,1)
	Todate=pd.datetime.today()
	Trange=pd.date_range(Fromdate,Todate)
	Trange=[T.date() for T in Trange if T.weekday()<=4]

	for stk in stocks:
		computequeries(stk.id,Trange)

		
