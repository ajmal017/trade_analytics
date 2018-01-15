# -*- coding: utf-8 -*-
from __future__ import unicode_literals,division
from django.contrib.auth.models import User
from django.db import models
from django.contrib.postgres.fields import ArrayField,JSONField
import computeapp.models as cmpmd
import os
import utility.models as utymd
# Create your models here.



class FeaturesMeta(models.Model):
	# Userfilename = models.CharField(max_length=150,help_text="User ID from database",blank=True)
	# FeatureCode=models.ForeignKey(FeatureComputeCode,on_delete=models.CASCADE,null=True)
	Featurelabel=models.CharField(max_length=50,help_text="unique label",unique=True)
	FeatureFunction=models.CharField(max_length=50,null=True,help_text="function to compute the featurelabel")
	Featuredescription=models.CharField(max_length=100,null=True,blank=True,help_text="Company name")
	Category=models.CharField(max_length=100,null=True,blank=True,help_text="Company name")
	Returntype=models.CharField(max_length=100,null=True,blank=True,help_text="Company name")
	operators=ArrayField(models.CharField(max_length=10), blank=True)

	Query=models.BooleanField(help_text='Use it in query',default=True)


	created_at = models.DateTimeField(auto_now_add=True,null=True)
	updated_at = models.DateTimeField(auto_now=True,null=True)

	def __str__(self):
		return str(self.Featurelabel)+" "+str(self.Category)

class FeaturesData(models.Model):
	T=models.DateField()
	Symbol=models.CharField(db_index=True,max_length=20,null=True,blank=True)
	Symbol_id=models.IntegerField(null=True,db_index=True)
	
	Featuredata = JSONField(default={})

	
	created_at = models.DateTimeField(auto_now_add=True,null=True)
	updated_at = models.DateTimeField(auto_now=True,null=True)


	def __str__(self):
		return str(self.Symbol)+" "+str(self.T)+" "+str(len(self.Featuredata))


