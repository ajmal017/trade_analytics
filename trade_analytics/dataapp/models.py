from __future__ import unicode_literals

from django.db import models

# Create your models here.

class Stockprice(models.Model):
	_DATABASE='stockpricedata'
	
	Close=models.DecimalField(max_digits=9,decimal_places=2,null=True,blank=True,db_index=True)
	Open=models.DecimalField(max_digits=9,decimal_places=2,null=True,blank=True)
	High=models.DecimalField(max_digits=9,decimal_places=2,null=True,blank=True)
	Low=models.DecimalField(max_digits=9,decimal_places=2,null=True,blank=True)
	Volume=models.DecimalField(max_digits=15,decimal_places=2,null=True,blank=True)
	Date = models.DateField(db_index=True,null=False)

	Symbol=models.CharField(db_index=True,max_length=10,null=True,blank=True)

	def __str__(self):
		return str(self.Symbol)+' '+str(self.Date)+' '+str(self.Close)

	class Meta:
		ordering = ["Date"]