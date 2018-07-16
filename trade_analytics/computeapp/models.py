from __future__ import unicode_literals

from django.db import models
import pandas as pd



def getnowtime():
	return pd.datetime.now()

# Create your models here.
class ComputeSession(models.Model):
	Starttime=models.DateTimeField()
	Endtime=models.DateTimeField(null=True)
	Name = models.CharField(max_length=200,null=True,blank=True)
	Description = models.CharField(max_length=500,null=True,blank=True)

	@classmethod
	def make_newsession(cls,Name,Description):
		obj=cls(Starttime=getnowtime(), Name=Name,Description=Description)
		obj.save()
		return obj

	@classmethod
	def save_session_byId(cls,Id):
		obj=cls.objects.get(id=Id)
		obj.Endtime=getnowtime()
		obj.save()
		return obj

	@classmethod
	def save_session_byobj(cls,obj):
		obj.Endtime=getnowtime()
		obj.save()
		return obj


class ComputeStatus(models.Model):
	ComputeSession_id=models.IntegerField(null=True,db_index=True)

	Compute_status_choices=[('Fail','Fail'),('ToDo','ToDo'),('Success','Success'),('Running','Running')]
	ComputeStatus=models.CharField(choices=Compute_status_choices,max_length=30,null=True)

	Msg=models.TextField(null=True,blank=True) # any message to give more info

	ComputeStarttime = models.DateTimeField(null=True)
	ComputeEndtime = models.DateTimeField(null=True)


	@classmethod
	def make_newcompute(cls,ComputeSession_id):
		obj=cls(ComputeStarttime=getnowtime(),ComputeSession_id=ComputeSession_id,ComputeStatus='ToDo')
		obj.save()
		return obj

	
	def save_compute_byId(cls,Id,Status,Msg=''):
		obj=cls.objects.get(id=Id)
		obj.ComputeEndtime=getnowtime()
		obj.ComputeStatus=Status
		obj.Msg=Msg
		obj.save()
		return obj

	@classmethod
	def save_running_byId(cls,Id,Msg=''):
		obj=cls.objects.get(id=Id)
		obj.ComputeEndtime=getnowtime()
		obj.ComputeStatus='Running'
		obj.Msg=Msg
		obj.save()
		return obj
	@classmethod
	def save_success_byId(cls,Id,Msg=''):
		obj=cls.objects.get(id=Id)
		obj.ComputeEndtime=getnowtime()
		obj.ComputeStatus='Success'
		obj.Msg=Msg
		obj.save()
		return obj
	@classmethod
	def save_fail_byId(cls,Id,Msg=''):
		obj=cls.objects.get(id=Id)
		obj.ComputeEndtime=getnowtime()
		obj.ComputeStatus='Fail'
		obj.Msg=Msg
		obj.save()
		return obj

	@classmethod
	def save_compute_byobj(cls,obj,Status,Msg=''):
		obj.ComputeEndtime=getnowtime()
		obj.ComputeStatus=Status
		obj.Msg=Msg
		obj.save()
		return obj



