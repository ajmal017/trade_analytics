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

	def _inspectdb(self):
		pass
		
	def __init__(self):
		"""
		on iniitialization, inspect the table and get all the column names and types
		"""
		self.connectioncursor = connections[self._DATABASE].cursor



	def query(self):
		with self.connectioncursor() as cursor:
			cursor.execute("SELECT id, parent_id FROM test LIMIT 2")
			q=dictfetchall(cursor)
		return q