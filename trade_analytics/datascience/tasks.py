from __future__ import division
from celery import shared_task
import stockapp.models as stkmd
import dataapp.models as dtamd
import featureapp.models as ftmd
import datascience.models as dtscmd
import datascience.ML.MLmodels as MLmd

import itertools as itt
import numpy as np
import multiprocessing as mp
from Queue import Empty
import time
import pandas as pd
from django import db

import logging
logger = logging.getLogger('debug')



def TrainAllmodels():
	TData=MLmd.Data.objects.filter(Datatype='Train')
	for Data in TData:
		MLmodels=dtscmd.MLmodels.objects.filter(Data=Data,Status='UnTrained')
		for model in MLmodels:
			

			ModelCLass=MLmd.ModelFactory(model)
			
			MCL=ModelCLass(model)
			MCL.loadmodel()
			MCL.loaddata()
			MCL.train()
			MCL.Run_validation_all()
			MCL.savemodel()


