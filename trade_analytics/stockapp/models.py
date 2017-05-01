from __future__ import unicode_literals,division

from django.db import models
import datetime
import pandas as pd
import logging
from home import models as hmd
from multiselectfield import MultiSelectField
from django.db import connection,reset_queries



# Get an instance of a logger
logger = logging.getLogger(__name__)

"""
logger.error('Something went wrong!')
logger.debug()
logger.info()
logger.warning()
logger.error()
logger.critical()

"""

class StockMetaQuerySet(models.QuerySet):
	def IDchunks(self,N,limit=None):
		if limit is None:
			L=self.count()
		else:
			L=limit
			
		IDS=list(self.values_list('id',flat=True))
		for i in range(0,L,N):
			yield IDS[i:i+N]

	def IDs(self):
		# L=self.count()
		IDS=list(self.values_list('id',flat=True))
		return IDS

class StockMetaManager(models.Manager):
	
	def get_queryset(self):
		return StockMetaQuerySet(self.model, using=self._db)

class Stockmeta(models.Model):
	"""Model for stock meta data

	All the stock symbols, and other static information of stocks
	

	Raises:
		IOError: An error occurred accessing the bigtable.Table object.
	"""

	# objects = models.Manager() # The default manager.
	objects = StockMetaManager()

	Company=models.CharField(max_length=100,null=True,blank=True,help_text="Company name")
	Marketcap=models. DecimalField(max_digits=9,decimal_places=2,null=True,blank=True,help_text="Market Capitalization")
	Competitors=models.CharField(max_length=1100,null=True,blank=True,help_text="List of Competitors")
	Symbol = models.CharField(max_length=6,null=False,blank=True,db_index=True,help_text="Stock Symbol",default='SYMBOL')
	Sector = models.CharField(max_length=100,null=True,blank=True,db_index=True,help_text="Stock Sector")
	Industry = models.CharField(max_length=100,null=True,blank=True,db_index=True,help_text="Stock Industry")
	
	status_choices=(('Active','Active'),('Inactive','Inactive'))
	Status=models.CharField(max_length=25,choices=status_choices,null=True,blank=True,db_index=True,help_text="Active or not")
	
	LastPriceUpdate= models.DateField(null=True,db_index=True)
	Startdate=models.DateField(null=True)
	Lastdate=models.DateField(null=True)
	
	DownloadData=models.BooleanField(help_text='Download data for this Symbol',default=True)

	label_choices=( 
					('ETF','ETF'),
					('Stock','Stock'),
					('Gold','Gold'),
					('Silver','Silver'),
					('Oil','Oil'),
					('Inverse','Inverse'),
					('Copper','Copper'),
					('Entertainment','Entertainment'),
					('Uranium','Uranium'),
					('Coal','Coal'),
					('Index','Index'),
					('GroupIndex','GroupIndex'),

		)

	Labels = MultiSelectField(choices=label_choices,blank=True)

	def __str__(self):
		return self.Symbol


class IndexFunction(hmd.UserBase):
	IndexCode=models.TextField(help_text='Code to compute the index')
	IndexName=models.CharField(help_text='Name of the index',max_length=50)
	IndexDescription=models.CharField(help_text='Description of the index',max_length=200)

	created_at = models.DateTimeField(auto_now_add=True,null=True)
	updated_at = models.DateTimeField(auto_now=True,null=True)

class StockGroup(hmd.UserBase):
	GroupName=models.CharField(max_length=50,null=True)
	GroupDescription=models.CharField(max_length=1000,null=True,blank=True)
	Symbol = models.ManyToManyField(Stockmeta)
	Indicies = models.ManyToManyField(IndexFunction)

	created_at = models.DateTimeField(auto_now_add=True,null=True)
	updated_at = models.DateTimeField(auto_now=True,null=True)

	
	def __str__(self):
		return self.Watchlist_name
