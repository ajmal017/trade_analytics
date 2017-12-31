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


def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""

    if isinstance(obj, (datetime.datetime, datetime.date)):
        return obj.strftime("%Y-%m-%d")
    raise TypeError ("Type %s not serializable" % type(obj))
    
def saveas_h5(filepath,**kwargs):
    h5f = h5py.File(filepath, 'w')
    for key,value in kwargs.items():
        if isinstance(value,(dict,list)):
            string_dt = h5py.special_dtype(vlen=str)
            h5f.create_dataset(key, data=np.array([pkl.dumps(value)]), dtype=string_dt)
        else:
            h5f.create_dataset(key, data=value,compression="gzip")
    h5f.close()

def append_h5(filepath,**kwargs):
    h5f = h5py.File(filepath, 'w')
    for key,value in kwargs.items():
        if isinstance(value,(dict,list)):
            string_dt = h5py.special_dtype(vlen=str)
            h5f.create_dataset(key, data=np.array([pkl.dumps(value)]), dtype=string_dt)
        else:
            h5f.create_dataset(key, data=value,compression="gzip")
    h5f.close()

def load_h5(filepath,keys):
	data={}
	h5f = h5py.File(filepath, 'r')
	for ky in keys:
		data[ky] = h5f[ky][:]
		if len(data[ky])==1 and isinstance(data[ky][0],basestring):
			data[ky]=pkl.loads(data[ky][0])
		# Meta = json.loads(h5f['Meta'][:][0])
	h5f.close() 

	return data

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
		data=dtscmd.Data(TransfomerFunc=TransfomerFunc,Project=parentdata.project,GroupName=GroupName,tag=tag,Datatype=Datatype,Dataformat=data_format,Modeltype=Modeltype,ouput_type=ouput_type)
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






	