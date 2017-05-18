




import json
import pandas as pd
import numpy as np
import featureapp.models as ftmd
import stockapp.models as stkmd
import dataapp.models as dtamd
import dataapp.libs as dtalibs

class registerfeature(object):
	
	def __init__(self,filename=None,category=None,returntype=None,query=True,operators=None,null=False,cache=False):
		
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
			print "Updated feature ",featmeta

		else:
			featmeta=ftmd.FeaturesMeta(Featurelabel=self.name,Featuredescription=self.doc,
									Category=self.category,Returntype=self.returntype.__name__,
									operators=self.operators,Query=self.query,Userfilename=self.filename)
			featmeta.save()
			print "Saving feature ",featmeta

	def __call__(self,func):
		
		self.name=func.__name__
		self.doc=func.__doc__
		
		# if self.name in self.registry:
		# 	raise KeyError("label already there, please rename "+self.name)
		
		self.recordfeature()

		self.registry[self.name]={'doc':self.doc}
		
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
		dbfeatures=list( ftmd.FeaturesMeta.objects.filter(Userfilename=filename).values_list('Featurelabel',flat=True) )
		for ft in dbfeatures:
			if ft not in featurelist:
				print ft," is not there, so deleting it"
				ftmd.FeaturesMeta.objects.filter(Featurelabel=ft).delete()


	def computeall(self,skipdone=True):
		featurelist=self.getfeaturelist()	
		# print featurelist
		self.ComputedFeatures={}
		for ft in featurelist:
			self.ComputedFeatures[ft]={}
			for T in self.Trange:
				self.ComputedFeatures[ft][T]=self.getfeaturefunc(ft)(T)

		print "Done compute"

		return self.ComputedFeatures
	

		

	def saveall(self):

		for T in self.Trange:
			if ftmd.FeaturesData.objects.filter(Symbol=self.stk,T=T).exists():
				featdata=ftmd.FeaturesData.objects.get(Symbol=self.stk,T=T)
			else:
				featdata=ftmd.FeaturesData(Symbol=self.stk,T=T)
				featdata.save()

			for ft in self.ComputedFeatures.keys():
				v=self.ComputedFeatures[ft][T]
				try:
					if pd.isnull(v):
						featdata.Featuredata[ft]=None
					else:
						featdata.Featuredata[ft]=v
				except:
					print type(v)

			featdata.save()
		print "Done save"

	def chartfeatures(self,df,cols,ip=5558):
		import zmq
		import zlib
		import pickle as pkl

		context = zmq.Context()

		#  Socket to talk to server
		print("Connecting to charting server")
		socket = context.socket(zmq.REQ)
		socket.connect("tcp://localhost:%s" % ip)

		msg={'featcols':cols,'df':df.round(decimals=3)}
		p=pkl.dumps(msg)
		z=zlib.compress(p)

		socket.send(z)

		#  Get the reply.
		message = socket.recv()
		print message
		socket.close()
