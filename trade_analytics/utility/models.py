import abc
import json
import os
from django.db import models
# from django.contrib.auth.models import User
import shutil
import time
import pandas as pd
import copy
import pdb


def set_or_create(mdl,primary_fields={},secondary_fields={}):
	"""
	chekc by primary and then update using all primary and secondary
	"""
	# pdb.set_trace()

	primary_fields=copy.deepcopy(primary_fields)
	secondary_fields=copy.deepcopy(secondary_fields)

	fieldnames=[fld.name for fld in mdl._meta.get_fields()]
	pkeys=primary_fields.keys()
	for key in pkeys:
		if key not in fieldnames:
			del primary_fields[key]
	skeys=secondary_fields.keys()
	for key in skeys:
		if key not in fieldnames:
			del secondary_fields[key]

	# pdb.set_trace()

	if mdl.objects.filter(**primary_fields).exists():
		obj=mdl.objects.get(**primary_fields)
		for key,value in secondary_fields.items():
			setattr(obj,key,value)
		# pdb.set_trace()
		obj.save()
		# print "Updated feature ",featmeta

	else:
		primary_fields.update(secondary_fields)
		obj=mdl(**primary_fields)
		obj.save()


