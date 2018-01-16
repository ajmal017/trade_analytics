from __future__ import division
import pandas as pd
import pandas_datareader.data as web
import stockapp.models as stkmd
from django.db import connections
from dataapp import models as dtamd
import featureapp.models as ftamd
import utility.codemanager as utcdmng
import datetime
import time
import pdb
from talib import abstract
import numpy as np
from utility import maintenance as mnt
import json
import h5py
import pickle as pkl
import logging
logger=logging.getLogger('dataapp')

import time
import json

from dataapp import stdcolumns as dtastdcols

import dataapp.dataapp_manager_impl as dtamang_impl
# import dataapp.data_download.data_download.dataapp_downloadmanager_impl as dta_dwnld_mang_impl

def get_trading_dates():
	return dtamd.TradingDates.objects.all().values_list('Date',flat=True).distinct()



class DataManager(dtamang_impl):
	def __init__(self,collist):
		self.collist=collist

	def getdf(self):
		pass
		
	def addindicators(df,cols):
		pass

	def addstockmeta(self,df):
		pass

	# concat, dict, list
	def getstockdata_byrange(Symbolids,
						Fromdate=pd.datetime(2002,1,1).date(),
						Todate=pd.datetime.today().date(),
						format='concat'):
		pass
	def getstockdata_bydates(Symbolids,
						dates=pd.datetime(2002,1,1).date(),
						format='concat'):
		pass