
import featureapp.models as ftmd
import stockapp.models as stkmd
from dataapp.datamanager import DataManager
import json
import utility.models as utymd
import numpy as np
import pandas as pd

class register_featurefunction(object):
	featurefuncdict={}

	def __init__(self,filename,featurelabels):
		self.featurelabels=featurelabels
		self.FC=ftmd.FeatureComputeCode.objects.get(Username=filename)
	
	@classmethod
	def finalize(self):

	def __call__(self,func):
		"""
		conveneient decorator function
		"""
		for featlabel in self.featurelabels:
			FM=ftmd.FeaturesMeta.objects.get(FeatureCode=self.FC,Featurelabel=featlabel)
			FM.FeatureFunction=func.__name__
			FM.save()



		@functools.wraps(func)
		def func2(*args,**kwargs):
			return func(*args,**kwargs)

		func2.isfeature=True
		
		return func2


class featuremodel(object):
	"""
	1. Compute features
	2. Rerun mode: re run and overwrite
	3. Non-rerun: find missing and fill them up
	4. register the featuers
		- if features were changed, remove them from db also
	5. 
	"""
	def __new__(cls):
		cls.recordedfeatures=set([])

	def __init__(self,Symbolid,Trange):

		self.RegisterFeatures()

		self.Symbolid=Symbolid
		self.Trange=Trange
		self.Fromdate=Trange[0]
		self.Todate=Trange[-1]
		self.stk=stkmd.Stockmeta.objects.get(id=Symbolid)
		self.DM=DataManager(SymbolIds=[Symbolid])

		self.FC=ftmd.FeatureComputeCode.objects.get(Username=self.filename)
		self.LoadFeatures_db()
		self.CleanUpfeatures_db()

		self.LoadStockData()
		self.LoadFeatureData()

		self.preprocessing()

	@classmethod
	def recordfeature(cls,name=None,FeatureFunction=None,doc=None,category=None,required=None,returntype=None,query=True,operators=None,null=False):
		if name is None or FeatureFunction is None or doc is None or category is None or returntype is None or query is None or operators is None:
			raise Exception('Fields missing in kwargs recordfeature')

		info={'name':name,'FeatureFunction':FeatureFunction,'doc':doc,'Category':category,'Query':query,'Returntype':returntype,'operators':operators,'null':null,'filename':self.filename}
		cls.recordedfeatures.add(name)

		secondary_fields={	'Featuredescription':doc,'FeatureCode'=self.FC,} 
		secondary_fields.update(self.info)

		utymd.set_or_create(ftmd.FeaturesMeta,primary_fields={'Featurelabel':name},secondary_fields=secondary_fields)


	def preprocessing(self):
		pass

	def LoadFeatures_db(self):
		self.dffeatfuncs = pd.DataFrame( list( ftmd.FeaturesMeta.objects.filter(FeatureCode=self.FC).values('Featurelabel','FeatureFunction') ) )

	def CleanUpfeatures_db(self):
		for Featurelabel in self.dffeatfuncs['Featurelabel'].unique():
			if Featurelabel not in self.recordedfeatures:
				ftmd.FeaturesMeta.objects.filter(FeatureCode=self.FC,Featurelabel=Featurelabel).delete()
		self.LoadFeatures_db()


	def LoadFeatureData(self,featcols):
		self.DM.Addfeaturecols(self.dffeatfuncs['Featurelabel'].unique())


	def LoadStockData(self,*args,**kwargs):
		self.DM.GetStockData()

	def Addindicators(self,cols):
		self.DM.AddIndicators(cols)
		

	@property
	def df(self):
		return self.DM[self.Symbolid]

	def getfeaturelist(self):
		return self.dffeatfuncs['Featurelabel'].unique()

	def getfunctionlist(self):
		return self.dffeatfuncs['FeatureFunction'].unique()

	def getfeature_function(self,Featurelabel):
		funcname= self.dffeatfuncs[self.dffeatfuncs['Featurelabel']=='Featurelabel']['FeatureFunction'].iloc[0]
		return getattr(self,funcname)


	# @mnt.logexception('debug',appendmsg='featuremodel',printit=True)
	# @mnt.logperf('debug',appendmsg='featuremodel',printit=True)
	def computefeatureTrange(self,ft,T):
		func=self.getfeaturefunc(ft)
		func(T)

	def computeallfeatures(self):
		featurelist=self.dffeatfuncs['Featurelabel'].unique()	
		# print featurelist
		for ft in featurelist:
			self.computefeatureTrange(ft,self.Trange)

		print "Done compute"

	def computeonlyfeature(self,featurelist=[]):
		for ft in featurelist:
			self.computefeatureTrange(ft,self.Trange)

		print "Done compute"		
	
	# @mnt.logperf('debug',appendmsg='featuremodel',printit=True)
	def postprocessing(self):
		"""
		clean up formatting before saving
		"""
		self.df = self.df.where((pd.notnull(self.df)), None)
		for cc in self.df.columns:
			if ftmd.FeaturesMeta.objects.filter(Featurelabel=cc).exists():
				rettype=ftmd.FeaturesMeta.objects.get(Featurelabel=cc).Returntype
				if rettype=='json':
					self.df[cc]=self.df[cc].apply(lambda x: mnt.replaceNaN2None(x))
				else:
					self.df[cc]=self.df[cc].astype(eval(rettype))

			elif cc in ['Close','Open','High','Low']:
				self.df[cc]=self.df[cc].astype(float)				

	
	def saveonly_overwrite(self,featurelist=[]):
		self.postprocessing()
		for Tind in self.df.index:
			if ftmd.FeaturesData.objects.filter(Symbol=self.stk.Symbol,T=Tind).exists():
				featdata=ftmd.FeaturesData.objects.get(Symbol=self.stk.Symbol,T=Tind)
			else:
				featdata=ftmd.FeaturesData(Symbol=self.stk.Symbol,Symbol_id=self.stk.id,T=Tind)

			for ft in featurelist:
				if ft in self.df.columns:
					featdata.Featuredata[ft]=mnt.replaceNaN2None( self.df.loc[Tind,ft] )
			featdata.save()

		print "Done save"


	# @mnt.logperf('debug',appendmsg='saveallfeatures',printit=True)
	def saveall_overwrite(self):

		self.postprocessing()

		ftmd.FeaturesData.objects.filter(Symbol=self.stk.Symbol,T__in=self.Trange).delete()

		featurelist=self.getfeaturelist()
		bulkfeats=[]
		for Tind in self.df.index:
			featdata=ftmd.FeaturesData(Symbol=self.stk.Symbol,Symbol_id=self.stk.id,T=Tind)
			for ft in featurelist:
				if ft in self.df.columns:
					featdata.Featuredata[ft]=mnt.replaceNaN2None( self.df.loc[Tind,ft] )

			bulkfeats.append(featdata)
		
		ftmd.FeaturesData.objects.bulk_create(bulkfeats)	
		# featdata.save()


		print "Done save"

	def chartfeatures(self,addpricecols=(),addfeatcols=(),ip=5558):
		import zmq
		import zlib
		import pickle as pkl
		context = zmq.Context()
		colors=['b','g','r','c','m','y','k','w']


		if not hasattr(self,'df'):
			self.df=self.GetStockData(self.Symbolid)


		self.df=self.addindicators(self.df,[
										{'name':'SMA','timeperiod':20,'colname':'SMA20'},
										{'name':'SMA','timeperiod':50,'colname':'SMA50'},
										{'name':'SMA','timeperiod':100,'colname':'SMA100'},
										{'name':'SMA','timeperiod':200,'colname':'SMA200'},
										{'name':'EMA','timeperiod':8,'colname':'EMA8'},
									])


		pricecols=[
					{'colname':'SMA20','plotargs':('r',),'plotkwargs':{'label':'SMA20',}},
					{'colname':'SMA50','plotargs':('b',),'plotkwargs':{'label':'SMA50',}},
					{'colname':'SMA100','plotargs':('g',),'plotkwargs':{'label':'SMA100',}},
					{'colname':'SMA200','plotargs':('m',),'plotkwargs':{'label':'SMA200',}},
					{'colname':'EMA8','plotargs':('r--',),'plotkwargs':{'label':'EMA8',}},
				]+list(addpricecols)

		featcols=[]
		
		for ftblock in addfeatcols:
			FT=[]
			i=0
			for ft in ftblock:
				if ft not in self.df.columns:
					self.df[ft]=self.LoadFeature(ft)

				FT.append( {'colname':ft,'plotargs':(colors[i],),'plotkwargs':{'label':ft,}} ) 
				i=i+1							

			featcols.append(FT)

		#  Socket to talk to server
		print("Connecting to charting server")
		socket = context.socket(zmq.REQ)
		socket.connect("tcp://localhost:%s" % ip)

		msg={'pricecols':pricecols,'querycols':[],'featcols':featcols,'df':self.df.round(decimals=3)}
		p=pkl.dumps(msg)
		z=zlib.compress(p)

		socket.send(z)

		#  Get the reply.
		message = socket.recv()
		print message
		socket.close()
