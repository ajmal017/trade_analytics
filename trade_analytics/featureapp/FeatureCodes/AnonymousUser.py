from __future__ import division
from featureapp.libs import registerfeature, featuremodel
import pandas as pd
import numpy as np
filename=__name__.split('.')[-1]


# --------------  features has to be the name of the class ------------------
# Define your features in this class

class features(featuremodel):
	
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