from django.shortcuts import render
from django.http import HttpResponse
from django.template import RequestContext
from django import db

from . import models as md


import json
import time
import pdb
from multiprocessing import Process
import sys
from pathlib import Path
import os






from . import tasks as tks


def ViewCharts(request):
	context = RequestContext(request)
	context['error']=None

	if request.method == 'POST':
		if request.POST.get('view_charts', '')=="View Charts":
			viewchartform = md.Charts_view_form(request.POST,user=request.user)
			chartprop=md.Chartprops(request.POST,user=request.user)
			if viewchartform.is_valid() and chartprop.is_valid():
				if chartprop.cleaned_data['saved_chartstyles']=='':
					chartpropquery=chartprop.getquery()
				else:
					chartpropquery=chartprop.GetSavedChartProp()
				# print chartpropquery
				# pdb.set_trace()
				viewchartform.process_charts(user=request.user,chartpropquery=chartpropquery)
				
				# viewchartform = md.Charts_view_form(request.POST,username=request.user)
				# chartprop=md.Chartprops(request.POST)
			else:
				context['error']="invalid form return on watchlist/chartpprop select"
				viewchartform=md.Charts_view_form(user=request.user)
				chartprop=md.Chartprops(user=request.user)
		else:
			viewchartform=md.Charts_view_form(user=request.user)
				
		if request.POST.get('save_chartprop', '')=="Save Chart Properties as":
			chartprop=md.Chartprops(request.POST,user=request.user)
			if chartprop.is_valid():
				chartprop.update_chartstyle()
				viewchartform=md.Charts_view_form(user=request.user)
			else:
				context['error']="invalid chart name"
				viewchartform=md.Charts_view_form(user=request.user)
				chartprop=md.Chartprops(user=request.user)
		else:
			chartprop=md.Chartprops(user=request.user)
			# viewchartform=md.Charts_view_form(user=request.user)		
	else:
		viewchartform=md.Charts_view_form(user=request.user)
		chartprop=md.Chartprops(user=request.user)


	return render(request, 'charting/viewcharts.html', {'viewchartform': viewchartform,'chartprop':chartprop},context)
				
def Quickchart(request):

	Output=md.DecodeChartUrls(request.get_full_path())
	symbol=Output['symbol']
	window=Output['window']
	Interval=Output['Interval']
	tf=Output['tf']
	chartpropquery=Output['chartpropquery']
	chartstyle__pk=int(Output['chartstyle__pk'])
	upch_pk=int(Output['upch_pk'])
	chartname=Output['chartname']

	if upch_pk!=None and upch_pk!='':
		UC=md.UploadCharts.objects.get(pk=upch_pk)
		Symbol=UC.Symbol.Symbol
		T=UC.T
		window=UC.window
		Interval=UC.Interval
		pk=UC.pk
		db.connections.close_all()
		if bool(UC.image) is False:
			p=Process(target=tks.MakeChart, args=(Symbol,T.strftime("%Y,%m,%d"),window,Interval,pk,None))
			p.start()
			p.join()

			UC.refresh_from_db()
			return UC.load_responsepng(HttpResponse(content_type='image/png'))
		else:
			return UC.load_responsepng(HttpResponse(content_type='image/png'))

	else:
		if md.UploadCharts.objects.filter(user=None,chartname=chartname,chartstyle__pk=chartstyle__pk,window=window,T=tf,Symbol__Symbol=symbol,Interval=Interval).exists():
			UC=md.UploadCharts.objects.get(user=None,chartname=chartname,chartstyle__pk=chartstyle__pk,window=window,T=tf,Symbol__Symbol=symbol,Interval=Interval)
			return UC.load_responsepng(HttpResponse(content_type='image/png'))
		else:
			scp=md.StdChartProps.objects.get(pk=chartstyle__pk)
			UC=md.UploadCharts(user=None,chartname=chartname,chartstyle=scp,window=window,T=tf,Symbol__Symbol=symbol,Interval=Interval)
			UC.save()

		Symbol=UC.Symbol.Symbol
		T=UC.T
		window=UC.window
		Interval=UC.Interval
		pk=UC.pk
		db.connections.close_all()
		
		p=Process(target=tks.MakeChart, args=(Symbol,T.strftime("%Y,%m,%d"),window,Interval,pk,None))
		p.start()
		p.join()
		UC.refresh_from_db()
		return UC.load_responsepng(HttpResponse(content_type='image/png'))




# def Quickchart(request):
# 	print request.get_full_path()

# 	if md.SavedCharts.objects.filter(charttype=request.get_full_path().split('?')[1]).exists():
# 		print "Already exists"
# 		chart=md.SavedCharts.objects.get(charttype=request.get_full_path().split('?')[1])
# 		response=HttpResponse(content_type='image/png')
# 		response.content=chart.load_responsepng()
# 		return response


# 	symbol=request.GET.get('s', '')
# 	window=request.GET.get('w', '')
# 	Interval=request.GET.get('I', '')
# 	FromDate=request.GET.get('t0', '').split(',')
# 	ToDate=request.GET.get('tf', '').split(',')
	
# 	candle_indicators=request.GET.get('ci', '').split(',')
# 	volume_indicators=request.GET.get('vi', '').split(',')
# 	indicators=request.GET.get('i', '').split(',')
# 	candle_patterns=request.GET.get('cp', '').split(',')

# 	channels=request.GET.get('ch', '').split(',')
# 	LinearTrends=request.GET.get('lt', '').split(',')  #lt=top,mid,bottom

# 	if window!='':
# 		window=int(window)
# 	else:
# 		window=None

# 	if Interval=='':
# 		Interval='D'
			
# 	print "---"*5
# 	print symbol
# 	print FromDate
# 	print ToDate
# 	print Interval
# 	print window
# 	print candle_indicators
# 	print volume_indicators
# 	print indicators
# 	print candle_indicators
# 	print channels
# 	print LinearTrends
# 	print "+++"*5

# 	FromDate=[int(ff) for ff in FromDate]
# 	ToDate=[int(ff) for ff in ToDate]
# 	tf=pd.datetime(ToDate[0],ToDate[1],ToDate[2])

# 	if '' in FromDate and window is not None:
# 		t0=GC.GetWindowTfs(tf,window)[0]
# 	elif window is None and '' not in FromDate:
# 		t0=pd.datetime(FromDate[0],FromDate[1],FromDate[2])
# 		window=(tf-t0).days	
# 	else:
# 		t0=pd.datetime(FromDate[0],FromDate[1],FromDate[2])
# 		window=window


# 	stk=stkmd.Stock.objects.get(Symbol=symbol)
# 	df=stk.GetData(Fromdate=t0, Todate=tf )

# 	plotdeploy={
# 			  'show':False,
# 			  'save':True,
# 			  'mpld3':False,
# 			  'bokeh':False,
# 			  'savepath':HttpResponse(content_type='image/png'),
# 			  'ClosePlot':True,
# 			  'ImageCompress':False,
# 			  'XtremeImageCompress':False
# 			  }

# 	plotconfig={
# 			'bokeh':False,
# 			'fig':{'size':(20,15)}, 
# 			'subfig':[    
# 						 { 
# 						 'title':symbol,
# 						 'size':(10,15),   # has effect only for bokeh
# 						 'rowspan':2,
# 						 'Chart':'Price',
# 						 'type':'Candle',
# 						 'Dflines':{
# 								   # 'SMA10':{'norm':False,'c':'b','w':2},
# 								   # 'SMA20':{'norm':False,'c':'r','w':2},
# 								   # 'SMA50':{'norm':False,'c':'g','w':2},
# 								   # 'SMA100':{'norm':False,'c':'b--','w':3},
# 								   # 'SMA200':{'norm':False,'c':'r--','w':3}
# 								   }
								   
# 						 #'Customlines':[{'Xtype':'dates','X':[1,2,3],'Y':[3,2,1],'c':'r--','w':2}],
# 						 #'Circles':[{'Xtype':'dates','X0':3,'Y0':4,'R':1,'c':'g','w':2}]
# 						 },

# 						 {   
# 						 'title':'Volume',  
# 						 'size':(10,7),   # has effect only for bokeh
# 						 'rowspan':1,
# 						 'Chart':'Volume',
# 						 'type':'Bar',
# 						 'Dflines':{
# 								   # 'VolSMA10':{'norm':False,'c':'b','w':2},
# 								   # 'VolSMA20':{'norm':False,'c':'r','w':2}
# 									}
# 						 },

# 						 # {   
# 						 # 'title':'STD',
# 						 # 'size':(10,7),   # has effect only for bokeh
# 						 # 'rowspan':1,
# 						 # 'Chart':None,
# 						 # 'type':None,
# 						 # 'Dflines':{
# 						 #           'STD10':{'norm':True,'c':'b','w':2}
# 						 #           }
# 						 # },
				 
# 						 # {   
# 						 # 'title':'Amp SMA',
# 						 # 'size':(10,7),   # has effect only for bokeh
# 						 # 'rowspan':1,
# 						 # 'Chart':None,
# 						 # 'type':None,
# 						 # 'Dflines':{
# 						 #           'AmpSMA10':{'norm':True,'c':'b','w':2}
# 						 #           }
# 						 # },
						 
# 						 # {   
# 						 # 'title':'Max-Min SMA',
# 						 # 'size':(10,7),   # has effect only for bokeh
# 						 # 'rowspan':1,
# 						 # 'Chart':None,
# 						 # 'type':None,
# 						 # 'Dflines':{
# 						 #           'SMAmaxDiff':{'norm':True,'c':'b','w':2}
# 						 #           }
# 						 # }
				 
				 
				 
				 
# 					]
# 				}

# 	if '' not in candle_indicators:
# 		for ci in candle_indicators:
# 			plotconfig['subfig'][0]['Dflines'][ci]=stdsmaprops[ci]

# 	if '' not in volume_indicators:
# 		for vi in volume_indicators:
# 			plotconfig['subfig'][1]['Dflines'][vi]=stdsmaprops[vi]
# 	# pdb.set_trace()
# 	if '' not in channels:
# 		df=FE.LoadPattTubes(df)
# 		for ch in channels:
# 			plotconfig['subfig'][0]['Dflines'][ch+'_top']={'norm':False,'c':'r','w':2}
# 			plotconfig['subfig'][0]['Dflines'][ch+'_bottom']={'norm':False,'c':'r','w':2}

# 	if '' not in LinearTrends:
# 		if rmd.LinearTrends.objects.filter(Symbol=stkmd.Stock.objects.get(Symbol=symbol),T=tf.strftime("%Y-%m-%d"),window=window,Interval=Interval).exists()==False:
# 			Ltop,Lmid,Lbottom, Trendstop, TrendsMid, Trendsbottom=rmd.GenLinTrendWindFeat(stkmd.Stock.objects.get(Symbol=symbol),tf,window,Interval,lt=True,wf=False)
# 			if 'top' in LinearTrends:
# 				df['LinFittop']=Ltop
# 				plotconfig['subfig'][0]['Dflines']['LinFittop']={'norm':False,'c':'k','w':2}
# 			if 'mid' in LinearTrends:
# 				df['LinFitMid']=Lmid
# 				plotconfig['subfig'][0]['Dflines']['LinFitMid']={'norm':False,'c':'k','w':2}
# 			if 'bottom' in LinearTrends:
# 				df['LinFitbottom']=Lbottom
# 				plotconfig['subfig'][0]['Dflines']['LinFitbottom']={'norm':False,'c':'k','w':2}
# 		else:
# 			Dlin=rmd.LinearTrends.objects.get(Symbol=stkmd.Stock.objects.get(Symbol=symbol),T=tf.strftime("%Y-%m-%d"),window=window,Interval=Interval)
# 			if 'top' in LinearTrends:
# 				Trendstop=Dlin.GetTopTrends()
# 				df['LinFittop'],M=LTF.GetLineFromTrends_algo2(Trendstop,df)
# 				plotconfig['subfig'][0]['Dflines']['LinFittop']={'norm':False,'c':'k','w':3}

# 			if 'mid' in LinearTrends:
# 				TrendsMid=Dlin.GetMidTrends()
# 				df['LinFitMid'],M=LTF.GetLineFromTrends_algo2(TrendsMid,df)
# 				plotconfig['subfig'][0]['Dflines']['LinFitMid']={'norm':False,'c':'k','w':3}

# 			if 'bottom' in LinearTrends:
# 				Trendsbottom=Dlin.GetBottomTrends()
# 				df['LinFitbottom'],M=LTF.GetLineFromTrends_algo2(Trendsbottom,df)
# 				plotconfig['subfig'][0]['Dflines']['LinFitbottom']={'norm':False,'c':'k','w':3}


# 	q = Queue()
# 	p=Process(target=pltmag.PlotCandle, args=(df,plotconfig,plotdeploy,q))
# 	p.start()
# 	response=q.get()
# 	p.join()

	
# 	chart=md.SavedCharts(charttype=request.get_full_path().split('?')[1])
# 	chart.save_responsepng(response.content)
# 	chart.save()



# 	return response



def GetSavedchart(request):
	charttype=request.GET.get('charttype',None)
	print charttype
	try:
		chart=md.SavedCharts.objects.get(charttype=charttype)
		response=HttpResponse(content_type='image/png')
		response.content=chart.load_responsepng()
		return response
	except:
		return HttpResponse(content_type='image/png')







def Tvdatafeed(request,method):
	print "---===+++"*10
	print request
	print request.GET
	print method
	

	if method=='config':
		response_data ={
			'supports_search': 'false',
			'supports_group_request': 'true',
			'supported_resolutions': ["1", "5", "15", "30", "60", "1D", "1W", "1M"],
			'supports_marks': 'false',
			'supports_time': 'true'
		}
		# response_data ="""{
		# 	supports_search: false,
		# 	supports_group_request: true,
		# 	supported_resolutions: ["1", "5", "15", "30", "60", "1D", "1W", "1M"],
		# 	supports_marks: false,
		# 	supports_time: true
		# }""".replace('\n',' ').replace('\r',' ').replace('\t',' ')
		# return JsonResponse(response_data)
		return HttpResponse(json.dumps(response_data))
		# return HttpResponse('')
		# return None

	if method=='symbol_info':
		response_data ={
		   'symbol': "HMY",
		   'description': "HMY Inc",
		   'exchange-listed': "NYSE",
		   'exchange-traded': "NYSE",
		   'minmov': 1,
		   'minmov2': 0,
		   'pricescale': 2,
		   'has-dwm': 'true',
		   'has-intraday': 'true',
		   'has-no-volume': 'false',
		   'type': "stock",
		   'ticker': "HMY~0",
		   'timezone': 'America/New_York',
		   'session-regular': '0900-1600',
		}
		return HttpResponse(json.dumps(response_data))
		# return None

	#exactly the same as symbol_info but only for 1 symbol
	if method=='symbols':
		response_data ={
		   'symbol': "HMY",
		   'description': "HMY Inc",
		   'exchange-listed': "NYSE",
		   'exchange-traded': "NYSE",
		   'minmov': 1,
		   'minmov2': 0,
		   'pricescale': 2,
		   'has-dwm': 'true',
		   'has-intraday': 'true',
		   'has-no-volume': 'false',
		   'type': "stock",
		   'ticker': "HMY~0",
		   'timezone': 'America/New_York',
		   'session-regular': '0900-1600',
		}
		return HttpResponse(json.dumps(response_data))
		# return None
	if method=='history':
		symbol=request.GET.get('symbol', '')
		From=request.GET.get('from', '')
		To=request.GET.get('to', '')
		resolution=request.GET.get('resolution', '')
		
		response_data ={
		   "s": "ok",
		   "t": [1386493512, 1386493572, 1386493632, 1386493692],
		   "c": [42.1, 43.4, 44.3, 42.8],
		   "o": [41.0, 42.9, 43.7, 44.5],
		   "h": [43.0, 44.1, 44.8, 44.5],
		   "l": [40.4, 42.1, 42.8, 42.3],
		   "v": [12000, 18500, 24000, 45000]
		}

		return HttpResponse(json.dumps(response_data))


	if method=='marks':
		symbol=request.GET.get('symbol', '')
		From=request.GET.get('from', '')
		To=request.GET.get('to', '')
		resolution=request.GET.get('resolution', '')

		response_data ={
			"id": "[array of ids]",
			"time": "[array of times]",
			"color": "[array of colors]",
			"text": "[array of texts]",
			"label": "[array of labels]",
			"labelFontColor": "[array of label font colors]",
			"minSize": "[array of minSizes]",
		}

		return HttpResponse(json.dumps(response_data))

	if method=='quotes':
		symbols=request.GET.get('symbols', '')
		symbols=symbols.split(',')
		symbols=[ss.split(':')[1] for ss in symbols]

		response_data ={
							"s": "ok",
							"d": [{
								"s": "ok",
								"n": "NYSE:AA",
								"v": {
									"ch": "+0.16",
									"chp": "0.98",
									"short_name": "AA",
									"exchange": "NYSE",
									"description": "Alcoa Inc. Common",
									"lp": "16.57",
									"ask": "16.58",
									"bid": "16.57",
									"open_price": "16.25",
									"high_price": "16.60",
									"low_price": "16.25",
									"prev_close_price": "16.41",
									"volume": "4029041"
								}
							}, {
								"s": "ok",
								"n": "NYSE:F",
								"v": {
									"ch": "+0.15",
									"chp": "0.89",
									"short_name": "F",
									"exchange": "NYSE",
									"description": "Ford Motor Compan",
									"lp": "17.02",
									"ask": "17.03",
									"bid": "17.02",
									"open_price": "16.74",
									"high_price": "17.08",
									"low_price": "16.74",
									"prev_close_price": "16.87",
									"volume": "7713782"
								}
							}]
						}

		return HttpResponse(json.dumps(response_data))

	if method=="time":
		HttpResponse(int(time.time()))

	return HttpResponse(str(request)+"<br><br>"+str(request.GET)+"<br><br>"+str(method))