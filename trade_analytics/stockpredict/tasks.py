from __future__ import division
import stockapp.models as stkmd

import datascience.models as dtscmd
import datascience.libs as dtsclibs
import datascience.ML.MLmodels as MLmd
from django.conf import settings

import time
import pandas as pd
from utility import maintenance as mnt

import stockpredict.libs as stkprdctlibs

import logging
logger = logging.getLogger('debug')



if settings.USE_REDIS:
	from django_rq import job as shared_task

elif settings.USE_CELERY:
	from celery import shared_task
	from celery.exceptions import TimeoutError
	from celery.signals import worker_process_init

	@worker_process_init.connect
	def fix_multiprocessing(**kwargs):
	    from multiprocessing import current_process
	    try:
	        current_process()._config
	    except AttributeError:
	        current_process()._config = {'semprefix': '/mp'}
	    print "fixed multiprocessing"
else:
	# use dummy task
	raise Exception('Unknown option for task distribution')




@shared_task
def CreateBaseStockData_bySymbols(funcId,dataId):
	SymbolIds=stkmd.Stockmeta.objects.all().values_list('id',flat=True)
	for SymbolId in SymbolIds:
		stkprdctlibs.CreateStockData_mondays_directfrom_DM(SymbolId,dataId)

