from __future__ import division
from celery import shared_task
import stockapp.models as stkmd

import datascience.models as dtscmd
import datascience.libs as dtsclibs
import datascience.ML.MLmodels as MLmd

import time
import pandas as pd
from celery.exceptions import TimeoutError 
import logging
logger = logging.getLogger('debug')


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
		print cnt,len(M),len(result)
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


## Create Raw Stock Datasets ##################

@shared_task
def CreateStockData_ShardsBySymbol(T0TF_dict_X,T0TF_dict_Y,Symbol,dataId):
	T0TFSymbol_dict_X=[]
	for pp in T0TF_dict_X:
		pp['Symbol']=Symbol
		T0TFSymbol_dict_X.append(pp)

	T0TFSymbol_dict_Y=[]
	for pp in T0TF_dict_Y:
		pp['Symbol']=Symbol
		T0TFSymbol_dict_Y.append(pp)

	return dtsclibs.CreateStockData_ShardsBySymbol(T0TFSymbol_dict_X,T0TFSymbol_dict_Y,dataId)

@shared_task
def CreateStockData_1(T0TF_dict_X,T0TF_dict_Y,dataId,Symbols):
	if Symbols is None:
		Symbols=stkmd.Stockmeta.objects.all().values_list('Symbol',flat=True)
	
	for Symbol in Symbols:
		CreateStockData_ShardsBySymbol.delay(T0TF_dict_X,T0TF_dict_Y,Symbol,dataId)

@shared_task
def CreateStockData_2(window,window_fut,dataId,Symbols):
	if Symbols is None:
		Symbols=stkmd.Stockmeta.objects.all().values_list('Symbol',flat=True)
	
	T0TF_dict_X=map(lambda x: { 'T0':(x.date()-pd.DateOffset(window)).date(),'TF' :x.date(),'window':window },
			pd.date_range(start=pd.datetime(2010,1,1),end=pd.datetime.today(),freq='W-MON') )

	T0TF_dict_Y=map(lambda x: { 'T0':x.date(), 'TF' : (x.date()+pd.DateOffset(window_fut)).date(),'window':window_fut },
			pd.date_range(start=pd.datetime(2010,1,1),end=pd.datetime.today(),freq='W-MON') )
	
	# pdb.set_trace()

	for Symbol in Symbols:
		print "Working on Symbol ", Symbol
		CreateStockData_ShardsBySymbol.delay(T0TF_dict_X,T0TF_dict_Y,Symbol,dataId)



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



def train_valid_split(shard0Id,traindataId,validdataId,N):
	from sklearn.model_selection import train_test_split
	shard0=dtscmd.DataShard.objects.get(id=shard0Id)

	X,Y,Meta=shard0.getdata()
	X_train, X_test, y_train, y_test = train_test_split(X, Y, test_size=0.33, random_state=N)

	if traindataId is not None:
		shardt=dtscmd.DataShard(Data__id=traindataId)
		shardt.save()
		shardt.savedata(X=X_train,Y=y_train,Meta=Meta)

	if validdataId is not None:
		shardv=dtscmd.DataShard(Data__id=validdataId)
		shardv.save()
		shardv.savedata(X=X_test,Y=y_test,Meta=Meta)

### Do ML #######################

@shared_task
def TrainModel(modelid):
	"""
	Train a specific model with model id as modelid
	"""
	model=dtscmd.MLmodels.objects.filter(id=modelid)
	ModelCLass=MLmd.ModelFactory(model)

	MCL=ModelCLass(model)
	MCL.loadmodel()
	MCL.loaddata()
	MCL.train()
	MCL.Run_validation_all()
	MCL.savemodel()


@shared_task
def TrainProject(Projectid):
	"""
	Train all models of a Project with id as Projectid
	"""
	MLmodels_ids=dtscmd.MLmodels.objects.filter(Project__id=Projectid,Status='UnTrained').values_list('id',flat=True)
	for modelid in MLmodels_ids:
		TrainModel(modelid)


#	Model Validation
@shared_task
def ValidateModeldata(modelid,validationdataid):
	"""
	Run Validation on validationdata with id validationdataid using modelid
	"""
	model=dtscmd.MLmodels.objects.filter(id=modelid)
	ModelCLass=MLmd.ModelFactory(model)

	MCL=ModelCLass(model)
	MCL.loadmodel()
	MCL.loaddata()
	MCL.Run_validation_id(validationdataid)
	MCL.savemodel()

# TODO: Write help
@shared_task
def ValidateModel(modelid):
	"""
	Run Validation for modelid on all validation data.
	"""
	model=dtscmd.MLmodels.objects.filter(id=modelid)
	ModelCLass=MLmd.ModelFactory(model)

	MCL=ModelCLass(model)
	MCL.loadmodel()
	MCL.loaddata()

	for validationdataid in MCL.validation_datasets.values_list('id',flat=True):
		ValidateModeldata(modelid,validationdataid)



@shared_task
def ValidateProject(Projectid):
	"""
	Run validation for the whole project
	"""
	MLmodels_ids=dtscmd.MLmodels.objects.filter(Project__id=Projectid,Status='Trained').values_list('id',flat=True)
	for modelid in MLmodels_ids:
		ValidateModel(modelid)
