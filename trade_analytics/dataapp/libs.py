from __future__ import division
import pandas as pd
import pandas_datareader.data as web
import stockapp.models as stkmd
from dataapp import models as dtamd
import utility.codemanager as utcdmng
import datetime

def StockDataFrame_validate(df,columns=['Close','Open','High','Low','Volume']):
	for cc in columns:
		if cc not in df.columns:
			return False
	if type(df.index[0])!=pd.datetime:
		return False

	return True

def StockDataFrame_sanitize(df,standardize=False):
	df['Close']=df['Close'].astype(float)
	df['Open']=df['Open'].astype(float)
	df['High']=df['High'].astype(float)
	df['Low']=df['Low'].astype(float)
	df['Volume']=df['Volume'].astype(int)

	def setdate(x):
		if isinstance(x,basestring):
			return pd.to_datetime(x).date()
		if type(x)==datetime.datetime or type(x)==pd.datetime:
			return x.date()
		return x
	
	if 'Date' in df.columns:
		df['Date']=df['Date'].apply(setdate)
	else:
		df.index=df.index.map(setdate)

	if standardize:
		df.index=df['Date']
		df.drop(['Date'],axis=1,inplace=True)
		if 'id' in df.columns:
			df.drop(['id'],axis=1,inplace=True)
		if 'Symbol_id' in df.columns:
			df.drop(['Symbol_id'],axis=1,inplace=True)

	return df


def GetStockData(Symbolids,Fromdate,Todate,format,standardize=True):
	if type(Symbolids)!=list:
		Symbolids=list(Symbolids)


	if format=='list':
		L=[]
		for symbid in Symbolids:
			df=pd.DataFrame( list( dtamd.Stockprice.objects.filter(Symbol_id=symbid,Date__range=[Fromdate,Todate]).values() ) )
			df=StockDataFrame_sanitize(df,standardize=standardize)
			L.append( df )
		return L
	elif format=='dict':
		D={}
		for symbid in Symbolids:
			df=pd.DataFrame( list( dtamd.Stockprice.objects.filter(Symbol_id=symbid,Date__range=[Fromdate,Todate]).values() ) ) 
			df=StockDataFrame_sanitize(df,standardize=standardize)
			D[symbid]= df
		return D		
	elif format=='concat':
		df=pd.DataFrame( list( dtamd.Stockprice.objects.filter(Symbol_id__in=Symbolids,Date__range=[Fromdate,Todate]).values() ) )
		df=StockDataFrame_sanitize(df,standardize=standardize)
		return df
	
def DownloadData(Symbol, Fromdate,Todate):
	try:
		df=web.DataReader(Symbol, 'yahoo', Fromdate,Todate)
		return {'df':df,'status':'Success'}
	except:
		print "error downloading ",Symbol, " for input dates ",Fromdate,Todate
		return {'df':None,'status':'Fail'}

def ComputeIndex(stk,Fromdate,Todate):
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

def predownloadcheck(stk):
	Todate=pd.datetime.today().date()

	if stk.Lastdate is None:
		Fromdate=pd.datetime(2002,1,1).date()
	else:
		Fromdate=stk.Lastdate

	if (Todate-Fromdate).days<1:
		print "Already updated ",stk
		return {'status':'Success','Todate':Todate,'Fromdate':Fromdate}
	else:
		return {'status':'Run','Todate':Todate,'Fromdate':Fromdate}


	if stk.LastPriceUpdate==pd.datetime.today().date():
		print "skipping ",stk," as LastpriceUpdate is today "
		return {'status':'Success','Todate':Todate,'Fromdate':Fromdate}
	else:
		return {'status':'Run','Todate':Todate,'Fromdate':Fromdate}


def postdownloadcheck(stk,downloadLastdate):
	if stk.Lastdate is not None:
		if downloadLastdate<=stk.Lastdate:
			print "skipping ",stk," as it is already uptodate "
			return {'status':'Success'}
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
		comstat=stkmd.ComputeStatus_Stockdownload.objects.get(Status='ToDo',Symbol=stk)
		comstat.Status='Run'
		comstat.save()

		if stk.Update==False:
			comstat.Status='Success'
			comstat.save()
			continue

		UpCk=predownloadcheck(stk)
		if UpCk['status']=='Success':
			comstat.Status='Success'
			comstat.save()
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
			continue

		UpCk=postdownloadcheck(stk,df.index[-1].date())
		if UpCk['status']=='Success':
			stk.LastPriceUpdate=pd.datetime.today().date()
			stk.save()
			comstat.Status='Success'
			comstat.save()
			continue	


		df=StockDataFrame_sanitize(df,standardize=False)
		

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
			stk.Startdate=df.index[0].date()

		if df.index[0].date()<stk.Startdate:
			stk.Startdate=df.index[0].date()

		if stk.Lastdate is None:
			stk.Lastdate=df.index[-1].date()

		if df.index[-1].date()>stk.Lastdate:
			stk.Lastdate=df.index[-1].date()

		

		stk.save()
		comstat.Status='Success'
		comstat.save()

		print "Updated data for ", stk, " downloaded ", len(df)," with key = ",kwargs.get('lock',None)
		del df

	if semaphore:
		semaphore.release()

