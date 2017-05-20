from __future__ import unicode_literals,division

from django.db import models
from django.contrib.auth.models import User
import pandas as pd

from multiselectfield import MultiSelectField
import os



# Get an instance of a logger
import logging
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
	
	def asdf(self,columns=None):
		if columns is not None:
			columns=tuple(columns)
			df=pd.DataFrame(list(self.values(*columns)) )
		else:
			df=pd.DataFrame(list(self.values()) )

		return df

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

	objects = StockMetaManager()

	Company=models.CharField(max_length=100,null=True,blank=True,help_text="Company name")
	Marketcap=models. DecimalField(max_digits=9,decimal_places=2,null=True,blank=True,help_text="Market Capitalization")
	Competitors=models.CharField(max_length=1100,null=True,blank=True,help_text="List of Competitors")
	Symbol = models.CharField(max_length=10,unique=True,null=False,blank=True,db_index=True,help_text="Stock Symbol",default='SYMBOL')
	Sector = models.CharField(max_length=100,null=True,blank=True,db_index=True,help_text="Stock Sector")
	Industry = models.CharField(max_length=100,null=True,blank=True,db_index=True,help_text="Stock Industry")
	
	status_choices=(('Active','Active'),('Inactive','Inactive'))
	Status=models.CharField(max_length=25,choices=status_choices,null=True,blank=True,db_index=True,help_text="Active or not")
	
	LastPriceUpdate= models.DateField(null=True,db_index=True)
	Startdate=models.DateField(null=True)
	Lastdate=models.DateField(null=True)

	Labels = MultiSelectField(choices=label_choices,blank=True)

	Update=models.BooleanField(help_text='Update data for this Symbol',default=True)
	Derived=models.BooleanField(help_text='Download data for this Symbol',default=False)
	ComputeFeature=models.BooleanField(help_text='Compute Features for this Symbol',default=True)
	User = models.ForeignKey(User,on_delete=models.CASCADE, null = True)

	def __str__(self):
		return self.Symbol

class ComputeStatus_Stockdownload(models.Model):
	status_choices=(('ToDo','ToDo'),('Run','Run'),('Fail','Fail'),('Success','Success'))
	Status=models.CharField(choices=status_choices,max_length=10)
	Symbol=models.ForeignKey( Stockmeta,on_delete=models.CASCADE)
	created_at = models.DateField(auto_now_add=True,null=True)
	updated_at = models.DateTimeField(auto_now=True,null=True)

	def __str__(self):
		return ", ".join( [str(self.Symbol),str(self.Status),str(self.created_at),str(self.updated_at)] )

class IndexComputeCode(models.Model):
	Code=models.TextField(help_text='Code of all the indices')
	File=models.FilePathField(help_text='File of all the indices')
	User = models.ForeignKey(User,on_delete=models.CASCADE, blank = True, null = True)
	created_at = models.DateTimeField(auto_now_add=True,null=True)
	updated_at = models.DateTimeField(auto_now=True,null=True)

	def __str__(self):
		return ", ".join([ str(self.User),' ... ',str(self.File[-20:]) ])


	def getimportpath(self):
		if not self.User:
			username='AnonymousUser'
		else:
			username=self.User.username
		path = 'stockapp.IndexCodes.'+username
		return path

	def getfilepath(self):
		from django.conf import settings
		if not self.User:
			username='AnonymousUser'
		else:
			username=self.User.username
		path = os.path.join(settings.BASE_DIR,'stockapp','IndexCodes',username+'.py')
		return path

class IndexComputeClass(models.Model):
	ClassName=models.CharField(help_text='Name of the index',max_length=100)
	ClassDescription=models.CharField(help_text='Description of the index',max_length=500,null=True)
	IndexComputeCode = models.ForeignKey(IndexComputeCode,on_delete=models.CASCADE)
	created_at = models.DateTimeField(auto_now_add=True,null=True)
	updated_at = models.DateTimeField(auto_now=True,null=True)

	def __str__(self):
		return str(self.IndexComputeCode.id)+', '+str(self.ClassName)
	

class Index(models.Model):
	"""
	Names of all the index/functions/labels 
	We can apply the index to several groups
	"""
	IndexComputeClass=models.ForeignKey(IndexComputeClass,on_delete=models.CASCADE)

	IndexName=models.CharField(help_text='Long name',max_length=150, blank = True, null = True)
	IndexDescription=models.CharField(help_text='Description of the index',max_length=500, blank = True, null = True)
	IndexLabel=models.CharField(help_text='Unique Abbreviated label for index',max_length=50,  unique=True)
	IndexResultType=models.CharField(help_text='Description of the index',max_length=100, blank = True, null = True)
	
	computefeatures=models.BooleanField(help_text='Run feature extractions on this index',default=True)

	created_at = models.DateTimeField(auto_now_add=True,null=True)
	updated_at = models.DateTimeField(auto_now=True,null=True)

	def __str__(self):
		return ", ".join( [ str(self.IndexLabel),str(self.IndexName),str(self.IndexResultType),str(self.IndexComputeClass) ])

class StockGroup(models.Model):
	GroupName=models.CharField(max_length=50,null=True)
	GroupDescription=models.CharField(max_length=1000,null=True,blank=True)
	Symbol = models.ManyToManyField(Stockmeta)
	User = models.ForeignKey(User,on_delete=models.CASCADE, blank = True, null = True)
	created_at = models.DateTimeField(auto_now_add=True,null=True)
	updated_at = models.DateTimeField(auto_now=True,null=True)

	
	def __str__(self):
		return self.GroupName

class StockGroupIndex(models.Model):
	"""
	first add the new symbol in stockmeta, then add entry here for the group and the required index
	"""
	Symbol=models.ForeignKey(Stockmeta,on_delete=models.CASCADE)
	StockGroup=models.ForeignKey(StockGroup,on_delete=models.CASCADE)
	Index = models.ForeignKey(Index)

	def __str__(self):
		return self.Symbol.Symbol+', '+self.StockGroup.GroupName+', '+self.Index.IndexLabel

