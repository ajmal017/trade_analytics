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
logger=logging.getLogger('dataapp')

import time

def str2date(T):
	"""
	- Given a T, return the datetime object of type date
	- if T is string, first convert it
	- if T is datetime, convert to date
	"""

	if isinstance(T,basestring):
		try:
			TT=pd.to_datetime(T).date()
			return TT
		except:
			return T
	
	elif type(T)==datetime.datetime or type(T)==pd.datetime: 
		return T.date()

	elif type(T)==pd.datetime.date or type(T)==datetime.date:
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

@mnt.logperf('dataapp',printit=True)
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


@mnt.logperf('dataapp',printit=True)
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

class DataManager(object):
	MasterColDict={'SMA10':{'name':'SMA','colname':'SMA10','timeperiod':10},'SMA20':{'name':'SMA','colname':'SMA20','timeperiod':20},'SMA50':{'name':'SMA','colname':'SMA50','timeperiod':50},'SMA100':{'name':'SMA','colname':'SMA100','timeperiod':100},'SMA200':{'name':'SMA','colname':'SMA200','timeperiod':200},
					'CCI5':{'name':'CCI','colname':'CCI5','timeperiod':5},'CCI50':{'name':'CCI','colname':'CCI50','timeperiod':50},'CCI100':{'name':'CCI','colname':'CCI100','timeperiod':100},
					'VolSMA10':{'name':'VolSMA','timeperiod':10,'colname':'VolSMA10'},'VolSMA20':{'name':'VolSMA','timeperiod':20,'colname':'VolSMA20'},
	        		'EMA8':{'name':'EMA','timeperiod':8,'colname':'EMA8'},'EMA20':{'name':'EMA','timeperiod':20,'colname':'EMA20'},

					}
	max_cache=20 # maximum number of stocks for which to hold data

	def __init__(self,SymbolIds,RequiredCols=None,Append2RequiredCols=[],DF=None):
		"""
		DF is a dict with keys as ids and values as dataframes of the objects
		"""
		if RequiredCols is None:
			self.RequiredCols=['Close','Open','High','Low','Volume','VolSMA10','SMA10','SMA20','SMA50','SMA100','SMA200']
		else:
			self.RequiredCols=RequiredCols

		self.RequiredCols=self.RequiredCols+Append2RequiredCols
		self.RequiredCols=list( set(self.RequiredCols) )


		self.SymbolIds=SymbolIds
		self.stks={}
		self.Symbols={}
		self.Symbols2Ids={}
		for symbid in self.Symbolids:
			self.stks[symbid]=stkmd.Stockmeta.objects.get(id=symbid)
			self.Symbols[symbid]=self.stks[symbid].Symbol
			self.Symbols2Ids[ self.Symbols[symbid] ]=symbid

		if DF is not None:
			if set(DF.keys()) == set(SymbolIds):
				self.DF=DF
			else:
				raise Exception('SymbolIds and Keys  are not the same')
		else:
			self.DF={}


	def IndicatorCols(self,cols):
		IndicatorCols=[]
		for cc in cols: 
			if cc in self.MasterColDict:	
				IndicatorCols.append(self.MasterColDict[cc])
		return IndicatorCols

	def PullAllStockdata(self):
		self.DF=GetStockData(self.SymbolIds,Fromdate=pd.datetime(2002,1,1).date(),Todate=pd.datetime.today().date(),format='dict',standardize=True,addcols=None)
	
	def PullStockdata(self,SymbolId):
		if len(self.DF)==self.max_cache:
			del self.DF[self.DF.keys()[0]]

		if SymbolId not in self.DF:
			self.DF[SymbolId]=GetStockData(SymbolId,Fromdate=pd.datetime(2002,1,1).date(),Todate=pd.datetime.today().date(),format='concat',standardize=True,addcols=None)
		
		return self.DF[SymbolId]


	def Iterate_Stockdata_id(self):
		for SymbolId in self.SymbolIds:
			yield GetStockData(SymbolId,Fromdate=pd.datetime(2002,1,1).date(),Todate=pd.datetime.today().date(),format='concat',standardize=True,addcols=None)

	def AppendCols2df(self,SymbId,df):
		"""
		you can add any columns you want
		"""

		cols=self.RequiredCols
		ToDoCols=list( set(cols)-set(df.columns) )
		IndicatorCols=self.IndicatorCols(ToDoCols)
		if len(IndicatorCols)>0:
			df=addindicators(df,IndicatorCols)

		

		stk=self.stks[SymbId]

		if 'Sector' in ToDoCols:
			df['Sector']=stk.Sector
		if 'Industry' in ToDoCols:
			df['Industry']=stk.Industry
		if 'Marketcap' in ToDoCols:
			df['Marketcap']=stk.Industry

		if SymbId in self.DF.keys() and len(ToDoCols)>0:
			self.DF[SymbId]=df

		return df

	def AppendCols2DF(self):
		"""
		you can add any columns you want
		"""
		for SymbId,df in self.DF.items() : 	
			self.DF[SymbId]=self.AppendCols2df(SymbId,df)

	def postprocess(self,SymbId,df):
		df=self.AppendCols2df(SymbId,df)
		return df[self.RequiredCols]

	def GetProcessed_DF(self):
		RetDF={}
		for SymbId in self.DF.keys() : 	
			RetDF[SymbId]=self.postprocess(SymbId,self.DF[SymbId])
		return RetDF

	def GetProcessed_df(self,Symbol):
		for SymbId in self.DF.keys() : 	
			if self.Symbols[SymbId]==Symbol:
				return self.postprocess(SymbId,self.DF[SymbId])
	
	def Iterator_GetData_Process_df(self):
		for SymbolId in self.SymbolIds:
			df=GetStockData(SymbolId,Fromdate=pd.datetime(2002,1,1).date(),Todate=pd.datetime.today().date(),format='concat',standardize=True,addcols=None)
			df=self.postprocess(SymbolId,df)
			yield (SymbolId,self.Symbols[SymbolId],df)

	def Iterbatchdata_Ordered(self,dfinstants_list,padding=None,roundT2dfdate=True):
		"""
		DataFrame input as
		dfinstants_list =[dfinstants,dfinstants,dfinstants .... ]
		dfinstants= [ df(Symbol, TF,width), ..., or df(Symbol, T0,width) ]
		return in same order
		padding True/False
		"""
		AllSymbols=reduce( lambda x,y: x|y,map(lambda x: set(x['Symbol'].unique()),dfinstants_list) )
		Data=[]
		for i in range(len(dfinstants_list)):
			dfinstants_list[i].index=range(len(dfinstants_list[i]))
			Data.append({})

		for Symbol in AllSymbols:
			SymbId=self.Symbols2Ids[Symbol]
			df=self.PullStockdata(SymbId)
			df=self.AppendCols2df(SymbId,df)
			for i in range(len(dfinstants_list)):
				dfinstants=dfinstants_list[i]
				dfsymb=dfinstants[dfinstants['Symbol']==Symbol]

				for ind in dfsymb.index:
					width=dfsymb.loc[ind,'width']
					if 'TF' in dfsymb.columns and 'T0' in dfsymb.columns:
						raise Exception('Cannot have both TF and T0 in dfinstants')

					if 'TF' in dfsymb.columns:
						if isinstance(dfsymb.loc[ind,'TF'],basestring):
							TF=str2date( dfsymb.loc[ind,'TF'] )
						if roundT2dfdate:
							TFind=df.index[df.index<=TF][-1]
						else:
							TFind=df.index[df.index==TF]
							if len(TFind)==0:
								raise Exception('TF not in stock date index')
						ds=df.iloc[TFind-width:TFind]
						Nd=len(ds)-width
						if Nd>0 and padding is not None:
							d={}
							for cc in ds.columns:
								d[cc]=[np.nan]*Nd
							dummyfill=pd.DataFrame(d)
							ds=pd.concat([ dummyfill , ds ])


					elif 'T0' in dfsymb.columns:
						if isinstance(dfsymb.loc[ind,'T0'],basestring):
							T0=str2date( dfsymb.loc[ind,'T0'] )
						if roundT2dfdate:
							T0ind=df.index[df.index>=T0][0]
						else:
							T0ind=df.index[df.index==T0]
							if len(T0ind)==0:
								raise Exception('T0 not in stock date index')
						ds=df.iloc[T0ind:T0ind+width]
						Nd=len(ds)-width
						if Nd>0 and padding is not None:
							d={}
							for cc in ds.columns:
								d[cc]=[np.nan]*Nd
							dummyfill=pd.DataFrame(d)
							ds=pd.concat([ ds, dummyfill ])



					Data[i][ind]=np.expand_dims(ds.values,axis=0)
		

		for i in range(len(dfinstants_list)):
			X=None
			for ind in dfinstants_list[i].index:
				if X is None:
					X=Data[i][ind]
				else:
					X=np.vstack((X,Data[i][ind]))

			Meta={'shape':X.shape,'dfinstants':dfinstants_list[i],'columns':self.RequiredCols}

			yield X,Meta

	



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
				T0=str2date( dfsymb.loc[ind,'T0'] )
				TF=str2date( dfsymb.loc[ind,'TF'] )
				
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