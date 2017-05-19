




import json
import pandas as pd
import numpy as np
import queryapp.models as qymd
import stockapp.models as stkmd
import dataapp.models as dtamd
import featureapp.models as ftmd
import featureapp.libs as ftlibs
import dataapp.libs as dtalibs
import matplotlib.pyplot as plt

class registerquery(object):
	
	def __init__(self,filename=None,category=None):
		
		self.category=category
		self.filename=filename

		self.cache={}
		self.registry={}
	
	def recordquery(self):

		if qymd.QueryMeta.objects.filter(Querylabel=self.name).exists():
			qrymeta=qymd.QueryMeta.objects.get(Querylabel=self.name)
			qrymeta.Querydescription=self.doc
			qrymeta.Category=self.category
			qrymeta.Userfilename=self.filename
			qrymeta.save()
			print "Updated feature ",qrymeta

		else:
			qrymeta=qymd.QueryMeta(Querylabel=self.name,Querydescription=self.doc,Category=self.category,Userfilename=self.filename)
			qrymeta.save()
			print "Saving feature ",qrymeta

	def __call__(self,func):
		
		self.name=func.__name__
		self.doc=func.__doc__
		
		# if self.name in self.registry:
		# 	raise KeyError("label already there, please rename "+self.name)
		
		self.recordquery()

		self.registry[self.name]={'doc':self.doc}
		
		def func2(*args,**kwargs):
			
			return func(*args,**kwargs)
		func2.isquery=True
		
		return func2

class querymodel(object):



	def __init__(self,Symbolid,Trange):
		self.features={}
		self.Symbolid=Symbolid
		self.Trange=Trange
		self.Fromdate=Trange[0]
		self.Todate=Trange[-1]
		self.stk=stkmd.Stockmeta.objects.get(id=Symbolid)

		self.featcache={}


	def GetStockData(self,*args,**kwargs):
		return dtalibs.GetStockData(*args,**kwargs)
	def addindicators(self,*args,**kwargs):
		return dtalibs.addindicators(*args,**kwargs)

	def LoadFeature(self,feat,Symbol=None,Trange=None):
		if Symbol==None:
			stkid=self.Symbolid
		else:
			stkid=stkmd.Stockmeta.objects.get(Symbol=Symbol).id

		if Trange==None:
			Trange=self.Trange


		if str((stkid,Trange)) in self.featcache:
			return self.featcache[str((stkid,Trange))][feat]
		else:
			df3=ftlibs.GetFeature([stkid],Trange)
			self.featcache[str((stkid,Trange))]=df3
			return df3[feat]
	

	def getqueryfunc(self,feat):
		# print feat
		return getattr(self,feat)

	@classmethod
	def getquerylist(cls):
		return [x for x, y in cls.__dict__.items() if hasattr(cls.__dict__[x],'isquery')]

	@classmethod
	def finalize(cls,filename):
		querylist=cls.getquerylist()
		dbqueries=list( qymd.QueryMeta.objects.filter(Userfilename=filename).values_list('Querylabel',flat=True) )
		for qry in dbqueries:
			if qry not in querylist:
				print qry," is not there, so deleting it"
				qymd.QueryMeta.objects.filter(Querylabel=qry).delete()


	def computeall(self,skipdone=True):
		querylist=self.getquerylist()	
		# print featurelist
		self.ComputedQueries={}
		for qry in querylist:
			self.ComputedQueries[qry]={}
			for T in self.Trange:
				self.ComputedQueries[qry][T]=self.getqueryfunc(qry)(T)

		print "Done compute"

		return self.ComputedQueries
	

		

	def saveall(self):

		for T in self.Trange:
			if qymd.QueryData.objects.filter(Symbol=self.stk,T=T).exists():
				qrydata=qymd.QueryData.objects.get(Symbol=self.stk,T=T)
			else:
				qrydata=qymd.QueryData(Symbol=self.stk,T=T)
				qrydata.save()

			for qry in self.ComputedQueries.keys():
				v=self.ComputedQueries[qry][T]
				try:
					if pd.isnull(v):
						qrydata.Querydata[qry]=None
					else:
						qrydata.Querydata[qry]=v
				except:
					print type(v)

			qrydata.save()
		print "Done save"

	def OutcomeCharts(self,perf=[]):
		querylist=self.getquerylist()
		if len(perf)==0:
			return

		for pp in perf:
			if pp not in self.df.columns:
				self.df[pp]=self.LoadFeature(pp)

		color = dict(boxes='DarkGreen', whiskers='DarkOrange',medians='DarkBlue', caps='Gray')
		
		for qry in querylist:
			print "----------------- %s ---------------" % qry
			plt.figure()
			dp=self.df[(self.df[qry]==1) ][perf]
			dp.plot.box(color=color, sym='r+')
			plt.setp(plt.gca().get_xticklabels(), rotation=45, horizontalalignment='right')

			print "Number of signals = ",dp.shape
			plt.show()


	def chartfeatures(self,addpricecols=(),addquerycols=(),addfeatcols=(),ip=5558):
		import zmq
		import zlib
		import pickle as pkl
		context = zmq.Context()
		querylist=self.getquerylist()
		colors=['b','g','r','c','m','y','k','w']
		markers=['o','s','^','<','>','*','+']

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

		if addquerycols ==None:
			addquerycols=querylist

		querycols=[]
		for i,qry in enumerate(addquerycols):
			if qry in self.df.columns:
				querycols.append( {'colname':qry,'plotargs':(colors[i],),'plotkwargs':{'label':qry,'alpha':0.5,'marker':markers[i],'markerfacecolor':None,'markersize':15-i,'linestyle':''}} )
						
		
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

		msg={'pricecols':pricecols,'querycols':querycols,'featcols':featcols,'df':self.df.round(decimals=3)}
		p=pkl.dumps(msg)
		z=zlib.compress(p)

		socket.send(z)

		#  Get the reply.
		message = socket.recv()
		print message
		socket.close()
