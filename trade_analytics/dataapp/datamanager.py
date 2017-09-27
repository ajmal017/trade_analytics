import dataapp.libs as dtalibs
import dataapp.models as dtamd
import featureapp.models as ftamd
import stockapp.models as stkmd
import pandas as pd
import numpy as np
from custommeta import cstmdata

class DataManager(object):
	"""
	1. Pull in data from everywhere
	2. this is the main entry into all the raw data
	3. take in feature df and side concat
	4. Future if you get more fundamental data... join that too
	 
	"""
	
	max_cache=20 # maximum number of stocks for which to hold data

	def __init__(self,SymbolIds=[],RequiredCols=None,DF=None):
		"""
		DF is a dict with keys as ids and values as dataframes of the objects
		"""
		if RequiredCols is None: 
			self.RequiredCols= cstmdata.RequiredCols
		else:
			self.RequiredCols=RequiredCols



		self.SymbolIds=SymbolIds
		self.stks={}
		self.Symbols={}
		self.Symbols2Ids_dict={}
		self.Ids2Symbols_dict={}

		self.FeatureCols=[f for f in ftmd.FeaturesMeta.objects.all().values_list('Featurelabel',flat=True).distinct()]
		self.StockCols=[f.name for f in  stkmd.Stockmeta._meta.get_fields()]
		self.DataCols=[f.name for f in  dtamd.Stockprice._meta.get_fields()]

		# Symbols=stkmd.Stockmeta.objects.all().values()
		for symbid in self.SymbolIds:
			self.stks[symbid]=self.Stockmeta.objects.get(id=symbid)
			self.Symbols[symbid]=self.stks[symbid].Symbol
			self.Symbols2Ids[ self.Symbols[symbid] ]=symbid

		if DF is not None:
			if set(DF.keys()) == set(SymbolIds):
				self.DF=DF
			else:
				raise Exception('SymbolIds and Keys  are not the same')
		else:
			self.DF={}

	@classmethod
	def setTradingdates(cls):
		symbolids=stkmd.Stockmeta.objects.filter(Symbol__in=dtamd.TradingDates.CheckWith).values_list('id',flat=True)
		df=self.GetStockData(symbolids,Fromdate=pd.datetime(2002,1,1).date(),Todate=pd.datetime.today().date(),format='concat',standardize=True,addcols=None)
		Trange=list( df.index.unique() )
		# Trange.sorted()
		for TT in Trange:
			if dtamd.TradingDates.objects.filter(Date=TT).exists()==False:
				Td=dtamd.TradingDates(Date=TT)
				Td.save()

	@classmethod
	def getTradingdates(cls):
		return list( dtamd.TradingDates.objects.all().values_list('Date',flat=True).order_by('Date') )

	@property
	def Stockmeta(self):
		return stkmd.Stockmeta
	
	@property
	def GetStockData(self):
		return dtalibs.GetStockData
	
	@property
	def GetFeatures(self):
		return dtalibs.GetFeatures


	def Addfeaturecols(self,featcols):
		dffeats=self.GetFeatures(Symbolids=[self.Symbolid])
		self.df=dtalibs.ConcatFeats2Stockdata(self.df,dffeats)
		df['T']=df.index.copy()
		dffeat['T']=dffeat.index.copy()

		return df.merge(dffeat, how='inner', on=['T','Symbol'])
	
	def IndicatorCols(self,cols):
		IndicatorCols=[]
		for cc in cols: 
			if cc in self.MasterColNameDict:	
				IndicatorCols.append(self.MasterColNameDict[cc])
		return IndicatorCols

	def PullAllStockdata(self):
		self.DF=dtalibs.GetStockData(self.SymbolIds,Fromdate=pd.datetime(2002,1,1).date(),Todate=pd.datetime.today().date(),format='dict',standardize=True,addcols=None)
	
	def PullStockdata(self,SymbolId):
		if len(self.DF)==self.max_cache:
			del self.DF[self.DF.keys()[0]]

		if SymbolId not in self.DF:
			self.DF[SymbolId]=dtalibs.GetStockData(SymbolId,Fromdate=pd.datetime(2002,1,1).date(),Todate=pd.datetime.today().date(),format='concat',standardize=True,addcols=None)
		
		return self.DF[SymbolId]


	def Iterate_Stockdata_id(self):
		for SymbolId in self.SymbolIds:
			yield dtalibs.GetStockData(SymbolId,Fromdate=pd.datetime(2002,1,1).date(),Todate=pd.datetime.today().date(),format='concat',standardize=True,addcols=None)

	def AppendCols2df(self,SymbId,df):
		"""
		you can add any columns you want
		"""

		cols=self.RequiredCols
		ToDoCols=list( set(cols)-set(df.columns) )
		IndicatorCols=self.IndicatorCols(ToDoCols)
		if len(IndicatorCols)>0:
			df=dtalibs.addindicators(df,IndicatorCols)

		

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
			df=dtalibs.GetStockData(SymbolId,Fromdate=pd.datetime(2002,1,1).date(),Todate=pd.datetime.today().date(),format='concat',standardize=True,addcols=None)
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
		dfinstants_list=[dd for dd in dfinstants_list if dd is not None]

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
							TF=dtalibs.str2date( dfsymb.loc[ind,'TF'] )
						if roundT2dfdate:
							TFind=df.index[df.index<=TF][-1]
							if np.abs( (TFind-TF).days )<=3:
								ds=df.iloc[TFind-width:TFind]
							else:
								ds=pd.DataFrame()

						else:
							TFind=df.index[df.index==TF]
							if len(TFind)==0:
								ds=pd.DataFrame()
						
						Nd=len(ds)-width
						if Nd>0 and padding is not None:
							d={}
							for cc in ds.columns:
								d[cc]=[np.nan]*Nd
							dummyfill=pd.DataFrame(d)
							ds=pd.concat([ dummyfill , ds ])


					elif 'T0' in dfsymb.columns:
						if isinstance(dfsymb.loc[ind,'T0'],basestring):
							T0=dtalibs.str2date( dfsymb.loc[ind,'T0'] )
						if roundT2dfdate:
							T0ind=df.index[df.index>=T0][0]
							if np.abs( (TFind-TF).days )<=3:
								ds=df.iloc[T0ind:T0ind+width]
							else:
								ds=pd.DataFrame()
						else:
							T0ind=df.index[df.index==T0]
							if len(T0ind)==0:
								ds=pd.DataFrame()


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