# -*- coding: utf-8 -*-
from __future__ import unicode_literals,division
from django.contrib.auth.models import User
from django.db import models
from django.contrib.postgres.fields import ArrayField,JSONField
import os
import utility.models as utymd
# Create your models here.


class QueryMeta(models.Model):
	Userfilename = models.CharField(max_length=150,help_text="User ID from database",blank=True)
	Querylabel=models.CharField(max_length=50,help_text="unique label",unique=True)
	Querydescription=models.CharField(max_length=100,null=True,blank=True,help_text="Company name")
	Category=models.CharField(max_length=100,null=True,blank=True,help_text="Company name")

	created_at = models.DateTimeField(auto_now_add=True,null=True)
	updated_at = models.DateTimeField(auto_now=True,null=True)

	def __str__(self):
		return str(self.Querylabel)+" "+str(self.Category)+" "+str(self.Userfilename)

class QueryData(models.Model):
	T=models.DateField()
	Symbol=models.CharField(db_index=True,max_length=20,null=True,blank=True)
	Symbol_id=models.IntegerField(null=True,db_index=True)
	
	Querydata = JSONField(default={})

	created_at = models.DateTimeField(auto_now_add=True,null=True)
	updated_at = models.DateTimeField(auto_now=True,null=True)


	def __str__(self):
		return str(self.Symbol.Symbol)+" "+str(self.T)+" "+str(len(self.Querydata))


