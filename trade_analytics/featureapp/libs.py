




import json
import pandas as pd
import numpy as np
import featureapp.models as ftmd
import stockapp.models as stkmd
import dataapp.models as dtamd
import dataapp.libs as dtalibs
import functools
from utility import maintenance as mnt
import pdb
import logging
logger = logging.getLogger('debug')


def standardizefeaturedata(df):

	df.rename(columns={'Symbol__id':'Symbolid','Symbol__Symbol':'Symbol'},inplace=True)
	df['Symbol']=df['Symbol'].astype(str)
	df['Symbolid']=df['Symbolid'].astype(int)

	df['T']=df['T'].apply(lambda x: pd.to_datetime(x).date())
	df.index=df['T'].copy()
	df.drop(['T'],axis=1,inplace=True)


	dffeat=pd.DataFrame(df['Featuredata'].tolist())
	df.drop(['Featuredata'],axis=1,inplace=True)
	dffeat.index=df.index

	for cc in dffeat.columns:
		if ftmd.FeaturesMeta.objects.filter(Featurelabel=cc).exists():
			rettype=ftmd.FeaturesMeta.objects.get(Featurelabel=cc).Returntype
			if rettype!='json':
				dffeat[cc]=dffeat[cc].astype(eval(rettype))



	df=pd.concat([df, dffeat], axis=1)
	
	df = df.where((pd.notnull(df)), np.nan)
	df.sort_index(inplace=True)

	return df

@mnt.logperf('debug',printit=True)
def GetFeatures(Symbolids=None,Fromdate=pd.datetime(2002,1,1).date(),Todate=pd.datetime.today().date(),format='concat',standardize=True):

	if type(Symbolids)!=list and type(Symbolids)!=tuple:
		Symbolids=list((Symbolids))

	if format=='concat':
		Qrysets=ftmd.FeaturesData.objects.filter(Symbol__id__in=Symbolids,T__gte=Fromdate,T__lte=Todate).values('T','Symbol__id','Symbol__Symbol','Featuredata')
		df=pd.DataFrame( list(Qrysets ))
		if standardize:
			df=standardizefeaturedata(df)
		return df

	elif format=='dict':
		DF={}
		for Symbolid in Symbolids:
			Qrysets=ftmd.FeaturesData.objects.filter(Symbol__id=Symbolid,T__gte=Fromdate,T__lte=Todate).values('T','Symbol__id','Symbol__Symbol','Featuredata')
			DF[Symbolid]=pd.DataFrame( list(Qrysets ))
			if standardize:
				DF[Symbolid]=standardizefeaturedata(DF[Symbolid])


		return DF


def GetFeature_iterator(Symbolids=None,Trange=[T.date() for T in pd.date_range(pd.datetime(2002,1,1),pd.datetime.today()) if T.weekday()<=4] ):
	if Symbolids==None:
		Symbolids=stkmd.Stockmeta.objects.all().values_list('id',flat=True)

	if type(Symbolids)!=list and type(Symbolids)!=tuple:
		Symbolids=list((Symbolids))

	for sid in Symbolids:
		yield ( stkmd.Stockmeta.objects.get(id=sid),GetFeatures(Symbolids=[sid],Trange=Trange) )


