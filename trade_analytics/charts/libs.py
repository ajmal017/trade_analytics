from __future__ import division
import matplotlib
matplotlib.use('Agg', force=True)
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter, WeekdayLocator,\
	DayLocator, MONDAY,date2num,num2date,AutoDateLocator
from matplotlib.finance import quotes_historical_yahoo_ohlc, candlestick_ohlc,candlestick2_ochl

import dataapp.libs as dtalibs
import featureapp.libs as ftlibs
import stockapp.models as stkmd

import numpy as np
import pandas as pd
import base64
import gc
try:
	from cStringIO import StringIO
except:
	from StringIO import StringIO

import time






def MakeChart_1(df,pricecols,querycols,featcols):
	"""
	pricecols are additional columns that have same range as close
	querycols are true/false snapped to close price
	featcols are additional that are plotted below
	
	For example:
	pricecols=[{'colname':'sma20','plotargs':('g',),'plotkwargs':{'label':'sma20',}},
		  {'colname':'sma50','plotargs':('r',),'plotkwargs':{'label':'sma50',}}]
	querycols=[{'colname':'hasCherries','plotargs':('y',),'plotkwargs':{'label':'hasCherries','marker':'o','markersize':15,'linestyle':''}}]
	featcols=[ [{'colname':'cci5','plotargs':('r--',),'plotkwargs':{'label':'cci5',}}],
			   [ {'colname':'cci50','plotargs':('g',),'plotkwargs':{'label':'cci50',}}]
			 ]  
	"""
#     df=dF[T0:T].copy()
#     dfperf=dF[T:(T+pd.DateOffset(360)).date()].copy()
	
	df['datenum']=date2num(df.index)
	autodate=AutoDateLocator()
	mondays = WeekdayLocator(MONDAY)        # major ticks on the mondays
	alldays = DayLocator()              # minor ticks on the days
	weekFormatter = DateFormatter('%Y %b %d')  # e.g., Jan 12
	dayFormatter = DateFormatter('%d')      # e.g., 12
	
	Nsubplots=len(featcols)
	fig, ax = plt.subplots(1,2,figsize=(15,7+2*Nsubplots))
#     plt.figure(num=None, figsize=(30, 10), dpi=80, facecolor='w', edgecolor='k')
#     fig.subplots_adjust(bottom=0.2)
	ax1 = plt.subplot2grid((2+Nsubplots, 1), (0, 0), rowspan=2)
	axft=[]
	for i in range(Nsubplots):
		axft.append(plt.subplot2grid((2+Nsubplots, 1), (2+i, 0),sharex=ax1))
		
	ax1.xaxis.set_major_locator(autodate)
	ax1.xaxis.set_minor_locator(alldays)
	ax1.xaxis.set_major_formatter(weekFormatter)
	
	

	quotes=[tuple(x) for x in df[['datenum','Open','High','Low','Close','Volume']].to_records(index=False)]
	ret=candlestick_ohlc(ax1, quotes, width=0.6)
	
	for prcl in pricecols:
		ax1.plot(df['datenum'],df[prcl['colname'] ],*prcl['plotargs'],**prcl['plotkwargs'] )
	
	L=df['High'].max()-df['Low'].min()
	mm=df['Volume'].max()
	ax1.bar(df['datenum'],0.5*L*df['Volume']/mm,bottom=df['Low'].min()-1.5,color='y',alpha=0.5)
#     volume_overlay3(ax[0], quotes, colorup='k', colordown='r', width=4, alpha=1.0)
	
	df['gap']=0
	for qcl in  querycols:
		dp=df[df[qcl['colname']]==True]
		ax1.plot(dp['datenum'],dp['High']+dp['gap'],*qcl['plotargs'],**qcl['plotkwargs'])
		for gind in dp.index:
			df.loc[gind,'gap']=df.loc[gind,'gap']+2

	ax1.set_xlim(quotes[0][0],quotes[-1][0])
	ax1.set_ylim(df['Low'].min()*0.9,df['High'].max()*1.1)
	ax1.xaxis_date()
	ax1.xaxis.tick_top()
	ax1.autoscale_view()
	ax1.legend()
	ax1.grid()
	
	ax12 = ax1.twinx()
	ax12.set_ylim(df['Low'].min()*0.9,df['High'].max()*1.1)
	ax12.grid()
	
	plt.setp(ax1.get_xticklabels(), rotation=45, horizontalalignment='left')
		
	for i in range(len(featcols)):
		autodate=AutoDateLocator()
		mondays = WeekdayLocator(MONDAY)        # major ticks on the mondays
		alldays = DayLocator()              # minor ticks on the days
		weekFormatter = DateFormatter('%Y %b %d')  # e.g., Jan 12
		dayFormatter = DateFormatter('%d')      # e.g., 12
		
		axft[i].xaxis.set_major_locator(autodate)
		axft[i].xaxis.set_minor_locator(alldays)
		axft[i].xaxis.set_major_formatter(weekFormatter)
		
		ftymax=-1000000
		ftymin=100000
		for ft in featcols[i]:
			axft[i].plot(df['datenum'],df[ ft['colname'] ],*ft['plotargs'],**ft['plotkwargs'])
			ftymin=min([ftymin,df[ft['colname']].min()])
			ftymax=max([ftymax,df[ft['colname']].max()])

#         axft[i].set_ylim(ftymin*0.8,ftymax*1.2)
		axft[i].set_xlim(quotes[0][0],quotes[-1][0])
		axft[i].autoscale_view()
		axft[i].legend()
		axft[i].grid()
		
		if i==len(featcols)-1:
			axft[i].xaxis_date()
			plt.setp(axft[i].get_xticklabels(), rotation=45, horizontalalignment='right')
		else:
			axft[i].get_xaxis().set_visible(False)


	figfile = StringIO()
	fig.savefig(figfile,bbox_inches='tight',format='png')
	time.sleep(0.1)
	plt.close(fig)
	figfile.seek(0)
	image= base64.b64encode(figfile.getvalue())
	gc.collect()
	return image


def CurrentByFutureChart_bydf(T0,TF,pricecols=(),querycols=(),featcols=(),df=pd.DataFrame()):
	if df.empty:
		return None

	img1=MakeChart_1(df[T0:TF],pricecols,querycols,featcols)
	img2=MakeChart_1(df[TF:(TF+pd.DateOffset(180)).date()],pricecols,querycols,featcols)
	return {'T0':T0,'TF':TF,'image':[img1,img2]}

def CurrentByFutureChart_bydb(T0,TF,Symbol,indicatorlist=(),pricecols=(),querycols=(),featcols=()):
	stk=stkmd.Stockmeta.objects.get(Symbol=Symbol)
	df=dtalibs.GetStockData([stk.id])
	df=dtalibs.addindicators(df,indicatorlist)

	df=ftlibs.GetFeature(Symbolids=[stk.id],dfmain=df)
	for prcl in pricecols:
		if prcl['colname'] not in df.columns:
			df[prcl['colname'] ]=np.nan
	
	for qrycl in querycols:
		if qrycl['colname'] not in df.columns:
			df[qrycl['colname'] ]=np.nan
	
	for ftcl in featcols:
		if ftcl['colname'] not in df.columns:
			df[ftcl['colname'] ]=np.nan

	img1=MakeChart_1(df[T0:TF],pricecols,querycols,featcols)
	img2=MakeChart_1(df[TF:(TF+pd.DateOffset(180)).date()],pricecols,querycols,featcols)
	return {'T0':T0,'TF':TF,'image':[img1,img2]}