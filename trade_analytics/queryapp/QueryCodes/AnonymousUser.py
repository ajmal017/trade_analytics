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
			self.df['CCICHERRIES']=( (self.df['CCI50']-self.df['CCI5'])>180  )
			self.df['CCICHERRIES']=self.df['CCICHERRIES'].apply(lambda x: int(x))
			

		ind=self.df.index[self.df.index<=T]
		if len(ind)>0:
			ind=ind[-1]
			return self.df.loc[ind,'CCICHERRIES'] 
		else:
			return None
		
	@registerquery(filename=filename,category='Momentum')
	def CCICHERRIES_CCI50(self,T):
		"""
		HasCherries
		"""
		if not hasattr(self,'df'):
			self.df=self.GetStockData(self.Symbolid)

		if 'CCI5' not in self.df.columns:
			self.df['CCI5']=self.LoadFeature('CCI5')

		if 'CCI50' not in self.df.columns:
			self.df['CCI50']=self.LoadFeature('CCI50')

		if 'CCICHERRIES_CCI50' not in self.df.columns:
			self.df['CCICHERRIES_CCI50']=( (self.df['CCI50']-self.df['CCI5'])>180 & (self.df['CCI50']>100) )
			self.df['CCICHERRIES_CCI50']=self.df['CCICHERRIES_CCI50'].apply(lambda x: int(x))
			

		ind=self.df.index[self.df.index<=T]
		if len(ind)>0:
			ind=ind[-1]
			return self.df.loc[ind,'CCICHERRIES_CCI50'] 
		else:
			return None


	@registerquery(filename=filename,category='Price')
	def SMA20BOUNCE1(self,T):
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
		
		if 'SMA20BOUNCE1' not in self.df.columns:		
			def signal(row):
				p=row.get('poly',np.nan)
				err_min=row.get('err_min',np.nan)
				err=np.array(row.get('err',np.nan))
				SMAstd20_mean=row.get('SMAstd20_mean',np.nan)
				if len(err[err>=0])>=1*len(err)/2 and p[0]>0 and abs(err_min)<=0.5*SMAstd20_mean:
					return 1
				else:
					return 0

			self.df['SMA20BOUNCE1']=self.df['SMALowPoly2win4Fit'].apply(lambda x: signal(x) if not pd.isnull(x) else None)
		

		ind=self.df.index[self.df.index<=T]
		if len(ind)>0:
			ind=ind[-1]
			return self.df.loc[ind,'SMA20BOUNCE1'] 
		else:
			return None


	@registerquery(filename=filename,category='Price')
	def SMA20BOUNCE2(self,T):
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
		
		if 'SMA20BOUNCE2' not in self.df.columns:		
			def signal(row):
				p=row.get('poly',np.nan)
				err_min=row.get('err_min',np.nan)
				err_max=row.get('err_max',np.nan)
				err=np.array(row.get('err',np.nan))
				SMAstd20_mean=row.get('SMAstd20_mean',np.nan)
				if len(err[err>=0])>=1*len(err)/2 and p[0]>0 and abs(err_min)<=0.4*err_max:
					return 1
				else:
					return 0

			self.df['SMA20BOUNCE2']=self.df['SMALowPoly2win4Fit'].apply(lambda x: signal(x) if not pd.isnull(x) else None)
		

		ind=self.df.index[self.df.index<=T]
		if len(ind)>0:
			ind=ind[-1]
			return self.df.loc[ind,'SMA20BOUNCE2'] 
		else:
			return None

	@registerquery(filename=filename,category='Price')
	def SMA20BOUNCE3(self,T):
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
		
		if 'SMA20BOUNCE3' not in self.df.columns:		
			def signal(row):
				p=row.get('poly',np.nan)
				err_min=row.get('err_min',np.nan)
				err_max=row.get('err_max',np.nan)
				err=np.array(row.get('err',np.nan))
				SMAstd20_mean=row.get('SMAstd20_mean',np.nan)
				SMA20_mean=row.get('SMA20_mean',np.nan)
				if len(err[err>=0])>=1*len(err)/2 and p[0]>0 and abs(err_min)<=0.4*SMA20_mean:
					return 1
				else:
					return 0

			self.df['SMA20BOUNCE3']=self.df['SMALowPoly2win4Fit'].apply(lambda x: signal(x) if not pd.isnull(x) else None)
		

		ind=self.df.index[self.df.index<=T]
		if len(ind)>0:
			ind=ind[-1]
			return self.df.loc[ind,'SMA20BOUNCE3'] 
		else:
			return None







	@registerquery(filename=filename,category='Price')
	def EMA8BOUNCE1(self,T):
		"""
		HasCherries
		"""
		if not hasattr(self,'df'):
			self.df=self.GetStockData(self.Symbolid)

		if 'EMA8' not in self.df.columns:
			self.df['EMA8']=self.LoadFeature('EMA8')

		if 'EMAstd8' not in self.df.columns:
			self.df['EMAstd8']=self.LoadFeature('EMAstd8')

		if 'EMALowPoly2win4Fit' not in self.df.columns:
			self.df['EMALowPoly2win4Fit']=self.LoadFeature('EMALowPoly2win4Fit')
		
		if 'EMA8BOUNCE1' not in self.df.columns:		
			def signal(row):
				p=row.get('poly',np.nan)
				err_min=row.get('err_min',np.nan)
				err=np.array(row.get('err',np.nan))
				EMAstd8_mean=row.get('EMAstd8_mean',np.nan)
				if len(err[err>=0])>=1*len(err)/2 and p[0]>0 and abs(err_min)<=0.5*EMAstd8_mean:
					return 1
				else:
					return 0

			self.df['EMA8BOUNCE1']=self.df['EMALowPoly2win4Fit'].apply(lambda x: signal(x) if not pd.isnull(x) else None)
		

		ind=self.df.index[self.df.index<=T]
		if len(ind)>0:
			ind=ind[-1]
			return self.df.loc[ind,'EMA8BOUNCE1'] 
		else:
			return None


	@registerquery(filename=filename,category='Price')
	def EMA8BOUNCE2(self,T):
		"""
		HasCherries
		"""
		if not hasattr(self,'df'):
			self.df=self.GetStockData(self.Symbolid)

		if 'EMA8' not in self.df.columns:
			self.df['EMA8']=self.LoadFeature('EMA8')

		if 'EMAstd8' not in self.df.columns:
			self.df['EMAstd8']=self.LoadFeature('EMAstd8')

		if 'EMALowPoly2win4Fit' not in self.df.columns:
			self.df['EMALowPoly2win4Fit']=self.LoadFeature('EMALowPoly2win4Fit')
		
		if 'EMA8BOUNCE2' not in self.df.columns:		
			def signal(row):
				p=row.get('poly',np.nan)
				err_min=row.get('err_min',np.nan)
				err_max=row.get('err_max',np.nan)
				err=np.array(row.get('err',np.nan))
				if len(err[err>=0])>=1*len(err)/2 and p[0]>0 and abs(err_min)<=0.4*err_max:
					return 1
				else:
					return 0

			self.df['EMA8BOUNCE2']=self.df['EMALowPoly2win4Fit'].apply(lambda x: signal(x) if not pd.isnull(x) else None)
		

		ind=self.df.index[self.df.index<=T]
		if len(ind)>0:
			ind=ind[-1]
			return self.df.loc[ind,'EMA8BOUNCE2'] 
		else:
			return None

	@registerquery(filename=filename,category='Price')
	def EMA8BOUNCE3(self,T):
		"""
		HasCherries
		"""
		if not hasattr(self,'df'):
			self.df=self.GetStockData(self.Symbolid)

		if 'EMA8' not in self.df.columns:
			self.df['EMA8']=self.LoadFeature('EMA8')

		if 'EMAstd8' not in self.df.columns:
			self.df['EMAstd8']=self.LoadFeature('EMAstd8')

		if 'EMALowPoly2win4Fit' not in self.df.columns:
			self.df['EMALowPoly2win4Fit']=self.LoadFeature('EMALowPoly2win4Fit')
		
		if 'EMA8BOUNCE3' not in self.df.columns:		
			def signal(row):
				p=row.get('poly',np.nan)
				err_min=row.get('err_min',np.nan)
				err=np.array(row.get('err',np.nan))
				EMA8_mean=row.get('EMA8_mean',np.nan)
				if len(err[err>=0])>=1*len(err)/2 and p[0]>0 and abs(err_min)<=0.4*EMA8_mean:
					return 1
				else:
					return 0

			self.df['EMA8BOUNCE3']=self.df['EMALowPoly2win4Fit'].apply(lambda x: signal(x) if not pd.isnull(x) else None)
		

		ind=self.df.index[self.df.index<=T]
		if len(ind)>0:
			ind=ind[-1]
			return self.df.loc[ind,'EMA8BOUNCE3'] 
		else:
			return None





	@registerquery(filename=filename,category='Price')
	def CHERRYSMABOUNCE(self,T):
		"""
		HasCherries
		"""
		if not hasattr(self,'df'):
			self.df=self.GetStockData(self.Symbolid)

		if 'CCICHERRIES' not in self.df.columns:
			self.CCICHERRIES(T)
		
		if 'SMA20BOUNCE1' not in self.df.columns:
			self.SMA20BOUNCE1(T)
		if 'SMA20BOUNCE2' not in self.df.columns:
			self.SMA20BOUNCE2(T)
		if 'SMA20BOUNCE3' not in self.df.columns:
			self.SMA20BOUNCE3(T)

		if 'EMA8BOUNCE1' not in self.df.columns:
			self.EMA8BOUNCE1(T)

		if 'EMA8BOUNCE2' not in self.df.columns:
			self.EMA8BOUNCE2(T)

		if 'EMA8BOUNCE3' not in self.df.columns:
			self.EMA8BOUNCE3(T)

		if 'PastPROFIT10days' not in self.df.columns:
			self.LoadFeature('PastPROFIT10days')

		if 'PastLOSS10days' not in self.df.columns:
			self.LoadFeature('PastLOSS10days')

		if 'CCI50' not in self.df.columns:
			self.LoadFeature('CCI50')


		
		if 'CHERRYSMABOUNCE' not in self.df.columns:
			for i in range(10,len(self.df)):
				dp=self.df.loc[self.df.index[i-10:i],:]
				if (dp['SMA20BOUNCE1'].max()>0 or dp['SMA20BOUNCE2'].max()>0 or dp['SMA20BOUNCE3'].max()>0 or dp['EMA8BOUNCE1'].max()>0 or dp['EMA8BOUNCE2'].max()>0 or dp['EMA8BOUNCE3'].max()>0) and dp['PastPROFIT10days'].min()>0 and dp['PastLOSS10days'].max()>-10:
					self.df.loc[self.df.index[i],'CHERRYSMABOUNCE']=1

		

		ind=self.df.index[self.df.index<=T]
		if len(ind)>0:
			ind=ind[-1]
			return self.df.loc[ind,'CHERRYSMABOUNCE'] 
		else:
			return None



# --------- This is required to sync the features to the database -------------
queries.finalize(filename)