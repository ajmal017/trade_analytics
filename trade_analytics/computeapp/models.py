from __future__ import unicode_literals

from django.db import models

# Create your models here.

class ComputeStatus(models.Model):
	# Userfilename = models.CharField(max_length=150,help_text="User ID from database",blank=True)
	FeatureCode=models.ForeignKey(FeatureComputeCode,on_delete=models.CASCADE,null=True)
	Featurelabel=models.CharField(max_length=50,help_text="unique label",unique=True)
	Featuredescription=models.CharField(max_length=100,null=True,blank=True,help_text="Company name")
	Category=models.CharField(max_length=100,null=True,blank=True,help_text="Company name")
	Returntype=models.CharField(max_length=100,null=True,blank=True,help_text="Company name")
	operators=ArrayField(models.CharField(max_length=10), blank=True)

	Query=models.BooleanField(help_text='Use it in query',default=True)


	created_at = models.DateTimeField(auto_now_add=True,null=True)
	updated_at = models.DateTimeField(auto_now=True,null=True)


#TODO : 1. record the task ids, maintain a database to check if tasks are done
# 		2. provide a decorator to register a task, so you can keep track of remaining tasks of that type, take care of exceptions
#		3. provide progress bars rest api based on remaining number of tasks 
#		4. Keep log of failed tasks
#		5.


