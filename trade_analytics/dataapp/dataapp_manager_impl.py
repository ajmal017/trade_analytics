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


class datamanager_impl(object):

	# @mnt.logperf('dataapp',printit=True)
	def addindicators(df,cols):
		if len(cols)==0:
			return df

		inputs = {
	    'open': df['Open'].values,
	    'high': df['High'].values,
	    'low': df['Low'].values,
	    'close': df['Close'].values,
	    'volume': df['Volume'].values
		}
		for cc in cols:
			if cc['colname'] not in df.columns:
				try:
					if cc['name']=='CCI':
						df[cc['colname']]=abstract.CCI(inputs, timeperiod=cc['timeperiod'])
						df[cc['colname']]=df[cc['colname']].astype(float)

					elif cc['name']=='SMA':
						df[cc['colname']]=df['Close'].rolling(window=cc['timeperiod']).mean()
						df[cc['colname']]=df[cc['colname']].astype(float)

					elif cc['name']=='SMAstd':
						df[cc['colname']]=df['Close'].rolling(window=cc['timeperiod']).std()

					elif cc['name']=='EMA':
						df[cc['colname']]=df['Close'].ewm(span=cc['timeperiod']).mean()
						df[cc['colname']]=df[cc['colname']].astype(float)

					elif cc['name']=='EMAstd':
						df[cc['colname']]=df['Close'].ewm(span=cc['timeperiod']).std(bias=False)
						df[cc['colname']]=df[cc['colname']].astype(float)
					elif cc['name']=='VolSMA':
						df[cc['colname']]=df['Volume'].rolling(window=cc['timeperiod']).mean()
						df[cc['colname']]=df[cc['colname']].astype(float)
					else:
						print "Indicator not available"

				except Exception as e:
					print "error adding indicator ",cc['colname']
					logger.error("error adding indicator "+cc['colname']+" "+str(type(e))+" "+str(e))
					logger.exception(e)

		return df


	# @mnt.logperf('dataapp',printit=True)
	def GetStockData(Symbolids,Fromdate=pd.datetime(2002,1,1).date(),Todate=pd.datetime.today().date(),format='concat',standardize=True,addcols=None):
		if type(Symbolids)==list:
			Symbolids=list(Symbolids)

		elif type(Symbolids)==tuple:
			Symbolids=list(Symbolids)

		elif type(Symbolids)==int or isinstance(Symbolids,basestring)==True:
			Symbolids=list([Symbolids])

		if isinstance(Symbolids[0],basestring)==True:
			for i in range(len(Symbolids)):
				Symbolids[i]=stkmd.Stockmeta.objects.get(Symbol=Symbolids[i]).id

		Symbolids=tuple(Symbolids)
		if len(Symbolids)==1:
			sqlquery="SELECT * FROM dataapp_stockprice as dsp WHERE dsp.\"Symbol_id\" = %(ids)s AND dsp.\"Date\" BETWEEN '%(fromdate)s' AND '%(todate)s';"
			sqlQ=sqlquery%{'ids':str(Symbolids[0]),'fromdate':Fromdate.strftime("%Y-%m-%d"),'todate':Todate.strftime("%Y-%m-%d")}

		else:
			sqlquery="SELECT * FROM dataapp_stockprice as dsp WHERE dsp.\"Symbol_id\" IN %(ids)s AND dsp.\"Date\" BETWEEN '%(fromdate)s' AND '%(todate)s';"
			sqlQ=sqlquery%{'ids':str(tuple(Symbolids)),'fromdate':Fromdate.strftime("%Y-%m-%d"),'todate':Todate.strftime("%Y-%m-%d")}

		df=pd.read_sql(sqlQ,connections[dtamd.Stockprice._DATABASE])
		df=StockDataFrame_sanitize(df,standardize=standardize)


		if format=='list':
			L=[]
			for symbid in Symbolids:
				dp=df[df['Symbol_id']==symbid].copy()
				if addcols is not None:
					dp=addindicators(dp,addcols)
				L.append( dp )
			return L

		elif format=='dict':
			D={}
			for symbid in Symbolids:
				dp=df[df['Symbol_id']==symbid].copy()
				if addcols is not None:
					dp=addindicators(dp,addcols)
				D[symbid]=dp
			return D


		elif format=='concat':
			return df





