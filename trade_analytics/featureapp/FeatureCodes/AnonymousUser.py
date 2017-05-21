from __future__ import division
from featureapp.libs import registerfeature, featuremodel
import pandas as pd
import numpy as np
import json
filename=__name__.split('.')[-1]


# --------------  features has to be the name of the class ------------------
# Define your features in this class


class features(featuremodel):
	

	def preprocessing(self):
		self.df=self.GetStockData(self.Symbolid)
		self.df=self.addindicators(self.df,[ {'name':'SMA','timeperiod':20,'colname':'SMA20'} ] )
		self.df=self.addindicators(self.df,[ {'name':'SMAstd','timeperiod':20,'colname':'SMAstd20'} ] )
		self.df=self.addindicators(self.df,[ {'name':'EMA','timeperiod':8,'colname':'EMA8'} ]		 )
		self.df=self.addindicators(self.df,[ {'name':'EMAstd','timeperiod':8,'colname':'EMAstd8'} ] )
		self.df=self.addindicators(self.df,[ {'name':'CCI','timeperiod':5,'colname':'CCI5'} ] )
		self.df=self.addindicators(self.df,[  {'name':'CCI','timeperiod':50,'colname':'CCI50'} ] )



	def applyrollingfunc(self,newcolname,applyfunc,window,edge='right'):
		self.df[newcolname]=np.nan
		for i in range(1,len(self.df)-1):
			if edge=='right':
				dw=self.df.loc[ self.df.index[i-window:i],:  ]
			elif edge=='left':
				dw=self.df.loc[ self.df.index[i:i+window],:  ]
			else:
				dw=self.df.loc[ self.df.index[max(i-int(window/2),0):i+int(window/2)],:  ]
			s=applyfunc(dw)
			self.df.loc[self.df.index[i],newcolname]=s
			


	@registerfeature(filename=filename,category='Momentum',required=[],returntype='json',query=True,operators=['<','>','<=','>=','inrange','!=','!inrange'],null=False,cache=False)
	def SMALowPoly2win4Fit(self,Tvec):
		"""
		HasCherries
		"""


		def getbouncefeatures(dw):
			err=(dw['Low']-dw['SMA20']).values
			p=np.polyfit(np.arange(len(err)),err,2)
			p=map(lambda x : None if np.isnan(x) else x,p)
			return json.dumps({'poly':p,'err':map(lambda x : None if np.isnan(x) else x,list(err)),
								'err_mean': np.mean(err),'err_max': max(err),'err_min': min(err),
								'SMAstd20_mean': dw['SMAstd20'].mean(),'SMAstd20_max': dw['SMAstd20'].max(),'SMAstd20_min': dw['SMAstd20'].min(),
								'SMA20_mean': dw['SMA20'].mean(),'SMA20_max': dw['SMA20'].max(),'SMA20_min': dw['SMA20'].min()
								})
		
		self.applyrollingfunc('SMALowPoly2win4Fit',getbouncefeatures,4,edge='center')
		self.df['SMALowPoly2win4Fit']=self.df['SMALowPoly2win4Fit'].apply(lambda x : json.loads(x) if not pd.isnull(x) else None).copy()


		self.df.loc[Tvec,'SMALowPoly2win4Fit'] 
		
	@registerfeature(filename=filename,category='Momentum',required=[],returntype='json',query=True,operators=['<','>','<=','>=','inrange','!=','!inrange'],null=False,cache=False)
	def EMALowPoly2win4Fit(self,Tvec):
		"""
		HasCherries
		"""




		def getbouncefeatures(dw):
			err=(dw['Low']-dw['EMA8']).values
			p=np.polyfit(np.arange(len(err)),err,2)
			p=map(lambda x : None if np.isnan(x) else x,p)
			return json.dumps({'poly':p,'err':map(lambda x : None if np.isnan(x) else x,list(err)),
								'err_mean': np.mean(err),'err_max': max(err),'err_min': min(err),
								'EMAstd8_mean': dw['EMAstd8'].mean(),'EMAstd8_max': dw['EMAstd8'].max(),'EMAstd8_min': dw['EMAstd8'].min(),
								'EMA8_mean': dw['EMA8'].mean(),'EMA8_max': dw['EMA8'].max(),'EMA8_min': dw['EMA8'].min()
								})
		
		self.applyrollingfunc('EMALowPoly2win4Fit',getbouncefeatures,4,edge='center')
		self.df['EMALowPoly2win4Fit']=self.df['EMALowPoly2win4Fit'].apply(lambda x : json.loads(x) if not pd.isnull(x) else None).copy()




		self.df.loc[Tvec,'EMALowPoly2win4Fit'] 


	@registerfeature(filename=filename,category='Price',required=[],returntype=float,query=True,operators=['<','>','<=','>=','inrange','!=','!inrange'],null=False,cache=False)
	def SMA20(self,Tvec):
		"""
		HasCherries
		"""


		self.df.loc[Tvec,'SMA20'] 


	@registerfeature(filename=filename,category='Price',required=[],returntype=float,query=True,operators=['<','>','<=','>=','inrange','!=','!inrange'],null=False,cache=False)
	def SMAstd20(self,Tvec):
		"""
		HasCherries
		"""

		self.df.loc[Tvec,'SMAstd20'] 


	@registerfeature(filename=filename,category='Price',required=[],returntype=float,query=True,operators=['<','>','<=','>=','inrange','!=','!inrange'],null=False,cache=False)
	def EMA8(self,Tvec):
		"""
		HasCherries
		"""
		

		self.df.loc[Tvec,'EMA8'] 


	@registerfeature(filename=filename,category='Price',required=[],returntype=float,query=True,operators=['<','>','<=','>=','inrange','!=','!inrange'],null=False,cache=False)
	def EMAstd8(self,Tvec):
		"""
		HasCherries
		"""

		self.df.loc[Tvec,'EMAstd8'] 



	@registerfeature(filename=filename,category='Momentum',required=[],returntype=float,query=True,operators=['<','>','<=','>=','inrange','!=','!inrange'],null=False,cache=False)
	def CCI5(self,Tvec):
		"""
		HasCherries
		"""

		self.df.loc[Tvec,'CCI5'] 


	@registerfeature(filename=filename,category='Momentum',required=[],returntype=float,query=True,operators=['<','>','<=','>=','inrange','!=','!inrange'],null=False,cache=False)
	def CCI50(self,Tvec):
		"""
		HasCherries
		"""

		self.df.loc[Tvec,'CCI50'] 



		
	@registerfeature(filename=filename,category='Performance',required=[],returntype=float,query=False,operators=['<','>','<=','>=','inrange','!=','!inrange'],null=False,cache=False)
	def PastPROFIT10days(self,Tvec):



		if not hasattr(self,'DFpastperf10'):
			self.DFpastperf10=pd.DataFrame()
			for i in range(1,10):
				self.DFpastperf10[i]=100*self.df['Close'].diff(periods=i)/self.df['Close'].shift(periods=i)
			self.DFpastperf10['Zeroperf']=0

		if 'PastPROFIT10days' not in self.df.columns:
			self.df['PastPROFIT10days']=self.DFpastperf10.max(axis=1).round()




		self.df.loc[Tvec,'PastPROFIT10days'] 



	@registerfeature(filename=filename,category='Performance',required=[],returntype=float,query=False,operators=['<','>','<=','>=','inrange','!=','!inrange'],null=False,cache=False)
	def PastLOSS10days(self,Tvec):

		if not hasattr(self,'DFpastperf10'):
			self.DFpastperf10=pd.DataFrame()
			for i in range(1,10):
				self.DFpastperf10[i]=100*self.df['Close'].diff(periods=i)/self.df['Close'].shift(periods=i)
			self.DFpastperf10['Zeroperf']=0

		if 'PastLOSS10days' not in self.df.columns:
			self.df['PastLOSS10days']=self.DFpastperf10.min(axis=1).round()

		self.df.loc[Tvec,'PastLOSS10days'] 


	@registerfeature(filename=filename,category='Performance',required=[],returntype=float,query=False,operators=['<','>','<=','>=','inrange','!=','!inrange'],null=False,cache=False)
	def PastPROFIT30days(self,Tvec):



		if not hasattr(self,'DFpastperf30'):
			self.DFpastperf30=pd.DataFrame()
			for i in range(1,30):
				self.DFpastperf30[i]=100*self.df['Close'].diff(periods=i)/self.df['Close'].shift(periods=i)
			self.DFpastperf30['Zeroperf']=0

		if 'PastPROFIT30days' not in self.df.columns:
			self.df['PastPROFIT30days']=self.DFpastperf30.max(axis=1).round()

		self.df.loc[Tvec,'PastPROFIT30days'] 



	@registerfeature(filename=filename,category='Performance',required=[],returntype=float,query=False,operators=['<','>','<=','>=','inrange','!=','!inrange'],null=False,cache=False)
	def PastLOSS30days(self,Tvec):



		if not hasattr(self,'DFpastperf30'):
			self.DFpastperf30=pd.DataFrame()
			for i in range(1,30):
				self.DFpastperf30[i]=100*self.df['Close'].diff(periods=i)/self.df['Close'].shift(periods=i)
			self.DFpastperf30['Zeroperf']=0

		if 'PastLOSS30days' not in self.df.columns:
			self.df['PastLOSS30days']=self.DFpastperf30.min(axis=1).round()

		self.df.loc[Tvec,'PastLOSS30days'] 




	@registerfeature(filename=filename,category='Outcome',required=[],returntype=float,query=False,operators=['<','>','<=','>=','inrange','!=','!inrange'],null=False,cache=False)
	def FutPROFIT10days(self,Tvec):



		if not hasattr(self,'DFperf10'):
			self.DFperf10=pd.DataFrame()
			for i in range(1,10):
				self.DFperf10[i]=-100*self.df['Close'].diff(periods=-i)/self.df['Close']
			self.DFperf10['Zeroperf']=0

		if 'FutPROFIT10days' not in self.df.columns:
			self.df['FutPROFIT10days']=self.DFperf10.max(axis=1).round()



		self.df.loc[Tvec,'FutPROFIT10days'] 



	@registerfeature(filename=filename,category='Outcome',required=[],returntype=float,query=False,operators=['<','>','<=','>=','inrange','!=','!inrange'],null=False,cache=False)
	def FutLOSS10days(self,Tvec):


		if not hasattr(self,'DFperf10'):
			self.DFperf10=pd.DataFrame()
			for i in range(1,10):
				self.DFperf10[i]=-100*self.df['Close'].diff(periods=-i)/self.df['Close']
			self.DFperf10['Zeroperf']=0
			
		if 'FutLOSS10days' not in self.df.columns:
			self.df['FutLOSS10days']=self.DFperf10.min(axis=1).round()


		self.df.loc[Tvec,'FutLOSS10days'] 



	@registerfeature(filename=filename,category='Outcome',required=[],returntype=float,query=False,operators=['<','>','<=','>=','inrange','!=','!inrange'],null=False,cache=False)
	def FutPROFIT30days(self,Tvec):


		if not hasattr(self,'DFperf30'):
			self.DFperf30=pd.DataFrame()
			for i in range(1,30):
				self.DFperf30[i]=-100*self.df['Close'].diff(periods=-i)/self.df['Close']
			self.DFperf30['Zeroperf']=0

		if 'FutPROFIT30days' not in self.df.columns:
			self.df['FutPROFIT30days']=self.DFperf30.max(axis=1).round()

		self.df.loc[Tvec,'FutPROFIT30days'] 



	@registerfeature(filename=filename,category='Outcome',required=[],returntype=float,query=False,operators=['<','>','<=','>=','inrange','!=','!inrange'],null=False,cache=False)
	def FutLOSS30days(self,Tvec):

	
		if not hasattr(self,'DFperf30'):
			self.DFperf30=pd.DataFrame()
			for i in range(1,30):
				self.DFperf30[i]=-100*self.df['Close'].diff(periods=-i)/self.df['Close']
			self.DFperf30['Zeroperf']=0
			
		if 'FutLOSS30days' not in self.df.columns:
			self.df['FutLOSS30days']=self.DFperf30.min(axis=1).round()

		self.df.loc[Tvec,'FutLOSS30days'] 



	@registerfeature(filename=filename,category='Outcome',required=[],returntype=float,query=False,operators=['<','>','<=','>=','inrange','!=','!inrange'],null=False,cache=False)
	def FutPROFIT90days(self,Tvec):


		if not hasattr(self,'DFperf90'):
			self.DFperf90=pd.DataFrame()
			for i in range(1,90):
				self.DFperf90[i]=-100*self.df['Close'].diff(periods=-i)/self.df['Close']
			self.DFperf90['Zeroperf']=0

		if 'FutPROFIT90days' not in self.df.columns:
			self.df['FutPROFIT90days']=self.DFperf90.max(axis=1).round()

		self.df.loc[Tvec,'FutPROFIT90days'] 



	@registerfeature(filename=filename,category='Outcome',required=[],returntype=float,query=False,operators=['<','>','<=','>=','inrange','!=','!inrange'],null=False,cache=False)
	def FutLOSS90days(self,Tvec):


		if not hasattr(self,'DFperf90'):
			self.DFperf90=pd.DataFrame()
			for i in range(1,90):
				self.DFperf90[i]=-100*self.df['Close'].diff(periods=-i)/self.df['Close']
			self.DFperf90['Zeroperf']=0
			
		if 'FutLOSS90days' not in self.df.columns:
			self.df['FutLOSS90days']=self.DFperf90.min(axis=1).round()

		self.df.loc[Tvec,'FutLOSS90days'] 







# --------- This is required to sync the features to the database -------------
features.finalize(filename)