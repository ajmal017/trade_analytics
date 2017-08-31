from __future__ import division
import stockapp.models as stkmd

import datascience.models as dtscmd
import datascience.libs as dtsclibs
import datascience.ML.MLmodels as MLmd
from django.conf import settings

import time
import pandas as pd
from utility import maintenance as mnt

import logging
logger = logging.getLogger('debug')



if settings.USE_REDIS:
	from django_rq import job as shared_task

elif settings.USE_CELERY:
	from celery import shared_task
	from celery.exceptions import TimeoutError
	from celery.signals import worker_process_init

	@worker_process_init.connect
	def fix_multiprocessing(**kwargs):
	    from multiprocessing import current_process
	    try:
	        current_process()._config
	    except AttributeError:
	        current_process()._config = {'semprefix': '/mp'}
	    print "fixed multiprocessing"
else:
	# use dummy task
	raise Exception('Unknown option for task distribution')



	


## Compute Function Mapper ####################
@shared_task
def applyfunc(Func_id,arg):
	"""
	arg is tuple of arguments
	"""
	Func=dtscmd.ComputeFunc.objects.filter(id=Func_id).last().getfunc()
	return Func(arg)



@shared_task
def Mapper_wait(Func_id,args):
	result=[]
	for i in range(len(args)):
		result.append( applyfunc.delay(Func_id,args[i]) )

	# result=group(result)
	time.sleep(1)
	# M=[v for v in result.collect()]
	M={}
	cnt=len(result)-1
	while 1:
		try:
			M[cnt]=result[cnt].get(timeout=2)
		except TimeoutError:
			pass

		cnt=cnt-1
		if cnt==-1:
			cnt=len(result)-1
		if len(M)==len(result):
			break
		# print cnt,len(M),len(result)
		# print cnt,len(M),len(result)

	return M

@shared_task
def Mapper_nowait(Func_id,args):
	result=[]
	for i in range(len(args)):
		result.append( applyfunc.delay(Func_id,args[i]) )
	return None

## wirk on shards ##############

@shared_task
def applyfunc2data(funcId,dataId,wait=False):
	"""
	apply a Computefunc to a data shard
	def func(shardId):
		...

	"""
	shardIds=dtscmd.DataShard.objects.filter(Data__id=dataId).values_list('id',flat=True)

	if wait==True:
		return Mapper_wait(funcId,shardIds)
	else:
		return Mapper_nowait(funcId,shardIds)



### Do DataSet transformers to new Datasets ########################

@shared_task
def shardTransformer(shard0Id,dataId1):
	return dtsclibs.shardTransformer(shard0Id,dataId1)

@shared_task
def Perform_TransformData(dataId1):
	data1=dtscmd.Data.objects.get(id=dataId1)
	data0=data1.ParentData
	# funcId=data1.TransfomerFunc.id
	shard0Ids=dtscmd.DataShard.objects.filter(Data=data0).values_list('id',flat=True)

	for shard0Id in shard0Ids:
		shardTransformer.delay(shard0Id,dataId1)


@shared_task
def train_valid_split(traindataId,validdataId,N):
	from sklearn.model_selection import train_test_split

	data0Id=dtscmd.Data.objects.get(id=validdataId).ParentData.id
	print "Working on ", data0Id, " --> ", traindataId," , ", validdataId

	for shard0 in dtscmd.DataShard.objects.filter(Data__id=data0Id) :

	# shard0=dtscmd.DataShard.objects.get(id=shard0Id)

		X,Y,Meta=shard0.getdata()
		# print X.shape
		if len(X.shape)==0:
			continue

		if X.shape[0]<5:
			continue

		X_train, X_test, y_train, y_test = train_test_split(X, Y, test_size=0.33, random_state=N)

		if traindataId is not None:
			traindata=dtscmd.Data.objects.get(id=traindataId)
			shardt=dtscmd.DataShard(Data=traindata)
			shardt.save()
			shardt.savedata(X=X_train,Y=y_train,Meta=Meta)

		if validdataId is not None:
			validdata=dtscmd.Data.objects.get(id=validdataId)
			shardv=dtscmd.DataShard(Data=validdata)
			shardv.save()
			shardv.savedata(X=X_test,Y=y_test,Meta=Meta)

### Do Training and Validation #######################
@mnt.logperf('datascience',printit=True)
def trainmodel_wrapper(modelid):
	model=dtscmd.MLmodels.objects.get(id=modelid)


	MCode=dtscmd.ModelCode.objects.get(Username=model.Userfilename)
	Mclass=MCode.importobject(model.Name)

	M=Mclass()
	M.loadmodel(model)
	M.loaddata()
	M.train()

@shared_task
def TrainModel(modelid):
	"""
	Train a specific model with model id as modelid
	"""
	trainmodel_wrapper(modelid)


@shared_task
def TrainProject(Projectid):
	"""
	Train all models of a Project with id as Projectid
	"""
	MLmodels_ids=dtscmd.MLmodels.objects.filter(Project__id=Projectid,Status='UnTrained').values_list('id',flat=True)
	for modelid in MLmodels_ids:
		TrainModel.delay(modelid)


#	Model Validation
@mnt.logperf('datascience',printit=True)
def validationmodel_wrapper(modelid,validationdataid):
	model=dtscmd.MLmodels.objects.get(id=modelid)


	MCode=dtscmd.ModelCode.objects.get(Username=model.Userfilename)
	Mclass=MCode.importobject(model.Name)

	M=Mclass()
	M.loadmodel(model)
	M.loaddata()
	M.Run_validation_id(validationdataid)
	
@shared_task
def ValidateModeldata(modelid,validationdataid):
	"""
	Run Validation on validationdata with id validationdataid using modelid
	"""
	validationmodel_wrapper(modelid,validationdataid)


# TODO: Write help
@shared_task
def ValidateModel(modelid):
	"""
	Run Validation for modelid on all validation data.
	"""
	model=dtscmd.MLmodels.objects.get(id=modelid)


	MCode=dtscmd.ModelCode.object.get(Username=model.Userfilename)
	Mclass=MCode.importobject(model.Name)

	M=Mclass()
	M.loadmodel(model)
	M.loaddata()

	for validationdataid in M.validation_datasets.values_list('id',flat=True):
		ValidateModeldata.delay(modelid,validationdataid)



@shared_task
def ValidateProject(Projectid):
	"""
	Run validation for the whole project
	"""
	MLmodels_ids=dtscmd.MLmodels.objects.filter(Project__id=Projectid,Status='Trained').values_list('id',flat=True)
	for modelid in MLmodels_ids:
		ValidateModel.delay(modelid)
