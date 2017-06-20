from __future__ import division
import datascience.MLmodels as MLmd
import datascience.models as dtascmd
import numpy as np
import pandas as pd
import time
import threading
from sklearn.model_selection import train_test_split


def default_shardgroupby(df,maxsize=100):
	size=df.memory_usage(index=True).sum()/1000000
	if size<=maxsize:
		yield (df,'full')

def Compute_ShardMisc(Dataid,shardname):
	Data=dtascmd.Data.objects.get(id=Dataid)
	data=Data.getshard_dict(shardname)
	ShardInfo=Data.ShardInfo['shardname']
	
	ShardInfo['Y_shape']=data['Y'].shape
	ShardInfo['X_shape']=data['X'].shape
	ShardInfo['N_samples']=data['X'].shape[0]

	if Data.Modeltype=='Classification':
		ShardInfo['classes']=np.unique(data['Y'][:,0])
		ShardInfo['samples_per_class']={}
		for cl in ShardInfo['classes']:
			Y=data['Y']
			ShardInfo['samples_per_class'][cl]=Y[Y==cl].shape[0]
		
	return ShardInfo

def Compute_DataMisc(ShardsInfo):
	Y_shape=[]
	X_shape=[]
	N_samples=[]
	for shardname in ShardsInfo.keys():
		Y_shape.append( ShardsInfo[shardname]['Y_shape'] )
 		X_shape.append( ShardsInfo[shardname]['X_shape'] )
 		N_samples.append( ShardsInfo[shardname]['N_samples'] )



def get_train_test_from_RawProcessed(InputData,shardgroupby=default_shardgroupby):
	"""
	- Make 5 sets of training and test data 70:30 splits 
	- Make additional 20  30% slits 

	- Make 5 sets of Balanced training and test data 70:30 splits 
	- Make additional 20  30% slits 
	
	- Start a thread, and monitor the size of the numpy array and then make a separate shard
	"""
	if InputData.Datatype!='RawProcessed':
		print "Data has to have Datatype as  RawProcessed"
		return False


	for split in range(5):
		s=time.time()
		s=(s-int(s))* 10000+split
		N=np.random.seed(s)

		TrainData= dtascmd.Data(Project=InputData.Project,ParentData=InputData,GroupName='BasicSplit',tag='Split_%s'%split,Modeltype=InputData.Modeltype,Datatype='Train',Dataformat='h5')
		TrainData.save()
		TrainData.initialize()

		ValidationData= dtascmd.Data(Project=InputData.Project,ParentData=InputData,GroupName='BasicSplit',tag='Split_%s'%split,Modeltype=InputData.Modeltype,Datatype='Validation',Dataformat='h5')
		ValidationData.save()
		ValidationData.initialize()

		for df in InputData.gen_readshard():
			  
			df_train, df_test, y_train, y_test = train_test_split(df, df.index, test_size=0.33, random_state=N)
			
			shardname,shardpath=TrainData.newshardpath()
			df_train.to_hdf(shardpath,'table')
			TrainData.ShardInfo[shardname]['#samples'] =len(df_train)

			shardname,shardpath=ValidationData.newshardpath()
			df_test.to_hdf(shardpath,'table')
			ValidationData.ShardInfo[shardname]['#samples'] =len(df_test)


	for split in range(5,25):
		s=time.time()
		s=(s-int(s))* 10000+split
		N=np.random.seed(s)

		ValidationData= dtascmd.Data(Project=InputData.Project,ParentData=InputData,GroupName='BasicSplit',tag='Split_%s'%split,Modeltype=InputData.Modeltype,Datatype='Validation',Dataformat='h5')
		ValidationData.save()
		ValidationData.initialize()

		for df in InputData.gen_readshard():
			  
			df_train, df_test, y_train, y_test = train_test_split(df, df.index, test_size=0.33, random_state=N)
			
			shardname,shardpath=ValidationData.newshardpath()
			df_test.to_hdf(shardpath,'table')
			ValidationData.ShardInfo[shardname]['#samples'] =len(df_test)
			

