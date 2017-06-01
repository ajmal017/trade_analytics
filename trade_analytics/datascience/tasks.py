from __future__ import division
from celery import shared_task
import stockapp.models as stkmd
import dataapp.models as dtamd
import featureapp.models as ftmd
import datascience.models as dtscmd
import datascience.MLmodels as MLmd

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
	MLmodels=dtscmd.MLmodels.objects.filter(Status='UnTrained')
	for model in MLmodels:

		modelpath=model.modelpath()
		modelname=model.Name
		modelinfo=model.Misc['modelinfo']
		modelpara=model.Misc['modelpara']

		ModelCLass=MLmd.GetModelClass(model.Info['ModelClass'])
		
		MCL=ModelCLass.loadmodel(modelpath,modelname,modelinfo,modelpara)
		
		MCL.preprocessing_train(X_train,y_train)
		MCL.trainmodel(modelname)
		MCL.postprocess_model(modelname)
		MCL.savemodel(modelname,modelpath)
		MCL.preprocessing_test(X_test,y_test)
		metrics=MCL.getmetrics(modelname)
		model.Misc['metrics']=metrics
		model.save()
