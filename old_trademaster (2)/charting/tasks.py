from __future__ import unicode_literals
from __future__ import division

import pandas as pd

from django.contrib.auth.models import User

import tempfile
from django.core.files import File
from celery import shared_task


import CTA.PlotingManager as pltmag
import CTA.PatternRecognition.FeaturesExtraction as FE
import CTA.PatternRecognition.LinearTrendFit as LTF

stdsmaprops={
				'SMA10':{'norm':False,'c':'b','w':2},
				'SMA20':{'norm':False,'c':'r','w':2},
				'SMA50':{'norm':False,'c':'g','w':2},
				'SMA100':{'norm':False,'c':'b--','w':3},
				'SMA200':{'norm':False,'c':'r--','w':3},
				'VolSMA10':{'norm':False,'c':'b','w':2},
				'VolSMA20':{'norm':False,'c':'r','w':2},
}


@shared_task
def MakeChart(symbol,tf,window,Interval,upload__pk=None,chartpropquery__pk=None):
	from . import models as md
	from stockdata import models as stkmd
	from research import models as rmd
	from research import tasks as rmtk
	if type(tf)==str or type(tf)==unicode:
		try:
			tf=pd.to_datetime(tf,format="%Y,%m,%d")
		except:
			tf=pd.to_datetime(tf,format="%Y-%m-%d")

	stk=stkmd.Stock.objects.get(Symbol=symbol)
	if chartpropquery__pk==None:
		scp=md.StdChartProps.objects.get(chartstylename='@default@')
		chartpropquery=scp.GetChartProp()
		chartpropquery__pk=scp.pk

	UC=None
	if upload__pk!=None:
		UC=md.UploadCharts.objects.get(pk=int(upload__pk))
		chartpropquery=UC.chartstyle.GetChartProp()
		chartpropquery__pk=UC.chartstyle.pk

	else:
		# make a entry if upload__pk=-1
		if upload__pk==-1:
			if md.UploadCharts.objects.filter(chartsrc='C',chartstyle=md.StdChartProps.objects.get(pk=chartpropquery__pk), 
									window=int(window),Interval=Interval,T=tf,Symbol=stk,
									user=User.objects.get(username='@general@')).exists():
				UC=md.UploadCharts.objects.get(chartsrc='C',chartstyle=md.StdChartProps.objects.get(pk=chartpropquery__pk), 
									window=int(window),Interval=Interval,T=tf,Symbol=stk,
									user=User.objects.get(username='@general@'))
			else:
				UC=md.UploadCharts(chartsrc='C',chartstyle=md.StdChartProps.objects.get(pk=chartpropquery__pk), 
									window=int(window),Interval=Interval,T=tf,Symbol=stk,
									user=User.objects.get(username='@general@'))
				UC.save()


	

	t0=tf-pd.DateOffset(window)

	

	candle_indicators=chartpropquery['ci']
	volume_indicators=chartpropquery['vi']
	indicators=chartpropquery['i']
	candle_patterns=chartpropquery['cp']

	channels=chartpropquery['ch']
	LinearTrends=chartpropquery['lt']

	

	
	df=stk.GetData(Fromdate=t0, Todate=tf )
	stk.DeleteData()
	
	tempfigfile = tempfile.NamedTemporaryFile(suffix='.png',delete=False)
	plotdeploy={
			  'show':False,
			  'save':True,
			  'mpld3':False,
			  'bokeh':False,
			  'savepath':tempfigfile.name,
			  'ClosePlot':True,
			  'ImageCompress':False,
			  'XtremeImageCompress':True
			  }

	plotconfig={
			'bokeh':False,
			'fig':{'size':(20,15)}, 
			'subfig':[    
						 { 
						 'title':str(symbol),
						 'size':(10,15),   # has effect only for bokeh
						 'rowspan':2,
						 'Chart':'Price',
						 'type':'Candle',
						 'Dflines':{}
						 },

						 {   
						 'title':'Volume',  
						 'size':(10,7),   # has effect only for bokeh
						 'rowspan':1,
						 'Chart':'Volume',
						 'type':'Bar',
						 'Dflines':{}
						 },
					]
				}
	# pdb.set_trace()

	if '' not in candle_indicators and len(candle_indicators)>0:
		for ci in candle_indicators:
			plotconfig['subfig'][0]['Dflines'][ci]=stdsmaprops[ci]

	if '' not in volume_indicators and len(volume_indicators)>0:
		for vi in volume_indicators:
			plotconfig['subfig'][1]['Dflines'][vi]=stdsmaprops[vi]
	# pdb.set_trace()
	if '' not in channels and len(channels)>0:
		df=FE.LoadPattTubes(df)
		for ch in channels:
			plotconfig['subfig'][0]['Dflines'][ch+'_top']={'norm':False,'c':'r','w':2}
			plotconfig['subfig'][0]['Dflines'][ch+'_bottom']={'norm':False,'c':'r','w':2}

	if '' not in LinearTrends and len(LinearTrends)>0:
		if rmd.LinearTrends.objects.filter(Symbol=stkmd.Stock.objects.get(Symbol=symbol),T=tf.strftime("%Y-%m-%d"),window=window,Interval=Interval).exists()==False:
			rmtk.GenLinTrendsCustomFeats(symbol,tf,int(window),Interval,[],lintrendonly=True)
		
		if rmd.LinearTrends.objects.filter(Symbol=stkmd.Stock.objects.get(Symbol=symbol),T=tf.strftime("%Y-%m-%d"),window=window,Interval=Interval).exists()==True:
			Dlin=rmd.LinearTrends.objects.get(Symbol=stkmd.Stock.objects.get(Symbol=symbol),T=tf.strftime("%Y-%m-%d"),window=window,Interval=Interval)
			if 'top' in LinearTrends:
				Trendstop=Dlin.GetTopTrends()
				df['LinFittop'],M=LTF.GetLineFromTrends_algo2(Trendstop,df)
				plotconfig['subfig'][0]['Dflines']['LinFittop']={'norm':False,'c':'k','w':3}

			if 'mid' in LinearTrends:
				TrendsMid=Dlin.GetMidTrends()
				df['LinFitMid'],M=LTF.GetLineFromTrends_algo2(TrendsMid,df)
				plotconfig['subfig'][0]['Dflines']['LinFitMid']={'norm':False,'c':'k','w':3}

			if 'bottom' in LinearTrends:
				Trendsbottom=Dlin.GetBottomTrends()
				df['LinFitbottom'],M=LTF.GetLineFromTrends_algo2(Trendsbottom,df)
				plotconfig['subfig'][0]['Dflines']['LinFitbottom']={'norm':False,'c':'k','w':3}




	pltmag.PlotCandle(df,plotconfig,plotdeploy,None)
	
	temp = open(tempfigfile.name, 'r')
	UC.image = File(temp)
	UC.save()
	tempfigfile.close()



	import gc
	gc.collect()

	return "done"

@shared_task
def MakeAllCharts_T(T,window=360,Interval='D'):
	if type(T)==str or type(T)==unicode:
		T=pd.to_datetime(T,format="%Y-%m-%d")
		
	from stockdata import models as stkmd
	import charting.models as md
	chartstyle__pk=md.StdChartProps.objects.get(chartstylename='@defaultlinear@').pk
	L=stkmd.Stock.objects.all().count()
	for stk in stkmd.Stock.objects.all().order_by('LastPriceUpdate'):
		L=L-1
		print [T,stk.Symbol,L]
		md.UploadCharts.GetCreateMakeChart(stk.Symbol ,T,window,Interval,'StockChart','C',chartstyle__pk )