from __future__ import unicode_literals,division
from django.contrib.postgres.fields import JSONField
from django.db import models

# Create your models here.



class StdCharts(models.Model):
	
	Chartname=models.CharField(max_length=50,null=True,blank=True)
	Chartdescription=models.CharField(max_length=200,null=True,blank=True)

	Template=models.CharField(max_length=50,null=True,blank=True)
	TempBlocs = JSONField()

	inputtype=models.CharField(max_length=50,null=True,blank=True)









