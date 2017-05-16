




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
			key=json.dumps([args[1:],kwargs])
			if self.usecache:
				if key in self.cache:
					return self.cache[key]
				else:
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