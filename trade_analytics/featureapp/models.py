# -*- coding: utf-8 -*-
from __future__ import unicode_literals,division
from django.contrib.auth.models import User
from django.db import models
import stockapp.models as stkmd
from django.contrib.postgres.fields import ArrayField,JSONField
import os
# Create your models here.


class FeatureComputeCode(models.Model):
	Code=models.TextField(help_text='Code of all the features')
	File=models.FilePathField(help_text='File of all the features')
	User = models.ForeignKey(User,on_delete=models.CASCADE, blank = True, null = True)
	created_at = models.DateTimeField(auto_now_add=True,null=True)
	updated_at = models.DateTimeField(auto_now=True,null=True)

	def __str__(self):
		return ", ".join([ str(self.User),' ... ',str(self.File[-20:]) ])


	def getimportpath(self):
		if not self.User:
			username='AnonymousUser'
		else:
			username=self.User.username
		path = 'featureapp.FeatureCodes.'+username
		return path

	def getfilepath(self):
		from django.conf import settings
		if not self.User:
			username='AnonymousUser'
		else:
			username=self.User.username
		path = os.path.join(settings.BASE_DIR,'featureapp','FeatureCodes',username+'.py')
		return path



class FeaturesMeta(models.Model):
	Userfilename = models.CharField(max_length=150,help_text="User ID from database",blank=True)
	Featurelabel=models.CharField(max_length=50,help_text="unique label",unique=True)
	Featuredescription=models.CharField(max_length=100,null=True,blank=True,help_text="Company name")
	Category=models.CharField(max_length=100,null=True,blank=True,help_text="Company name")
	Returntype=models.CharField(max_length=100,null=True,blank=True,help_text="Company name")
	operators=ArrayField(models.CharField(max_length=10), blank=True)

	Query=models.BooleanField(help_text='Use it in query',default=True)


	created_at = models.DateTimeField(auto_now_add=True,null=True)
	updated_at = models.DateTimeField(auto_now=True,null=True)

	def __str__(self):
		return str(self.Featurelabel)+" "+str(self.Category)+" "+str(self.Userfilename)

class FeaturesData(models.Model):
	T=models.DateField()
	Symbol = models.ForeignKey(stkmd.Stockmeta,on_delete=models.CASCADE)
	
	Featuredata = JSONField(default={})

	created_at = models.DateTimeField(auto_now_add=True,null=True)
	updated_at = models.DateTimeField(auto_now=True,null=True)


	def __str__(self):
		return str(self.Symbol.Symbol)+" "+str(self.T)+" "+str(len(self.Featuredata))