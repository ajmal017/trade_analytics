from __future__ import division
import pandas as pd
import pandas_datareader.data as web
import stockapp.models as stkmd
from django.db import connections
from dataapp import models as dtamd
import featureapp.models as ftamd
import utility.codemanager as utcdmng
import datetime
import time
import pdb
from talib import abstract
import numpy as np
from utility import maintenance as mnt
import json
import h5py
import pickle as pkl
import logging
logger=logging.getLogger('dataapp')

import time

import json



def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""

    if isinstance(obj, (datetime.datetime, datetime.date)):
        return obj.strftime("%Y-%m-%d")
    raise TypeError ("Type %s not serializable" % type(obj))
    
def saveas_h5(filepath,**kwargs):
    h5f = h5py.File(filepath, 'w')
    for key,value in kwargs.items():
        if isinstance(value,(dict,list)):
            string_dt = h5py.special_dtype(vlen=str)
            h5f.create_dataset(key, data=np.array([pkl.dumps(value)]), dtype=string_dt)
        else:
            h5f.create_dataset(key, data=value,compression="gzip")
    h5f.close()

def append_h5(filepath,**kwargs):
    h5f = h5py.File(filepath, 'w')
    for key,value in kwargs.items():
        if isinstance(value,(dict,list)):
            string_dt = h5py.special_dtype(vlen=str)
            h5f.create_dataset(key, data=np.array([pkl.dumps(value)]), dtype=string_dt)
        else:
            h5f.create_dataset(key, data=value,compression="gzip")
    h5f.close()

def load_h5(filepath,keys):
	data={}
	h5f = h5py.File(filepath, 'r')
	for ky in keys:
		data[ky] = h5f[ky][:]
		if len(data[ky])==1 and isinstance(data[ky][0],basestring):
			data[ky]=pkl.loads(data[ky][0])
		# Meta = json.loads(h5f['Meta'][:][0])
	h5f.close() 

	return data

def getdatearrays(From=pd.datetime(2010,1,1).date(),To=pd.datetime.today().date(),ondays='EveryMonday'):
	D={}
	D['EveryMonday']=pd.date_range(start=pd.datetime(2010,1,1).date(),end=pd.datetime.today().date(),periods=None, freq='W-MON')
	D['EveryWednesday']=pd.date_range(start=pd.datetime(2010,1,1).date(),end=pd.datetime.today().date(),periods=None, freq='W-WED')
	D['EveryFriday']=pd.date_range(start=pd.datetime(2010,1,1).date(),end=pd.datetime.today().date(),periods=None, freq='W-FRI')
	D['EveryTueThu']=list(pd.date_range(start=pd.datetime(2010,1,1).date(),end=pd.datetime.today().date(),periods=None, freq='W-TUE'))+list(pd.date_range(start=pd.datetime(2010,1,1).date(),end=pd.datetime.today().date(),periods=None, freq='W-THU'))
	
	D['EveryMonWedFri']=list(set(list(D['EveryMonday'])+list(D['EveryWednesday'])+list(D['EveryFriday'])))
	D['EveryMonWedFri']=sorted(D['EveryMonWedFri'])
	return map(lambda x: x.date(),D[ondays])



def merge_on_TSymbol(df1,df2):
	if 'Symbol' not in df1.columns:
		raise KeyError('df1 needs T and Symbol')

	if 'Symbol' not in df2.columns:
		raise KeyError('df2 needs T and Symbol')

	df1['T']=df1.index
	df2['T']=df2.index

	df=df1.merge(df2, how='left', on=['T','Symbol'],suffixes=['1c1','2c2'])
	df.index=df['T'].copy()
	
	df.drop('T', axis=1, inplace=True)

	return df

def Convert2date(T):
	"""
	- Given a T, return the datetime object of type date
	- if T is string, first convert it
	- if T is datetime, convert to date
	"""
	if isinstance(T,list)==True:
		pass
	elif isinstance(T,np.ndarray)==True:
		pass
	else:
		T=[T]
	# else:
	# 	raise TypeError('scalar, list or array expected')


	for i in range(len(T)):
		if isinstance(T[i],basestring):
			try:
				T[i]=pd.to_datetime(T[i]).date()
			except:
				pass
		
		elif type(T[i])==datetime.datetime or type(T[i])==pd.datetime: 
			T[i]= T[i].date()

		elif type(T[i])==pd.datetime.date or type(T[i])==datetime.date:
			pass
		else:
			raise TypeError('No date found')


	if len(T)==1:
		return T[0]
	else:
		return T



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

# @mnt.logperf('dataapp',printit=True)
def addindicators(df,cols):
	if len(cols)==0:
		return df

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
				elif cc['name']=='VolSMA':
					df[cc['colname']]=df['Volume'].rolling(window=cc['timeperiod']).mean()
					df[cc['colname']]=df[cc['colname']].astype(float)
				else:
					print "Indicator not available"

			except Exception as e:
				print "error adding indicator ",cc['colname']
				logger.error("error adding indicator "+cc['colname']+" "+str(type(e))+" "+str(e))
				logger.exception(e)

	return df


# @mnt.logperf('dataapp',printit=True)
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


def setTradingdates():
	symbolids=stkmd.Stockmeta.objects.filter(Symbol__in=dtamd.TradingDates.CheckWith).values_list('id',flat=True)
	df=GetStockData(symbolids,Fromdate=pd.datetime(2002,1,1).date(),Todate=pd.datetime.today().date(),format='concat',standardize=True,addcols=None)
	Trange=list( df.index.unique() )
	# Trange.sorted()
	for TT in Trange:
		if dtamd.TradingDates.objects.filter(Date=TT).exists()==False:
			Td=dtamd.TradingDates(Date=TT)
			Td.save()

def getTradingdates():
	return dtamd.TradingDates.objects.all().values_list('Date',flat=True).order_by('Date') 

#############################################  Features

def standardizefeaturedata(df):
	if df.empty:
		return pd.DataFrame(columns=['T','Symbol_id','Symbol'])

	# df.rename(columns={'Symbol__Symbol':'Symbol'},inplace=True)
	df['Symbol']=df['Symbol'].astype(str)
	df['Symbol_id']=df['Symbol_id'].astype(int)

	df['T']=df['T'].apply(lambda x: pd.to_datetime(x).date())
	df.index=df['T'].copy()
	df.drop(['T'],axis=1,inplace=True)


	dffeat=pd.DataFrame(df['Featuredata'].tolist())
	df.drop(['Featuredata'],axis=1,inplace=True)
	dffeat.index=df.index

	for cc in dffeat.columns:
		try:
			if ftamd.FeaturesMeta.objects.filter(Featurelabel=cc).exists():
				rettype=ftamd.FeaturesMeta.objects.get(Featurelabel=cc).Returntype
				if rettype!='json':
					dffeat[cc]=dffeat[cc].astype(eval(rettype))
		except:
			pdb.set_trace()


	df=pd.concat([df, dffeat], axis=1)
	
	df = df.where((pd.notnull(df)), np.nan)
	df.sort_index(inplace=True)

	return df

# @mnt.logperf('debug',printit=True)
def GetFeatures(Symbolids=None,Fromdate=pd.datetime(2002,1,1).date(),Todate=pd.datetime.today().date(),format='concat',standardize=True):

	if type(Symbolids)!=list and type(Symbolids)!=tuple:
		Symbolids=list((Symbolids))

	if format=='concat':
		Qrysets=ftamd.FeaturesData.objects.filter(Symbol_id__in=Symbolids,T__gte=Fromdate,T__lte=Todate).values('T','Symbol_id','Symbol','Featuredata')
		df=pd.DataFrame( list(Qrysets ))
		if standardize:
			df=standardizefeaturedata(df)
		return df

	elif format=='dict':
		DF={}
		for Symbolid in Symbolids:
			Qrysets=ftamd.FeaturesData.objects.filter(Symbol_id=Symbolid,T__gte=Fromdate,T__lte=Todate).values('T','Symbol_id','Symbol','Featuredata')
			DF[Symbolid]=pd.DataFrame( list(Qrysets ))
			if standardize:
				DF[Symbolid]=standardizefeaturedata(DF[Symbolid])


		return DF





###########################  COmputing indicies  ######################################


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


###########################  Download stock data  ######################################

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






########################   Deprecated ########################################33


def Getbatchdata(dfinstants_req,padding=None,returnAs='StackedMatrix'):
	"""
	DataFrame input as
	dfinstants= [ (Symbol, T0,TF), ... ]
	return in same order
	padding can be : ['OnTop','FromBottom']
	"""
	if type(dfinstants_req)!=list:
		dfinstants_req=[dfinstants_req]

	ReturnData=[]
	ds={}
	cols=None

	addcols=[	{'name':'SMA','timeperiod':10,'colname':'SMA10'},
        		{'name':'SMA','timeperiod':20,'colname':'SMA20'},
        		{'name':'SMA','timeperiod':50,'colname':'SMA50'},
        		{'name':'SMA','timeperiod':100,'colname':'SMA100'},
        		{'name':'SMA','timeperiod':200,'colname':'SMA200'},
        		{'name':'VolSMA','timeperiod':10,'colname':'VolSMA10'},
        		{'name':'VolSMA','timeperiod':20,'colname':'VolSMA20'},
        		{'name':'EMA','timeperiod':8,'colname':'EMA8'},
        		{'name':'EMA','timeperiod':20,'colname':'EMA20'},
        	]


	for cnt in range(len(dfinstants_req)) :
		dfinstants = dfinstants_req[cnt]

		dfinstants.index=range(len(dfinstants))

		D={}
		
		NT=0
		for Symbol,dfsymb in dfinstants.groupby("Symbol"):
			if Symbol not in ds.keys():
				ds[Symbol]=GetStockData([Symbol])
				ds[Symbol]=addindicators(ds[Symbol],addcols)

			for ind in dfsymb.index:
				T0=Convert2date( dfsymb.loc[ind,'T0'] )
				TF=Convert2date( dfsymb.loc[ind,'TF'] )
				
				window=dfsymb.loc[ind,'window']
				NT=max([NT,window])
				
				D[ind]=ds[Symbol][T0:TF]

				if cols is None:
					if len(D[ind].index)>0:
						cols=D[ind].columns

		# padding
		for ind in dfinstants.index:
			if len(D[ind])<NT:
				d={}
				Nd=NT-len(D[ind])
				for cc in D[ind].columns:
					d[cc]=[np.nan]*Nd

				dummyfill=pd.DataFrame(d)
				
				if padding[cnt]=='OnTop':
					D[ind]=pd.concat([ dummyfill[cols] , D[ind][cols] ])

				elif padding[cnt]=='FromBottom':	
					D[ind]=pd.concat([ D[ind][cols], dummyfill[cols] ])


		X=None
		for ind in dfinstants.index:
			Y=np.expand_dims(D[ind][cols].values,axis=0)
			# print Y.shape

			if X is None:
				X=Y
			else:
				X=np.vstack((X,Y))

		Meta={'shape':X.shape,'dfinstants':dfinstants,'columns':cols}
		ReturnData.append( (X,Meta) )
	
	if len(ReturnData)==1:
		return ReturnData[0]
	else:
		return ReturnData