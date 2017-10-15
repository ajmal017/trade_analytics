from __future__ import division
from featureapp.featuremodel import featuremodel, pd, np, json
filename=__name__.split('.')[-1]

print filename,__name__


# --------------  features has to be the name of the class ------------------
# Define your features in this class


class features(featuremodel):
	filename=filename


	def RegisterFeatures(self):
		self.recordfeature(name='CCICHERRIES',FeatureFunction='CCICHERRIES',doc='has cherries',category='Momentum',required=[],returntype=int,query=True,operators=['<','>','<=','>=','inrange','!=','!inrange'],null=False,cache=False)
		self.recordfeature(name='CCICHERRIES_CCI50',FeatureFunction='CCICHERRIES',doc='has cherries',category='Momentum',required=[],returntype=int,query=True,operators=['<','>','<=','>=','inrange','!=','!inrange'],null=False,cache=False)

		self.recordfeature(name='CCI5',FeatureFunction='SMAs',doc='CCI',category='Momentum',required=[],returntype=int,query=True,operators=['<','>','<=','>=','inrange','!=','!inrange'],null=False,cache=False)
		self.recordfeature(name='CCI50',FeatureFunction='SMAs',doc='CCI',category='Momentum',required=[],returntype=int,query=True,operators=['<','>','<=','>=','inrange','!=','!inrange'],null=False,cache=False)

		self.recordfeature(name='SMA10',FeatureFunction='SMAs',doc='SMA',category='Price',required=[],returntype=int,query=True,operators=['<','>','<=','>=','inrange','!=','!inrange'],null=False,cache=False)
		self.recordfeature(name='SMA20',FeatureFunction='SMAs',doc='SMA',category='Price',required=[],returntype=int,query=True,operators=['<','>','<=','>=','inrange','!=','!inrange'],null=False,cache=False)
		self.recordfeature(name='SMA50',FeatureFunction='SMAs',doc='SMA',category='Price',required=[],returntype=int,query=True,operators=['<','>','<=','>=','inrange','!=','!inrange'],null=False,cache=False)
		self.recordfeature(name='SMA100',FeatureFunction='SMAs',doc='SMA',category='Price',required=[],returntype=int,query=True,operators=['<','>','<=','>=','inrange','!=','!inrange'],null=False,cache=False)
		self.recordfeature(name='SMA200',FeatureFunction='SMAs',doc='SMA',category='Price',required=[],returntype=int,query=True,operators=['<','>','<=','>=','inrange','!=','!inrange'],null=False,cache=False)
		self.recordfeature(name='SMAstd20',FeatureFunction='SMAs',doc='SMA',category='Price',required=[],returntype=int,query=True,operators=['<','>','<=','>=','inrange','!=','!inrange'],null=False,cache=False)
		self.recordfeature(name='EMA8',FeatureFunction='SMAs',doc='EMA',category='Price',required=[],returntype=int,query=True,operators=['<','>','<=','>=','inrange','!=','!inrange'],null=False,cache=False)
		self.recordfeature(name='EMAstd8',FeatureFunction='SMAs',doc='EMA',category='Price',required=[],returntype=int,query=True,operators=['<','>','<=','>=','inrange','!=','!inrange'],null=False,cache=False)

		self.recordfeature(name='PastPROFIT10days',FeatureFunction='PastProfit',doc='Performance',category='Performance',required=[],returntype=int,query=True,operators=['<','>','<=','>=','inrange','!=','!inrange'],null=False,cache=False)
		self.recordfeature(name='PastPROFIT30days',FeatureFunction='PastProfit',doc='Performance',category='Performance',required=[],returntype=int,query=True,operators=['<','>','<=','>=','inrange','!=','!inrange'],null=False,cache=False)
		self.recordfeature(name='PastLOSS10days',FeatureFunction='PastProfit',doc='Performance',category='Performance',required=[],returntype=int,query=True,operators=['<','>','<=','>=','inrange','!=','!inrange'],null=False,cache=False)
		self.recordfeature(name='PastLOSS30days',FeatureFunction='PastProfit',doc='Performance',category='Performance',required=[],returntype=int,query=True,operators=['<','>','<=','>=','inrange','!=','!inrange'],null=False,cache=False)

		self.recordfeature(name='FutPROFIT10days',FeatureFunction='FutPROFIT',doc='Performance',category='Output',required=[],returntype=int,query=True,operators=['<','>','<=','>=','inrange','!=','!inrange'],null=False,cache=False)
		self.recordfeature(name='FutPROFIT30days',FeatureFunction='FutPROFIT',doc='Performance',category='Output',required=[],returntype=int,query=True,operators=['<','>','<=','>=','inrange','!=','!inrange'],null=False,cache=False)
		self.recordfeature(name='FutLOSS10days',FeatureFunction='FutPROFIT',doc='Performance',category='Output',required=[],returntype=int,query=True,operators=['<','>','<=','>=','inrange','!=','!inrange'],null=False,cache=False)
		self.recordfeature(name='FutLOSS30days',FeatureFunction='FutPROFIT',doc='Performance',category='Output',required=[],returntype=int,query=True,operators=['<','>','<=','>=','inrange','!=','!inrange'],null=False,cache=False)


	def preprocessing(self):
		self.Addindicators(cols=['SMA10','SMA20','SMA50','SMA100','SMA200','SMAstd20','EMA8','EMAstd8','CCI5','CCI50'])

	def ModelPredictions(self,Tvec):
		import datascience.models as dtscmd
		from datascience.ML import MLmodels as ML
		models=dtscmd.MLmodels.objects.filter(Deploy=True)
		ML.ModelPredictionManager(models.values_list('id',flat=True))
		ML.load_Models_TransFuncs()
		Y=ML.getprediction_stocks_bySymbol(self.Symbolid,self.Trange)

		for model in models:
			modelname=model.getmodelname()
			self.recordfeature(name=modelname,doc=model.Info['description'],category='MLpdictions',required=[],returntype=json,query=True,operators=['<','>','<=','>=','inrange','!=','!inrange'],null=False,cache=False)

			self.df[modelname]=Y[modelname]

	def CCICHERRIES(self,Tvec):
		"""
		HasCherries
		"""


		self.df['CCICHERRIES']=( (self.df['CCI50']-self.df['CCI5'])>180  )
		self.df['CCICHERRIES']=self.df['CCICHERRIES'].apply(lambda x: int(x))
		
		self.df['CCICHERRIES_CCI50']=( (self.df['CCI50']-self.df['CCI5'])>180 & (self.df['CCI50']>100) )
		self.df['CCICHERRIES_CCI50']=self.df['CCICHERRIES_CCI50'].apply(lambda x: int(x))
		



	def SMAs(self,Tvec):
		pass

		
	def PastProfit(self,Tvec):

		DFpastperf30=pd.DataFrame()
		for i in range(1,30):
			DFpastperf30[i]=100*self.df['Close'].diff(periods=i)/self.df['Close'].shift(periods=i)
		DFpastperf30['Zeroperf']=0

		self.df['PastPROFIT10days']=self.DFpastperf30[[range(1,11)]+['Zeroperf']].max(axis=1).round()
		self.df['PastPROFIT30days']=self.DFpastperf30[[range(1,30)]+['Zeroperf']].max(axis=1).round()

		self.df['PastLOSS10days']=self.DFpastperf30[[range(1,11)]+['Zeroperf']].min(axis=1).round()
		self.df['PastLOSS30days']=self.DFpastperf30[[range(1,30)]+['Zeroperf']].min(axis=1).round()





	def FutPROFIT(self,Tvec):
		DFperf30=pd.DataFrame()
		for i in range(1,30):
			DFperf30[i]=-100*self.df['Close'].diff(periods=-i)/self.df['Close']
		DFperf30['Zeroperf']=0

		self.df['FutPROFIT10days']=self.DFperf30[[range(1,11)]+['Zeroperf']].max(axis=1).round()
		self.df['FutPROFIT30days']=self.DFperf30[[range(1,30)]+['Zeroperf']].max(axis=1).round()

		self.df['FutLOSS10days']=self.DFperf30[[range(1,11)]+['Zeroperf']].min(axis=1).round()
		self.df['FutLOSS30days']=self.DFperf30[[range(1,30)]+['Zeroperf']].min(axis=1).round()








# # --------- This is required to sync the features to the database -------------
# features.finalize(filename)