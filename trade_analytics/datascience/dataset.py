import pandas as pd
import numpy as np
import datascience.models as dtscmd

"""
Module for Datasets
- Dataset holds X,Y,Meta
- Can be a single file, single in memory X,Y
- Can be shards
- Has to support :
	- run a function that runs on a full column
	- run a function that runs on all columns simultaneously
	- run a function on set of samples

- apply a pipeline of functions that modify the sample
"""

class Dataset_shards(object):
	@classmethod
	def make_from_dataID(cls,data):
		if isinstance(data,dtscmd.Data):
			dataID=data.id
		elif type(data)==int:
			dataID=data
		else:
			raise Exception("Need Data instance or dataID")


		DS=cls()
		DS.dataID=dataID
		DS.data=dtscmd.Data.objects.get(id=dataID)
		DS.shards=dtscmd.DataShard.objects.filter(Data__id=dataID).values_list('id',flat=True)
		return DS

	@classmethod
	def make_from_TransfomerFunc(cls,TransfomerFunc,project,Modeltype,ouput_type,DataInfo,GroupName,tag,data_format='h5',DeleteShards_ifexists=False ,shardsize=100):
		data=register_dataset_base(project,TransfomerFunc,Modeltype,ouput_type,DataInfo,GroupName,tag,data_format='h5',DeleteShards_ifexists=False )
		Func=TransfomerFunc.getfunc()
		for X,Y,Meta in Func():
			
	def apply_pipeline(self,pipeline,axis=0):
		pass
