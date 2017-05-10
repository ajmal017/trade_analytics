from __future__ import unicode_literals
from __future__ import division
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

	Symbol=models.CharField(db_index=True,max_length=20,null=True,blank=True)
	Symbol_id=models.IntegerField(null=True,db_index=True)

	def __str__(self):
		return str(self.Symbol)+' '+str(self.Date)+' '+str(self.Close)

	class Meta:
		indexes = [
			models.Index(fields=['Date', 'Symbol_id']),
			models.Index(fields=['Date'], name='Date_idx'),
			models.Index(fields=['Symbol'], name='Symbol_idx'),
			models.Index(fields=['Symbol_id'], name='Symbol_id_idx'),
		]
		unique_together = ('Date', 'Symbol','Symbol_id')
		index_together = [
							['Date', 'Symbol','Symbol_id'],
							['Date', 'Symbol'],
							['Date', 'Symbol_id'],
						]

# TODO: Pymongo model
# TODO: save features in mongodb