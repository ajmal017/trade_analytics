




import json
import pandas as pd
import numpy as np
import featureapp.models as ftmd
import stockapp.models as stkmd
import dataapp.models as dtamd
import dataapp.libs as dtalibs
import functools
from utility import maintenance as mnt
import logging
logger = logging.getLogger('debug')


def standardizefeaturedata(Qrysets):
	if Qrysets.count()==0:
		return pd.DataFrame()

	df1=pd.DataFrame(list( Qrysets ) )
	df1.rename(columns={'Symbol__id':'Symbolid','Symbol__Symbol':'Symbol'},inplace=True)
	df1['Symbol']=df1['Symbol'].astype(str)

	df1['T']=df1['T'].apply(lambda x: pd.to_datetime(x).date())
	
	for cc in df1.columns:
		if ftmd.FeaturesMeta.objects.filter(Featurelabel=cc).exists():
			rettype=ftmd.FeaturesMeta.objects.get(Featurelabel=cc).Returntype
			if rettype!='json':
				df1[cc]=df1[cc].astype(eval(rettype))

		elif cc in ['Close','Open','High','Low']:
			df1[cc]=df1[cc].astype(float)

	if 'Featuredata' in df1.columns:
		df2=pd.DataFrame(df1['Featuredata'].tolist())
	else:
		df2=pd.DataFrame()

	df3=pd.concat([df1, df2], axis=1)
	del df1
	del df2
	df3.index=df3['T'].copy()
	
	if 'Featuredata' in df3.columns:
		df3.drop(['Featuredata'],axis=1,inplace=True)

	df3 = df3.where((pd.notnull(df3)), np.nan)
	df3.sort_index(inplace=True)

	return df3

@mnt.logperf('debug',printit=True)
def GetFeature(Symbolids=None,Trange=[T.date() for T in pd.date_range(pd.datetime(2002,1,1),pd.datetime.today()) if T.weekday()<=4],dfmain=None):
	if Symbolids==None:
		Symbolids=stkmd.Stockmeta.objects.all().values_list('id',flat=True)

	if type(Symbolids)!=list and type(Symbolids)!=tuple:
		Symbolids=list((Symbolids))

	Qrysets=ftmd.FeaturesData.objects.filter(Symbol__id__in=Symbolids,T__in=Trange).values('T','Symbol__id','Symbol__Symbol','Featuredata')
	if dfmain == None:
		return standardizefeaturedata(Qrysets)
	else:
		df=standardizefeaturedata(Qrysets)
		return pd.concat([dfmain, df], axis=1, join_axes=[dfmain.index])
	
def GetFeature_iterator(Symbolids=None,Trange=[T.date() for T in pd.date_range(pd.datetime(2002,1,1),pd.datetime.today()) if T.weekday()<=4] ):
	if Symbolids==None:
		Symbolids=stkmd.Stockmeta.objects.all().values_list('id',flat=True)

	if type(Symbolids)!=list and type(Symbolids)!=tuple:
		Symbolids=list((Symbolids))

	for sid in Symbolids:
		yield ( stkmd.Stockmeta.objects.get(id=sid),GetFeature(Symbolids=[sid],Trange=Trange) )



class registerfeature(object):
	
	def __init__(self,filename=None,category=None,required=[],returntype=None,query=True,operators=None,null=False,cache=False):
		
		self.category=category
		self.query=query
		self.returntype=returntype
		self.operators=operators
		self.null=null
		self.filename=filename


		self.usecache=cache
		self.cache={}
		self.registry={}
	
	def recordfeature(self):

		if ftmd.FeaturesMeta.objects.filter(Featurelabel=self.name).exists():
			featmeta=ftmd.FeaturesMeta.objects.get(Featurelabel=self.name)
			featmeta.Featuredescription=self.doc
			featmeta.Category=self.category
			featmeta.Returntype=self.returntype.__name__
			featmeta.operators=self.operators
			featmeta.Query=self.query
			featmeta.Userfilename=self.filename
			featmeta.save()
			# print "Updated feature ",featmeta

		else:
			featmeta=ftmd.FeaturesMeta(Featurelabel=self.name,Featuredescription=self.doc,
									Category=self.category,Returntype=self.returntype.__name__,
									operators=self.operators,Query=self.query,Userfilename=self.filename)
			featmeta.save()
			# print "Saving feature ",featmeta

	def __call__(self,func):
		
		self.name=func.__name__
		self.doc=func.__doc__
		
		# if self.name in self.registry:
		# 	raise KeyError("label already there, please rename "+self.name)
		
		self.recordfeature()

		self.registry[self.name]={'doc':self.doc}
		
		@functools.wraps(func)
		def func2(*args,**kwargs):
			

			# if self.usecache:
			# 	keyargs=[str(a) for a in args]
			# 	keykwargs={}
			# 	for k,v in kwargs.items():
			# 		keykwargs[k]=str(v)
			# 	key=json.dumps([keyargs,keykwargs])

			# 	if key in self.cache:
			# 		return self.cache[key]
			# 	else:
			# 		self.cache[key]=func(*args,**kwargs)
			# 		return self.cache[key]
			# else:

			return func(*args,**kwargs)
		func2.isfeature=True
		
		return func2



class featuremodel(object):



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

	def GetStockData(self,*args,**kwargs):
		return dtalibs.GetStockData(*args,**kwargs)

	

	def addindicators(self,*args,**kwargs):
		return dtalibs.addindicators(*args,**kwargs)

	def getfeaturefunc(self,feat):
		# print feat
		return getattr(self,feat)

	def LoadFeature(self,feat,Trange=None):
		stkid=self.Symbolid
		if Trange==None:
			Trange=self.Trange


		if str((stkid,Trange)) in self.featcache:
			if feat in self.featcache[str((stkid,Trange))].columns: 
				return self.featcache[str((stkid,Trange))][feat]
			else:
				cols=self.featcache[str((stkid,Trange))].columns
				return self.featcache[str((stkid,Trange))][cols[0]]*np.nan
		else:
			df3=GetFeature([stkid],Trange)
			self.featcache[str((stkid,Trange))]=df3
			if feat in df3.columns:
				return df3[feat]
			else:
				cols=self.featcache[str((stkid,Trange))].columns
				return self.featcache[str((stkid,Trange))][cols[0]]*np.nan
				
	@classmethod
	def getfeaturelist(cls):
		return [x for x, y in cls.__dict__.items() if hasattr(cls.__dict__[x],'isfeature')]

	@classmethod
	def finalize(cls,filename):
		featurelist=cls.getfeaturelist()
		dbfeatures=list( ftmd.FeaturesMeta.objects.filter(Userfilename=filename).values_list('Featurelabel',flat=True) )
		for ft in dbfeatures:
			if ft not in featurelist:
				print ft," is not there, so deleting it"
				ftmd.FeaturesMeta.objects.filter(Featurelabel=ft).delete()




	@mnt.logexception('debug',appendmsg='featuremodel',printit=True)
	@mnt.logperf('debug',appendmsg='featuremodel',printit=True)
	def computefeature(self,ft,T):
		return self.getfeaturefunc(ft)(T)

	def computeall(self,skipdone=True):
		featurelist=self.getfeaturelist()	
		# print featurelist
		for ft in featurelist:
			self.computefeature(ft,self.Trange)

		print "Done compute"

	

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

		
	@mnt.logperf('debug',appendmsg='saveallfeatures',printit=True)
	def saveall(self,mode='rerun'):
		self.postprocessing()

		if mode=='rerun':
			ftmd.FeaturesData.objects.filter(Symbol=self.stk,T__in=self.Trange).delete()

		featurelist=self.getfeaturelist()
		for Tind in self.df.index:
			if mode=='rerun':
				featdata=ftmd.FeaturesData(Symbol=self.stk,T=Tind)

			for ft in featurelist:
				featdata.Featuredata[ft]=mnt.replaceNaN2None( self.df.loc[Tind,ft] )

			featdata.save()


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
