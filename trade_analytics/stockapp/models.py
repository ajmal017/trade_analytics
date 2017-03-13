from __future__ import unicode_literals,division

from django.db import models
import datetime
import pandas as pd
from home import models as hmd
from multiselectfield import MultiSelectField



# Create your models here.



"""
okokokokoko
"""
class Stockmeta(models.Model):
	"""
	Model that contains all meta information

	"""
	Company=models.CharField(max_length=100,null=True,blank=True)
	Marketcap=models. DecimalField(max_digits=9,decimal_places=2,null=True,blank=True)
	Competitors=models.CharField(max_length=1100,null=True,blank=True)
	Symbol = models.CharField(max_length=6,null=True,blank=True)
	Sector = models.CharField(max_length=100,null=True,blank=True)
	Industry = models.CharField(max_length=100,null=True,blank=True)
	
	status_choices=(('Active','Active'),('Inactive','Inactive'))
	Status=models.CharField(max_length=25,choices=status_choices,null=True,blank=True)
	
	LastPriceUpdate= models.DateField(null=True)

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

		)

	Labels = MultiSelectField(choices=label_choices,blank=True)

	def __str__(self):
		return self.Symbol




class Watchlist(hmd.UserBase):
	Watchlist_name=models.CharField(max_length=50,null=True)
	Watchlist_description=models.CharField(max_length=1000,null=True,blank=True)
	Symbol = models.ManyToManyField(Stockmeta)

	created_at = models.DateTimeField(auto_now_add=True,null=True)
	updated_at = models.DateTimeField(auto_now=True,null=True)

	
	def __str__(self):
		return self.Watchlist_name
