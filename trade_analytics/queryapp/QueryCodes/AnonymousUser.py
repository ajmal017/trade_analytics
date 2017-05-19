from __future__ import division
from queryapp.libs import registerquery, querymodel
import pandas as pd
import numpy as np
filename=__name__.split('.')[-1]


# --------------  features has to be the name of the class ------------------
# Define your features in this class

class queries(querymodel):
	
	
	@registerquery(filename=filename,category='Momentum')
	def CCICHERRIES(self,T):
		"""
		HasCherries
		"""
		if not hasattr(self,'df'):
			self.df=self.GetStockData(self.Symbolid)

		if 'CCI5' not in self.df.columns:
			self.df['CCI5']=self.LoadFeature('CCI5')

		if 'CCI50' not in self.df.columns:
			self.df['CCI50']=self.LoadFeature('CCI50')

		if 'CCICHERRIES' not in self.df.columns:
			self.df['CCICHERRIES']=(self.df['CCI50']-self.df['CCI5'])>180
			self.df['CCICHERRIES']=self.df['CCICHERRIES'].apply(lambda x: int(x))
			

		ind=self.df.index[self.df.index<=T]
		if len(ind)>0:
			ind=ind[-1]
			return self.df.loc[ind,'CCICHERRIES'] 
		else:
			return None
		

	@registerquery(filename=filename,category='Price')
	def SMA20BOUNCE(self,T):
		"""
		HasCherries
		"""
		if not hasattr(self,'df'):
			self.df=self.GetStockData(self.Symbolid)

		if 'SMA20' not in self.df.columns:
			self.df['SMA20']=self.LoadFeature('SMA20')

		if 'SMAstd20' not in self.df.columns:
			self.df['SMAstd20']=self.LoadFeature('SMAstd20')

		if 'SMALowPoly2win4Fit' not in self.df.columns:
			self.df['SMALowPoly2win4Fit']=self.LoadFeature('SMALowPoly2win4Fit')
		
		if 'SMA20BOUNCE' not in self.df.columns:		
			def signal(row):
				p=row.get('poly',np.nan)
				err_min=row.get('err_min',np.nan)
				err=np.array(row.get('err',np.nan))
				SMAstd20_mean=row.get('SMAstd20_mean',np.nan)


				if len(err[err>=0])>=len(err)/2 and p[0]>0 and abs(err_min)<=0.5*SMAstd20_mean:
					return 1
				else:
					return 0

			self.df['SMA20BOUNCE']=self.df['SMALowPoly2win4Fit'].apply(lambda x: signal(x) if not pd.isnull(x) else None)
		

		ind=self.df.index[self.df.index<=T]
		if len(ind)>0:
			ind=ind[-1]
			return self.df.loc[ind,'SMA20BOUNCE'] 
		else:
			return None


	


# --------- This is required to sync the features to the database -------------
queries.finalize(filename)