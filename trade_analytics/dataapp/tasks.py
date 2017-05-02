from __future__ import division

import pandas as pd
import pandas_datareader.data as web
from celery import shared_task
import stockapp.models as stkmd
from dataapp import models as dtamd
import utility as uty
import itertools as itt
import numpy as np



def DownloadData(Symbol, Fromdate,Todate):
	df=web.DataReader(Symbol, 'yahoo', Fromdate,Todate)
	return df

def UpdateStockPriceDB(df):
	df.to_sql()

@shared_task
def UpdatePriceData(Symbols_ids,inputtype,*args,**kwargs):
	"""Update stock price data for given symbol ids

		Args:
			Symbols ids from db / Symbol strings,
			- args have to be json serializable for multiprocessing

	"""
	if type(Symbols_ids)!=list:
		Symbols_ids=[Symbols_ids ]

	if inputtype=='id':
		stocks=stkmd.Stockmeta.objects.filter(id__in=Symbols_ids)
	elif inputtype=='Symbol':
		stocks=stkmd.Stockmeta.objects.filter(Symbol__in=Symbols_ids)


	Todate=pd.datetime.today().date()

	for stk in stocks:
		comstat=stkmd.ComputeStatus_Stockmeta.get(Status='ToDo',Symbol=stk)
		comstat.Status='Run'
		comstat.save()

		if stk.Lastdate is None:
			Fromdate=pd.datetime(2002,1,1).date()
		else:
			Fromdate=stk.Lastdate

		if (Todate-Fromdate).days<1:
			print "Already updated ",stk, "\r",
			comstat.Status='Success'
			comstat.save()
			continue

		if stk.LastPriceUpdate==pd.datetime.today().date():
			print "skipping ",stk," as LastpriceUpdate is today \r",
			comstat.Status='Success'
			comstat.save()
			continue

		try:
			df=DownloadData(stk.Symbol, Fromdate,Todate)
		except:
			print "error downloading ",stk, " for input dates ",Fromdate,Todate
			comstat.Status='Fail'
			comstat.save()
			continue

		if stk.Lastdate is not None:
			if df.index[-1]<=stk.Lastdate:
				print "skipping ",stk," as it is already uptodate \r",
				stk.LastPriceUpdate=pd.datetime.today()
				stk.save()

				comstat.Status='Success'
				comstat.save()

				continue				

		objs=[]
		for ind in df.index:
			objs.append( dtamd.Stockprice(Close=df.loc[ind,'Close'], Open=df.loc[ind,'Open'] ,
										 High=df.loc[ind,'High'],Low=df.loc[ind,'Low'],
										 Volume=df.loc[ind,'Volume'],Date=ind,Symbol=stk.Symbol,Symbol_id=stk.id)  )
		
		if 'lock' not in kwargs:
			dtamd.Stockprice.objects.bulk_create(objs)
		else:
			kwargs['lock'].acquire()
			dtamd.Stockprice.objects.bulk_create(objs)
			kwargs['lock'].release()

		stk.LastPriceUpdate=pd.datetime.today()
		if stk.Startdate is None:
			stk.Startdate=df.index[0]
		if df.index[0]<stk.Startdate:
			stk.Startdate=df.index[0]

		if stk.Lastdate is None:
			stk.Lastdate=df.index[-1]
		if df.index[-1]>stk.Lastdate:
			stk.Lastdate=df.index[-1]

		

		stk.save()
		comstat.Status='Success'
		comstat.save()

		print "Updated data for ", stk, " downloaded ", len(df)," with key = ",kwargs.get('lock',default=None),'\r',
		del df

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
