
import featureapp.models as ftmd
import stockapp.models as stkmd
from dataapp.datamanager import DataManager
import dataapp.libs as dtalibs
import json
import utility.models as utymd
import numpy as np
import pandas as pd
import collections as clct
from utility import maintenance as mnt


class featuremodel(object):
	"""
	1. Compute features
	2. Rerun mode: re run and overwrite
	3. Non-rerun: find missing and fill them up
	4. register the featuers
		- if features were changed, remove them from db also
	5. 
	"""
	# def __new__(cls):
	# 	cls.recordedfeatures=set([])

	def __init__(self,Symbolid,Fromdate,Todate):
		self.Symbolid=Symbolid
		self.Fromdate=dtalibs.Convert2date( Fromdate )
		self.Todate=dtalibs.Convert2date( Todate )


		self.label2func={}
		self.func2label=clct.defaultdict(list)

		self.stk=stkmd.Stockmeta.objects.get(id=Symbolid)
		

		self.FC=None
		
		
		


	


	def Initialize(self):
		self.FC=ftmd.FeatureComputeCode.objects.get(Username=self.filename)


		# first register the features and the functions that call them
		self.RegisterFeatures()

		self.DM=DataManager(SymbolIds=[self.Symbolid])
		self.Trange=filter(lambda x: x>=self.Fromdate and x<=self.Todate,self.DM.TradingDates)
		self.DM.AddStockData()

		# get the feature compute code
		

		# load the features from db
		self.DM.Addfeaturecols()



	def RegisterFeatures(self):
		pass



	@property
	def df(self):
		return self.DM.DF[self.Symbolid ]

	def recordfeature(self,name=None,FeatureFunction=None,doc=None,category=None,required=None,returntype=None,query=True,operators=None,null=False,cache=False):
		if name is None or FeatureFunction is None or doc is None or category is None or returntype is None or query is None or operators is None:
			raise Exception('Fields missing in kwargs recordfeature')

		returntype=str(returntype)
		info={'name':name,'FeatureFunction':FeatureFunction,'doc':doc,'Category':category,'Query':query,'Returntype':returntype,'operators':operators,'null':null,'filename':self.filename}

		secondary_fields={	'Featuredescription':doc,'FeatureCode':self.FC,} 
		secondary_fields.update(info)

		utymd.set_or_create(ftmd.FeaturesMeta,primary_fields={'Featurelabel':name},secondary_fields=secondary_fields)

		self.label2func.update({name:FeatureFunction})
		self.func2label[FeatureFunction].append(name)





	def Getfunc(self,featfuncname):
		return getattr(self,featfuncname)

	def Getfeaturefunc(self,ftname):
		return Getfunc(self.label2func[ftname])



	# @mnt.logexception('debug',appendmsg='featuremodel',printit=True)
	# @mnt.logperf('debug',appendmsg='featuremodel',printit=True)
	def ComputeFeature(self,ft):
		func=self.Getfeaturefunc(ft)
		func(self.Trange)

	def ComputeAllFeatures(self):
		featurefuncs=self.func2label.keys()
		for ftfunc in featurefuncs:
			func=self.Getfunc(ftfunc)
			func(self.Trange)

		print "Done compute"

	
	
	# @mnt.logperf('debug',appendmsg='featuremodel',printit=True)
	def postprocessing(self):
		"""
		clean up formatting before saving
		"""
		self.DM.DF[self.Symbolid] = self.df.where((pd.notnull(self.df)), None)
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
	def saveall_overwrite(self):

		self.postprocessing()

		ftmd.FeaturesData.objects.filter(Symbol=self.stk.Symbol,T__in=self.Trange).delete()

		featurelist=self.label2func.keys()
		bulkfeats=[]
		for Tind in self.Trange:
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
