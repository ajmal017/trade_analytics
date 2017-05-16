# -*- coding: utf-8 -*-
from __future__ import unicode_literals,division

from django.db import models
# import stockapp.models as stkmd
from django.contrib.postgres.fields import ArrayField,JSONField

# Create your models here.

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

class FeaturesData(models.Model):
	T=models.DateField()
	Symbol = models.CharField(max_length=10,help_text="Symbol")
	
	Featuredata = JSONField(default={})

	created_at = models.DateTimeField(auto_now_add=True,null=True)
	updated_at = models.DateTimeField(auto_now=True,null=True)


	def __str__(self):
		return self.Symbol