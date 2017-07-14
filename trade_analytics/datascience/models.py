from __future__ import unicode_literals
import os
from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.contrib.postgres.fields import ArrayField
from django.contrib.postgres.fields import JSONField

import pandas as pd
import numpy as np
import joblib

# Create your models here.

"""
Create Custom labels for the data
"""
class Label(models.Model):
	label=models.CharField(max_length=100)
	Symbol=models.CharField(max_length=100)
	T = models.DateField(null=True)
	window = models.IntegerField(null=True)
	User = models.ForeignKey(User,on_delete=models.CASCADE, blank = True, null = True)
	created_at = models.DateTimeField(auto_now_add=True,null=True)
	updated_at = models.DateTimeField(auto_now=True,null=True)


"""
#########################################################################
####################  Machine learning Structure ########################
#########################################################################

|- ComputeFunc: Serializable Functions used for parallelization

|- Project
	|- Data: Datasets stored as shards
	|- MLmodels: Each Dataset has a model associated
	|- MLmetrics: Each model and each validation set has a metric


"""


class ComputeFunc(models.Model):
	"""
	Load the imports
	Load all functions from a group
	"""
	Name=models.CharField(max_length=200)
	Group=models.CharField(max_length=200,null=True)
	RequiredImports=JSONField(default={})
	RequiredGroup=JSONField(default={})

	Info=JSONField(default={})
	PklCode=models.BinaryField()
	SrcCode=models.TextField()

	created_at = models.DateTimeField(auto_now_add=True,null=True)
	updated_at = models.DateTimeField(auto_now=True,null=True)

	def getfunc(self,getlatest=True):
		import cloudpickle as cldpkl
		return cldpkl.loads(self.PklCode)

class Project(models.Model):
	Name=models.CharField(max_length=200)
	Info=JSONField(default={})

	created_at = models.DateTimeField(auto_now_add=True,null=True)
	updated_at = models.DateTimeField(auto_now=True,null=True)
	def __str__(self):
		return self.Name

	def bigdatapath(self):
		return os.path.join(settings.BIGDATA_DIR,'datascience','Projects',self.Name)

	def projectpath(self):
		return os.path.join(settings.BASE_DIR,'datascience','Projects',self.Name)

	def initialize(self):
		# make the bigdata path, to store large data
		path=self.bigdatapath()
		if not os.path.isdir(path):
			os.makedirs(path)

		# save the
		path=self.projectpath()
		if not os.path.isdir(path):
			os.makedirs(path)


class Data(models.Model):
	"""
	In the description, please mention the way the data is to be read
	ProjectName--> Data --> Raw --> DataName --> files
	Datashards have infor such as shardname: sample_shape, #smaples, # samples in each class
	bigdata/datascience/Projects/$ProjectName/Data/$Datatype/$GroupName_$tag
	"""
	Project=models.ForeignKey(Project,on_delete=models.CASCADE)
	ParentData=models.ForeignKey('self',on_delete=models.CASCADE,null=True)

	GroupName=models.CharField(max_length=200)
	Info=JSONField(default={})

	# tags that are same, are kind of pairs
	tag=models.CharField(max_length=200)

	model_types=[('Classification','Classification'),('Regression','Regression')]
	Modeltype=models.CharField(choices=model_types,max_length=20)

	data_choices=[('Raw','Raw'),('RawProcessed','RawProcessed'),('Train','Train'),('Validation','Validation'),('Test','Test')]
	Datatype=models.CharField(choices=data_choices,max_length=20)

	data_format=[('npz','npz'),('h5','h5'),('pkl','pkl'),('joblib','joblib'),('json','json')]
	Dataformat=models.CharField(choices=data_format,max_length=30)


	# Binary is always 0/1, classes are labelled by integers 0,1,2,...
	# binary 1 is the important class i.e. like fraud==1 , nofraud==0
	ouput_choices=[('binary','binary'),('multiclass','multiclass'),('continuous','continuous')]
	ouput_type=models.CharField(choices=data_format,max_length=30)

	# Datashards=JSONField(default={})

	created_at = models.DateTimeField(auto_now_add=True,null=True)
	updated_at = models.DateTimeField(auto_now=True,null=True)

	def __str__(self):
		return " ".join( map(lambda x: str(x),[self.Project, self.GroupName,self.tag, self.Modeltype, self.Datatype, self.Dataformat ]) )

	def datapath(self):
		return os.path.join(settings.BIGDATA_DIR,'datascience','Projects',self.Project.Name,"Data",self.Datatype,self.GroupName+"_"+self.tag)

	def initialize(self):
		# make the data path
		path=self.datapath()
		if not os.path.isdir(path):
			os.makedirs(path)

	def get_shardnames(self):
		return self.ShardInfo.keys()


	def getshard_dict(self,name):
		path=os.path.join(self.datapath(),name+"."+self.Dataformat)
		if self.Dataformat=='joblib':
			with open(path,'r') as F:
				return joblib.load(F)
		elif self.Dataformat=='npz':
			np.load(path)

	def gen_shard(self):
		for name in self.ShardInfo.keys():
			yield self.getshard_dict(name)


	def get_first_shard(self):
		name = self.ShardInfo.keys()[0]
		return self.getshard_dict(name)


	def full_data(self):
		X=None
		Y=None
		for name in self.ShardInfo.keys():
			path=os.path.join(self.datapath(),name+"."+self.Dataformat)
			if self.Dataformat=='joblib':
				with open(path,'r') as F:
					D=joblib.load(F)
				if X is None:
					X=D['X']
					Y=D['Y']
				else:
					X=np.vstack((X,D['X']))
					Y=np.vstack((Y,D['Y']))

		return (X,Y)

class DataShard(models.Model):
	Data=models.ForeignKey(Data,on_delete=models.CASCADE)
	ShardInfo=JSONField(default={})

	created_at = models.DateTimeField(auto_now_add=True,null=True)
	updated_at = models.DateTimeField(auto_now=True,null=True)

	def __str__(self):
		return " ".join( map(lambda x: str(x),[self.Data.Project, self.Data.GroupName,self.Data.tag, self.Data.Modeltype, self.Data.Datatype, self.Data.Dataformat,str(self.id) ]) )

	def shardpath(self):
		# return os.path.join(settings.BIGDATA_DIR,'datascience','Projects',self.Project.Name,"Data",self.Datatype,self.GroupName+"_"+self.tag)
		name='shard'+"_"+self.Data.tag+"_"+str(self.id)
		path=os.path.join(self.Data.datapath(),name+"."+self.Data.Dataformat)
		return (name,path)


class MLmodels(models.Model):
	"""
	In the description, please mention the way the data is to be read
	ProjectName--> Data --> Raw --> DataName --> files
	"""
	Project=models.ForeignKey(Project,on_delete=models.CASCADE)
	Data=models.ForeignKey(Data,on_delete=models.CASCADE)

	Name=models.CharField(max_length=200,unique=True)
	Info=JSONField(default={})

	status_choices=[('Validated','Validated'),('Trained','Trained'),('UnTrained','UnTrained'),('Running','Running')]
	Status=models.CharField(choices=status_choices,max_length=30)


	save_format=[('npz','npz'),('h5','h5'),('pkl','pkl'),('joblib','joblib'),('xgboost','xgboost'),('keras','keras')]
	saveformat=models.CharField(choices=save_format,max_length=30)

	created_at = models.DateTimeField(auto_now_add=True,null=True)
	updated_at = models.DateTimeField(auto_now=True,null=True)

	def modelpath(self):
		return os.path.join(settings.BIGDATA_DIR,'datascience','Projects',self.Project.Name,"Models",str(self.id)+"_"+self.Name+"."+self.saveformat)

	def initialize(self):
		# make the model path
		path=self.modelpath()
		if not os.path.isdir(path):
			os.makedirs(path)


class ModelMetrics(models.Model):
	Data=models.ForeignKey(Data,on_delete=models.CASCADE)
	MLmodel=models.ForeignKey(MLmodels,on_delete=models.CASCADE)
	Metrics=JSONField(default={})
	Info=JSONField(default={})
