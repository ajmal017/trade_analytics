




import json
import pandas as pd
import featureapp.models as ftmd

class registerfeature(object):
	
	def __init__(self,filename=None,category=None,returntype=None,query=True,operators=None,null=False,cache=True):
		
		self.category=category
		self.query=query
		self.returntype=returntype
		self.operators=operators
		self.null=null
		self.filename=filename


		self.usecache=cache
		self.cache={}
		self.registry={}
	def __call__(self,func):
		
		self.name=func.__name__
		self.doc=func.__doc__
		
		# if self.name in self.registry:
		# 	raise KeyError("label already there, please rename "+self.name)


		if ftmd.FeaturesMeta.objects.filter(Featurelabel=self.name).exists():
			featmeta=ftmd.FeaturesMeta.objects.get(Featurelabel=self.name)
			featmeta.Featuredescription=self.doc
			featmeta.Category=self.category
			featmeta.returntype=self.returntype.__name__
			featmeta.operators=self.operators
			featmeta.Query=self.query
			featmeta.Userfilename=self.filename
			featmeta.save()

		else:
			featmeta=ftmd.FeaturesMeta(Featurelabel=self.name,Featuredescription=self.doc,
									Category=self.category,returntype=self.returntype.__name__,
									operators=self.operators,Query=self.query,Userfilename=self.filename)
			featmeta.save()


		self.registry[self.name]={'doc':self.doc}
		
		def func2(*args,**kwargs):
			key=json.dumps([args[1:],kwargs])
			if self.usecache:
				if key in self.cache:
					print "return cached result"
					return self.cache[key]
				else:
					print "computing and saving result"
					self.cache[key]=func(*args,**kwargs)
					return self.cache[key]
			else:
				return func(*args,**kwargs)
		func2.isfeature=True
		
		return func2

class featuremodel(object):
	def __init__(self,Symbol,Trange):
		self.features={}
		self.Symbol=Symbol
		self.Trange=Trange

	def __getitem__(self,feat):
		return getattr(self,feat)

	def getfeaturelist(self):
		return [x for x, y in self.__dict__.items() if hasattr(x,'isfeature')]

	def computeall(self):
		featurelist=self.getfeaturelist()	
		self.ComputedFeatures={}
		for ft in featurelist:
			self.ComputedFeatures[ft]={}
			for T in self.Trange:
				self.ComputedFeatures[ft][T]=self[ft](T)

		return self.ComputedFeatures
	def saveall(self):

		for T in self.Trange:
			if ftmd.FeaturesData.objects.filter(Symbol=self.Symbol,T=T).exists():
				featdata=ftmd.FeaturesData.objects.get(Symbol=self.Symbol,T=T)
			else:
				featdata=ftmd.FeaturesData(Symbol=self.Symbol,T=T)
				featdata.save()

			for ft in self.ComputedFeatures.keys():
				v=self.ComputedFeatures[ft][T]
				featdata.Featuredata[ft]=v

			featdata.save()