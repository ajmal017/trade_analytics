from __future__ import unicode_literals
import os
from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.contrib.postgres.fields import ArrayField
from django.contrib.postgres.fields import JSONField
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
	Info=JSONField()

	created_at = models.DateTimeField(auto_now_add=True,null=True)
	updated_at = models.DateTimeField(auto_now=True,null=True)

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
	"""
	Project=models.ForeignKey(Project,on_delete=models.CASCADE)
	ParentData=models.ForeignKey('self',on_delete=models.CASCADE,null=True)

	Name=models.CharField(max_length=200)
	Info=JSONField()
	
	data_choices=[('Raw','Raw'),('Derived','Derived'),('Train','Train'),('Validation','Validation'),('Test','Test')]
	Datatype=models.CharField(choices=data_choices,max_length=20)

	data_format=[('npz','npz'),('dataFrame','dataFrame'),('pkl','pkl')]
	Dataformat=models.CharField(choices=data_format,max_length=30)

	Datashards=ArrayField( models.CharField(max_length=50, blank=True) )
	
	created_at = models.DateTimeField(auto_now_add=True,null=True)
	updated_at = models.DateTimeField(auto_now=True,null=True)

	def datapath(self):
		return os.path.join(settings.BIGDATA_DIR,'datascience','Projects',self.Project.Name,"Data",self.Datatype,self.Name)

	def initialize(self):
		# make the data path
		path=self.datapath()
		if not os.path.isdir(path):
			os.makedirs(path)

	def newshardpath(self,name=None,tag=''):
		if name is None:
			name=tag+'_'+str(len(self.Datashards))

		self.Datashards.append(name)
		self.save()

		path=os.path.join(self.datapath(),name)

		return path



class MLmodels(models.Model):
	"""
	In the description, please mention the way the data is to be read
	ProjectName--> Data --> Raw --> DataName --> files
	"""
	Project=models.ForeignKey(Project,on_delete=models.CASCADE)
	Data=models.ForeignKey(Data,on_delete=models.CASCADE)

	Name=models.CharField(max_length=200,unique=True)
	Info=JSONField()
	
	created_at = models.DateTimeField(auto_now_add=True,null=True)
	updated_at = models.DateTimeField(auto_now=True,null=True)

	def modelpath(self):
		return os.path.join(settings.BIGDATA_DIR,'datascience','Projects',self.Project.Name,"Models",self.Name)

	def initialize(self):
		# make the model path
		path=self.modelpath()
		if not os.path.isdir(path):
			os.makedirs(path)


