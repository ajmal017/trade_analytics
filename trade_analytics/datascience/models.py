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


class Label(models.Model):
	label=models.CharField(max_length=100)
	Symbol=models.CharField(max_length=100)
	T = models.DateField(null=True)
	window = models.IntegerField(null=True)
	User = models.ForeignKey(User,on_delete=models.CASCADE, blank = True, null = True)
	created_at = models.DateTimeField(auto_now_add=True,null=True)
	updated_at = models.DateTimeField(auto_now=True,null=True)



class Project(models.Model):
	Name=models.CharField(max_length=200)
	Misc=JSONField(default={})

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
		path=self.ProjectPath()
		if not os.path.isdir(path):
			os.makedirs(path)


class Data(models.Model):
	"""
	In the description, please mention the way the data is to be read
	ProjectName--> Data --> Raw --> DataName --> files
	Datashards have infor such as shardname: sample_shape, #smaples, # samples in each class 
	"""
	Project=models.ForeignKey(Project,on_delete=models.CASCADE)
	ParentData=models.ForeignKey('self',on_delete=models.CASCADE,null=True)

	GroupName=models.CharField(max_length=200)
	Misc=JSONField(default={})

	# tags that are sane, are kind of pairs
	tag=models.CharField(max_length=200)

	model_types=[('Classification','Classification'),('Regression','Regression')]
	Modeltype=models.CharField(choices=model_types,max_length=20)

	data_choices=[('Raw','Raw'),('RawProcessed','RawProcessed'),('Derived','Derived'),('Train','Train'),('Validation','Validation'),('Test','Test')]
	Datatype=models.CharField(choices=data_choices,max_length=20)

	data_format=[('npz','npz'),('h5','h5'),('pkl','pkl'),('joblib','joblib')]
	Dataformat=models.CharField(choices=data_format,max_length=30)

	# Datashards=JSONField(default={})
	ShardInfo=JSONField(default={})
	
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

	def newshardpath(self,name=None,tag=''):
		if name is None:
			name='shard'+"_"+tag+"_"+str(len(self.ShardInfo))


		path=os.path.join(self.datapath(),name+"."+self.Dataformat)

		self.ShardInfo[name] ={'#samples': 0 } 
		self.save()

		return (name,path)

	def gen_shard(self):
		for name in self.ShardInfo.keys():
			path=os.path.join(self.datapath(),name+"."+self.Dataformat)
			if self.Dataformat=='joblib':
				with open(path,'r') as F:
					D=joblib.load(F)
				yield D

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


class MLmodels(models.Model):
	"""
	In the description, please mention the way the data is to be read
	ProjectName--> Data --> Raw --> DataName --> files
	"""
	Project=models.ForeignKey(Project,on_delete=models.CASCADE)
	Data=models.ForeignKey(Data,on_delete=models.CASCADE)

	Name=models.CharField(max_length=200,unique=True)
	Misc=JSONField(default={})
	
	status_choices=[('Trained','Trained'),('UnTrained','UnTrained')]
	Status=models.CharField(choices=status_choices,max_length=30)

	
	save_format=[('npz','npz'),('h5','h5'),('pkl','pkl'),('joblib','joblib')]
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

	def loadmodel(self):
		path=self.modelpath()
		if self.saveformat=='joblib':
			with open(path,'r') as F:
				clf=joblib.load(F)

		return clf
