import abc
import json
import os
from django.db import models
# from django.contrib.auth.models import User
import shutil
import time
import pandas as pd




class ComputeCode(models.Model):
	

	Code=models.TextField(help_text='Code of all the features',null = True)
	File=models.FilePathField(help_text='File of all the features',max_length=400,null = True)
	Username = models.CharField(max_length=150,help_text="User ID from database",blank=True,null=True)
	created_at = models.DateTimeField(auto_now_add=True,null=True)
	updated_at = models.DateTimeField(auto_now=True,null=True)

	module=None
	codesfolder=None
	computeclassname=None

	class Meta:
		abstract = True

	def __str__(self):
		if not self.User:
			username='AnonymousUser'
		else:
			username=self.User.username

		if not self.File:
			Filename='None'
		else:
			Filename=self.File

		return ", ".join([ str(username),' ... ',str(Filename[-20:]) ])


	def getimportpath(self):
		if not self.Username:
			username='AnonymousUser'
		else:
			username=self.Username
		path = ".".join([self.module,self.codesfolder,username])
		return path

	def importcomputeclass(self):
		import importlib
		modpath=self.getimportpath()
		module=importlib.import_module(modpath) 
		module=reload(module)
		compclass = getattr(module, self.computeclassname)
		return compclass


	def getfilepath(self):
		from django.conf import settings
		if not self.Username:
			username='AnonymousUser'
		else:
			username=self.Username
		path = os.path.join(settings.BASE_DIR,self.module,self.codesfolder,username+'.py')
		return path

	@classmethod
	def initialize(cls):
		if cls.objects.all().count()==0:
			print "initializing files"
			obj=cls(Code='')
			obj.save()
			obj.File=obj.getfilepath()
			obj.save()

			cls.Sync_db2files()

	@classmethod
	def Sync_db2files(cls):
		ObjCodes=cls.objects.all()
		for obj in ObjCodes:
			if obj.File is None:
				obj.File=obj.getfilepath()

			if os.path.isfile(obj.File):
				filetime=pd.to_datetime(time.ctime(os.path.getmtime(obj.File)))
				if obj.updated_at<filetime:
					# first make a copy of that file and then copy dbfile to disk
					shutil.move(obj.File,obj.File.replace('.py',filetime.strftime("%Y-%m-%d_%H-%M-%S")+'.py'))

			with open(obj.File,'w') as codestr:
				codestr.write(obj.Code)

	@classmethod
	def Sync_files2db(cls):
		ObjCodes=cls.objects.all()
		for obj in ObjCodes:
			print "Sync ",obj," to db"
			if obj.File is None:
				obj.File=obj.getfilepath()
			with open(obj.File,'r') as codestr:
				obj.Code=codestr.read()
			obj.save()




class Value(object):
	def __init__(self,value=None,serializer='str',deserializer='int'):
		"""
		serializer have to be functions or lambda fnctions
		"""
		self.value=value
		self.serializedvalue=None
		self.serializer=serializer
		self.deserializer=deserializer
	
	def SerializeValue(self):
		if self.serializedvalue:
			return self.serializedvalue
		F=eval(self.serializer)
		self.serializedvalue=F(self.value)

		return {'class':'Value','deserializer':self.deserializer,'serializer':self.serializer,'serializedvalue':self.serializedvalue }
	
	@classmethod
	def deserialize(cls,obj):
		obj=json.loads(obj)
		F=eval(obj['deserializer'] )
		value=F(obj['serializedvalue'])
		return cls(value=value,serializer=obj['serializer'],deserializer=obj['deserializer'])


class basecode(object):
	def __init__(self):
		self.meta={}

	def register(self,*args,**kwargs):
		"""
		register the meta information: like description, names labels etc
		need unique label
		"""
		if 'label' not in kwargs:
			raise KeyError("label is required")

		if kwargs['label'] not in self.meta.keys():
			self.meta[kwargs['label']]={}

		for key,value in kwargs.items():
			if key!='label':
				self.meta[kwargs['label']][key]=value

	def setvalue(self,key,value,serilizer=str):
		if key not in self.meta:
			raise KeyError(key+" not registered")
		self.meta[key]['value']=value

	def getvalue(self,key):
		if key not in self.meta:
			raise KeyError(key+" not registered")
		return self.meta[key]['value']

	def sandoxtest(self):
		pass
	def isvalid(self):
		pass
	def compute(self,*args,**kwargs):
		pass
	def finalize(self):
		"""
		return the final
		"""
		pass



class index(basecode):
	name='index'
	


class feature(basecode):
	name='feature'
	

class query(basecode):
	name='query'

class chart(basecode):
	name='chart'
