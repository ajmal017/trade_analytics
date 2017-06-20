from __future__ import division
import pandas as pd
import pandas_datareader.data as web
import stockapp.models as stkmd
from django.db import connections
from dataapp import models as dtamd
import utility.codemanager as utcdmng
import datetime
import time
import pdb
from talib import abstract
import numpy as np
from utility import maintenance as mnt

import logging
logger=logging.getLogger('debug')

import time

def StockDataFrame_validate(df,columns=['Close','Open','High','Low','Volume']):
	for cc in columns:
		if cc not in df.columns:
			return False
	if type(df.index[0])!=pd.datetime:
		return False

	return True

def StockDataFrame_sanitize(df,standardize=False):
	if len(df)==0:
		return df
			
	df['Close']=df['Close'].astype(float)
	df['Open']=df['Open'].astype(float)
	df['High']=df['High'].astype(float)
	df['Low']=df['Low'].astype(float)
	df['Volume']=df['Volume'].astype(int)

	def setdate(x):
		if isinstance(x,basestring):
			return pd.to_datetime(x).date()
		if type(x)==datetime.datetime or type(x)==pd.datetime or type(x)==pd.Timestamp:
			return x.date()
		return x
	
	if 'Date' in df.columns:
		df['Date']=df['Date'].apply(setdate)
		df.sort_values(by=['Date'],inplace=True)
		
	index_is_datetype=False
	if isinstance(df.index[0],basestring):
		try:
			pd.to_datetime(df.index[0]).date()
			index_is_datetype=True
		except:
			index_is_datetype=False
	elif type(df.index[0])==datetime.datetime or type(df.index[0])==pd.datetime or type(df.index[0])==pd.datetime.date or type(df.index[0])==datetime.date or type(df.index[0])==pd.Timestamp:
		index_is_datetype=True


	if index_is_datetype:
		df.index=map(lambda x :setdate(x),df.index)



	if standardize:
		df.index=df['Date']
		df.drop(['Date'],axis=1,inplace=True)
		if 'id' in df.columns:
			df.drop(['id'],axis=1,inplace=True)
		if 'Symbol_id' in df.columns:
			df.drop(['Symbol_id'],axis=1,inplace=True)
		df.sort_index(inplace=True)

	return df

@mnt.logperf('debug',printit=True)
def addindicators(df,cols):
	inputs = {
    'open': df['Open'].values,
    'high': df['High'].values,
    'low': df['Low'].values,
    'close': df['Close'].values,
    'volume': df['Volume'].values
	}
	for cc in cols:
		if cc['colname'] not in df.columns:
			try:
				if cc['name']=='CCI':
					df[cc['colname']]=abstract.CCI(inputs, timeperiod=cc['timeperiod'])
					df[cc['colname']]=df[cc['colname']].astype(float)

				elif cc['name']=='SMA':
					df[cc['colname']]=df['Close'].rolling(window=cc['timeperiod']).mean()
					df[cc['colname']]=df[cc['colname']].astype(float)

				elif cc['name']=='SMAstd':
					df[cc['colname']]=df['Close'].rolling(window=cc['timeperiod']).std()
			
				elif cc['name']=='EMA':
					df[cc['colname']]=df['Close'].ewm(span=cc['timeperiod']).mean()
					df[cc['colname']]=df[cc['colname']].astype(float)

				elif cc['name']=='EMAstd':
					df[cc['colname']]=df['Close'].ewm(span=cc['timeperiod']).std(bias=False)
					df[cc['colname']]=df[cc['colname']].astype(float)
				else:
					print "Indicator not available"
					
			except Exception as e:
				df[cc['colname']]=np.nan
				print "error adding indicator ",cc['colname']
				logger.error("error adding indicator "+cc['colname']+" "+str(type(e))+" "+str(e))
				logger.exception(e)

	return df


@mnt.logperf('debug',printit=True)
def GetStockData(Symbolids,Fromdate=pd.datetime(2002,1,1).date(),Todate=pd.datetime.today().date(),format='concat',standardize=True,addcols=None):
	if type(Symbolids)==list:
		Symbolids=list(Symbolids)

	elif type(Symbolids)==tuple:
		Symbolids=list(Symbolids)

	elif type(Symbolids)==int or isinstance(Symbolids,basestring)==True:
		Symbolids=list([Symbolids])
	
	if isinstance(Symbolids[0],basestring)==True:
		for i in range(len(Symbolids)):
			Symbolids[i]=stkmd.Stockmeta.objects.get(Symbol=Symbolids[i]).id

	Symbolids=tuple(Symbolids)
	if len(Symbolids)==1:
		sqlquery="SELECT * FROM dataapp_stockprice as dsp WHERE dsp.\"Symbol_id\" = %(ids)s AND dsp.\"Date\" BETWEEN '%(fromdate)s' AND '%(todate)s';"
		sqlQ=sqlquery%{'ids':str(Symbolids[0]),'fromdate':Fromdate.strftime("%Y-%m-%d"),'todate':Todate.strftime("%Y-%m-%d")}

	else:
		sqlquery="SELECT * FROM dataapp_stockprice as dsp WHERE dsp.\"Symbol_id\" IN %(ids)s AND dsp.\"Date\" BETWEEN '%(fromdate)s' AND '%(todate)s';"
		sqlQ=sqlquery%{'ids':str(tuple(Symbolids)),'fromdate':Fromdate.strftime("%Y-%m-%d"),'todate':Todate.strftime("%Y-%m-%d")}

	df=pd.read_sql(sqlQ,connections[dtamd.Stockprice._DATABASE])
	df=StockDataFrame_sanitize(df,standardize=standardize)


	if format=='list':
		L=[]
		for symbid in Symbolids:
			dp=df[df['Symbol_id']==symbid].copy()
			if addcols is not None:
				dp=addindicators(dp,addcols)
			L.append( dp )
		return L

	elif format=='dict':
		D={}
		for symbid in Symbolids:
			dp=df[df['Symbol_id']==symbid].copy()
			if addcols is not None:
				dp=addindicators(dp,addcols)
			D[symbid]=dp 
		return D		
	

	elif format=='concat':
		return df
	



def predownloadcheck(stk):
	Todate=pd.datetime.today().date()

	if stk.Lastdate is None:
		Fromdate=pd.datetime(2002,1,1).date()
	else:
		Fromdate=stk.Lastdate


	if stk.LastPriceUpdate==pd.datetime.today().date():
		print "skipping ",stk," as LastpriceUpdate is today "
		return {'status':'Success','Todate':Todate,'Fromdate':Fromdate}
	else:
		return {'status':'Run','Todate':Todate,'Fromdate':Fromdate}


	if Todate.dayofweek>=5:
		print "Today is weekend so no download ",stk
		return {'status':'Success','Todate':Todate,'Fromdate':Fromdate}

	if (Todate-Fromdate).days<1:
		print "Already updated ",stk
		return {'status':'Success','Todate':Todate,'Fromdate':Fromdate}
	else:
		return {'status':'Run','Todate':Todate,'Fromdate':Fromdate}


	
def DownloadData(Symbol, Fromdate,Todate):
	try:
		df=web.DataReader(Symbol, 'yahoo', Fromdate,Todate)
		return {'df':df,'status':'Success'}
	except:
		print "error downloading ",Symbol, " for input dates ",Fromdate,Todate
		return {'df':None,'status':'Fail'}

def ComputeIndex(stk,Fromdate,Todate):
	print "----------------------------------------"
	print "Compute Index on ",stk.Symbol
	print "----------------------------------------"

	stkgrpindex=stkmd.StockGroupIndex.objects.get(Symbol=stk)
	stkgrp=stkgrpindex.StockGroup
	stkind=stkgrpindex.Index
	grpstks_ids=stkgrp.Symbol.all().values_list('id',flat=True)
	try:
		code=stkind.IndexComputeClass.IndexComputeCode.Code
		ClassName=stkind.IndexComputeClass.ClassName
		module,computeclass=utcdmng.import_computeindexclass(code,"indexmodule",membername=ClassName)
		CC=computeclass()
		CC.compute(Fromdate=Fromdate,Todate=Todate,grpstks_ids=grpstks_ids)
		df=CC.getvalue(stkind.IndexLabel)
		return {'df':df,'status':'Success'}
	except:
		print "error computing index ",stk, " for input dates ",Fromdate,Todate	
		return {'df':None,'status':'Fail'}

def postdownloadcheck(stk,dfStartdate,dfLastdate):
	if stk.Lastdate is not None:
		if dfLastdate<=stk.Lastdate:
			print "skipping ",stk," as it is already uptodate "
			return {'status':'Success'}
		elif dfStartdate<=stk.Lastdate:
			print stk," download data has overlap "
			return {'status':'Overlap'}
		else:
			return {'status':'Run'}
	else:
		return {'status':'Run'}
		
def UpdatePriceData(Symbols_ids,*args,**kwargs):
	"""Update stock price data for given symbol ids

		Args:
			Symbols ids from db / Symbol strings,
			- args have to be json serializable for multiprocessing

	"""
	semaphore=kwargs.get('semaphore',None)
	if semaphore:
		semaphore.acquire()

	stocks=stkmd.Stockmeta.objects.filter(id__in=Symbols_ids)

	for stk in stocks:
		print "Working on ",stk.Symbol," ",stk.id
		comstat=stkmd.ComputeStatus_Stockdownload.objects.get(Status='ToDo',Symbol=stk)
		comstat.Status='Run'
		comstat.save()

		if stk.Update==False:
			print "skipping as update was set to False"
			comstat.Status='Success'
			comstat.save()
			stk.LastPriceUpdate=pd.datetime.today().date()
			stk.save()
			continue

		UpCk=predownloadcheck(stk)
		if UpCk['status']=='Success':
			comstat.Status='Success'
			comstat.save()
			stk.LastPriceUpdate=pd.datetime.today().date()
			stk.save()
			continue
		else:
			Fromdate=UpCk['Fromdate']
			Todate=UpCk['Todate']
		


		if stk.Derived:
			DD=ComputeIndex(stk, Fromdate,Todate)
		else:
			DD=DownloadData(stk.Symbol, Fromdate,Todate)


		if DD['status']=='Success':
			df=DD['df']
		else:
			comstat.Status='Fail'
			comstat.save()
			stk.LastPriceUpdate=pd.datetime.today().date()
			stk.save()
			continue

		df=StockDataFrame_sanitize(df,standardize=False)

		UpCk=postdownloadcheck(stk,df.index[0],df.index[-1])
		if UpCk['status']=='Success':
			stk.LastPriceUpdate=pd.datetime.today().date()
			stk.save()
			comstat.Status='Success'
			comstat.save()
			continue	
		elif UpCk['status']=='Overlap':
			df=df[df.index>stk.Lastdate]
		

		objs=[]
		for ind in df.index:
			objs.append( dtamd.Stockprice(Close=df.loc[ind,'Close'], Open=df.loc[ind,'Open'] ,
										 High=df.loc[ind,'High'],Low=df.loc[ind,'Low'],
										 Volume=df.loc[ind,'Volume'],Date=ind,Symbol=stk.Symbol,Symbol_id=stk.id)  )
		

		# use a lock/semaphore if required
		if kwargs.get('lock',None):
			with kwargs['lock']:
				dtamd.Stockprice.objects.bulk_create(objs)
		else:
			dtamd.Stockprice.objects.bulk_create(objs)
						
		stk.LastPriceUpdate=pd.datetime.today().date()

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

		print "Updated data for ", stk, " downloaded ", len(df)

	if semaphore:
		semaphore.release()

