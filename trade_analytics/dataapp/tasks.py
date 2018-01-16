from __future__ import division


import stockapp.models as stkmd
import dataapp.models as dtamd
import utility.parallelcomputations as utpc
import itertools as itt
import dataapp.libs as dtalibs
import dataapp.data_download.datadownloadmanager as dtadwnmang
import pandas as pd
import computeapp.models as cmpmd

# make the function shared
from django.conf import settings
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
def UpdatePriceData(Symbols_id,compute_session_id):
	stk=stkmd.Stockmeta.objects.get(id=Symbols_id)
	compute_status_obj=cmpmd.ComputeStatus.make_newcompute(compute_session_id)
	ddm=dtadwnmang.DataDownloadManager(stk,compute_status_obj)
	ddm.update_data()













