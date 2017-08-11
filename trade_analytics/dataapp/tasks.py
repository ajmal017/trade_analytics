from __future__ import division


import stockapp.models as stkmd
import dataapp.models as dtamd
import utility.parallelcomputations as utpc
import itertools as itt
import dataapp.libs as dtalibs

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
def UpdatePriceData(Symbols_ids,*args,**kwargs):
	dtalibs.UpdatePriceData(Symbols_ids,*args,**kwargs)


def RunDataDownload():
	# get chumks of ids to work on. This is a iterable of lists
	stkmd.ComputeStatus_Stockdownload.objects.filter(Status='Success').delete()
	stkmd.ComputeStatus_Stockdownload.objects.filter(Status='Run').delete()
	stkmd.ComputeStatus_Stockdownload.objects.filter(Status='ToDo').delete()
	objs=[]
	for stk in stkmd.Stockmeta.objects.all():
		objs.append( stkmd.ComputeStatus_Stockdownload(Status='ToDo',Symbol=stk) )
	stkmd.ComputeStatus_Stockdownload.objects.bulk_create(objs)

	#append the additional arg of 'id'
	# computeargs_iter=itt.imap(lambda x: itt.izip([x],['id']) , stocksiter)

	# run in parallel
	stocksiter=list(stkmd.Stockmeta.objects.filter(Derived=False).values_list('id',flat=True))+list(stkmd.Stockmeta.objects.filter(Derived=True).values_list('id',flat=True))
	PllCmpt=utpc.ParallelCompute( stocksiter, UpdatePriceData )
	from django import db
	db.connections.close_all()
	# PllCmpt.ParallelRun(chunkby=100,Lock=False,Semaphore=True)
	PllCmpt.ConsumerQueuerun(chunkby=100,Lock=False)
	# PllCmpt.SingleRun()


