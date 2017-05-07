from __future__ import division

from celery import shared_task
import stockapp.models as stkmd
import utility as uty
import itertools as itt
import dataapp.libs as dtalibs

# make the function shared
UpdatePriceData=shared_task(dtalibs.UpdatePriceData)



def RunDataDownload():
	# get chumks of ids to work on. This is a iterable of lists
	stocksiter=stkmd.Stockmeta.objects.all().IDchunks(100)
	stkmd.ComputeStatus_Stockmeta.objects.filter(Status='Success').delete()
	stkmd.ComputeStatus_Stockmeta.objects.filter(Status='Run').delete()
	stkmd.ComputeStatus_Stockmeta.objects.filter(Status='ToDo').delete()
	objs=[]
	for stk in stkmd.Stockmeta.objects.all():
		objs.append( stkmd.ComputeStatus_Stockmeta(Status='ToDo',Symbol=stk) )
	stkmd.ComputeStatus_Stockmeta.objects.bulk_create(objs)

	#append the additional arg of 'id'
	# computeargs_iter=itt.imap(lambda x: itt.izip([x],['id']) , stocksiter)
	computeargs_iter=itt.izip(stocksiter,itt.repeat('id') )

	# run in parallel
	PllCmpt=uty.ParallelCompute( computeargs_iter, UpdatePriceData )
	PllCmpt.parallelrun()

