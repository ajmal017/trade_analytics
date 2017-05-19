from __future__ import division
from featureapp.libs import registerfeature, featuremodel
import pandas as pd
import numpy as np
import json
filename=__name__.split('.')[-1]


# --------------  features has to be the name of the class ------------------
# Define your features in this class


	

class features(featuremodel):
	
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
			



	@registerfeature(filename=filename,category='Momentum',returntype=bool,query=True,operators=['<','>','<=','>=','inrange','!=','!inrange'],null=False,cache=False)
	def SMALowPoly2win4Fit(self,T):
		"""
		HasCherries
		"""

		if not hasattr(self,'df'):
			self.df=self.GetStockData(self.Symbolid)

		if 'SMA20' not in self.df.columns:
			self.df=self.addindicators(self.df,[ {'name':'SMA','timeperiod':20,'colname':'SMA20'} ] )

		if 'SMAstd20' not in self.df.columns:
			self.df=self.addindicators(self.df,[ {'name':'SMAstd','timeperiod':20,'colname':'SMAstd20'} ] )

		if 'SMALowPoly2win4Fit' not in self.df.columns:
			def getbouncefeatures(dw):
				n=int( len(dw)/2.0 )
				err=(dw['Low']-dw['SMA20']).values
				p=np.polyfit(np.arange(len(err)),err,2)
				p=map(lambda x : None if np.isnan(x) else x,p)
				return json.dumps({'poly':p,'err':map(lambda x : None if np.isnan(x) else x,list(err)),
									'err_mean':np.mean(err),'err_max':max(err),'err_min':min(err),
									'SMAstd20_mean':dw['SMAstd20'].mean(),'SMAstd20_max':dw['SMAstd20'].max(),'SMAstd20_min':dw['SMAstd20'].min(),
									'SMA20_mean':dw['SMA20'].mean(),'SMA20_max':dw['SMA20'].max(),'SMA20_min':dw['SMA20'].min()
									})
			
			self.applyrollingfunc('SMALowPoly2win4Fit',getbouncefeatures,4,edge='center')
			self.df['SMALowPoly2win4Fit']=self.df['SMALowPoly2win4Fit'].apply(lambda x : json.loads(x) if not pd.isnull(x) else None).copy()




		ind=self.df.index[self.df.index<=T]
		if len(ind)>0:
			ind=ind[-1]
			return self.df.loc[ind,'SMALowPoly2win4Fit'] 
		else:
			return None

	@registerfeature(filename=filename,category='Price',returntype=bool,query=True,operators=['<','>','<=','>=','inrange','!=','!inrange'],null=False,cache=False)
	def SMA20(self,T):
		"""
		HasCherries
		"""
		if not hasattr(self,'df'):
			self.df=self.GetStockData(self.Symbolid)

		if 'SMA20' not in self.df.columns:
			self.df=self.addindicators(self.df,[ {'name':'SMA','timeperiod':20,'colname':'SMA20'} ] )

		ind=self.df.index[self.df.index<=T]
		if len(ind)>0:
			ind=ind[-1]
			return self.df.loc[ind,'SMA20'] 
		else:
			return None

	@registerfeature(filename=filename,category='Price',returntype=bool,query=True,operators=['<','>','<=','>=','inrange','!=','!inrange'],null=False,cache=False)
	def SMAstd20(self,T):
		"""
		HasCherries
		"""
		if not hasattr(self,'df'):
			self.df=self.GetStockData(self.Symbolid)

		if 'SMAstd20' not in self.df.columns:
			self.df=self.addindicators(self.df,[ {'name':'SMAstd','timeperiod':20,'colname':'SMAstd20'} ] )

		ind=self.df.index[self.df.index<=T]
		if len(ind)>0:
			ind=ind[-1]
			return self.df.loc[ind,'SMAstd20'] 
		else:
			return None

	@registerfeature(filename=filename,category='Price',returntype=bool,query=True,operators=['<','>','<=','>=','inrange','!=','!inrange'],null=False,cache=False)
	def EMA8(self,T):
		"""
		HasCherries
		"""
		if not hasattr(self,'df'):
			self.df=self.GetStockData(self.Symbolid)

		if 'EMA8' not in self.df.columns:
			self.df=self.addindicators(self.df,[ {'name':'EMA','timeperiod':8,'colname':'EMA8'} ] )

		ind=self.df.index[self.df.index<=T]
		if len(ind)>0:
			ind=ind[-1]
			return self.df.loc[ind,'EMA8'] 
		else:
			return None

	@registerfeature(filename=filename,category='Price',returntype=bool,query=True,operators=['<','>','<=','>=','inrange','!=','!inrange'],null=False,cache=False)
	def EMAstd8(self,T):
		"""
		HasCherries
		"""
		if not hasattr(self,'df'):
			self.df=self.GetStockData(self.Symbolid)

		if 'EMAstd8' not in self.df.columns:
			self.df=self.addindicators(self.df,[ {'name':'EMAstd','timeperiod':8,'colname':'EMAstd8'} ] )

		ind=self.df.index[self.df.index<=T]
		if len(ind)>0:
			ind=ind[-1]
			return self.df.loc[ind,'EMAstd8'] 
		else:
			return None


	@registerfeature(filename=filename,category='Momentum',returntype=bool,query=True,operators=['<','>','<=','>=','inrange','!=','!inrange'],null=False,cache=False)
	def CCI5(self,T):
		"""
		HasCherries
		"""

		if not hasattr(self,'df'):
			self.df=self.GetStockData(self.Symbolid)


		if 'CCI5' not in self.df.columns:
			self.df=self.addindicators(self.df,[ {'name':'CCI','timeperiod':5,'colname':'CCI5'} ] )




		ind=self.df.index[self.df.index<=T]
		if len(ind)>0:
			ind=ind[-1]
			return self.df.loc[ind,'CCI5'] 
		else:
			return None

	@registerfeature(filename=filename,category='Momentum',returntype=bool,query=True,operators=['<','>','<=','>=','inrange','!=','!inrange'],null=False,cache=False)
	def CCI50(self,T):
		"""
		HasCherries
		"""

		if not hasattr(self,'df'):
			self.df=self.GetStockData(self.Symbolid)

		if 'CCI50' not in self.df.columns:
			self.df=self.addindicators(self.df,[  {'name':'CCI','timeperiod':50,'colname':'CCI50'} ] )




		ind=self.df.index[self.df.index<=T]
		if len(ind)>0:
			ind=ind[-1]
			return self.df.loc[ind,'CCI50'] 
		else:
			return None


		
	@registerfeature(filename=filename,category='Performance',returntype=bool,query=False,operators=['<','>','<=','>=','inrange','!=','!inrange'],null=False,cache=False)
	def PastPROFIT10days(self,T):

		if not hasattr(self,'df'):
			self.df=self.GetStockData(self.Symbolid)

		if not hasattr(self,'DFpastperf10'):
			self.DFpastperf10=pd.DataFrame()
			for i in range(1,10):
				self.DFpastperf10[i]=100*self.df['Close'].diff(periods=i)/self.df['Close'].shift(periods=i)
			self.DFpastperf10['Zeroperf']=0

		if 'PastPROFIT10days' not in self.df.columns:
			self.df['PastPROFIT10days']=self.DFpastperf10.max(axis=1).round()

		ind=self.df.index[self.df.index<=T]
		if len(ind)>0:
			ind=ind[-1]
			return self.df.loc[ind,'PastPROFIT10days'] 
		else:
			return None


	@registerfeature(filename=filename,category='Performance',returntype=bool,query=False,operators=['<','>','<=','>=','inrange','!=','!inrange'],null=False,cache=False)
	def PastLOSS10days(self,T):

		if not hasattr(self,'df'):
			self.df=self.GetStockData(self.Symbolid)

		if not hasattr(self,'DFpastperf10'):
			self.DFpastperf10=pd.DataFrame()
			for i in range(1,10):
				self.DFpastperf10[i]=100*self.df['Close'].diff(periods=i)/self.df['Close'].shift(periods=i)
			self.DFpastperf10['Zeroperf']=0

		if 'PastLOSS10days' not in self.df.columns:
			self.df['PastLOSS10days']=self.DFpastperf10.min(axis=1).round()

		ind=self.df.index[self.df.index<=T]
		if len(ind)>0:
			ind=ind[-1]
			return self.df.loc[ind,'PastLOSS10days'] 
		else:
			return None

	@registerfeature(filename=filename,category='Performance',returntype=bool,query=False,operators=['<','>','<=','>=','inrange','!=','!inrange'],null=False,cache=False)
	def PastPROFIT30days(self,T):

		if not hasattr(self,'df'):
			self.df=self.GetStockData(self.Symbolid)

		if not hasattr(self,'DFpastperf30'):
			self.DFpastperf30=pd.DataFrame()
			for i in range(1,30):
				self.DFpastperf30[i]=100*self.df['Close'].diff(periods=i)/self.df['Close'].shift(periods=i)
			self.DFpastperf30['Zeroperf']=0

		if 'PastPROFIT30days' not in self.df.columns:
			self.df['PastPROFIT30days']=self.DFpastperf30.max(axis=1).round()

		ind=self.df.index[self.df.index<=T]
		if len(ind)>0:
			ind=ind[-1]
			return self.df.loc[ind,'PastPROFIT30days'] 
		else:
			return None


	@registerfeature(filename=filename,category='Performance',returntype=bool,query=False,operators=['<','>','<=','>=','inrange','!=','!inrange'],null=False,cache=False)
	def PastLOSS30days(self,T):

		if not hasattr(self,'df'):
			self.df=self.GetStockData(self.Symbolid)

		if not hasattr(self,'DFpastperf30'):
			self.DFpastperf30=pd.DataFrame()
			for i in range(1,30):
				self.DFpastperf30[i]=100*self.df['Close'].diff(periods=i)/self.df['Close'].shift(periods=i)
			self.DFpastperf30['Zeroperf']=0

		if 'PastLOSS30days' not in self.df.columns:
			self.df['PastLOSS30days']=self.DFpastperf30.min(axis=1).round()

		ind=self.df.index[self.df.index<=T]
		if len(ind)>0:
			ind=ind[-1]
			return self.df.loc[ind,'PastLOSS30days'] 
		else:
			return None



	@registerfeature(filename=filename,category='Outcome',returntype=bool,query=False,operators=['<','>','<=','>=','inrange','!=','!inrange'],null=False,cache=False)
	def FutPROFIT10days(self,T):

		if not hasattr(self,'df'):
			self.df=self.GetStockData(self.Symbolid)

		if not hasattr(self,'DFperf10'):
			self.DFperf10=pd.DataFrame()
			for i in range(1,10):
				self.DFperf10[i]=-100*self.df['Close'].diff(periods=-i)/self.df['Close']
			self.DFperf10['Zeroperf']=0

		if 'FutPROFIT10days' not in self.df.columns:
			self.df['FutPROFIT10days']=self.DFperf10.max(axis=1).round()

		ind=self.df.index[self.df.index<=T]
		if len(ind)>0:
			ind=ind[-1]
			return self.df.loc[ind,'FutPROFIT10days'] 
		else:
			return None


	@registerfeature(filename=filename,category='Outcome',returntype=bool,query=False,operators=['<','>','<=','>=','inrange','!=','!inrange'],null=False,cache=False)
	def FutLOSS10days(self,T):

		if not hasattr(self,'df'):
			self.df=self.GetStockData(self.Symbolid)

		if not hasattr(self,'DFperf10'):
			self.DFperf10=pd.DataFrame()
			for i in range(1,10):
				self.DFperf10[i]=-100*self.df['Close'].diff(periods=-i)/self.df['Close']
			self.DFperf10['Zeroperf']=0
			
		if 'FutLOSS10days' not in self.df.columns:
			self.df['FutLOSS10days']=self.DFperf10.min(axis=1).round()

		ind=self.df.index[self.df.index<=T]
		if len(ind)>0:
			ind=ind[-1]
			return self.df.loc[ind,'FutLOSS10days'] 
		else:
			return None


	


# --------- This is required to sync the features to the database -------------
features.finalize(filename)