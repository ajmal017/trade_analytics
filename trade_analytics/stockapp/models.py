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
    def authors(self):
        return self.filter(role='A')

    def editors(self):
        return self.filter(role='E')

class StockMetaManager(models.Manager):
    def with_counts(self):
    	reset_queries()
    	
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT p.id, p.question, p.poll_date, COUNT(*)
                FROM polls_opinionpoll p, polls_response r
                WHERE p.id = r.poll_id
                GROUP BY p.id, p.question, p.poll_date
                ORDER BY p.poll_date DESC""")
            result_list = []
            for row in cursor.fetchall():
                p = self.model(id=row[0], question=row[1], poll_date=row[2])
                p.num_responses = row[3]
                result_list.append(p)

        connection.queries

        return result_list

    # def get_queryset(self):
    #     return super(StockMetaManager, self).get_queryset().filter(author='Roald Dahl')

    def get_queryset(self):
        return StockMetaQuerySet(self.model, using=self._db)

"""
okokokokoko
"""
class Stockmeta(models.Model):
	"""Fetches rows from a Bigtable.

    Retrieves rows pertaining to the given keys from the Table instance
    represented by big_table.  Silly things may happen if
    other_silly_variable is not None.

    Args:
        big_table: An open Bigtable Table instance.
        keys: A sequence of strings representing the key of each table row
            to fetch.
        other_silly_variable: Another optional variable, that has a much
            longer name than the other args, and which does nothing.

    Returns:
        A dict mapping keys to the corresponding table row data
        fetched. Each row is represented as a tuple of strings. For
        example:

        {'Serak': ('Rigel VII', 'Preparer'),
         'Zim': ('Irk', 'Invader'),
         'Lrrr': ('Omicron Persei 8', 'Emperor')}

        If a key from the keys argument is missing from the dictionary,
        then that row was not found in the table.

    Raises:
        IOError: An error occurred accessing the bigtable.Table object.
    """

	objects = models.Manager() # The default manager.
	# stockmeta_objects = StockMetaManager()

	Company=models.CharField(max_length=100,null=True,blank=True,help_text="Company name")
	Marketcap=models. DecimalField(max_digits=9,decimal_places=2,null=True,blank=True,help_text="Market Capitalization")
	Competitors=models.CharField(max_length=1100,null=True,blank=True,help_text="List of Competitors")
	Symbol = models.CharField(max_length=6,null=False,blank=True,db_index=True,help_text="Stock Symbol")
	Sector = models.CharField(max_length=100,null=True,blank=True,db_index=True,help_text="Stock Sector")
	Industry = models.CharField(max_length=100,null=True,blank=True,db_index=True,help_text="Stock Industry")
	
	status_choices=(('Active','Active'),('Inactive','Inactive'))
	Status=models.CharField(max_length=25,choices=status_choices,null=True,blank=True,db_index=True,help_text="Active or not")
	
	LastPriceUpdate= models.DateField(null=True,db_index=True)

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
