from __future__ import unicode_literals
from __future__ import division
import time 
import numpy as np
import pandas as pd
from itertools import repeat
import copy
import sys
from pathlib import Path
from os import path
from celery import shared_task,result
import json
import pdb
from django.core.mail import EmailMessage
import tzlocal
from memory_profiler import profile
import gc

def chunks(l, n):
	"""Yield successive n-sized chunks from l."""
	for i in range(0, len(l), n):
		yield l[i:i+n]

@shared_task
def add(x,y):
	return x+y


@shared_task
def GenLinTrendsCustomFeats(symb,T,window,Interval,featids,lintrendonly=False,stockDFfilters=['Close>=2']):
	import research.featuremanager as featmng

	if type(T)==str or type(T)==unicode:
		T=pd.to_datetime(T,format="%Y-%m-%d")
	from . import models as md
	import stockdata.models as stkmd
	
	import CTA.GenConfig as GC
	import CTA.PatternRecognition.LinearTrendFit as LTF

	stks=stkmd.Stock.objects.get(Symbol=symb)

	print stks


	t0=GC.GetWindowTfs(T,window)[0]

	DF= stks.GetData(Fromdate=t0,Todate=T ) #Dfpm1y[t0:T].copy()
	if DF.empty:
		return "Empty"
	if DF.index[-1]!=T:
		print "Need to update Data for "+str(symb)+ " to date "+T.strftime("%Y-%m-%d")
		return "Need to update Data for "+str(symb)+ " to date "+T.strftime("%Y-%m-%d")

	if len(DF)<0.6*window:
		print "Not enough data in the window"
		return "Not enough Data"
	if len( DF[pd.isnull(DF['Close']) | pd.isnull(DF['Volume'])] )>0.3*window:
		print "nans in data"
		return "Nans in data"
	
	if len(stockDFfilters)>0:
		if 'Close>=2' in stockDFfilters:
			if DF['Close'].mean() <2:
				print "Close price has to be greater than 2"
				return "Close price has to be greater than 2"


	# Get the combined feature entry
	if md.CombinesFeaturesEntry.objects.filter(window=window,T=T,Symbol=stks,Interval = Interval).exists():
		 gfeatentry=md.CombinesFeaturesEntry.objects.get(window=window,T=T,Symbol=stks,Interval = Interval)
	else:
		gfeatentry=md.CombinesFeaturesEntry(window=window,T=T,Symbol=stks,Interval = Interval) 
		gfeatentry.save()


	TrendsMid=None
	LMid=None
	TrendsTop=None
	LTop=None
	TrendsBottom=None
	LBottom=None


	if md.LinearTrends.objects.filter(Symbol=stks,T=T.strftime("%Y-%m-%d"),window=window,Interval=Interval).exists()==True:
		pass
	else:
		

		sttime=time.time()
		windcndlslen=len(DF)
		FLG=0
		try:
			PP=LTF.LinTrendfitcvx(DF['Close'],weights=None,method='mid',PLOT='No',InterpRes=int(0.5*windcndlslen),vlambda=10,vlambda_bias=20,NchannelStrength=10)
			TrendsMid=PP[0]
			LMid=PP[1]
			DF['LinFitMid']=LMid
			FLG=FLG+1
		except:
			pass
		

		try:
			PPtop=LTF.LinTrendfitcvx(DF['High'],weights=None,method='top',PLOT='No',InterpRes=int(0.5*windcndlslen),vlambda=20,vlambda_bias=5,NchannelStrength=5)
			TrendsTop=PPtop[0]
			LTop=PPtop[1]
			DF['LinFitTop']=LTop
			FLG=FLG+1
		except:
			pass
		

		try:
			PPbottom=LTF.LinTrendfitcvx(DF['Low'],weights=None,method='bottom',PLOT='No',InterpRes=int(0.5*windcndlslen),vlambda=20,vlambda_bias=5,NchannelStrength=5)
			TrendsBottom=PPbottom[0]
			LBottom=PPbottom[1]
			DF['LinFitBottom']=LBottom	
			FLG=FLG+1
		except:
			pass
		
		if FLG==3:
			Dlin=md.LinearTrends(Symbol=stks,T=T.strftime("%Y-%m-%d"),window=window,Interval=Interval)
			Dlin.UpdateTrends(top=TrendsTop,mid=TrendsMid,bottom=TrendsBottom)
			Dlin.save()
			print "time taken for Lin Trend is "+str(time.time()-sttime)
			print "Done with Liner trends for "+str(stks)
		else:
			print "Some linear fits not done so not saving anything"
			if md.LinearTrends.objects.filter(Symbol=stks,T=T.strftime("%Y-%m-%d"),window=window,Interval=Interval).exists():
				Dlin=md.LinearTrends.objects.get(Symbol=stks,T=T.strftime("%Y-%m-%d"),window=window,Interval=Interval)
				Dlin.delete()


	if md.LinearTrends.objects.filter(Symbol=stks,T=T.strftime("%Y-%m-%d"),window=window,Interval=Interval).exists():
		Dlin=md.LinearTrends.objects.get(Symbol=stks,T=T.strftime("%Y-%m-%d"),window=window,Interval=Interval)
		TrendsMid=Dlin.GetMidTrends()
		TrendsTop=Dlin.GetTopTrends()
		TrendsBottom=Dlin.GetBottomTrends()
	else:
		TrendsMid=pd.DataFrame()
		TrendsTop=pd.DataFrame()
		TrendsBottom=pd.DataFrame()

	# pdb.set_trace()

	DF['LinFitTop'],DF['LinSlpTop']=LTF.GetLineFromTrends_algo2(TrendsTop,DF)
	DF['LinFitMid'],DF['LinSlpMid']=LTF.GetLineFromTrends_algo2(TrendsMid,DF)
	DF['LinFitBottom'],DF['LinSlpBottom']=LTF.GetLineFromTrends_algo2(TrendsBottom,DF)

	if lintrendonly==True:
		return
	
	if md.GeneralFeatureValue.objects.filter(gfeatentry=gfeatentry,gfeature_id__in=featids,value__gte=-100000,value__lte=100000).count()!=len(featids):

		value_save={}   
		with featmng.featuremanager() as FM:
			FM.LoadEvalData(DF,TrendsMid,  TrendsTop,  TrendsBottom)
			FM.LoadFeatureModule()

			for fid in featids:
				feat=md.GeneralFeature.objects.get(pk=fid)
				if str(feat.name) in md.PerfFeats:
					continue
			
				value=FM.EvalFeatures(str(feat.name))
				value_save[feat]=value
				print "Done feat "+str(feat.name) +' '+str(feat.pk)+' for '+str(stks)

		
		for feat,value in value_save.items():   
			if md.GeneralFeatureValue.objects.filter(gfeatentry=gfeatentry,gfeature=feat).exists()==False:
				GFV=md.GeneralFeatureValue(gfeatentry=gfeatentry,gfeature=feat,value=value)
				GFV.save()


			else:
				GFV=md.GeneralFeatureValue.objects.get(gfeatentry=gfeatentry,gfeature=feat)
				GFV.value=value;
				GFV.save()

		###### -------- Mandatory Performance featuers 
		# stkmd.BasicInitialize()
		Dfpm1y=stks.GetData(Fromdate=(t0-pd.DateOffset(90)),Todate=(T+pd.DateOffset(360)) )
		if Dfpm1y.empty:
			return "Empty"
		
		p=str( Path(path.abspath(__file__)).parents[2] )
		sys.path.append(p)
		import CTA.PatternRecognition.FeaturesExtraction as FE
		perffeats=FE.GetFutPastPerf(Dfpm1y,t0,T)
		for pf,value in perffeats.items():
			if np.isnan(value)==True:
				value=None
				
			feat=md.GeneralFeature.objects.get(name=pf)
			if md.GeneralFeatureValue.objects.filter(gfeatentry=gfeatentry,gfeature=feat).exists():
				GFV=md.GeneralFeatureValue.objects.get(gfeatentry=gfeatentry,gfeature=feat)
				GFV.value=value
				GFV.save()
			else:
				GFV=md.GeneralFeatureValue(gfeatentry=gfeatentry,gfeature=feat,value=value)    
				GFV.save()  

	stks.ClearData()
	del DF
	try:
		del Dfpm1y
	except:
		pass

	del stks
	del GC
	del LTF
	try:
		del Dlin
	except:
		pass

	try:
		del TrendsMid
	except:
		pass
	try:
		del TrendsTop
	except:
		pass
	try:
		del TrendsBottom
	except:
		pass

	try:
		del FE
	except:
		pass
	try:
		GFV
	except:
		pass

	try:
		del PP
	except:
		pass
	try:
		del PPtop
	except:
		pass
	try:
		del PPbottom
	except:
		pass

	gc.collect()

	return "Done all for stock = "+str(symb)



@shared_task
def GenLinTrendsCustomFeats_chunks(argss):
	for argg in argss:
		try:
			GenLinTrendsCustomFeats(argg[0],argg[1],argg[2],argg[3],argg[4])
		except:
			print "failed for ",argg[0],argg[1],argg[2],argg[3],argg[4]
	return "Done all"


@shared_task
def ComputeAllFeatures(TT=[pd.datetime.today()],window=360,Interval='D'):
	for i in range(len(TT)):
		if type(TT[i])==str or type(TT[i])==unicode:
			TT[i]=pd.to_datetime(TT[i],format="%Y-%m-%d")

	window=int(window)
	import stockdata.models as stkmd
	from . import models as md


	stocks_symbs=list(stkmd.Stock.objects.all().values_list('Symbol',flat=True) ) 
	stocks_symbs=[s for s in stocks_symbs if len(s)<=4]

	featids=list(md.GeneralFeature.objects.all().values_list('pk',flat=True))
	args_compute=[]
	for T in TT:
		print T			
		args_compute=args_compute+zip(stocks_symbs,repeat(T.strftime("%Y-%m-%d")),repeat(window),repeat(Interval),repeat(featids) )


	starttime=time.time()
	for argg_chnk in chunks(args_compute,50):
	    GenLinTrendsCustomFeats_chunks.delay(argg_chnk) 
	try:
		del args_compute
	except:
		pass
	
	
	print "time taken to do all args in is "+str(time.time()-starttime)


	return "All jobs sent and done"


@shared_task
def SectorIndustryPerfProfiles(TT=[pd.datetime.today()],window=360,Interval='D'):
	for i in range(len(TT)):
		if type(TT[i])==str or type(TT[i])==unicode:
			TT[i]=pd.to_datetime(TT[i],format="%Y-%m-%d")


	from . import models as md
	from .libs import per20,per50,per80
	import stockdata.models as stkmd
	watchlists=stkmd.Watchlist.objects.all()
	for T in TT:
		for W in watchlists:
			if md.WatchlistPerf.objects.filter(watchlist=W,T=T).exists():
				print 'done with ', T,' ' ,str(W)
				WPF=md.WatchlistPerf.objects.get(watchlist=W,T=T)
			else:
				WPF=md.WatchlistPerf(watchlist=W,T=T)

			stk_ids=W.stocks.values_list('pk',flat=True)
			if len(stk_ids)<=5:
				print 'Too few stocks in this watchlist need atleast 5'
				continue

			print T, str(W),len(stk_ids)
			dfgf=pd.DataFrame(list( md.GeneralFeature.objects.filter(name__in=md.PerfFeats).values('pk','name') )).rename(columns={'pk':'gfeature_id'})
			dfgf['gfeature_id']=dfgf['gfeature_id'].astype(int)
			dfgf['name']=dfgf['name'].astype(str)

			CFE_pk=md.CombinesFeaturesEntry.objects.filter(window=window,Interval=Interval,T=T,Symbol_id__in=stk_ids).values_list('pk',flat=True)
			
			if len(CFE_pk)==0:
				continue

			df=pd.DataFrame(list(md.GeneralFeatureValue.objects.filter(gfeature_id__in=dfgf['gfeature_id'].tolist(),gfeatentry_id__in=CFE_pk)
																							.values('value','gfeature_id')))
			if df.empty:
				continue
			df['value']=df['value'].astype(float)
			df['gfeature_id']=df['gfeature_id'].astype(int)

			dd=pd.merge(df,dfgf,how='left',on=['gfeature_id'])
			del df
			del dfgf
			dd.drop('gfeature_id',axis=1,inplace=True)

			df=dd.groupby('name').agg({'value':[per20,per50,per80]})
			del dd
			dd=df
			# pdb.set_trace()
			dd=dd.round(decimals=2)

			WPF.PastMNRtAn_per20=dd.loc['PastMNRtAn','value']['per20']			
			WPF.PastMNRtAn_per50=dd.loc['PastMNRtAn','value']['per50']
			WPF.PastMNRtAn_per80=dd.loc['PastMNRtAn','value']['per80']

			WPF.PastMNRtHf_per20=dd.loc['PastMNRtHf','value']['per20']
			WPF.PastMNRtHf_per50=dd.loc['PastMNRtHf','value']['per50']
			WPF.PastMNRtHf_per80=dd.loc['PastMNRtHf','value']['per80']
			
			WPF.PastMNRtQt_per20=dd.loc['PastMNRtQt','value']['per20']
			WPF.PastMNRtQt_per50=dd.loc['PastMNRtQt','value']['per50']
			WPF.PastMNRtQt_per80=dd.loc['PastMNRtQt','value']['per80']

			WPF.PastMXRtAn_per20=dd.loc['PastMXRtAn','value']['per20']			
			WPF.PastMXRtAn_per50=dd.loc['PastMXRtAn','value']['per50']
			WPF.PastMXRtAn_per80=dd.loc['PastMXRtAn','value']['per80']

			WPF.PastMXRtHf_per20=dd.loc['PastMXRtHf','value']['per20']
			WPF.PastMXRtHf_per50=dd.loc['PastMXRtHf','value']['per50']
			WPF.PastMXRtHf_per80=dd.loc['PastMXRtHf','value']['per80']
			
			WPF.PastMXRtQt_per20=dd.loc['PastMXRtQt','value']['per20']
			WPF.PastMXRtQt_per50=dd.loc['PastMXRtQt','value']['per50']
			WPF.PastMXRtQt_per80=dd.loc['PastMXRtQt','value']['per80']

			WPF.save()
			del dd
			gc.collect()



@shared_task
def ProcessSavedQuery(SQ_pk,T):
	gc.collect()
	from . import models as md
	from . import libs
	if type(T)==str or type(T)==unicode:
		T=pd.to_datetime(T,format="%Y-%m-%d")

	if md.SavedQueries.objects.filter(pk=int(SQ_pk) ).exists()==False:
		print "SQ with given pk = ",SQ_pk," does nto exist"
		return "SQ with given pk = ",SQ_pk," does nto exist"

	SQ=md.SavedQueries.objects.get(pk=int(SQ_pk) )
	window=SQ.window
	Interval=SQ.Interval
	filjson=json.loads(SQ.Filjson)

	# # ---------------------START QUERY----------------------------
	starttime=time.time()

	CFE=md.CombinesFeaturesEntry.objects.filter(T=T,window=window,Interval=Interval)
	if CFE.count()==0:
		print "No CFE objects for this date = "+T.strftime("%Y-%m-%d")
		return "No CFE objects for this date = "+T.strftime("%Y-%m-%d")

	GF=md.GeneralFeature.objects.all()
	GFV=md.GeneralFeatureValue.objects.all()
	df=libs.SQLquery_Q_rawsql(GFV,CFE,GF,filjson,int(window) )

	if df.empty:
		print "Query returned empty dataframe for T = "+T.strftime("%Y-%m-%d")
		return "Query returned empty dataframe for T = "+T.strftime("%Y-%m-%d")
		
	print "time taken first query "+str(time.time()-starttime)

	# # ---------------------END QUERY----------------------------

	import charting.models as chrtmd
	df['Ycharts']=df.apply(lambda row: chrtmd.GetYahooCharts_url(row['Symbol'],row['window']),axis=1)
	df=df.round(decimals=2)

	df['No']=df.index
	

	if md.SavedQueries_DF.objects.filter(savedquery=SQ,T=T).exists():
		SQDF=md.SavedQueries_DF.objects.get(savedquery=SQ,T=T)
	else:
		SQDF=md.SavedQueries_DF(savedquery=SQ,T=T)

	SQDF.DFname='QueryDF'
	SQDF.uploadDF(df)
	SQDF.save()

	# pdb.set_trace()
	from . import plotmanager as pltmng
	pltmng.SummaryPlots(df,returnfmt={'SQ':{'SQ':SQ,'T':T}}  )
	# pdb.set_trace()
	del SQDF
	del SQ
	del df

	gc.collect()


	return "Done"


@shared_task
def ComputeAllSavedQueries(TT=[pd.datetime.today().strftime("%Y-%m-%d")]):
	from . import models as md
	SQs=md.SavedQueries.objects.all()
	for T in TT:
		for SQ in SQs:
			ProcessSavedQuery(SQ.pk,T)


@shared_task
def SequenceJobs_1(TT=[]):
	email = EmailMessage('Inside Seq_1', 'Ok', to=['n.adurthi@gmail.com'])
	email.send()

	if len(TT)==0:
		TT=[]
		for i in range(1,9):
			T=(pd.datetime.today()-pd.DateOffset(i))
			if T.weekday()<5:
				TT.append(T.strftime("%Y-%m-%d"))
				break

	
	TTweekday=[]
	for i in range(len(TT)):		
		if type(TT[i])==str or type(TT[i])==unicode:
			T=pd.to_datetime(TT[i],format="%Y-%m-%d")
		if T.weekday()<5:
			TTweekday.append(TT[i])
	# import pdb
	# pdb.set_trace()
	print 'dates are', TT, ' : ',TTweekday
	if len(TTweekday)>0:		
		print 'working on', TTweekday
		import stockdata.tasks as stktks
		email = EmailMessage('Stock Update', 'Started '+str(TTweekday), to=['n.adurthi@gmail.com'])
		email.send()
		stktks.process_stock_update()
		
		email = EmailMessage('StockUpdate Done', 'ComputeAllFeatures started '+str(TTweekday), to=['n.adurthi@gmail.com'])
		email.send()
		ComputeAllFeatures(TT=TTweekday,window=360,Interval='D')
		email = EmailMessage('ComputeAllFeatures ended', ' wait for them to complete '+str(TTweekday), to=['n.adurthi@gmail.com'])
		email.send()

	else:
		return "runs only on weeday dates"


@shared_task
def SequenceJobs_2(TT=[] ):
	email = EmailMessage('Inside Seq_2', 'Ok', to=['n.adurthi@gmail.com'])
	email.send()

	if len(TT)==0:
		TT=[]
		for i in range(1,9):
			T=(pd.datetime.today()-pd.DateOffset(i))
			if T.weekday()<5:
				TT.append(T.strftime("%Y-%m-%d"))
				break

	
	TTweekday=[]
	for i in range(len(TT)):		
		if type(TT[i])==str or type(TT[i])==unicode:
			T=pd.to_datetime(TT[i],format="%Y-%m-%d")
		if T.weekday()<5:
			TTweekday.append(TT[i])

	print 'dates are', TT, ' : ',TTweekday
	if len(TTweekday)>0:	
		print 'working on', TTweekday	
		email = EmailMessage('SectorIndustryPerfProfiles Started', 'Ok '+str(TTweekday), to=['n.adurthi@gmail.com'])
		email.send()
		SectorIndustryPerfProfiles(TT=TTweekday,window=360,Interval='D')

		email = EmailMessage('SectorIndustryPerfProfiles ended', ' and ComputeAllSavedQueries started '+str(TTweekday), to=['n.adurthi@gmail.com'])
		email.send()


		ComputeAllSavedQueries(TT=TTweekday)
		email = EmailMessage('ComputeAllSavedQueries ended', ' and ComputeStatus started '+str(TTweekday), to=['n.adurthi@gmail.com'])
		email.send()

		import research.libs as libs
		libs.MasterQueryUpdate(TT=TTweekday,window=360,Interval='D')
		email = EmailMessage('ComputeStatus ended', ' Updating master table '+str(TTweekday), to=['n.adurthi@gmail.com'])
		email.send()

		libs.ComputeStatus_master(TT=TTweekday)
		email = EmailMessage('Done Master Table Update', '  All done  '+str(TTweekday), to=['n.adurthi@gmail.com'])
		email.send()

		

	else:
		return "runs only on weeday dates"

@shared_task
def SequenceJobs_3(TT=[] ):
	email = EmailMessage('Inside Seq_3', 'Ok', to=['n.adurthi@gmail.com'])
	email.send()

	if len(TT)==0:
		TT=[]
		for i in range(1,9):
			T=(pd.datetime.today()-pd.DateOffset(i))
			if T.weekday()==5:
				TT.append(T.strftime("%Y-%m-%d"))
				break

	
	TTweekday=[]
	for i in range(len(TT)):		
		if type(TT[i])==str or type(TT[i])==unicode:
			T=pd.to_datetime(TT[i],format="%Y-%m-%d")
		if T.weekday()==5:
			TTweekday.append(TT[i])

	print 'dates are', TT, ' : ',TTweekday
	if len(TTweekday)>0:	
		print 'working on', TTweekday	
		
		import research.libs as libs
		libs.MasterQueryUpdate(window=360,Interval='D')
		email = EmailMessage('ComputeStatus ended', ' Updating master table '+str(TTweekday), to=['n.adurthi@gmail.com'])
		email.send()

		libs.ComputeStatus_master()
		email = EmailMessage('Done Master Table Update', '  All done  '+str(TTweekday), to=['n.adurthi@gmail.com'])
		email.send()

		

	else:
		return "runs only on weedend dates"

@shared_task
def DownloadQuery_recursive(GNFcsv_pk,window,Interval,filjson,Tf,T0,watchlist_pk,Symbols):
	from . import libs
	import stockdata.models as stkmd
	import research.models as rmd
	import charting.models as chrtmd

	if type(Tf)==str or type(Tf)==unicode:
		Tf=pd.to_datetime(Tf,format="%Y-%m-%d")

	if type(T0)==str or type(T0)==unicode:
		T0=pd.to_datetime(T0,format="%Y-%m-%d")

	TT=libs.GetHistoricalQueryTdate(Tf,T0)

	chartstyle__pk=chrtmd.StdChartProps.objects.get(chartstylename='@defaultlinear@').pk 
	


	# # ---------------------START QUERY----------------------------
	starttime=time.time()
	stocks,symbs=stkmd.GetStocks_selected(int(watchlist_pk),Symbols,None)
	symbs=[str(ss) for ss in symbs]
	# if rmd.GeneralFile.objects.filter(T=pd.datetime.today().date(),name='QueryDownload',extn='.csv').exists():
	# 	GNFcsv=rmd.GeneralFile.objects.get(T=pd.datetime.today().date(),name='QueryDownload',extn='.csv')
	# else:
	# 	GNFcsv=rmd.GeneralFile(T=pd.datetime.today().date(),name='QueryDownload',extn='.csv')

	GNFcsv=rmd.GeneralFile.objects.get(pk=int(GNFcsv_pk))
	GNFcsv.DeleteFileIfexists()
	kk=0
	for T in TT:
		print T
		CFE=rmd.CombinesFeaturesEntry.objects.filter(T=T,window=window,Interval=Interval)
		if stocks is not None:
			CFE=CFE.filter(Symbol__in=stocks)
		GF=rmd.GeneralFeature.objects.all()
		GFV=rmd.GeneralFeatureValue.objects.all()
		# try: #first try the master then go to the traditional
		CFE_fil=['"T"::date = \''+str(T.strftime("%Y-%m-%d"))+'\''  ]
		CFE_fil.append('"window"='+str(window))
		CFE_fil.append('"Interval"='+"'"+str(Interval)+"'")

		if len(symbs)==1:
			CFE_fil.append('"Symbol" IN '+str(symbs[0]))	
		elif len(symbs)==0:
			pass
		else:
			CFE_fil.append('"Symbol" IN '+str(tuple(symbs)))

		
		df=libs.SQLquery_Q_master(CFE_fil,filjson,int(window) )
		df['No']=df.index
		df['charts']=df.apply( lambda row: chrtmd.UploadCharts.GetCreateUrl_QuickCharturl(row['Symbol'] ,row['T'],row['window'],row['Interval'],'StockChart','C',chartstyle__pk ,mode=None) , axis=1)
		
		if kk==0:
			GNFcsv.uploadDF2csv_recursive(df,header=True)
		else:
			GNFcsv.uploadDF2csv_recursive(df,header=False)
		kk=kk+1
		GNFcsv.save()
		# DF=pd.concat([DF,df])
		del df
	print "time taken first query "+str(time.time()-starttime)
		## ----------------------END QUERY -------------------------------

	GNFcsv.uploadDF2csv_recursive_finalize()
	GNFcsv.save()

	# DF['No']=df.index
	# chartstyle__pk=chrtmd.StdChartProps.objects.get(chartstylename='@defaultlinear@').pk 

	# DF['charts']=DF.apply( lambda row: chrtmd.UploadCharts.GetCreateUrl_QuickCharturl(row['Symbol'] ,row['T'],row['window'],row['Interval'],'StockChart','C',chartstyle__pk ,mode=None) , axis=1)


	# if rmd.GeneralFile.objects.filter(T=pd.datetime.today().date(),name='QueryDownload',extn='.csv').exists():
	# 	GNF=rmd.GeneralFile.objects.get(T=pd.datetime.today().date(),name='QueryDownload',extn='.csv')
	# else:
	# 	GNF=rmd.GeneralFile(T=pd.datetime.today().date(),name='QueryDownload',extn='.csv')
	

	
	# del DF
	
	return GNFcsv.GetcleanedCSVURL()