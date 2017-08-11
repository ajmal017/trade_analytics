from __future__ import division
from django.db.models import Q
from django.conf import settings
import stockdata.models as stkmd
import charting.models as chrtmd
from . import models as md
import logging
logger = logging.getLogger(__name__)
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import pandas as pd
import numpy as np
from django.utils.safestring import mark_safe
from django.contrib.auth.models import User
import collections
from django.forms import ModelForm
from django import forms
from django.core.validators import RegexValidator
import research.featuremanager as featmng
import json
import time

import pdb



## model helpers-----------------------------------------------------------------------------

def LoadUpSavedQueries_choices(user):
	Coljson={'None'.encode('utf-8'):''.encode('utf-8')}
	Filjson={'None'.encode('utf-8'):''.encode('utf-8')}
	SavedQmeta_options={'None'.encode('utf-8'):''.encode('utf-8')}

	SQ=md.SavedQueries.objects.filter(user=user)
	choices=[('None','-----')]
	for ss in SQ:
		choices.append( (str(ss.pk), ss.Queryname) )
		Coljson[str(ss.pk).encode('utf-8')]=ss.Coljson.encode('utf-8')
		Filjson[str(ss.pk).encode('utf-8')]=ss.Filjson.encode('utf-8')
		SavedQmeta_options[str(ss.pk).encode('utf-8')]={}
		if ss.Queryname==None:
			SavedQmeta_options[str(ss.pk).encode('utf-8')]['name']=''
		else:
			SavedQmeta_options[str(ss.pk).encode('utf-8')]['name']=ss.Queryname.encode('utf-8')
		if ss.Querydescription==None:
			SavedQmeta_options[str(ss.pk).encode('utf-8')]['desc']=''
		else:
			SavedQmeta_options[str(ss.pk).encode('utf-8')]['desc']=ss.Querydescription.encode('utf-8')


	if str(user)!='@general@':
		SQ=md.SavedQueries.objects.filter(user__username='@general@')
		for ss in SQ:
			if ss.Queryname=='StockMarket':
				continue
				
			choices.append( (str(ss.pk), ss.Queryname) )
			Coljson[str(ss.pk).encode('utf-8')]=ss.Coljson.encode('utf-8')
			Filjson[str(ss.pk).encode('utf-8')]=ss.Filjson.encode('utf-8')
			SavedQmeta_options[str(ss.pk).encode('utf-8')]={}
			SavedQmeta_options[str(ss.pk).encode('utf-8')]['name']=ss.Queryname.encode('utf-8')
			SavedQmeta_options[str(ss.pk).encode('utf-8')]['desc']=ss.Querydescription.encode('utf-8')	

	return choices,Coljson,Filjson,SavedQmeta_options


def LoadUpGeneralFeature_choices(user):
	GF=md.GeneralFeature.objects.filter(user=User.objects.get(username='@general@'))
	choices=[(str(ss.pk), ss.name) for ss in GF]
	choices=choices+[('None','-----')]

	if str(user)!='@general@':
		GF=md.GeneralFeature.objects.filter(user=user)
		choices=choices+[(str(ss.pk), ss.name) for ss in GF]
	
	return choices



def StockAlphabetGrpCont_forchartname(symbs):
	if symbs==None:
		return 'AllStocks'
	symbs=sorted(symbs)
	symbs=[ss[0] for ss in symbs]

	# Alpha=['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z']
	# pdb.set_trace()
	counter=collections.Counter(symbs)
	ss=''
	for key,value in dict(counter).items():
		ss=ss+str(key)+str(value)
	return ss







## -------------------------------FORMS  --------------------------------


class CreateModifyFeatureForm(forms.Form):
	alphanumeric = RegexValidator(r'^[a-zA-Z][_0-9a-zA-Z]*$', 'Should Begin with alphabet and the name should contain only alphanumeric characters or "_" .')
	customfeature_code = forms.CharField(label='enter feature code here',widget=forms.Textarea,required=False)
	customfeature_name = forms.CharField(label='feature name',required=False, validators=[alphanumeric])
	customfeature_description = forms.CharField(label='feature description',widget=forms.Textarea(attrs={'rows': 2,'cols': 50,}),required=False)
	customfeature_group = forms.CharField(label='Enter a feature group',widget=forms.TextInput,required=False)
	
	select_group=forms.ChoiceField(label='Select the Group', widget=forms.Select,choices=[],initial='None') #choices=intervals

	operators=forms.MultipleChoiceField(
		required=False,
		widget=forms.CheckboxSelectMultiple,
		choices=[(ss.operators,md.FeatureOperator.choices[ss.operators]) for ss in md.FeatureOperator.objects.all()],
		initial=[ss.operators for ss in md.FeatureOperator.objects.all()],
	)
	units=forms.MultipleChoiceField(
		required=False,
		widget=forms.CheckboxSelectMultiple,
		choices=[(ss.units,md.FeatureUnit.choices[ss.units]) for ss in md.FeatureUnit.objects.all()],
		initial=[ss.units for ss in md.FeatureUnit.objects.all()],
	)

	def __init__(self, *args, **kwargs):
		self.user=kwargs.pop('user')
		self.username=str(self.user)
		super(CreateModifyFeatureForm, self).__init__(*args, **kwargs)
		self.user,self.username=stkmd.CleanUpUser(self.user)

		self.fields['select_group'].choices=[('None','Select')]+[(ss,ss) for ss in list(set(md.GeneralFeature.objects.values_list('group',flat=True))) ]
		self.nameisset=None

		with featmng.featuremanager() as FM:
			FM.LoadTestData()
			FM.LoadFeatureModule()
			testmeta=FM.testmeta

		# testdata,t0,T,window,Interval,Symbol=GetFeatureTestData()

			genfeats=md.GeneralFeature.objects.filter(user__username='@general@').exclude(name__in=['FutMNRtQt','FutMNRtHf','FutMNRtAn','PastMNRtQt','PastMNRtHf','PastMNRtAn','FutMXRtQt','FutMXRtHf','FutMXRtAn','PastMXRtQt','PastMXRtHf','PastMXRtAn']).order_by('group')
			if str(self.user)!='@general@':
				userfeats=md.GeneralFeature.objects.filter(user=self.user).order_by('group')


			self.SavedGenfeatures=[]
			for gg in genfeats:
				# testdata['code_str']=gg.code
				# testdata['name']=gg.name
				a=FM.TestFeatures(gg.name)
				# a=featex.check_feature_code(testdata.copy(),gg.code,gg.name)
				self.SavedGenfeatures.append( {'output':a,'type':'general','group':gg.group,'id':gg.pk, 'description': gg.description,'code':gg.code,'name':gg.name  }   )


			self.SavedUserfeatures=[]
			for gg in userfeats:
				# testdata['code_str']=gg.code
				# testdata['name']=gg.name
				# a=featex.check_feature_code(testdata.copy(),gg.code,gg.name)
				a=FM.TestFeatures(gg.name)
				self.SavedUserfeatures.append( {'output':a,'type':'user','group':gg.group,'id':gg.pk, 'description': gg.description,'code':gg.code,'name':gg.name}   )

		self.featvalue=None
		
		if chrtmd.UploadCharts.objects.filter(chartname='FeatureCreateTestPlot',chartsrc='C',chartstyle=chrtmd.StdChartProps.objects.get(chartstylename='@defaultlinear@',user__username='@general@'), 
								window=testmeta['window'],Interval=testmeta['Interval'],T=testmeta['T'],Symbol=stkmd.Stock.objects.get(Symbol=testmeta['Symbol']),
								user=User.objects.get(username='@general@')).exists():
			upch=chrtmd.UploadCharts.objects.get(chartname='FeatureCreateTestPlot',chartsrc='C',chartstyle=chrtmd.StdChartProps.objects.get(chartstylename='@defaultlinear@',user__username='@general@'), 
								window=testmeta['window'],Interval=testmeta['Interval'],T=testmeta['T'],Symbol=stkmd.Stock.objects.get(Symbol=testmeta['Symbol']),
								user=User.objects.get(username='@general@'))
		else:
			upch=chrtmd.UploadCharts(chartname='FeatureCreateTestPlot',chartsrc='C',chartstyle=chrtmd.StdChartProps.objects.get(chartstylename='@defaultlinear@',user__username='@general@'), 
								window=testmeta['window'],Interval=testmeta['Interval'],T=testmeta['T'],Symbol=stkmd.Stock.objects.get(Symbol=testmeta['Symbol']),
								user=User.objects.get(username='@general@'))
			upch.save()

		self.chart=upch.GetorMakeChartUrls()

	def GenerateInitialdefCode(self):
		self.nameisset=True
		name=self.cleaned_data['customfeature_name']
		# self.cleaned_data['customfeature_code']='def '+name+'(data):\r\n\t#numpy available as np\r\n\t#pandas available as pd\r\n\t# No other module can be used\r\n\tT=data["T"]\r\n\tdf=data["df"]\r\n\tTrendsMid=data["TrendsMid"]\r\n\tTrendsTop=data["TrendsTop"]\r\n\tTrendsBottom=data["TrendsBottom"]\r\n\t# Use data["DebugOutput"] to show output for debugging\r\n\t'
		
		with featmng.featuremanager() as FM:
			self.cleaned_data['customfeature_code']=FM.GetEmptyFeatCode_str(name)

		self.cleaned_data['operators']=[ss.operators for ss in md.FeatureOperator.objects.all() if ss.operators!='contains']
		self.cleaned_data['units']=[ss.units for ss in md.FeatureUnit.objects.all() if ss.units!='%']
		

	def SaveFeatureCode(self):
		if md.GeneralFeature.objects.filter(user__username='@general@',name=self.cleaned_data['customfeature_name']).exists():
			return (False,'Feature name already exists in general(public) category, use the general feature or rename your feature',None)
		if self.user.username!='@general@':
			if md.GeneralFeature.objects.filter(user=self.user,name=self.cleaned_data['customfeature_name']).exists():
				return (False,'Feature name already exists, use a different name or modify the esisting feature',None)

		# get a test data to check if the feature works well
		# testdata,t0,T,window,Interval,Symbol=GetFeatureTestData()
		# testdata['code_str']=self.cleaned_data['customfeature_code']
		# testdata['name']=self.cleaned_data['customfeature_name']
		with featmng.featuremanager() as FM:
			FM.LoadTestData()
			a=FM.CheckFeaturecode_str(self.cleaned_data['customfeature_name'],self.cleaned_data['customfeature_code'])
			# a=featex.check_feature_code(testdata,self.cleaned_data['customfeature_code'],self.cleaned_data['customfeature_name'])
		
		if a[0]==True:
			if md.GeneralFeature.objects.filter(user=self.user,name=self.cleaned_data['customfeature_name']).exists():
				GF=md.GeneralFeature.objects.get(user=self.user,name=self.cleaned_data['customfeature_name'])
				GF.code=self.cleaned_data['customfeature_code']
				GF.group=self.cleaned_data['customfeature_group']
				GF.description=self.cleaned_data['customfeature_description']
				operators=list(GF.operators.all())
				
				for op in operators:
					GF.operators.remove(op)
				units=list(GF.units.all())
				for un in units:
					GF.units.remove(un)
				# pdb.set_trace()
				GF.operators.add(*md.FeatureOperator.objects.filter(operators__in=self.cleaned_data['operators']))
				GF.units.add(*md.FeatureUnit.objects.filter(units__in=self.cleaned_data['units']))
				
				GF.save()
				self.featvalue=a[2]
				return (True,'Feature Updated',None)

			else:
				GF=md.GeneralFeature(user=self.user,name=self.cleaned_data['customfeature_name'])
				GF.code=self.cleaned_data['customfeature_code']
				GF.group=self.cleaned_data['customfeature_group']
				GF.description=self.cleaned_data['customfeature_description']
				GF.save()
				GF.operators.add(*md.FeatureOperator.objects.filter(operators__in=self.cleaned_data['operators']))
				GF.units.add(*md.FeatureUnit.objects.filter(units__in=self.cleaned_data['units']))
				self.featvalue=a[2]
				return a
			
			with featmng.featuremanager() as FM:
				FM.DumpFeatureCodes2file()

			return (True,None,None)
		else:
			return a

	def ModifyFeatureCode(self,id,code):
		GF=md.GeneralFeature.objects.get(pk=int(id))
		with featmng.featuremanager() as FM:
			FM.LoadTestData()
			a=FM.CheckFeaturecode_str(GF.name,code)

		# a=featex.check_feature_code(testdata,code,GF.name)
		if a[0]==True:
			GF.code=code
			GF.save()
			with featmng.featuremanager() as FM:
				FM.DumpFeatureCodes2file()

			# tasks.DumpFeatureCodes2file()
			return a                
		else:
			return a

	def DeleteFeatureCode(self,id):
		GF=md.GeneralFeature.objects.get(pk=int(id))
		GF.delete()
		return (True,None,None)





#  This form has custom features and chained select
class WindowQueryTool_advanced(forms.Form):
	watchlist = forms.ChoiceField(label='Select Stocks from Watchlist', widget=forms.Select,choices=[],initial='271')
	symbol = forms.CharField(label='and/or Enter the symbols (comma/space separated for multiple)',widget=forms.Textarea( attrs={'rows': 1,
								  'cols': 40,
								  'style': 'height: 2em;'}),required=False)
	
	T = forms.DateField(label='Select the end date for T ',initial=pd.datetime.today().date(),input_formats=['%Y-%m-%d'],widget=forms.SelectDateWidget(years=chrtmd.years,
		empty_label=("Choose Year", "Choose Month", "Choose Day"),
	))
	T0 = forms.DateField(label='Select the end date for T ',initial=pd.datetime.today().date(),input_formats=['%Y-%m-%d'],widget=forms.SelectDateWidget(years=chrtmd.years,
		empty_label=("Choose Year", "Choose Month", "Choose Day"),
	))

	window=forms.ChoiceField(label="Select the length of the window(w)", widget=forms.Select,choices=[(360,'1 year'),(180,'6 months')],initial=360)
	Interval = forms.ChoiceField(label='Select the Interval for Price', widget=forms.Select,choices=[('D','Daily')],initial='D') #choices=intervals

	filjson=forms.CharField(widget=forms.Textarea(attrs={'name':'filjson', 'id': 'filjson','rows': 2,'cols': 60,'hidden': ''}),required=False) #
	coljson=forms.CharField(widget=forms.Textarea(attrs={'name':'coljson', 'id': 'coljson','rows': 2,'cols': 60,'hidden': ''}),required=False)

	loadsavedQs = forms.ChoiceField(label='load a saved query', widget=forms.Select(attrs={'style':'width:100px'}),choices=[('None','Select')],initial='None',required=False)
	saveQs = forms.CharField(label='Save query as : ',widget=forms.Textarea(attrs={'rows': 1,'cols': 20,}),required=False)
	saveQs_description = forms.CharField(label='Query description as : ',widget=forms.Textarea(attrs={'rows': 3,'cols': 42,}),required=False)
	savemodifyQ_bool = forms.BooleanField(label='Save the query',initial=False,required=False)
	deleteQ_bool = forms.BooleanField(label='Delete the query',initial=False,required=False)


	chartstyle= forms.ChoiceField(label='Select Chartstyle', widget=forms.Select(attrs={'style':'width:300px'}),choices=[],required=False,initial='@default@')

	pageno=forms.IntegerField(label='page number',required=False,initial=None) # widget = forms.HiddenInput(),
	initial={'window':360,'Interval':'D','watchlist':'All Symbols','chartstyle':'@default@'}

	def __init__(self, *args, **kwargs):
		self.user=kwargs.pop('user')
		self.username=str(self.user)



		super(WindowQueryTool_advanced, self).__init__(*args, **kwargs)
		self.user,self.username=stkmd.CleanUpUser(self.user)

		self.fields['watchlist'].choices=stkmd.LoadUpWatchlists_choices(self.user,self.username)

		self.fields['loadsavedQs'].choices,Coljson,Filjson,SavedQmeta_options=LoadUpSavedQueries_choices(self.user)
		self.Coljson=mark_safe(str(Coljson) ) 
		self.Filjson=mark_safe( str(Filjson) )  
		self.SavedQmeta_options=mark_safe( str(SavedQmeta_options) ) 

		# pdb.set_trace()

		self.fields['chartstyle'].choices=chrtmd.LoadChartStyle_choice(self.user,self.username)
		
		from . import libs
		feature_options=libs.GenrateAdvanced_Filter_Colm_Options(self.user)

		self.browser_feature_options={}
		for ss in feature_options.keys():
			self.browser_feature_options[ss]=mark_safe(json.dumps( feature_options[ss],indent=4, separators=(',', ': ') ) )





	def SaveQuery(self,request=None):
		# pdb.set_trace()
		# if request.GET.get('savemodifyQ_bool','')=='on':
		# 	self.cleaned_data['savemodifyQ_bool']=True
		# else:
		# 	self.cleaned_data['savemodifyQ_bool']=False

		

		


		if str(self.user)=='@general@':
			pass
		elif self.cleaned_data['saveQs']!='' and self.cleaned_data['saveQs']!=' ' and self.cleaned_data['saveQs']!='None' and self.cleaned_data['saveQs']!=None:
			if md.SavedQueries.objects.filter(Queryname=self.cleaned_data['saveQs'],user=self.user).exists()==True:
				SQ=md.SavedQueries.objects.get(Queryname=self.cleaned_data['saveQs'],user=self.user)
				if self.cleaned_data['deleteQ_bool']==False:
					SQ.Filjson=self.cleaned_data['filjson']
					SQ.Coljson=self.cleaned_data['coljson']
					SQ.window=int(self.cleaned_data['window'])
					SQ.Interval=self.cleaned_data['Interval']
					SQ.Querydescription=self.cleaned_data['saveQs_description']

					if self.cleaned_data['watchlist']!='' and self.cleaned_data['watchlist']!='None' and self.cleaned_data['watchlist']!=None:
						SQ.watchlist=stkmd.Watchlist.objects.get(pk=int(self.cleaned_data['watchlist']))
					SQ.save()
				else:
					SQ.delete()

			else:
				# pdb.set_trace()
				SQ=md.SavedQueries(Queryname=self.cleaned_data['saveQs'],user=self.user,Filjson=self.cleaned_data['filjson'],Coljson=self.cleaned_data['coljson'])
				SQ.window=int(self.cleaned_data['window'])
				SQ.Interval=self.cleaned_data['Interval']
				SQ.Querydescription=self.cleaned_data['saveQs_description']
				
				if self.cleaned_data['watchlist']!='' and self.cleaned_data['watchlist']!='None' and self.cleaned_data['watchlist']!=None:
					SQ.watchlist=stkmd.Watchlist.objects.get(pk=int(self.cleaned_data['watchlist']))
				SQ.save()
		
			self.cleaned_data['saveQs']=''

			self.fields['loadsavedQs'].choices,Coljson,Filjson,SavedQmeta_options=LoadUpSavedQueries_choices(self.user)
			self.Coljson=mark_safe(str(Coljson)   )
			self.Filjson=mark_safe( str(Filjson) ) 
			self.SavedQmeta_options=mark_safe( str(SavedQmeta_options) ) 

			self.cleaned_data['loadsavedQs']=str(SQ.pk)

		else:
			pass

		return self.cleaned_data

	
	def ProcessQuery(self):
		from . import libs
		
		# Save the query if required
		# self.SaveQuery()

		window=self.cleaned_data['window']
		Interval=self.cleaned_data['Interval']
		self.cleaned_data['filjson']=json.loads(self.cleaned_data['filjson'])

		Tf=self.cleaned_data['T']
		T0=self.cleaned_data['T0']
		TT=libs.GetHistoricalQueryTdate(Tf,T0)


		# # ---------------------START QUERY----------------------------
		starttime=time.time()
		self.stocks,self.symbs=stkmd.GetStocks_selected(self.cleaned_data['watchlist'],self.cleaned_data['symbol'],self.user)
		self.symbs=[str(ss) for ss in self.symbs]
		CFE=md.CombinesFeaturesEntry.objects.filter(T__in=TT,window=window,Interval=Interval)
		if self.stocks is not None:
			CFE=CFE.filter(Symbol__in=self.stocks)
		GF=md.GeneralFeature.objects.all()
		GFV=md.GeneralFeatureValue.objects.all()
		# try: #first try the master then go to the traditional
		if len(TT)==1:
			CFE_fil=['"T"::date = '+str(TT[0].strftime("%Y-%m-%d"))  ]	
		elif len(TT)==0:
			pass
		else:
			CFE_fil=['"T"::date IN '+str(tuple([t.strftime("%Y-%m-%d") for t in TT]))  ]
		CFE_fil.append('"window"='+str(window))
		CFE_fil.append('"Interval"='+"'"+str(Interval)+"'")

		if len(self.symbs)==1:
			CFE_fil.append('"Symbol" IN '+str(self.symbs[0]))	
		elif len(self.symbs)==0:
			pass
		else:
			CFE_fil.append('"Symbol" IN '+str(tuple(self.symbs)))

		
		df=libs.SQLquery_Q_master(CFE_fil,self.cleaned_data['filjson'],int(window) )
		# except:
		# 	df=libs.SQLquery_Q_rawsql(GFV,CFE,GF,self.cleaned_data['filjson'],int(window) )
		print "time taken first query "+str(time.time()-starttime)
		## ----------------------END QUERY -------------------------------


		from . import plotmanager as pltmng
		# # --------------------SUMMARY PLOTS A-----------------------------    
		starttime=time.time()     
		Plotstrs=pltmng.GethistPlotsQuery_perf_faster(df)
		self.SummaryCharts=[]
		self.SummaryCharts.append( [ Plotstrs['PastMXRtQt'], Plotstrs['FutMXRtQt']] )
		self.SummaryCharts.append( [ Plotstrs['PastMXRtHf'], Plotstrs['FutMXRtHf']] )
		self.SummaryCharts.append( [ Plotstrs['PastMXRtAn'], Plotstrs['FutMXRtAn']] )
		print "time taken hists "+str(time.time()-starttime)  
		# # --------------------END END ENF SUMMARY PLOTS  A----------------------------- 



		## -------------------- PAGINATION -----------------------------
		starttime=time.time()
		paginator = Paginator(df.index, 100)
		try:
			self.pages = paginator.page(self.cleaned_data['pageno'])
		except PageNotAnInteger:
			# If page is not an integer, deliver first page.
			self.pages = paginator.page(1)
			self.cleaned_data['pageno']=1
		except EmptyPage:
			# If page is out of range (e.g. 9999), deliver last page of results.
			self.pages = paginator.page(paginator.num_pages)
		dfindex_pag=self.pages.object_list
		dd=df.loc[dfindex_pag, :].copy()
		del df
		df=dd
		print "time taken 2nd query "+str(time.time()-starttime)
		# # ---------------------END QUERY----------------------------


		df['No']=df.index


		cols=['No','T','Symbol']+[ss[1].split('^')[1] for ss in json.loads( self.cleaned_data['coljson'] )]
		# pdb.set_trace()
	  

		# Get the chart props
		if self.cleaned_data['chartstyle']=='@default@' or self.cleaned_data['chartstyle']=='' or self.cleaned_data['chartstyle']=='None' or self.cleaned_data['chartstyle']==None:
			chartstyle__pk=chrtmd.StdChartProps.objects.get(chartstylename='@default@') 
		else:
			ch=chrtmd.StdChartProps.objects.get(pk=int(self.cleaned_data['chartstyle'])) 
			chartstyle__pk=ch.pk
		

		# Add charts to the dataframe
		df['t0']=df['T']-df['window'].apply(lambda x: pd.DateOffset(x) )
		chartwindows={	'Chart1y':{'wprev':360,'wnext':0},
						'Chart6m':{'wprev':180,'wnext':0},
						'Chart1y6m':{'wprev':360,'wnext':180},
					}
		

		for charts,vals in chartwindows.items():
			if charts in cols:
				df['wmod']=vals['wprev']  
				df['Tmod']=df['T']+pd.DateOffset( vals['wnext'] )
				# pdb.set_trace()
				df[charts]=df.apply( lambda row: chrtmd.UploadCharts.GetCreateUrl_QuickCharturl(row['Symbol'] ,row['Tmod'],row['wmod'],row['Interval'],'StockChart','C',chartstyle__pk ) , axis=1)

		if 'wmod' in df.columns:
			df.drop('wmod', axis=1, inplace=True)
		if 'Tmod' in df.columns:
			df.drop('Tmod', axis=1, inplace=True)


		# SectorPerf=pd.read_hdf(settings.DATABASES['StockDataH5']['NAME'],'SectorPerf')
		# IndustryPerf=pd.read_hdf(settings.DATABASES['StockDataH5']['NAME'],'IndustryPerf')
		# df=pd.merge(df,SectorPerf,how='left',on=['T','Sector'])
		# df=pd.merge(df,IndustryPerf,how='left',on=['T','Industry'],suffixes=['_sec','_ind'])


		# add category tags
		# Get the tag catogories list
		starttime=time.time() 
		# Cats=md.Category.objects.filter(Q(user__username='@general@') |  Q(user=self.user),Type='G').order_by('user__username')
		# GG=md.Grading.objects.filter(user=self.user).prefetch_related('Symbol')

		dfCats=pd.DataFrame(list(md.Category.objects.filter(Q(user__username='@general@') |  Q(user=self.user),Type='G').order_by('user__username')
																													.values('pk',
																															'user__username',
																															'name',
																															'Type')))
		dfCats.index=range(len(dfCats))

		dfGG=pd.DataFrame(list(md.Grading.objects.filter(user=self.user).prefetch_related('Symbol').values('user__username',
																											'Category__name',
																											'Category__pk',
																											'T',
																											'window',
																											'Symbol__Symbol',
																											'Interval',
																											'Grade'	) ))

		dfGG.index=range(len(dfGG))

		print "Doing tags" 
		df['tag']=0
		df['tag']=df.apply(lambda row: libs.render_tag_str_fast(dfCats,dfGG,row,self.user.username),axis=1 )
		# df['tag']=df.apply(lambda row: libs.render_tag_str(Cats,GG,row,self.user),axis=1 )
		cols.append('tag')
		print "time taken tags "+str(time.time()-starttime)  

		delcols=[]
		for cc in df.columns:
			if cc not in cols:
				delcols.append(cc)

		# pdb.set_trace()
		if len(delcols)>0:
			df.drop(delcols, axis=1, inplace=True)

		ss=str(df[cols].to_html(classes=["tablesorter"],index=False,escape=False))
		ss=ss.replace('tablesorter"','tablesorter" id="myTable"').replace('dataframe','').replace('border="1"','')
		self.dftable =mark_safe( ss )


	def DownloadQuery(self):
		import research.tasks as tks
		window=self.cleaned_data['window']
		Interval=self.cleaned_data['Interval']
		self.cleaned_data['filjson']=json.loads(self.cleaned_data['filjson'])

		Tf=self.cleaned_data['T']
		T0=self.cleaned_data['T0']

		if md.GeneralFile.objects.filter(T=pd.datetime.today().date(),name='QueryDownload',extn='.csv').exists():
			GNFcsv=md.GeneralFile.objects.get(T=pd.datetime.today().date(),name='QueryDownload',extn='.csv')
		else:
			GNFcsv=md.GeneralFile(T=pd.datetime.today().date(),name='QueryDownload',extn='.csv')
		GNFcsv.DeleteFileIfexists()
		GNFcsv.uploadDF2csv(pd.DataFrame())
		url=GNFcsv.GetcleanedCSVURL()

		tks.DownloadQuery_recursive.delay(GNFcsv.pk,window,Interval,self.cleaned_data['filjson'],Tf.strftime("%Y-%m-%d"),T0.strftime("%Y-%m-%d"),self.cleaned_data['watchlist'],self.cleaned_data['symbol'])
		
		self.QueryDownloadURL=url



class CategoryManagerForm_create(ModelForm):
	class Meta:
		model = md.Category
		fields =['name','description','Type','ParentCategory']

	def checkifcatexists(self,user):
		# pdb.set_trace()
		return md.Category.objects.filter(user=user,name=self.cleaned_data['name']).exists()

# can view all teh general categories and his own
# cannot modify or delete or add to general category
class CategoryManagerForm_view(forms.Form):
	Categoryname=forms.ChoiceField(label='Select your Category', widget=forms.Select,choices=[])

	def __init__(self, *args, **kwargs):

		if 'user' in kwargs.keys():
			self.user=kwargs.pop('user')
			self.username=str(self.user)
			if str(self.user)=='AnonymousUser':
				self.username='@general@'
				self.user=User.objects.get(username=self.username)
		   
		else:
			self.username='@general@'
			self.user=User.objects.get(username='@general@')


		super(CategoryManagerForm_view, self).__init__(*args, **kwargs)

		self.fields['Categoryname'].choices=[(str(ss.id),str(ss)) for ss in md.Category.objects.filter(user=User.objects.get(username='@general@')) ]
		self.fields['Categoryname'].choices=self.fields['Categoryname'].choices+[('------','------')]

		if self.username!='@general@':
			try:
				self.fields['Categoryname'].choices=self.fields['Categoryname'].choices+[(str(ss.id),str(ss)) for ss in md.Category.objects.filter(user=self.user) ]
			except:
				pass



class StockStudyForm(forms.Form):
	Symbol = forms.ChoiceField(label='Select Stocks from Watchlist', widget=forms.Select,choices=[],initial='All Symbols')

