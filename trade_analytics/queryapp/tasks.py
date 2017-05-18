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

def computefeatuers(stkid,Trange):
	featurecodes=ftmd.FeatureComputeCode.objects.all()
	for computecode in featurecodes:
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
		computefeatuers(stk.id,Trange)

		
