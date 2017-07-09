from __future__ import unicode_literals

from django.utils.safestring import mark_safe
from django.forms import ModelForm
from django import forms
from django.contrib.auth.models import User
import pandas as pd
import pdb
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
# Create your models here.

def chunks(l, n):
	"""Yield successive n-sized chunks from l."""
	for i in range(0, len(l), n):
		yield l[i:i+n]



class UserForm(ModelForm):
	password = forms.CharField(widget=forms.PasswordInput())

	class Meta:
		model = User
		fields = ('username', 'email', 'password')


class UserLoginForm(ModelForm):
	password = forms.CharField(widget=forms.PasswordInput())

	class Meta:
		model = User
		fields = ('username', 'password')

def SavedQueriesView():
	import research.models as rmd
	SQview={}
	for SQ in rmd.SavedQueries.objects.all():
		Tlast=SQ.savedqueries_plots_set.order_by('T').last().T
		name=SQ.Queryname+' '+Tlast.strftime("%Y-%m-%d")
		SQview[name]={'Table':[],'SummaryCharts':{} }

		if SQ.savedqueries_df_set.count()>0:
			SQDF=SQ.savedqueries_df_set.get(T=Tlast)
			df=SQDF.readDF()
			df.index=range(len(df))
			n=5
			for ckkind in chunks(df.index,n):
				SQview[name]['Table'].append( df.loc[ckkind,'Ycharts'].tolist()  )
		
		if SQ.savedqueries_plots_set.filter(T=Tlast)>0:
			summplots=SQ.savedqueries_plots_set.filter(T=Tlast)
			for sp in summplots:
				SQview[name]['SummaryCharts'][sp.plotname]=sp.GetImage(width=sp.plotsize['width'],height=sp.plotsize['height'])
				# pdb.set_trace()
				
	return SQview

# SQVIEW=[{'pk':2,'pageno':10},{'pk':3,'pageno':22}]
def SQVIEW(SQVIEW=[]):
	import research.models as rmd
	if len(SQVIEW)==0:
		SS=[]
		for SQ in rmd.SavedQueries.objects.all().order_by('Queryname'):
			if SQ.Queryname=='StockMarket':
				Tlast=SQ.savedqueries_plots_set.order_by('T').last().T
				date=Tlast.strftime("%Y-%m-%d")
				name=SQ.Queryname
				SS.append({'date':date,'name':name,'Table':[],'SummaryCharts':{},'pk':SQ.pk ,'pages':[],'pageno':None})
			else:
				Tlast=SQ.savedqueries_plots_set.order_by('T').last().T
				date=Tlast.strftime("%Y-%m-%d")
				name=SQ.Queryname
				SQVIEW.append({'date':date,'name':name,'Table':[],'SummaryCharts':{},'pk':SQ.pk ,'pages':[],'pageno':None})
		SQVIEW=SS+SQVIEW

	for i in range(len(SQVIEW)):
		SQ=rmd.SavedQueries.objects.get(pk=int(SQVIEW[i]['pk']))
		pageno=SQVIEW[i]['pageno']
		Tlast=SQ.savedqueries_plots_set.order_by('T').last().T
		date=Tlast.strftime("%Y-%m-%d")
		SQVIEW[i]['date']=date
		SQVIEW[i]['name']=SQ.Queryname
		SQVIEW[i]['Table']=[]
		SQVIEW[i]['SummaryCharts']={}
		if SQ.savedqueries_df_set.count()>0:
			SQDF=SQ.savedqueries_df_set.get(T=Tlast)
			df=SQDF.readDF()
			df.index=range(len(df))
			paginator = Paginator(df.index, 25)
			try:
				pages = paginator.page(pageno)
			except PageNotAnInteger:
				# If page is not an integer, deliver first page.
				pages = paginator.page(1)
				pageno=1
			except EmptyPage:
				# If page is out of range (e.g. 9999), deliver last page of results.
				pages = paginator.page(paginator.num_pages)
			SQVIEW[i]['pages']=pages
			SQVIEW[i]['pageno']=pageno
			dfindex_pag=pages.object_list
			dd=df.loc[dfindex_pag, :]
			n=5
			for ckkind in chunks(dd.index,n):
				SQVIEW[i]['Table'].append( dd.loc[ckkind,'Ycharts'].tolist()  )
		
		if SQ.savedqueries_plots_set.filter(T=Tlast)>0:
			summplots=SQ.savedqueries_plots_set.filter(T=Tlast)
			for sp in summplots:
				SQVIEW[i]['SummaryCharts'][sp.plotname]=sp.GetImage(width=sp.plotsize['width'],height=sp.plotsize['height'])
				
	return SQVIEW




