import cloudpickle as cldpkl
from dill.source import getsource
from datascience import models as dtscmd

import h5py
import functools
import pandas as pd
import logging
import pdb
import numpy as np
import json

logger = logging.getLogger('datascience')

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




def GetTransformerList(dataid):
	data=dtscmd.Data.objects.get( id=dataid) 
	Transformers=[]
	while data.TransfomerFunc is not None:
		Transformers.append(data.TransfomerFunc.id)
		data=dtscmd.Data.objects.get( id=data.ParentData.id) 

	Transformers=list(reversed(Transformers))
	return tuple(Transformers)

def ApplyTransformerList(Xbase,Meta,TransFList):
	for funcid in TransFList: 
		Func=dtscmd.ComputeFunc.objects.filter(id=funcid).last()
		if Func.Group=='BaseDataSet':
			pass
		elif Func.Group=='Transformer':
			Xbase,Meta=Func.getfunc()(Xbase,None,Meta)

	return Xbase,Meta

def GetTransformedData(Xbase,Meta,dataid):
	Transformers=GetTransformerList(dataid)
	return ApplyTransformerList(Xbase,Meta,Transformers)





	