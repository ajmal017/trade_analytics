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
		
		

		projectid,traindataId=dtsclibs.register_dataset(ParentDataId=DataId,Datatype='Train',tag=str(data.tag)+'_train_'+str(split) , DeleteShards=True)
		projectid,validdataId=dtsclibs.register_dataset(ParentDataId=DataId,Datatype='Validation',tag=str(data.tag)+'_valid_'+str(split) , DeleteShards=True)
		s=time.time()
		N=int( (s-int(s))* 10000+split )

		# for shard in dtscmd.DataShard.objects.filter(Data=data) :
		dtsctks.train_valid_split.delay(traindataId,validdataId,N)

			
	# create more validation sets
	for split in range(5,10):
		
		projectid,validdataId=dtsclibs.register_dataset(ParentDataId=DataId,Datatype='Validation',tag=str(data.tag)+'_valid_'+str(split), DeleteShards=True )
		s=time.time()
		N=int( (s-int(s))* 10000+split )

		dtsctks.train_valid_split.delay(None,validdataId,N)
