
import featureapp.models as ftmd
import featureapp.libs as ftlibs
import json
import utility.models as utymd
import numpy as np
import pandas as pd

class featurefunc(object):
	functionregistry={}
	def __init__(self,featurelabels):
		self.featurelabels=featurelabels
	def __call__(self,func):
		"""
		conveneient decorator function
		"""
		
		self.functionregistry[func.__name__]=self.featurelabels

		@functools.wraps(func)
		def func2(*args,**kwargs):
			return func(*args,**kwargs)

		func2.isfeature=True
		
		return func2


class registerfeature(object):
	featureregistry={}
	def __init__(self,filename):
		self.filename=filename

	def recordfeature(self,name=None,doc=None,category=None,required=None,returntype=None,query=True,operators=None,null=False):
		if name is None or doc is None or category is None or returntype is None or query is None or operators is None:
			raise Exception('Fields missing in kwargs recordfeature')

		self.info={'name':name,'doc':doc,'Category':category,'Query':query,'Returntype':returntype,'operators':operators,'null':null,'filename':self.filename}


		self.featureregistry[self.info['name']]={'doc':self.info['doc']}

		FC=ftmd.FeatureComputeCode.objects.get(Username=self.info['filename'])
		secondary_fields={	'Featuredescription':doc,'FeatureCode'=FC,} 
		secondary_fields.update(self.info)

		utymd.set_or_create(ftmd.FeaturesMeta,primary_fields={'Featurelabel':name},secondary_fields=secondary_fields)







class featuremodel(object):
	"""
	1. Compute features
	2. Rerun mode: re run and overwrite
	3. Non-rerun: find missing and fill them up
	4. register the featuers
		- if features were changed, remove them from db also
	5. 
	"""


	def __init__(self,Symbolid,Trange):
		self.features={}
		self.Symbolid=Symbolid
		self.Trange=Trange
		self.Fromdate=Trange[0]
		self.Todate=Trange[-1]
		self.stk=stkmd.Stockmeta.objects.get(id=Symbolid)

		self.preprocessing()
		self.stockTrange=set(self.df.index)
		self.Trange=[T for T in self.Trange if T in self.stockTrange]

		self.featcache={}

	def __del__(self):
		if hasattr(self,'df'):
			del self.df

	def LoadFeatures(self):
		self.df=GetFeature(Symbolids=[self.Symbolid],Trange=self.Trange,dfmain=self.df)

	def GetStockData(self,*args,**kwargs):
		return dtalibs.GetStockData(*args,**kwargs)

	

	def addindicators(self,*args,**kwargs):
		return dtalibs.addindicators(*args,**kwargs)

	def getfeaturefunc(self,feat):
		# print feat
		return getattr(self,feat)


				
	@classmethod
	def getfeaturelist(cls):
		return [x for x, y in cls.__dict__.items() if hasattr(cls.__dict__[x],'isfeature')]

	@classmethod
	def finalize(cls,filename):
		featurelist=cls.getfeaturelist()
		if ftmd.FeatureComputeCode.objects.filter(Username=filename).exists():
			FC=ftmd.FeatureComputeCode.objects.get(Username=filename)
			dbfeatures=list( ftmd.FeaturesMeta.objects.filter(FeatureCode=FC).values_list('Featurelabel',flat=True) )
			for ft in dbfeatures:
				if ft not in featurelist:
					print ft," is not there, so deleting it"
					ftmd.FeaturesMeta.objects.filter(Featurelabel=ft).delete()




	# @mnt.logexception('debug',appendmsg='featuremodel',printit=True)
	# @mnt.logperf('debug',appendmsg='featuremodel',printit=True)
	def computefeature(self,ft,T):
		return self.getfeaturefunc(ft)(T)

	def computeall(self,skipdone=True):
		featurelist=self.getfeaturelist()	
		# print featurelist
		for ft in featurelist:
			self.computefeature(ft,self.Trange)

		print "Done compute"

	def computeonly(self,featurelist=[]):
		for ft in featurelist:
			self.computefeature(ft,self.Trange)

		print "Done compute"		
	
	# @mnt.logperf('debug',appendmsg='featuremodel',printit=True)
	def postprocessing(self):
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

		
	# @mnt.logperf('debug',appendmsg='saveallfeatures',printit=True)
	def saveall(self,mode='rerun'):

		self.postprocessing()

		if mode=='rerun':
			ftmd.FeaturesData.objects.filter(Symbol=self.stk.Symbol,T__in=self.Trange).delete()


		featurelist=self.getfeaturelist()
		bulkfeats=[]
		for Tind in self.df.index:
			if mode=='rerun':
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
