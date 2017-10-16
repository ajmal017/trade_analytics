from __future__ import unicode_literals
import os
from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.contrib.postgres.fields import ArrayField
from django.contrib.postgres.fields import JSONField
import utility.models as utymd
import h5py
import pandas as pd
import numpy as np
import joblib
import json

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



class DataCode(utymd.ComputeCode):

	module='datascience'
	codesfolder='DataCodes'


class ComputeFunc(models.Model):
	"""
	Load the imports
	Load all functions from a group
	"""
	Name=models.CharField(max_length=200)
	Group=models.CharField(max_length=200,null=True)
	Userfilename = models.CharField(max_length=150,help_text="User Name from database",blank=True)

	RequiredImports=JSONField(default={})
	RequiredGroup=JSONField(default={})

	Transformer=models.BooleanField(default=False)

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
		return os.path.join(settings.BIGDATA_DIR,'datascience','Projects',str(self.id)+'_'+self.Name)


	def initialize(self):
		# make the bigdata path, to store large data
		path=self.bigdatapath()
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
	TransfomerFunc=models.ForeignKey(ComputeFunc,on_delete=models.SET_NULL,null=True)

	GroupName=models.CharField(max_length=200)
	Info=JSONField(default={},null=True)

	# tags that are same, are kind of pairs
	tag=models.CharField(max_length=200)

	model_types=[('Classification','Classification'),('Regression','Regression')]
	Modeltype=models.CharField(choices=model_types,max_length=20)

	data_structures=[('Channels','Channels'),('Flattened','Flattened')]
	DataStructure=models.CharField(choices=data_structures,max_length=20,default='Channels')

	# Raw has all missing etc, Base is cleaned up
	data_choices=[('Raw','Raw'),('Base','Base'),('RawProcessed','RawProcessed'),('Train','Train'),('Validation','Validation'),('Test','Test')]
	Datatype=models.CharField(choices=data_choices,max_length=20)

	data_format=[('npz','npz'),('h5','h5'),('pkl','pkl'),('joblib','joblib'),('json','json')]
	Dataformat=models.CharField(choices=data_format,max_length=30)


	# Binary is always 0/1, classes are labelled by integers 0,1,2,...
	# binary 1 is the important class i.e. like fraud==1 , nofraud==0
	ouput_choices=[('binary','binary'),('multiclass','multiclass'),('continuous','continuous')]
	ouput_type=models.CharField(choices=data_format,max_length=30,default='binary')

	# Datashards=JSONField(default={})

	created_at = models.DateTimeField(auto_now_add=True,null=True)
	updated_at = models.DateTimeField(auto_now=True,null=True)

	def __str__(self):
		return " ".join( map(lambda x: str(x),[self.Project, self.GroupName,self.tag, self.Modeltype, self.Datatype, self.Dataformat ]) )

	def datapath(self):
		return os.path.join(settings.BIGDATA_DIR,'datascience','Projects',self.Project.Name,"Data",self.Datatype,str(self.id)+'_'+self.GroupName+"_"+self.tag)

	def initialize(self):
		# make the data path
		path=self.datapath()
		if not os.path.isdir(path):
			os.makedirs(path)

	def getfulldatapath(self):
		return os.path.join(self.datapath(),'fulldata'+"."+self.Dataformat)

	def deletefulldata(self):
		filename=self.getfulldatapath()
		import os
		os.remove(filename)
		
	def getdata(self):

		filename=self.getfulldatapath()
		if not os.path.isfile(filename):
			import datascience.libs as dtsclibs
			dtsclibs.combineshards(self.id,filename,self.Dataformat)
		
		try:
			if self.Dataformat=='npz':
				data=np.load(filename)

			return ( data['X'], data['Y'], data['Meta'][()] )
		except:
			
			import datascience.libs as dtsclibs
			dtsclibs.combineshards(self.id,filename,self.Dataformat)

			if self.Dataformat=='npz':
				data=np.load(filename)

			return ( data['X'], data['Y'], data['Meta'][()] )

class DataShard(models.Model):
	Data=models.ForeignKey(Data,on_delete=models.CASCADE)
	ShardInfo=JSONField(default={})

	created_at = models.DateTimeField(auto_now_add=True,null=True)
	updated_at = models.DateTimeField(auto_now=True,null=True)

	def __str__(self):
		return " ".join( map(lambda x: str(x),[self.Data.Project, self.Data.GroupName,self.Data.tag, self.Data.Modeltype, self.Data.Datatype, self.Data.Dataformat,str(self.id) ]) )

	def shardpath(self,extratag=''):
		# return os.path.join(settings.BIGDATA_DIR,'datascience','Projects',self.Project.Name,"Data",self.Datatype,self.GroupName+"_"+self.tag)
		name=str(self.id)+'_'+'shard'+"_"+self.Data.tag+extratag
		path=os.path.join(self.Data.datapath(),name+"."+self.Data.Dataformat)
		return (name,path)

	def savedata(self,**kwargs):
		name,path=self.shardpath()
		if self.Data.Dataformat=='npz':
			np.savez_compressed(path,**kwargs)
		elif self.Data.Dataformat=='h5':
			h5f = h5py.File(path, 'w')
			for key,value in kwargs.items():
				if type(value)==dict:
					string_dt = h5py.special_dtype(vlen=str)
					h5f.create_dataset('key', data=np.array([json.dumps(value)]), dtype=string_dt)
				else:
					h5f.create_dataset(key, data=value,compression="gzip")
			h5f.close() 


	def getdata(self):
		name,path=self.shardpath()
		if self.Data.Dataformat=='npz':
			data=np.load(path)
			X=data['X']
			Y=data['Y']
			Meta=data['Meta'][()]
		elif self.Data.Dataformat=='h5':
			h5f = h5py.File(path, 'r')
			X = h5f['X'][:]
			Y = h5f['Y'][:]
			Meta = json.loads(h5f['Meta'][:][0])
			h5f.close() 

			
		return ( X, Y, Meta )


class ModelCode(utymd.ComputeCode):

	module='datascience'
	codesfolder='ModelCodes'

	
class MLmodels(models.Model):
	"""
	In the description, please mention the way the data is to be read
	ProjectName--> Data --> Raw --> DataName --> files
	"""
	
	Project=models.ForeignKey(Project,on_delete=models.SET_NULL,null=True)
	Data=models.ForeignKey(Data,on_delete=models.SET_NULL,null=True)
	ModelCode=models.ForeignKey(ModelCode,on_delete=models.CASCADE,null=True)

	Deploy=models.BooleanField(default=False)

	Name=models.CharField(max_length=200)
	Info=JSONField(default={})
	
	# Userfilename is same as username
	# Userfilename = models.CharField(max_length=150,help_text="User ID from database",blank=True)

	status_choices=[('Validated','Validated'),('Trained','Trained'),('UnTrained','UnTrained'),('Running','Running')]
	Status=models.CharField(choices=status_choices,max_length=30)


	save_format=[('npz','npz'),('h5','h5'),('pkl','pkl'),('joblib','joblib'),('xgboost','xgboost'),('keras','keras')]
	saveformat=models.CharField(choices=save_format,max_length=30)

	created_at = models.DateTimeField(auto_now_add=True,null=True)
	updated_at = models.DateTimeField(auto_now=True,null=True)

	def modeldir(self):
		return os.path.join(settings.BIGDATA_DIR,'datascience','Projects',self.Project.Name,"Models")

	def modelpath(self):
		return os.path.join(settings.BIGDATA_DIR,'datascience','Projects',self.Project.Name,"Models",str(self.id)+"_"+self.Name+"."+self.saveformat)

	def getmodelname(self):
		name=self.Name+'_'+self.id
		return name

	def initialize(self):
		# make the model path
		path=self.modeldir()
		if not os.path.isdir(path):
			os.makedirs(path)

	def getmodelclass(self):
		MC=ModelCode.objects.get(id=self.ModelCode.id)
		return MC.importobject(self.Name)


class ModelMetrics(models.Model):
	Data=models.ForeignKey(Data,on_delete=models.CASCADE)
	MLmodel=models.ForeignKey(MLmodels,on_delete=models.CASCADE)
	Metrics=JSONField(default={})
	Info=JSONField(default={})
