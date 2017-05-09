from __future__ import division

from celery import shared_task
import stockapp.models as stkmd
import dataapp.models as dtamd
import utility.parallelcomputations as utpc
import itertools as itt
import dataapp.libs as dtalibs

# make the function shared
UpdatePriceData=shared_task(dtalibs.UpdatePriceData)


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


