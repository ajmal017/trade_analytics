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
		return dataset

	@classmethod
	def make_dataset(cls,X,Y,Meta):
		dataset=cls()
		dataset.X=X
		dataset.Y=Y
		dataset.Meta=Meta

		return dataset

	@classmethod
	def make_from_function(cls,Func,args,kwargs):
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


	def get_single_df(self):
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



# class FlatDataset(_Dataset):


def register_project(project_Name,project_Info):
	if dtscmd.Project.objects.filter(Name=project_Name).exists()==True:
		print "Project ",project_Name, " already exists"
		project=dtscmd.Project.objects.get(Name=project_Name)

	else:
		project=dtscmd.Project(Name=project_Name,Info=project_Info)
		project.save()
	project.initialize()

	return project


def register_dataset_base(project,TransfomerFunc,Modeltype,ouput_type,DataInfo,GroupName,tag,data_format='h5',DeleteShards_ifexists=False ):
	"""
	TransfomerFunc is the function used to create the base dataset
	"""
	Datatype='Base'
	if dtscmd.Data.objects.filter(Project=project,GroupName=GroupName,tag=tag,Datatype=Datatype,Dataformat=data_format,Modeltype=Modeltype,ouput_type=ouput_type).exists():
		data=dtscmd.Data.objects.get(Project=project,GroupName=GroupName,tag=tag,Datatype=Datatype,Dataformat=data_format,Modeltype=Modeltype,ouput_type=ouput_type)
		data.TransfomerFunc=TransfomerFunc
		data.initialize()

	else:
		data=dtscmd.Data(Project=project,TransfomerFunc=TransfomerFunc,DataInfo=DataInfo,GroupName=GroupName,tag=tag,Datatype=Datatype,Dataformat=data_format,Modeltype=Modeltype,ouput_type=ouput_type)
		data.save()
		data.initialize()

	if DeleteShards_ifexists==True:
		dtscmd.DataShard.objects.filter(Data=data).delete()

	return data

def register_dataset_transformed_from_parent(ParentData,TransfomerFunc,GroupName=None,tag=None,Datatype=None,Modeltype=None,ouput_type=None,DeleteShards_ifexists=False ):
	parentdata=dtscmd.Data.objects.get(ParentData=ParentData)

	ouput_type=parentdata.ouput_type if ouput_type is None else ouput_type
	GroupName=parentdata.GroupName if GroupName is None else GroupName
	tag=parentdata.tag if tag is None else tag
	Datatype=parentdata.Datatype if Datatype is None else Datatype
	Modeltype=parentdata.Modeltype if Modeltype is None else Modeltype

	if dtscmd.Data.objects.filter(Project=parentdata.project,GroupName=GroupName,tag=tag,Datatype=Datatype,Dataformat=data_format,Modeltype=Modeltype,ouput_type=ouput_type).exists():
		data=dtscmd.Data.objects.get(Project=parentdata.project,GroupName=GroupName,tag=tag,Datatype=Datatype,Dataformat=data_format,Modeltype=Modeltype,ouput_type=ouput_type)
		data.TransfomerFunc=TransfomerFunc
		data.save()
		data.initialize()

	else:
		data=dtscmd.Data(TransfomerFunc=TransfomerFuncProject=parentdata.project,GroupName=GroupName,tag=tag,Datatype=Datatype,Dataformat=data_format,Modeltype=Modeltype,ouput_type=ouput_type)
		data.save()
		data.initialize()

	if DeleteShards_ifexists==True:
		dtscmd.DataShard.objects.filter(Data=data).delete()

	return data


def register_compute_function(func,Group,defaultargs={}):
	PklCode=cldpkl.dumps(func)
	SrcCode=getsource(func)
	Info={}
	Info['doc']=func.__doc__
	Info['defaultargs']=defaultargs

	cf=dtscmd.ComputeFunc(Name=func.__name__,Group=self.Group,PklCode=PklCode,Info=Info,SrcCode=SrcCode)
	cf.save()
	return cf






	