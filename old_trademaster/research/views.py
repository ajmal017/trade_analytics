from __future__ import division
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.template import RequestContext
from django.contrib import messages
from django.utils.safestring import mark_safe
import os
from django.views.decorators.csrf import csrf_exempt
from . import models as md
from . import forms as fm
import stockdata.models as stkmd
import traceback
import pandas as pd
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import numpy as np
import pdb
from django.conf import settings
import subprocess as sbp


def ComputationsStatus(request):
	import django_tables2 as tables
	md.LinearTrends.objects.all()
	
	class WindowFeatureTable_advanced(tables.Table):
            class Meta:
                orderable = False
                attrs = {'id':'QTable','class': 'tablesorter', 'th' : {
                '_ordering': {
                    'orderable': False, # Instead of `orderable`
                }
                }}

def QueryTool(request):
	context = RequestContext(request)
	if request.method == 'POST':
		if request.POST.get('query_submit', '')=="Submit Query":
			# print request.POST
			print request.POST.get("columns", "")
			# print request.POST.get("sqlquery", "")


	return render(request, 'research/querytool.html',{'RQ':md.RQ,
														'wc1_volume':md.wc1_volume["columns"],
														'wc1_perf':md.wc1_perf["columns"],
														'wc1_price':md.wc1_price["columns"],
														'wc1_SMA':md.wc1_SMA["columns"],
														'wc1_trends':md.wc1_trends["columns"],
														'wc1_channels':md.wc1_channels["columns"],
														'wc1_correlation':md.wc1_correlation["columns"],
														'wc1_candlepattern':md.wc1_candlepattern["columns"]



		},context)



@login_required(login_url='/login/')
def WindowQueryTool_advanced(request):
	context = RequestContext(request)
	print request.user

	if request.method == 'GET':
		# pdb.set_trace()

		if request.GET.get('query_savemod', '')=="Save/Modify Query":
			WindowQueryTool_advanced=fm.WindowQueryTool_advanced(request.GET,user=request.user)
			if WindowQueryTool_advanced.is_valid():
				WindowQueryTool_advanced.SaveQuery(request=request)
			
		elif request.GET.get('query_download', '')=="Download Query Results":
			WindowQueryTool_advanced=fm.WindowQueryTool_advanced(request.GET,user=request.user)
			if WindowQueryTool_advanced.is_valid():
				WindowQueryTool_advanced.DownloadQuery()

		elif request.GET.get('query_submit', '')=="Submit Query":
			WindowQueryTool_advanced=fm.WindowQueryTool_advanced(request.GET,user=request.user)
			
			if WindowQueryTool_advanced.is_valid():
				WindowQueryTool_advanced.ProcessQuery()

				# if hasattr(WindowQueryTool_advanced, 'table'):
				# 	WindowQueryTool_advanced.table.paginate(page=request.GET.get('page', 1), per_page=5000)
			else:
				WindowQueryTool_advanced=fm.WindowQueryTool_advanced(request.GET,user=request.user)
		

		else:
			WindowQueryTool_advanced=fm.WindowQueryTool_advanced(user=request.user,initial={'pageno':None})	
	else:
		WindowQueryTool_advanced=fm.WindowQueryTool_advanced(user=request.user,initial={'pageno':None})

	return render(request, 'research/windowquerytool_advanced.html',{'WindowQueryTool_advanced':WindowQueryTool_advanced},context)



@login_required(login_url='/login/')
def CategoryManager(request):
	context = RequestContext(request)
	print request.user

	if request.method == 'POST':
		if request.POST.get('cat_create', '')=="Create Category":
			category=md.Category(user=request.user)
			CategoryManagerForm_create=fm.CategoryManagerForm_create(request.POST,instance=category)
			if CategoryManagerForm_create.is_valid():
				
				if CategoryManagerForm_create.checkifcatexists(request.user)==False:
					CategoryManagerForm_create.save()
					CategoryManagerForm_view=fm.CategoryManagerForm_view()
				else:
					context['error']="Category already exists"
					CategoryManagerForm_create=fm.CategoryManagerForm_create(request.POST)
					CategoryManagerForm_view=fm.CategoryManagerForm_view()

		else:# request.POST.get('cat_view', '')=="View Category":
			CategoryManagerForm_create=fm.CategoryManagerForm_create()
			CategoryManagerForm_view=fm.CategoryManagerForm_view(user=request.user)

	else:
		CategoryManagerForm_create=fm.CategoryManagerForm_create()
		CategoryManagerForm_view=fm.CategoryManagerForm_view(user=request.user)


	return render(request, 'research/categorymanager.html',{'CategoryManagerForm_create':CategoryManagerForm_create,
															'CategoryManagerForm_view':CategoryManagerForm_view},context)



@login_required(login_url='/login/')
def CreateModifyFeature(request):
	context = RequestContext(request)
	print request.user

	if request.method == 'POST':


		if request.POST.get('feature_create', '')=="Create Feature":
			CreateModifyFeatureForm=fm.CreateModifyFeatureForm(request.POST,user=request.user)
			if CreateModifyFeatureForm.is_valid():
				CreateModifyFeatureForm.GenerateInitialdefCode()
				CreateModifyFeatureForm=fm.CreateModifyFeatureForm(user=request.user,initial=CreateModifyFeatureForm.cleaned_data)
				CreateModifyFeatureForm.nameisset=True

					
		elif request.POST.get('feature_create_save', '')=="Save New Feature":
			CreateModifyFeatureForm=fm.CreateModifyFeatureForm(request.POST,user=request.user)
			CreateModifyFeatureForm.nameisset=True
			if CreateModifyFeatureForm.is_valid():
				a=CreateModifyFeatureForm.SaveFeatureCode()
				context['error']=a[1]
				messages.error(request, a[1])

		else:
			CreateModifyFeatureForm=fm.CreateModifyFeatureForm(request.POST,user=request.user)
			for key,value in request.POST.items():
				if 'feature_modify_' in key:
					if request.POST.get(key)=='Modify Feature':
						if CreateModifyFeatureForm.is_valid():
							idd=int(key.split('_')[-1])
							codestr=request.POST.get('textcode_'+str(idd) )
							a=CreateModifyFeatureForm.ModifyFeatureCode(idd,codestr)
							context['error']=a[1]
							messages.error(request, a[1])
					if request.POST.get(key)=='Delete Feature':
						if CreateModifyFeatureForm.is_valid():
							idd=int(key.split('_')[-1])
							a=CreateModifyFeatureForm.DeleteFeatureCode(idd)
							context['error']=a[1]
							messages.error(request, a[1])

			CreateModifyFeatureForm=fm.CreateModifyFeatureForm(user=request.user)

	else:
		CreateModifyFeatureForm=fm.CreateModifyFeatureForm(user=request.user)



	return render(request, 'research/createmodifyfeature.html',{'CreateModifyFeatureForm':CreateModifyFeatureForm},context)





@csrf_exempt
def tagsubmit(request):
	context = RequestContext(request)
	print request.user
	if str(request.user)=='AnonymousUser' or str(request.user)=='@general@':
		return HttpResponse("login to tag data")

		
	if request.method == 'POST':
		try:
			print request.POST
			Symbol=request.POST.get('Symbol')
			stk=stkmd.Stock.objects.get(Symbol=Symbol)
			T=request.POST.get('T')
			T=pd.to_datetime(T,format="%Y-%m-%d")
			Interval=request.POST.get('Interval')
			window=int(request.POST.get('window'))
			requser=request.POST.get('user')

			if str(requser)=='AnonymousUser' or str(requser)=='@general@':
				return HttpResponse("login to tag data")

			try:
				requser=User.objects.get(username=requser)
			except:
				return HttpResponse("Invalid User, register and login to tag data")
			

			cats=md.Category.objects.filter(Type='G')

			print T
			print Symbol
			print Interval
			print window
			print cats

			for cc in cats:
				if request.POST.get('cat'+str(cc.pk),'-101-')=='-101-':
					if md.Grading.objects.filter(user=requser,Symbol=stk,Category__pk=cc.pk,T=T,Interval=Interval,window=window).exists()==True:
						gg=md.Grading.objects.get(user=requser,Symbol=stk,Category__pk=cc.pk,T=T,Interval=Interval,window=window)
						gg.delete()

				else:
					grade=request.POST.get('cat'+str(cc.pk),'-101-')

					if md.Grading.objects.filter(user=requser,Symbol=stk,Category__pk=cc.pk,T=T,Interval=Interval,window=window).exists()==False:
						gg=md.Grading(user=requser,Symbol=stk,Category_id=cc.pk,T=T,Interval=Interval,window=window,Grade=grade)
						gg.save()
					else:
						gg=md.Grading.objects.get(user=requser,Symbol=stk,Category__pk=cc.pk,T=T,Interval=Interval,window=window)
						gg.Grade=grade
						gg.save()

			return HttpResponse("Updated")
		except Exception as e:
			return HttpResponse("error processing tag: "+str(traceback.format_exc()))		
	else:
		return HttpResponse("error reading request")


@login_required(login_url='/login/')
def Study(request):
	context = RequestContext(request)
	print request.user

	if request.method == 'POST':
		if request.POST.get('submit', '')=="Submit":
			StudyForm=fm.WindowQueryForm(request.POST,user=request.user,mode='Study')
			if StudyForm.is_valid():
				StudyForm

			else:
				StudyForm=fm.WindowQueryForm(user=request.user,mode='Study')

		elif request.POST.get('shift_left', '')=="Shift T to left":
			pass

		elif request.POST.get('shift_right', '')=="Shift T to right":
			pass

		else:
			StudyForm=fm.WindowQueryForm(user=request.user,mode='Study')	


	else:
		StudyForm=fm.WindowQueryForm(user=request.user,mode='Study')

	return render(request, 'research/study.html',{'StudyForm':StudyForm},context)


def ResearchStatus(request):
	context = RequestContext(request)
	import research.libs as libs
	df=libs.ComputeStatus()
	dAll=mark_safe(str(df.to_html(index=False,escape=False,classes=["TFtable"])) ) 
	del df

	return render(request, 'research/researchstatus.html',{'dAll':dAll},context)


def ComputeLog(request):
	ff=os.path.join( settings.BASE_DIR,'celerylog' )
	if os.path.isfile(ff)==True:
		celerylog=mark_safe(sbp.check_output(['tail','-100',ff ]).replace('\n','<br>\n'))
	else:
	    celerylog="log file does not exist yet"

	ff=os.path.join( settings.BASE_DIR,'djangolog' )
	if os.path.isfile(ff)==True:
		djangolog=mark_safe(sbp.check_output(['tail','-100',ff ]).replace('\n','<br>\n'))
	else:
	    djangolog="log file does not exist yet"

	return render(request, 'research/compute_logs.html',{'djangolog':djangolog,
															'celerylog':celerylog
															})

def Learning(request):
	context = RequestContext(request)
	pp=os.path.join('/mnt/volume-nyc1-01/media/Learning/','Classification_1.h5')
	N=100
	Learning={}
	Learning['pageno']=int(request.GET.get('pageno', -1))
	k=1
	isset=False
	for reader in pd.read_hdf(pp,'table',chunksize=N):
		if Learning['pageno'] >=0:
			if k==int(Learning['pageno']):
				isset=True
				break
		else:
			Learning['pageno']=1
			isset=True
			break
		k=k+1
	if isset==False:
		for reader in pd.read_hdf(pp,'table',chunksize=N):
			Learning['pageno']=1
			break

	reader.index=reader.index+1
	df=reader[['No','T','Symbol','Industry','Sector','FutMNRtQt','FutMXRtQt','FutMNRtHf','FutMXRtHf','FutMNRtAn','FutMXRtAn','charts']].copy()
	del reader
	df['Target']='Sell'
	df['Target']=df.apply(lambda row: 'Hold' if row['FutMXRtHf']>=10 else row['Target'],axis=1)
	df['Target']=df.apply(lambda row: 'Buy' if row['FutMNRtHf']>=-10 and row['FutMXRtHf']>=10 else row['Target'],axis=1)
	df=df[['No','Target','T','Symbol','Industry','Sector','FutMNRtQt','FutMXRtQt','FutMNRtHf','FutMXRtHf','FutMNRtAn','FutMXRtAn','charts']]
 	ss=str(df.to_html(classes=["tablesorter"],index=False,escape=False))
	ss=ss.replace('tablesorter"','tablesorter" id="myTable"').replace('dataframe','').replace('border="1"','')
	ss=ss.replace('<th>','<th class="rotate"><div><span>').replace('</th>','</span></div></th>')
 	Learning['table']=mark_safe( ss ) 
 	Learning['description']="""
 	This is all the charts from January 2015 to December 2015 for every Monday. The columns shown below
 	show the best possible Profit and loss. The objective is to design features using only the price data so as to classify them as a Buy or not. Typically a good
 	Buy is the one which leads to higher profit and minimal drawdown. Once you design a feature go ahead and code up the feature
 	"""

	# paginator = Paginator(df.index, 25)
	# try:
	# 	pages = paginator.page(pageno)
	# except PageNotAnInteger:
	# 	# If page is not an integer, deliver first page.
	# 	pages = paginator.page(1)
	# 	pageno=1
	# except EmptyPage:
	# 	# If page is out of range (e.g. 9999), deliver last page of results.
	# 	pages = paginator.page(paginator.num_pages)
	# SQVIEW[i]['pages']=pages
	# SQVIEW[i]['pageno']=pageno

	return render(request, 'research/Learning.html',{'Learning':Learning},context)
