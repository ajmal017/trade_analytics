from __future__ import division
import pandas as pd
import pandas_datareader.data as web
import stockapp.models as stkmd
from dataapp import models as dtamd


def StockDataFrame_validate(df,columns=['Close','Open','High','Low','Volume']):
	for cc in columns:
		if cc not in df.columns:
			return False
	if type(df.index[0])!=pd.datetime:
		return False

	return True

def StockDataFrame_sanitize(df,setindex=False):
	df['Close']=df['Close'].astype(float)
	df['Open']=df['Open'].astype(float)
	df['High']=df['High'].astype(float)
	df['Low']=df['Low'].astype(float)
	df['Volume']=df['Volume'].astype(int)
	df['Date']=df['Date'].apply(lambda x: pd.to_datetime(x).date() if isinstance(x,basestring) else x.date() )
	if setindex:
		df.index=df['Date']
		df.drop(['Date'],axis=1,inplace=True)
	return df


def GetStockData(Symbolids,Fromdate,Todate,format):
	if type(Symbolids)!=list:
		Symbolids=list(Symbolids)


	if format=='list':
		L=[]
		for symbid in Symbolids:
			L.append( pd.DataFrame( list( dtamd.Stockprice.objects.filter(Symbol_id=symbid,Date__range=[Fromdate,Todate]).values() ) ) )
		return L
	elif format=='dict':
		D={}
		for symbid in Symbolids:
			D[symbid]= pd.DataFrame( list( dtamd.Stockprice.objects.filter(Symbol_id=symbid,Date__range=[Fromdate,Todate]).values() ) ) 
		return D		
	elif format=='concat':
		return pd.DataFrame( list( dtamd.Stockprice.objects.filter(Symbol_id__in=Symbolids,Date__range=[Fromdate,Todate]).values() ) )
	
def DownloadData(Symbol, Fromdate,Todate):
	try:
		df=web.DataReader(Symbol, 'yahoo', Fromdate,Todate)
		return {'df':df,'status':'Success'}
	except:
		print "error downloading ",Symbol, " for input dates ",Fromdate,Todate
		return {'df':None,'status':'Fail'}
		

def UpdateStockPriceDB(df):
	df.to_sql()


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

def UpdatePriceData(Symbols_ids,*args,**kwargs):
	"""Update stock price data for given symbol ids

		Args:
			Symbols ids from db / Symbol strings,
			- args have to be json serializable for multiprocessing

	"""

	stocks=stkmd.Stockmeta.objects.filter(id__in=Symbols_ids)

	for stk in stocks:
		comstat=stkmd.ComputeStatus_Stockmeta.objects.get(Status='ToDo',Symbol=stk)
		comstat.Status='Run'
		comstat.save()

		UpCk=predownloadcheck(stk)
		if UpCk['status']=='Success':
			comstat.Status='Success'
			comstat.save()
			continue
		else:
			Fromdate=UpCk['Fromdate']
			Todate=UpCk['Todate']
		
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


		df=StockDataFrame_sanitize(df)
		

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



def UpdateIndexPriceData(stkgrpindex_ids,*args,**kwargs):


	stkgrpindicies=stkmd.StockGroupIndex.objects.filter(id__in=stkgrpindex_ids)
	Todate=pd.datetime.today().date()

	for stkgrpindex in stkgrpindicies:
		comstat=stkmd.ComputeStatus_StockGroupIndex.objects.get(Status='ToDo',StockGroupIndex=stkgrpindex)
		comstat.Status='Run'
		comstat.save()

		stk=stkgrpindex.Symbol
		stkgrp=stkgrpindex.StockGroup
		stkind=stkgrpindex.Index
		grpstks_ids=stkgrp.Symbol.all().values_list('id',flat=True)

		UpCk=predownloadcheck(stk)
		if UpCk['status']=='Success':
			comstat.Status='Success'
			comstat.save()
			continue
		else:
			Fromdate=UpCk['Fromdate']
			Todate=UpCk['Todate']



		try:
			ClassName,computeclass=stkind.IndexComputeClass.importcomputeclass()
			CC=computeclass()
			CC.compute(Fromdate=Fromdate,Todate=Todate,grpstks_ids=grpstks_ids)
			df=CC.getvalue(stkind.IndexLabel)

		except:
			print "error computing index ",stk, " for input dates ",Fromdate,Todate
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

		df['Close']=df['Close'].astype(float)
		df['Open']=df['Open'].astype(float)
		df['High']=df['High'].astype(float)
		df['Low']=df['Low'].astype(float)
		df['Volume']=df['Volume'].astype(int)

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

		stk.LastPriceUpdate=pd.datetime.today().date()

		if stk.Startdate is None:
			stk.Startdate=df.index[0].date()

		print type(df.index[0].date()),type(stk.Startdate)
		
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
