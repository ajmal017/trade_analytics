# -*- coding: utf-8 -*-
from __future__ import unicode_literals,division

from django.db import models
from django.db import connections
# Create your models here.

def dictfetchall(cursor):
    "Return all rows from a cursor as a dict"
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]


class FeatureData(object):
	_DATABASE='featuredata'
	_TABLE='featuredata'
	_dbindexname='dbindex'
	def _inspectdb(self):
		pass
	def _createtable(self):
		# if self.connection.vendor=='sqlite'
		with self.connectioncursor() as cursor:
			cursor.execute("""CREATE TABLE %(TABLENAME)s (
				id int PRIMARY KEY,
				Date date,
				Symbol varchar(20)
				);""")
			q=dictfetchall(cursor)

	def _createindex(self):
		with self.connectioncursor() as cursor:
			cursor.execute("CREATE UNIQUE INDEX %(dbindexname)s;"%{'dbindexname':self._dbindexname})
	

	def __init__(self):
		"""
		on iniitialization, inspect the table and get all the column names and types
		"""
		self.connection = connections[self._DATABASE]
		self.connectioncursor = connections[self._DATABASE].cursor



	def query(self):
		with self.connectioncursor() as cursor:
			cursor.execute("SELECT id, parent_id FROM test LIMIT 2")
			q=dictfetchall(cursor)
		return q