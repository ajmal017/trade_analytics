from __future__ import unicode_literals

from django.db import models

# Create your models here.



#TODO : 1. record the task ids, maintain a database to check if tasks are done
# 		2. provide a decorator to register a task, so you can keep track of remaining tasks of that type, take care of exceptions
#		3. provide progress bars rest api based on remaining number of tasks 
#		4. Keep log of failed tasks
#		5.




class ComputeStatus_Stockdownload(models.Model):
	status_choices=(('ToDo','ToDo'),('Run','Run'),('Fail','Fail'),('Success','Success'))
	Status=models.CharField(choices=status_choices,max_length=10)
	Symbol=models.ForeignKey( Stockmeta,on_delete=models.CASCADE)
	created_at = models.DateField(auto_now_add=True,null=True)
	updated_at = models.DateTimeField(auto_now=True,null=True)

	def __str__(self):
		return ", ".join( [str(self.Symbol),str(self.Status),str(self.created_at),str(self.updated_at)] )
