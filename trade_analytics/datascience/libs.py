import cloudpickle as cldpkl
from dill.source import getsource
from datascience import models as dtscmd
import dataapp.libs as dtalibs

import functools
import pandas as pd
from utility import maintenance as mnt
import logging
import pdb

logger = logging.getLogger('datascience')


def register_dataset(project_Name=None,project_Info=None,DataInfo=None,
					Datatype=None,GroupName=None,tag=None,data_format=None,Modeltype=None,
					TransformedFromDataId=None,TransFuncId=None,use_project_ifexists=True ):

	# project_Name="PredictReturn_TSLA", 
	# use_project_ifexists=True,
	# project_Info={'description': "Testing the algorithms on TSLA to predict next 10 day return \n"+
	#                              "Data taken on every Friday"},
	# Datatype='RawProcessed',
	# GroupName="Fullstocktime",
	# tag="1",
	# data_format='npz',
	# Modeltype='Regression',

	# if you want to create a data set from another data make sure:
	# - The new dataset has no shards
	# - The old dataset that is being transformed has some shards	
	if (not TransformedFromDataId and TransFuncId) or (TransformedFromDataId and not TransFuncId):
		print "the pair (TransformedFromDataId,TransFuncId) both have to have a value or both None simultaneously"
		return False

	if TransformedFromDataId and TransFuncId:
		# check if function exists
		if dtscmd.ComputeFunc.objects.filter(id=TransFuncId).exists()==False:
			print "Transformer function does not exists"
			return False
			
		# first get data0, if some shards exists for it
		if dtscmd.DataShard.objects.filter(Data__id=TransformedFromDataId).exists():
			data0=dtscmd.Data.objects.get(id=TransformedFromDataId)
		else:
			print "TransformedFromDataId = ",TransformedFromDataId, "has no data"
			return False

		

		if not project_Name:
			project_Name=data0.Project.Name
		if not project_Info:	
			project_Info=data0.Project.Name
		if not Datatype:	
			Datatype=data0.Datatype
		if not GroupName:	
			GroupName=data0.GroupName
		if not tag:	
			tag=data0.tag
		if not data_format:	
			data_format=data0.Dataformat
		if not Modeltype:	
			Modeltype=data0.Modeltype
		if not data_format:	
			data_format=data0.Dataformat



	

	if dtscmd.Project.objects.filter(Name=project_Name).exists()==True:
		print "Project ",project_Name, " already exists"
		project=dtscmd.Project.objects.get(Name=project_Name)

		if use_project_ifexists:
			pass	
		else:
			print "project already exists"
			# return None

	else:
		project=dtscmd.Project(Name=project_Name,Info=project_Info)
		project.save()

	project.initialize()

	if dtscmd.Data.objects.filter(Project=project,GroupName=GroupName,tag=tag,Datatype=Datatype,Dataformat=data_format,Modeltype=Modeltype).exists():
		data=dtscmd.Data.objects.get(Project=project,GroupName=GroupName,tag=tag,Datatype=Datatype,Dataformat=data_format,Modeltype=Modeltype)
		print "The dataset already exists"
		if DataInfo is not None:
			data.Info=DataInfo
			print "updating data info"
		data.save()

		data.initialize()

	else:
		data=dtscmd.Data(Project=project,Info=DataInfo,GroupName=GroupName,tag=tag,Datatype=Datatype,Dataformat=data_format,Modeltype=Modeltype)
		data.save()
		data.initialize()


	if TransformedFromDataId and TransFuncId:
		if dtscmd.DataShard.objects.filter(Data=data).exists():
			print "the new dataset already has shard, trasnformation not possible, delete them first and run again"
			return False

		if data.id==data0.id:
			print "Looks like you might over write the data, fail safe create a new dataset"
			return False
		
		data.ParentData=data0;
		data.TransfomerFunc=dtscmd.ComputeFunc.objects.get(id=TransFuncId)
		data.save()
		data.initialize()
		print "saving transfoermer function to this dataset"
	

	print ("project id","data id")," : ",(project.id,data.id)
	return project.id,data.id


# @register_func(overwrite_if_exists=False)
class register_compfunc(object):
	def __init__(self,Group='',RequiredGroup=[],RequiredImports=[],overwrite_if_exists=False):
		self.Group=Group
		self.RequiredImports=RequiredImports
		self.RequiredGroup=RequiredGroup
		self.overwrite_if_exists=overwrite_if_exists


   	def __call__(self,func):
   		func.id=None

   		if self.overwrite_if_exists:
   			if dtscmd.ComputeFunc.objects.filter(Name=func.__name__,Group=self.Group).exists():
   				print "over writing previous function"
   				cf=dtscmd.ComputeFunc.objects.get(Name=func.__name__,Group=self.Group)
   			else:
   				print "creating new func"
   				cf=dtscmd.ComputeFunc(Name=func.__name__,Group=self.Group)
   		else:
   			print "creating new func"
			cf=dtscmd.ComputeFunc(Name=func.__name__,Group=self.Group)

   		cf.Info['doc']=func.__doc__
   		cf.PklCode=cldpkl.dumps(func)
   		cf.RequiredGroup['Group']=self.RequiredGroup
   		cf.RequiredImports['import']=self.RequiredImports

   		try:
   			cf.SrcCode=getsource(func)
   		except:
   			cf.SrcCode=''

   		cf.save()
   		print "saving function : ", cf.Name

   		func.id=cf.id
 		print "function id = ",cf.id
   		return func



@mnt.logperf('datascience',printit=True)
def CreateStockData_ShardsBySymbol(T0TFSymbol_dict_X,T0TFSymbol_dict_Y,dataId):
	"""
	T0TFSymbol_dict= [{'T0':,'Tf':,'Symbol':},{}]
	"""
	dfinstants_X=pd.DataFrame(T0TFSymbol_dict_X)
	dfinstants_Y=pd.DataFrame(T0TFSymbol_dict_Y)

	BatchData=dtalibs.Getbatchdata([dfinstants_X,dfinstants_Y],padding=['OnTop','FromBottom'])

	X,MetaX=BatchData[0]
	Y,MetaY=BatchData[1]

	
	
	data=dtscmd.Data.objects.get(id=dataId)	
	shard=dtscmd.DataShard(Data=data)
	shard.save()
	print "starting to save"
	shard.savedata(X=X,Y=Y,Meta={'MetaX':MetaX,'MetaY':MetaY})



def shardTransformer(shardId0,dataId1):
	"""
	Transform shardId0 to a new shard under dataId1
	using the transformner function saved in dataId1
	"""
	data1=dtscmd.Data.objects.get(id=dataId1)
	
	
	shard0=dtscmd.DataShard.objects.get(id=shardId0)
	X,Y,Meta=shard0.getdata()
	
	data1=dtscmd.Data.objects.get(id=dataId1)
	func=data1.TransfomerFunc.getfunc()	

	X1,Y1,Meta1=func(X,Y,Meta)

	shard1=dtscmd.DataShard(Data=data1)
	shard1.save()
	shard1.savedata(X=X1,Y=Y1,Meta=Meta1)
	print "done transforming shardId0 ",shardId0," to new shardid = ",shard1.id


