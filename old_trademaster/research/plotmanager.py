from __future__ import division
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import mpld3
from django.utils.safestring import mark_safe
import gc
import collections
import numpy as np
import pdb
import pandas as pd
import pdb

def percentile20(x):
	x=x[~np.isnan(x)]
	if len(x)==0:
		return np.nan
	return np.percentile(x,20)
def percentile50(x):
	x=x[~np.isnan(x)]
	if len(x)==0:
		return np.nan
	return np.percentile(x,50)
def percentile80(x):
	x=x[~np.isnan(x)]
	if len(x)==0:
		return np.nan
	return np.percentile(x,80)

def countnonnan(x):
	x=x[~np.isnan(x)]
	return np.count_nonzero(~np.isnan(x))


#mode='CombinedQry'
#mode='GenQry'
def GethistPlotsQuery_perf_faster(df):
	import research.models as rmd
	Vars=['FutMXRtQt','FutMXRtHf','FutMXRtAn','PastMXRtQt','PastMXRtHf','PastMXRtAn']
	bins=[0,5,10,25,50,100,200,300,400]
	QHST={}
	for var in Vars:
		QHST[var]=[]
		Q={}
		# dd=df[df['name']==var ]
		for bb in bins:
			Q[bb]=len( df[df[var]>=bb])
			
		for bi in range(len(bins)-1):
			QHST[var].append( Q[ bins[bi] ]-Q[ bins[bi+1] ] )
		QHST[var].append(Q[bins[-1]])

	Vars=['FutMNRtQt','FutMNRtHf','FutMNRtAn','PastMNRtQt','PastMNRtHf','PastMNRtAn']
	bins=[0,-5,-10,-25,-50,-100,-200,-300,-400]

	for var in Vars:
		QHST[var]=[]
		Q={}
		for bb in bins:
			Q[bb]=len( df[df[var]<=bb])
		
		for bi in range(len(bins)-1):
			QHST[var].append( Q[ bins[bi] ]-Q[ bins[bi+1] ] )
		QHST[var].append(Q[bins[-1]])
		

	Plotstrs={}

	# ---------------------------------------------------
	width=1
	fig, ax = plt.subplots(figsize=(5,3))
	bins=[0,5,10,25,50,100,200,300,400]
	ax.bar([0,1,2,3,4,5,6,7,8], QHST['FutMXRtQt'], width, color='b',alpha=0.5, label='Profit')

	bins=[0,-5,-10,-25,-50,-100,-200,-300,-400]
	ax.bar([0,-1,-2,-3,-4,-5,-6,-7,-8], QHST['FutMNRtQt'], -width, color='r',alpha=0.5, label='Loss')

	ax.set_title('Best possible Profit and loss in T+3months',fontsize=8)
	ax.set_xticks([-8,-7,-6,-5,-4,-3,-2,-1,0,1,2,3,4,5,6,7,8])
	ax.set_xticklabels([r'$\leq$-400','-300','-200','-100','-50','-25','-10','-5','0','5','10','25','50','100','200','300',r'$\geq$400'], fontsize=20,rotation=45)
	ax.grid()
	ax.legend(loc='upper center',borderaxespad=0., bbox_to_anchor=(0.5, 1.3),ncol=2, fancybox=True, shadow=True,fontsize=10)
	ax.set_xlabel('%Return',fontsize=8)
	ax.set_ylabel('Number of T-dates',fontsize=8)
	ax.tick_params(axis='x', which='major', labelsize=10)
	ax.tick_params(axis='y', which='major', labelsize=10)
	plt.tight_layout()

	if rmd.GeneralFile.objects.filter(T=pd.datetime.today().date(),name='Query_FutMNRtQt_FutMXRtQt',extn='.png').exists():
		GnF=rmd.GeneralFile.objects.get(T=pd.datetime.today().date(),name='Query_FutMNRtQt_FutMXRtQt',extn='.png')
	else:
		GnF=rmd.GeneralFile(T=pd.datetime.today().date(),name='Query_FutMNRtQt_FutMXRtQt',extn='.png')
		GnF.save()

	GnF.uploadfig2file(fig)
	Plotstrs['FutMXRtQt']=GnF.GetImage(width="500px",height="300px",mode='lazy')
	plt.close(fig)
	gc.collect()
	# ---------------------------------------------------

	width=1
	fig, ax = plt.subplots(figsize=(5,3))
	bins=[0,5,10,25,50,100,200,300,400]
	ax.bar([0,1,2,3,4,5,6,7,8], QHST['FutMXRtHf'], width, color='b',alpha=0.5, label='Profit')

	bins=[0,-5,-10,-25,-50,-100,-200,-300,-400]
	ax.bar([0,-1,-2,-3,-4,-5,-6,-7,-8], QHST['FutMNRtHf'], -width, color='r',alpha=0.5, label='Loss')

	ax.set_title('Best possible Profit and loss in T+6months',fontsize=8)
	ax.set_xticks([-8,-7,-6,-5,-4,-3,-2,-1,0,1,2,3,4,5,6,7,8])
	ax.set_xticklabels([r'$\leq$-400','-300','-200','-100','-50','-25','-10','-5','0','5','10','25','50','100','200','300',r'$\geq$400'], fontsize=20,rotation=45)
	ax.grid()
	ax.legend(loc='upper center',borderaxespad=0., bbox_to_anchor=(0.5, 1.3),ncol=2, fancybox=True, shadow=True,fontsize=10)
	ax.set_xlabel('%Return',fontsize=8)
	ax.set_ylabel('Number of T-dates',fontsize=8)
	ax.tick_params(axis='x', which='major', labelsize=10)
	ax.tick_params(axis='y', which='major', labelsize=10)
	plt.tight_layout()

	name='Query_FutMNRtHf_FutMXRtHf'
	if rmd.GeneralFile.objects.filter(T=pd.datetime.today().date(),name=name,extn='.png').exists():
		GnF=rmd.GeneralFile.objects.get(T=pd.datetime.today().date(),name=name,extn='.png')
	else:
		GnF=rmd.GeneralFile(T=pd.datetime.today().date(),name=name,extn='.png')
		GnF.save()

	GnF.uploadfig2file(fig)
	Plotstrs['FutMXRtHf']=GnF.GetImage(width="500px",height="300px",mode='lazy')
	plt.close(fig)
	gc.collect()




	# ---------------------------------------------------
	width=1
	fig, ax = plt.subplots(figsize=(5,3))
	bins=[0,5,10,25,50,100,200,300,400]
	ax.bar([0,1,2,3,4,5,6,7,8], QHST['FutMXRtAn'], width, color='b',alpha=0.5, label='Profit')

	bins=[0,-5,-10,-25,-50,-100,-200,-300,-400]
	ax.bar([0,-1,-2,-3,-4,-5,-6,-7,-8], QHST['FutMNRtAn'], -width, color='r',alpha=0.5, label='Loss')

	ax.set_title('Best possible Profit and loss in T+1year',fontsize=8)
	ax.set_xticks([-8,-7,-6,-5,-4,-3,-2,-1,0,1,2,3,4,5,6,7,8])
	ax.set_xticklabels([r'$\leq$-400','-300','-200','-100','-50','-25','-10','-5','0','5','10','25','50','100','200','300',r'$\geq$400'], fontsize=20,rotation=45)
	ax.grid()
	ax.legend(loc='upper center',borderaxespad=0., bbox_to_anchor=(0.5, 1.3),ncol=2, fancybox=True, shadow=True,fontsize=10)
	ax.set_xlabel('%Return',fontsize=8)
	ax.set_ylabel('Number of T-dates',fontsize=8)
	ax.tick_params(axis='x', which='major', labelsize=10)
	ax.tick_params(axis='y', which='major', labelsize=10)
	plt.tight_layout()
	
	name='Query_FutMNRtAn_FutMXRtAn'
	if rmd.GeneralFile.objects.filter(T=pd.datetime.today().date(),name=name,extn='.png').exists():
		GnF=rmd.GeneralFile.objects.get(T=pd.datetime.today().date(),name=name,extn='.png')
	else:
		GnF=rmd.GeneralFile(T=pd.datetime.today().date(),name=name,extn='.png')
		GnF.save()

	GnF.uploadfig2file(fig)
	Plotstrs['FutMXRtAn']=GnF.GetImage(width="500px",height="300px",mode='lazy')
	plt.close(fig)
	gc.collect()




	# ------------------PAST Perf---------------------------------
	width=1
	fig, ax = plt.subplots(figsize=(5,3))
	bins=[0,5,10,25,50,100,200,300,400]
	ax.bar([0,1,2,3,4,5,6,7,8], QHST['PastMXRtQt'], width, color='b',alpha=0.5, label='Profit')

	bins=[0,-5,-10,-25,-50,-100,-200,-300,-400]
	ax.bar([0,-1,-2,-3,-4,-5,-6,-7,-8], QHST['PastMNRtQt'], -width, color='r',alpha=0.5, label='Loss')

	ax.set_title('Best possible Profit and loss in T-3months',fontsize=8)
	ax.set_xticks([-8,-7,-6,-5,-4,-3,-2,-1,0,1,2,3,4,5,6,7,8])
	ax.set_xticklabels([r'$\leq$-400','-300','-200','-100','-50','-25','-10','-5','0','5','10','25','50','100','200','300',r'$\geq$400'], fontsize=20,rotation=45)
	ax.grid()
	ax.legend(loc='upper center',borderaxespad=0., bbox_to_anchor=(0.5, 1.3),ncol=2, fancybox=True, shadow=True,fontsize=10)
	ax.set_xlabel('%Return',fontsize=8)
	ax.set_ylabel('Number of T-dates',fontsize=8)
	ax.tick_params(axis='x', which='major', labelsize=10)
	ax.tick_params(axis='y', which='major', labelsize=10)
	plt.tight_layout()

	name='Query_PastMNRtQt_PastMXRtQt'
	if rmd.GeneralFile.objects.filter(T=pd.datetime.today().date(),name=name,extn='.png').exists():
		GnF=rmd.GeneralFile.objects.get(T=pd.datetime.today().date(),name=name,extn='.png')
	else:
		GnF=rmd.GeneralFile(T=pd.datetime.today().date(),name=name,extn='.png')
		GnF.save()

	GnF.uploadfig2file(fig)
	Plotstrs['PastMXRtQt']=GnF.GetImage(width="500px",height="300px",mode='lazy')
	plt.close(fig)
	gc.collect()




	# ---------------------------------------------------
	width=1
	fig, ax = plt.subplots(figsize=(5,3))
	bins=[0,5,10,25,50,100,200,300,400]
	ax.bar([0,1,2,3,4,5,6,7,8], QHST['PastMXRtHf'], width, color='b',alpha=0.5, label='Profit')

	bins=[0,-5,-10,-25,-50,-100,-200,-300,-400]
	ax.bar([0,-1,-2,-3,-4,-5,-6,-7,-8], QHST['PastMNRtHf'], -width, color='r',alpha=0.5, label='Loss')

	ax.set_title('Best possible Profit and loss in T-6months',fontsize=8)
	ax.set_xticks([-8,-7,-6,-5,-4,-3,-2,-1,0,1,2,3,4,5,6,7,8])
	ax.set_xticklabels([r'$\leq$-400','-300','-200','-100','-50','-25','-10','-5','0','5','10','25','50','100','200','300',r'$\geq$400'], fontsize=20,rotation=45)
	ax.grid()
	ax.legend(loc='upper center',borderaxespad=0., bbox_to_anchor=(0.5, 1.3),ncol=2, fancybox=True, shadow=True,fontsize=10)
	ax.set_xlabel('%Return',fontsize=8)
	ax.set_ylabel('Number of T-dates',fontsize=8)
	ax.tick_params(axis='x', which='major', labelsize=10)
	ax.tick_params(axis='y', which='major', labelsize=10)
	plt.tight_layout()

	name='Query_PastMNRtHf_PastMXRtHf'
	if rmd.GeneralFile.objects.filter(T=pd.datetime.today().date(),name=name,extn='.png').exists():
		GnF=rmd.GeneralFile.objects.get(T=pd.datetime.today().date(),name=name,extn='.png')
	else:
		GnF=rmd.GeneralFile(T=pd.datetime.today().date(),name=name,extn='.png')
		GnF.save()

	GnF.uploadfig2file(fig)
	Plotstrs['PastMXRtHf']=GnF.GetImage(width="500px",height="300px",mode='lazy')
	plt.close(fig)
	gc.collect()



	# ---------------------------------------------------
	width=1
	fig, ax = plt.subplots(figsize=(5,3))
	bins=[0,5,10,25,50,100,200,300,400]
	ax.bar([0,1,2,3,4,5,6,7,8], QHST['PastMXRtAn'], width, color='b',alpha=0.5, label='Profit')

	bins=[0,-5,-10,-25,-50,-100,-200,-300,-400]
	ax.bar([0,-1,-2,-3,-4,-5,-6,-7,-8], QHST['PastMNRtAn'], -width, color='r',alpha=0.5, label='Loss')

	ax.set_title('Best possible Profit and loss in T-1year',fontsize=8)
	ax.set_xticks([-8,-7,-6,-5,-4,-3,-2,-1,0,1,2,3,4,5,6,7,8])
	ax.set_xticklabels([r'$\leq$-400','-300','-200','-100','-50','-25','-10','-5','0','5','10','25','50','100','200','300',r'$\geq$400'], fontsize=20,rotation=45)
	ax.grid()
	ax.legend(loc='upper center',borderaxespad=0., bbox_to_anchor=(0.5, 1.3),ncol=2, fancybox=True, shadow=True,fontsize=10)
	ax.set_xlabel('%Return',fontsize=8)
	ax.set_ylabel('Number of T-dates',fontsize=8)
	ax.tick_params(axis='x', which='major', labelsize=10)
	ax.tick_params(axis='y', which='major', labelsize=10)
	plt.tight_layout()
	
	name='Query_PastMNRtAn_PastMXRtAn'
	if rmd.GeneralFile.objects.filter(T=pd.datetime.today().date(),name=name,extn='.png').exists():
		GnF=rmd.GeneralFile.objects.get(T=pd.datetime.today().date(),name=name,extn='.png')
	else:
		GnF=rmd.GeneralFile(T=pd.datetime.today().date(),name=name,extn='.png')
		GnF.save()

	GnF.uploadfig2file(fig)
	Plotstrs['PastMXRtAn']=GnF.GetImage(width="500px",height="300px",mode='lazy')
	plt.close(fig)
	gc.collect()



	return Plotstrs


#  Make summary plots for a given query df
def SummaryPlots(df,returnfmt={'mpld3':True}):
	from . import models as md
	if 'SQ' in returnfmt:
		SQ=returnfmt['SQ']['SQ']
		T=returnfmt['SQ']['T']


	# Number of stocks in each sector
	counter=collections.Counter(df['Sector'].tolist())
	fig, ax = plt.subplots(figsize=(20,50))	
	ax.pie(counter.values(), explode=[0.1]*len(counter.keys()),labels=counter.keys(),autopct='%1.1f%%', shadow=True, startangle=90)
	ax.set_aspect('equal')
	# ax.set_fontsize(12)
	plt.tight_layout()
	SQPl1=md.SavedQueries_plots.objects.filter(savedquery=SQ,T=T,plotname='SectorPie')
	if SQPl1.exists():
		SQDF=md.SavedQueries_plots.objects.get(savedquery=SQ,T=T,plotname='SectorPie')
	else:
		SQDF=md.SavedQueries_plots(savedquery=SQ,T=T,plotname='SectorPie')
	SQDF.plotsize={'width':'300px','height':'300px'}
	SQDF.uploadfig2file(fig)
	SQDF.save()
	plt.clf()
	plt.close(fig)
	gc.collect()

	del SQDF
	del SQPl1
	del counter

	# 20-50-80 plots for sector performances
	for pp in md.PastPerfFeats:
		fig, ax = plt.subplots(1,2,figsize=(30,15))
		figname='Sector'+' '+pp[0]+'-'+pp[1]
		dd=df[['Sector',pp[0],pp[1]]].groupby('Sector').agg([percentile20,percentile50,percentile80,countnonnan])
		dd['#stocks']=np.minimum(dd[pp[0]]['countnonnan'].values,dd[pp[1]]['countnonnan'].values)
		dd=dd[dd['#stocks']>5]
		xtmax=max([dd[pp[0]]['percentile80'].abs().max(),dd[pp[0]]['percentile20'].abs().max(),dd[pp[1]]['percentile80'].abs().max(),dd[pp[1]]['percentile20'].abs().max()])+10
		dd=dd.loc[dd.index!='nan',:]
		dd.sort_index(ascending=False,inplace=True)
		# pdb.set_trace()
		dd['Sector']=dd.index
		width=0.3
		bins=np.arange(len(dd))
		ax[0].barh(bins, (dd[pp[0]]['percentile80']-dd[pp[0]]['percentile20']).values, width, left=dd[pp[0]]['percentile20'].values, color='r',alpha=0.5)
		for kk in range(len(dd)):
			ax[0].plot([ dd[pp[0]]['percentile50'].iloc[kk],dd[pp[0]]['percentile50'].iloc[kk] ],[bins[kk],bins[kk]+width ],'b',linewidth=2)
		ax[0].grid()
		ax[0].set_title('Sector Performance '+pp[0],fontsize=25)
		xticks=np.rint(np.linspace(-xtmax,0,15)) 
		xticks=[int(xx) for xx in xticks]


		ax[0].set_xticks(xticks)
		ax[0].set_yticks(bins+width/2)
		ax[0].set_yticklabels(dd['Sector'], rotation=0,fontsize=30)
		ax[0].set_xticklabels(xticks, rotation=45,fontsize=25)
		# ax[0].yaxis.tick_right()
		ax[0].set_yticks([])

		ax[1].barh(bins, (dd[pp[1]]['percentile80']-dd[pp[1]]['percentile20']).values, width, left=dd[pp[1]]['percentile20'].values, color='b',alpha=0.5)
		for kk in range(len(dd)):
			ax[1].plot([ dd[pp[1]]['percentile50'].iloc[kk],dd[pp[1]]['percentile50'].iloc[kk] ],[bins[kk],bins[kk]+width ],'r',linewidth=2)
		ax[1].grid()
		ax[1].set_title('Sector Performance '+pp[1],fontsize=25)
		xticks=np.round(np.linspace(0,xtmax,15))
		xticks=[int(xx) for xx in xticks]
		ax[1].set_xticks(xticks)
		ax[1].set_yticks(bins+width/2)
		ax[1].set_yticklabels(dd['Sector'], rotation=0,fontsize=30)
		ax[1].set_xticklabels(ax[1].get_xticks(), rotation=45,fontsize=25,ha='center')
		plt.draw()
		yax = ax[1].get_yaxis()
		pad = min(T.label.get_window_extent().width for T in yax.majorTicks)
		yax.set_tick_params(pad=pad)

		plt.tight_layout()
		
		SQPl1=md.SavedQueries_plots.objects.filter(savedquery=SQ,T=T,plotname=figname)
		if SQPl1.exists():
			SQDF=md.SavedQueries_plots.objects.get(savedquery=SQ,T=T,plotname=figname)
		else:
			SQDF=md.SavedQueries_plots(savedquery=SQ,T=T,plotname=figname)
		
		SQDF.plotsize={'width':'400px','height':'300px'}

		SQDF.uploadfig2file(fig)
		SQDF.save()
		plt.clf()
		plt.close(fig)
		gc.collect()

		del SQPl1
		del SQDF
	
	# 20-50-80 plots for industry performances
	for pp in md.PastPerfFeats:
		fig, ax = plt.subplots(1,2,figsize=(30,90))
		figname='Industry'+' '+pp[0]+'-'+pp[1]
		dd=df[['Industry',pp[0],pp[1]]].groupby('Industry').agg([percentile20,percentile50,percentile80,countnonnan])
		dd['#stocks']=np.minimum(dd[pp[0]]['countnonnan'].values,dd[pp[1]]['countnonnan'].values)
		dd=dd[dd['#stocks']>5]

		xtmax=max([dd[pp[0]]['percentile80'].abs().max(),dd[pp[0]]['percentile20'].abs().max(),dd[pp[1]]['percentile80'].abs().max(),dd[pp[1]]['percentile20'].abs().max()])+10
		dd=dd.loc[dd.index!='nan',:]
		dd.sort_index(ascending=False,inplace=True)
		# pdb.set_trace()
		dd['Industry']=dd.index
		width=1
		bins=np.arange(len(dd))*2
		ax[0].barh(bins, (dd[pp[0]]['percentile80']-dd[pp[0]]['percentile20']).values, width, left=dd[pp[0]]['percentile20'].values, color='r',alpha=0.5)
		for kk in range(len(dd)):
		    ax[0].plot([ dd[pp[0]]['percentile50'].iloc[kk],dd[pp[0]]['percentile50'].iloc[kk] ],[bins[kk],bins[kk]+width ],'b',linewidth=2)
		ax[0].grid()
		ax[0].set_title('Industry Performance '+pp[0],fontsize=25)
		xticks=np.rint(np.linspace(-xtmax,0,15)) 
		xticks=[int(xx) for xx in xticks]
		ax[0].set_xticks(xticks)
		ax[0].set_yticks(bins+width/2)
		ax[0].set_yticklabels(dd['Industry'], rotation=0,fontsize=25)
		ax[0].set_ylim([min(bins)-5*width,max(bins)+5*width])
		ax[0].set_xticklabels(xticks, rotation=45,fontsize=25)
		# ax[0].yaxis.tick_right()
		ax[0].set_yticks([])

		ax[1].barh(bins, (dd[pp[1]]['percentile80']-dd[pp[1]]['percentile20']).values, width, left=dd[pp[1]]['percentile20'].values, color='b',alpha=0.5)
		for kk in range(len(dd)):
		    ax[1].plot([ dd[pp[1]]['percentile50'].iloc[kk],dd[pp[1]]['percentile50'].iloc[kk] ],[bins[kk],bins[kk]+width ],'r',linewidth=2)
		ax[1].grid()
		ax[1].set_title('Industry Performance '+pp[1],fontsize=25)
		xticks=np.round(np.linspace(0,xtmax,15))
		xticks=[int(xx) for xx in xticks]
		ax[1].set_xticks(xticks)
		ax[1].set_yticks(bins+width/2)
		ax[1].set_yticklabels(dd['Industry'], rotation=0,fontsize=25)
		ax[1].set_ylim([min(bins)-5*width,max(bins)+5*width])
		ax[1].set_xticklabels(ax[1].get_xticks(), rotation=45,fontsize=25,ha='center')
		plt.draw()
		yax = ax[1].get_yaxis()
		pad = min(T.label.get_window_extent().width for T in yax.majorTicks)
		yax.set_tick_params(pad=pad)

		plt.tight_layout()

		
		SQPl1=md.SavedQueries_plots.objects.filter(savedquery=SQ,T=T,plotname=figname)
		if SQPl1.exists():
			SQDF=md.SavedQueries_plots.objects.get(savedquery=SQ,T=T,plotname=figname)
		else:
			SQDF=md.SavedQueries_plots(savedquery=SQ,T=T,plotname=figname)
		
		SQDF.plotsize={'width':'500px','height':'2000px'}
		
		SQDF.uploadfig2file(fig)
		SQDF.save()
		plt.clf()
		plt.close(fig)
		gc.collect()

		del SQPl1
		del SQDF


	try:
		del fig
	except:
		pass
	try:
		del ax
	except:
		pass

	gc.collect()
	return 1
	# Performce Plots
	



