from __future__ import division
import datascience.models as dtscmd
import datascience.libs as dtsclibs
import datascience.tasks as dtsctks
import numpy as np
import pandas as pd
import time
import threading








def get_train_test_from_RawProcessed(DataId):
	"""
	- Make 5 sets of training and test data 70:30 splits
	- Make additional 20  30% slits

	- Make 5 sets of Balanced training and test data 70:30 splits
	- Make additional 20  30% slits

	- Start a thread, and monitor the size of the numpy array and then make a separate shard
	"""
	data=dtscmd.Data.objects.get(id=DataId)

	

	for split in range(5):
		s=time.time()
		s=(s-int(s))* 10000+split
		N=np.random.seed(s)

		projectid,traindataId=dtsclibs.register_dataset(ParentdataId=DataId,Datatype='Train',tag=str(data.tag)+'_train_'+str(split) )
		projectid,validdataId=dtsclibs.register_dataset(ParentdataId=DataId,Datatype='Validation',tag=str(data.tag)+'_valid_'+str(split) )

		for shard in dtscmd.DataShard.objects.filter(Data=data) :
			dtsctks.train_valid_split(shard.id,traindataId,validdataId,N)

			
	# create more validation sets
	for split in range(5,10):
		s=time.time()
		s=(s-int(s))* 10000+split
		N=np.random.seed(s)

		projectid,validdataId=dtsclibs.register_dataset(ParentdataId=DataId,Datatype='Validation',tag=str(data.tag)+'_valid_'+str(split) )
		
		for shard in dtscmd.DataShard.objects.filter(Data=data) :
			dtsctks.train_valid_split(shard.id,None,validdataId,N)
