from __future__ import division
from featureapp.featuremodel import featuremodel, pd, np, json


class CCI(featuremodel):
	requires_features=[]
	return_type=float
	compute_features=['CCI50','CCICHERRIES','CCICHERRIES_CCI50']

	def compute(self,Tvec):
		self.df['CCICHERRIES']=( (self.df['CCI50']-self.df['CCI5'])>180  )
		self.df['CCICHERRIES']=self.df['CCICHERRIES'].apply(lambda x: int(x))
		
		self.df['CCICHERRIES_CCI50']=( (self.df['CCI50']-self.df['CCI5'])>180 & (self.df['CCI50']>100) )
		self.df['CCICHERRIES_CCI50']=self.df['CCICHERRIES_CCI50'].apply(lambda x: int(x))
	

class SMA(featuremodel):
	requires_features=[]
	return_type=float
	compute_features=['SMA10','SMA20','SMA50','SMA100','SMA200','SMAstd20','EMA8','EMAstd8','CCI5','CCI50']
	
	def compute(self,Tvec):
		self.DM.AddIndicatorCols(cols=['SMA10','SMA20','SMA50','SMA100','SMA200','SMAstd20','EMA8','EMAstd8','CCI5','CCI50'])
	

class PastPerf(featuremodel):
	def PastProfit(self,Tvec):

		
		DFpastperf30=pd.DataFrame()
		for i in range(1,30):
			DFpastperf30[i]=100*self.df['Close'].diff(periods=i)/self.df['Close'].shift(periods=i)
		DFpastperf30['Zeroperf']=0

		self.df['PastPROFIT10days']=DFpastperf30[range(1,11)+['Zeroperf']].max(axis=1).round()
		self.df['PastPROFIT30days']=DFpastperf30[range(1,30)+['Zeroperf']].max(axis=1).round()

		self.df['PastLOSS10days']=DFpastperf30[range(1,11)+['Zeroperf']].min(axis=1).round()
		self.df['PastLOSS30days']=DFpastperf30[range(1,30)+['Zeroperf']].min(axis=1).round()


class FuturePerf(featuremodel):
	def FutPROFIT(self,Tvec):
		DFperf30=pd.DataFrame()
		for i in range(1,30):
			DFperf30[i]=-100*self.df['Close'].diff(periods=-i)/self.df['Close']
		DFperf30['Zeroperf']=0

		self.df['FutPROFIT10days']=DFperf30[range(1,11)+['Zeroperf']].max(axis=1).round()
		self.df['FutPROFIT30days']=DFperf30[range(1,30)+['Zeroperf']].max(axis=1).round()

		self.df['FutLOSS10days']=DFperf30[range(1,11)+['Zeroperf']].min(axis=1).round()
		self.df['FutLOSS30days']=DFperf30[range(1,30)+['Zeroperf']].min(axis=1).round()








