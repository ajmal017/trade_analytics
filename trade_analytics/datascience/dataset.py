import cloudpickle as cldpkl
from dill.source import getsource
from datascience import models as dtscmd
import copy
import h5py
import functools
import pandas as pd
import logging
import pdb
import numpy as np
import json

logger = logging.getLogger('datascience')


def shardTransformer(shardId_from,dataId_to):
	"""
	Transform shardId0 to a new shard under dataId1
	using the transformner function saved in dataId1
	"""
	data1=dtscmd.Data.objects.get(id=dataId_to)
	
	
	shard0=dtscmd.DataShard.objects.get(id=shardId_from)
	X,Y,Meta=shard0.getdata()
	
	func=data1.TransfomerFunc.getfunc()	

	X1,Y1,Meta1=func(X,Y,Meta)

	shard1=dtscmd.DataShard(Data=data1)
	shard1.save()
	shard1.savedata(X=X1,Y=Y1,Meta=Meta1)
	print "done transforming shardId0 ",shardId0," to new shardid = ",shard1.id


def combineshards(dataID,filename):
	data=dtscmd.Data.objects.get(id=dataID)
	shards=dtscmd.DataShard.objects.filter(Data=data)
	Xm=None
	Ym=None
	Metam=None
	for shard in shards:
		X,Y,Meta=shard.getdata()
		if Xm is None:
			Xm=X
			Ym=Y
			Metam=Meta
		else:
			Xm=np.vstack((Xm,X))
			Ym=np.vstack((Ym,Y))




def Get_pipeline_transform(dataid):
	data=dtscmd.Data.objects.get( id=dataid) 
	pipeline=[]
	while data.TransfomerFunc is not None:
		Transformers.append(data.TransfomerFunc.id)
		data=dtscmd.Data.objects.get( id=data.ParentData.id) 

	Transformers=list(reversed(Transformers))
	return tuple(Transformers)








class _Dataset(object):
	def __init__():
		self.data=None
		self.X=None
		self.Y=None
		self.Meta=None

	def setdataID(dataID):
		self.data=dtscmd.Data.objects.get(id=dataID)
		return self

	@classmethod
	def make_from_dataID(cls,dataID):
		dataset=cls()
		dataset.data=dtscmd.Data.objects.get(id=dataID)
		dataset.shards=dtscmd.DataShard.objects.filter(Data=dataset.data)

		return dataset

	@classmethod
	def make_from_XYMeta(cls,X,Y,Meta):
		dataset=cls()
		dataset.X=X
		dataset.Y=Y
		dataset.Meta=Meta

		return dataset

	@classmethod
	def make_from_function(cls,Func,args,kwargs):
		"""
		Func(*args,**kwargs) has to return X,Y,Meta	
		"""
		dataset=cls()
		dataset.X,dataset.Y,dataset.Meta= Func(*args,**kwargs)	
		return dataset	


	def pipeline_transform(self,pipelinefuns=[]):
		"""
		assuming the dataset has already been created and is in X,Y,Meta forms

		"""
		Xt=self.X.copy()
		Yt=self.Y.copy()
		Metat=copy.deepcopy( self.Meta )

		for func,kwargs in pipelinefuns:
			Xt,Yt,Metat=func(Xt,Yt,Metat,**kwargs)

		return (Xt,Yt,Metat)

	def apply_transform(self,Func,kwargs={},inplace=False):
		"""
		Xt,Yt,Metat=Func(X,Y,Meta,**kwargs)
		"""
		if inplace:
			self.X,self.Y,self.Meta=Func(self.X,self.Y,self.Meta,**kwargs)
		else:
			return Func(self.X.copy(),self.Y.copy(),copy.deepcopy(self.Meta),**kwargs) 

	def get_combined_df(self):
		shards=dtscmd.DataShard.objects.filter(Data=self.data)
		Xm=None
		Ym=None
		Metam=None
		for shard in shards:
			X,Y,Meta=shard.getdata()
			if Xm is None:
				Xm=X
				Ym=Y
				Metam=Meta
			else:
				Xm=np.vstack((Xm,X))
				Ym=np.vstack((Ym,Y))
				Metam.update(Metam)

		return (Xm,Ym,Metam)



	def saveas_h5(self):
		data=dtscmd.Data.objects.get(id=dataID)
		shard=dtscmd.DataShard(Data=data)
		shard.save()

		name,path=shard.shardpath()

		h5f = h5py.File(path, 'w')
		string_dt = h5py.special_dtype(vlen=str)
		h5f.create_dataset('Meta', data=np.array([json.dumps(self.Meta)]), dtype=string_dt)
		h5f.create_dataset('X', data=self.X,compression="gzip")
		h5f.create_dataset('Y', data=self.Y,compression="gzip")
		h5f.close() 


