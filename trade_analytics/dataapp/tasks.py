from __future__ import division

import pandas as pd
import pandas_datareader.data as web
from celery import shared_task
import stockapp.models as stkmd
from dataapp import models as dtamd
import utility as uty
import itertools as itt


def DownloadData(Symbol, Fromdate,Todate):
	df=web.DataReader(Symbol, 'yahoo', Fromdate,Todate)
	return df

def UpdateStockPriceDB(df):
	df.to_sql()

@shared_task
def UpdatePriceData(Symbols_ids,inputtype='id'):
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


	Todate=pd.datetime.today()

	for stk in stocks:

		if stk.Startdate is None:
			Fromdate=pd.datetime(2002,1,1)
		else:
			Fromdate=stk.Startdate
		df=DownloadData(stk.Symbol, Fromdate,Todate)
		objs=[]
		for ind in df.index:
			objs.append( dtamd.Stockprice(Close=df.loc[ind,'Close'], Open=df.loc[ind,'Open'] ,
	                                     High=df.loc[ind,'High'],Low=df.loc[ind,'Low'],
	                                     Volume=df.loc[ind,'Volume'],Date=ind,Symbol=stk.Symbol,Symbol_id=stk.id)  )
	    
    	dtamd.Stockprice.objects.bulk_create(objs)

    	print "Updated data for ", stk, " downloaded ", len(df),'\r',

def RunDataDownload():
	# get chumks of ids to work on. This is a iterable of lists
	stocksiter=stkmd.Stockmeta.objects.all().IDchunks()

	#append the additional arg of 'id'
	computeargs_iter=itt.imap(lambda x: itt.izip(x,itt.repeat('id')) , stocksiter)
	
	# run in parallel
	PllCmpt=uty.ParallelCompute( computeargs_iter, UpdatePriceData )
	PllCmpt.parallelrun()
