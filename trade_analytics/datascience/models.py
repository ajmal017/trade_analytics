from __future__ import unicode_literals
import os
from django.db import models
from django.contrib.auth.models import User
from django.conf import settings

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
	Description=models.CharField(max_length=800)
	FolderRelPath=models.FilePathField(help_text='Folder relative path',max_length=400)

	created_at = models.DateTimeField(auto_now_add=True,null=True)
	updated_at = models.DateTimeField(auto_now=True,null=True)

	def absfolderpath(self):
		return os.path.join(settings.BIGDATA_DIR,self.FolderRelPath)

	def initialize(self):
		path=self.absfolderpath()
		if not os.path.isdir(path):
			os.mkdir(path)

