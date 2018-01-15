import json
import pandas as pd
import numpy as np
import featureapp.models as filename







#############################################  Features

def standardizefeaturedata(df):
	if df.empty:
		return pd.DataFrame(columns=['T','Symbol_id','Symbol'])

	# df.rename(columns={'Symbol__Symbol':'Symbol'},inplace=True)
	df['Symbol']=df['Symbol'].astype(str)
	df['Symbol_id']=df['Symbol_id'].astype(int)

	df['T']=df['T'].apply(lambda x: pd.to_datetime(x).date())
	df.index=df['T'].copy()
	df.drop(['T'],axis=1,inplace=True)


	dffeat=pd.DataFrame(df['Featuredata'].tolist())
	df.drop(['Featuredata'],axis=1,inplace=True)
	dffeat.index=df.index

	for cc in dffeat.columns:
		try:
			if ftamd.FeaturesMeta.objects.filter(Featurelabel=cc).exists():
				rettype=ftamd.FeaturesMeta.objects.get(Featurelabel=cc).Returntype
				if rettype!='json':
					dffeat[cc]=dffeat[cc].astype(eval(rettype))
		except:
			pdb.set_trace()


	df=pd.concat([df, dffeat], axis=1)
	
	df = df.where((pd.notnull(df)), np.nan)
	df.sort_index(inplace=True)

	return df

# @mnt.logperf('debug',printit=True)
def GetFeatures(Symbolids=None,Fromdate=pd.datetime(2002,1,1).date(),Todate=pd.datetime.today().date(),format='concat',standardize=True):

	if type(Symbolids)!=list and type(Symbolids)!=tuple:
		Symbolids=list((Symbolids))

	if format=='concat':
		Qrysets=ftamd.FeaturesData.objects.filter(Symbol_id__in=Symbolids,T__gte=Fromdate,T__lte=Todate).values('T','Symbol_id','Symbol','Featuredata')
		df=pd.DataFrame( list(Qrysets ))
		if standardize:
			df=standardizefeaturedata(df)
		return df

	elif format=='dict':
		DF={}
		for Symbolid in Symbolids:
			Qrysets=ftamd.FeaturesData.objects.filter(Symbol_id=Symbolid,T__gte=Fromdate,T__lte=Todate).values('T','Symbol_id','Symbol','Featuredata')
			DF[Symbolid]=pd.DataFrame( list(Qrysets ))
			if standardize:
				DF[Symbolid]=standardizefeaturedata(DF[Symbolid])


		return DF
