from __future__ import division
from datascience.ML.MLmodels  import *
import datascience.libs as dtsclibs
import datascience.models as dtscmd
import pdb

filename=__name__.split('.')[-1]

#################### ------------ Some Data Statistics-------------- ##################################

@dtsclibs.register_compfunc(Group='Meta',overwrite_if_exists=True)
def DataShardMeta_1(DataShardId):
	"""
	Get meta data from shards
	- Get Nans in X and Y
	- Get shapes of X and Y
	"""
	shard=dtscmd.DataShard.objects.get(id=DataShardId)
	X,Y,Meta=shard.getdata()
	NXnans=np.count_nonzero(np.isnan(X))
	NYnans=np.count_nonzero(np.isnan(Y))


	return (NXnans,NYnans,X.shape,Y.shape)

#################### ------------ Some Data Transformers-------------- ##################################

@dtsclibs.register_compfunc(Group='Transformer',overwrite_if_exists=True)
def StandardizeData_1(X,Y,Meta):
	"""
	A transformer function has to take X,Y,Meta and return another modified X,Y,Meta
	1. Normalize all data as 
		1. Volume to 0-1
		2. Prices --> also 0-1
	2. For output Y data:
		1. Take only Close
		2. Pull out best returns in first 5 days, 10 days, 30 days, 60 days, 90 days
		3. Pull out worst loss in first 5 days, 10 days, 30 days, 60 days, 90 days
	
   
	"""
	
	import pandas as pd
	import numpy as np

	# next normalize the volume to 0-1
	Nsamples=X.shape[0]
	Tsteps=X.shape[1]
	Nfeat=X.shape[2]
	volumecols=['Volume','VolSMA10','VolSMA20']
	pricecols=['Close','Open','High','Low','SMA10','SMA20','SMA50','SMA100','SMA200','EMA8','EMA20']
	colsX=list( Meta['MetaX']['columns'] )
	colsY=list( Meta['MetaY']['columns'] )
	FinalXcols=pricecols+volumecols
	FinalYcols=['FutProfit5days','FutProfit10days','FutProfit30days','FutProfit60days','FutProfit90days']+['FutLoss5days',
									'FutLoss10days','FutLoss30days','FutLoss60days','FutLoss90days']
	
	Xn=None
	Yn=None
	Metan=None
	for i in range(Nsamples):
		dfX=pd.DataFrame(X[i,:,:],columns=colsX)
		dfY=pd.DataFrame(Y[i,:,:],columns=colsY)
		
		
		# clean up Y
		dfY.drop('Symbol',axis=1,inplace=True)
		
		dfY.drop(volumecols,axis=1,inplace=True)
		dfY.drop([cc for cc in pricecols if cc!='Close'],axis=1,inplace=True)
		
		Ydict={}
		dfY['ZeroPerf']=0
	
#         dfY['FutProfit5days']=-100*self.df['Close'].diff(periods=-5)/self.df['Close']
		dfY['Returns']=100*(dfY['Close']-dfY['Close'].iloc[0])/dfY['Close'].iloc[0]
		
		Ydict['FutProfit5days']=dfY[['Returns','ZeroPerf']].iloc[0:5].max(axis=1).round().max()
		Ydict['FutProfit10days']=dfY[['Returns','ZeroPerf']].iloc[0:10].max(axis=1).round().max()
		Ydict['FutProfit30days']=dfY[['Returns','ZeroPerf']].iloc[0:30].max(axis=1).round().max()
		Ydict['FutProfit60days']=dfY[['Returns','ZeroPerf']].iloc[0:60].max(axis=1).round().max()
		Ydict['FutProfit90days']=dfY[['Returns','ZeroPerf']].iloc[0:90].max(axis=1).round().max()
		
		Ydict['FutLoss5days']=dfY[['Returns','ZeroPerf']].iloc[0:5].min(axis=1).round().min()
		Ydict['FutLoss10days']=dfY[['Returns','ZeroPerf']].iloc[0:10].min(axis=1).round().min()
		Ydict['FutLoss30days']=dfY[['Returns','ZeroPerf']].iloc[0:30].min(axis=1).round().min()
		Ydict['FutLoss60days']=dfY[['Returns','ZeroPerf']].iloc[0:60].min(axis=1).round().min()
		Ydict['FutLoss90days']=dfY[['Returns','ZeroPerf']].iloc[0:90].min(axis=1).round().min()
		
		# clean up X
		dfX.drop('Symbol',axis=1,inplace=True)
		
		mxvol=dfX['Volume'].max()
		dfX['Volume']=dfX['Volume']/mxvol
		dfX['VolSMA10']=dfX['VolSMA10']/mxvol
		dfX['VolSMA20']=dfX['VolSMA20']/mxvol
		
		mxHigh=dfX['High'].max()
		mnLow=dfX['Low'].min()
		for cc in pricecols:
			dfX[cc]=(dfX[cc]-mnLow)/mxHigh
		
		XX=np.expand_dims( dfX[FinalXcols].astype(float).values   ,axis=0     )
		YY=np.expand_dims( np.array([int(Ydict[key]) for key in FinalYcols]),axis=0 )
		if Xn is None:
			Xn=XX
			Yn=YY
		else:
			Xn=np.vstack((Xn,XX))
			Yn=np.vstack((Yn,YY))
	
	Metan=Meta
	Metan['MetaX']['columns']=FinalXcols
	Metan['MetaY']['columns']=FinalYcols
	
	return Xn,Yn,Metan


@dtsclibs.register_compfunc(Group='Transformer',overwrite_if_exists=True)
def StandardizeData_CloseReturnVolume01(X,Y,Meta):
	"""
	A transformer function has to take X,Y,Meta and return another modified X,Y,Meta
	1. Normalize all data as 
		1. Volume to 0-1
		2. Close --> Return
	2. For output Y data:
		1. Take only Close
		2. FutProfit5days
	
   
	"""
	import pandas as pd
	import numpy as np

	# next normalize the volume to 0-1
	Nsamples=X.shape[0]
	Tsteps=X.shape[1]
	Nfeat=X.shape[2]
	volumecols=['Volume']
	pricecols=['Close']
	colsX=list( Meta['MetaX']['columns'] )
	colsY=list( Meta['MetaY']['columns'] )
	FinalXcols=pricecols+volumecols
	FinalYcols=['FutProfit5days']
	
	Xn=None
	Yn=None
	Metan=None
	for i in range(Nsamples):
		dfX=pd.DataFrame(X[i,:,:],columns=colsX)
		dfY=pd.DataFrame(Y[i,:,:],columns=colsY)
		
		
		# clean up Y
		dfY.drop('Symbol',axis=1,inplace=True)
		
		dfY.drop(volumecols,axis=1,inplace=True)
		dfY.drop([cc for cc in pricecols if cc!='Close'],axis=1,inplace=True)
		
		Ydict={}
		dfY['ZeroPerf']=0
	
#         dfY['FutProfit5days']=-100*self.df['Close'].diff(periods=-5)/self.df['Close']
		dfY['Returns']=100*(dfY['Close']-dfY['Close'].iloc[0])/dfY['Close'].iloc[0]
		
		Ydict['FutProfit5days']=dfY[['Returns','ZeroPerf']].iloc[0:5].max(axis=1).round().max()
		Ydict['FutProfit10days']=dfY[['Returns','ZeroPerf']].iloc[0:10].max(axis=1).round().max()
		Ydict['FutProfit30days']=dfY[['Returns','ZeroPerf']].iloc[0:30].max(axis=1).round().max()
		Ydict['FutProfit60days']=dfY[['Returns','ZeroPerf']].iloc[0:60].max(axis=1).round().max()
		Ydict['FutProfit90days']=dfY[['Returns','ZeroPerf']].iloc[0:90].max(axis=1).round().max()
		
		Ydict['FutLoss5days']=dfY[['Returns','ZeroPerf']].iloc[0:5].min(axis=1).round().min()
		Ydict['FutLoss10days']=dfY[['Returns','ZeroPerf']].iloc[0:10].min(axis=1).round().min()
		Ydict['FutLoss30days']=dfY[['Returns','ZeroPerf']].iloc[0:30].min(axis=1).round().min()
		Ydict['FutLoss60days']=dfY[['Returns','ZeroPerf']].iloc[0:60].min(axis=1).round().min()
		Ydict['FutLoss90days']=dfY[['Returns','ZeroPerf']].iloc[0:90].min(axis=1).round().min()
		
		# clean up X
		dfX.drop('Symbol',axis=1,inplace=True)
		
		mxvol=dfX['Volume'].max()
		dfX['Volume']=dfX['Volume']/mxvol
		dfX['VolSMA10']=dfX['VolSMA10']/mxvol
		dfX['VolSMA20']=dfX['VolSMA20']/mxvol
		
		mxHigh=dfX['High'].max()
		mnLow=dfX['Low'].min()
		for cc in pricecols:
			dfX[cc]=(dfX[cc]-mnLow)/mxHigh
		
		XX=np.expand_dims( dfX[FinalXcols].astype(float).values   ,axis=0     )
		YY=np.expand_dims( np.array([int(Ydict[key]) for key in FinalYcols]),axis=0 )
		if Xn is None:
			Xn=XX
			Yn=YY
		else:
			Xn=np.vstack((Xn,XX))
			Yn=np.vstack((Yn,YY))
	
	Metan=Meta
	Metan['MetaX']['columns']=FinalXcols
	Metan['MetaY']['columns']=FinalYcols
	
	return Xn,Yn,Metan


@dtsclibs.register_compfunc(Group='Transformer',overwrite_if_exists=True)
def StandardizeData_Close01Volume01(X,Y,Meta):
	"""
	A transformer function has to take X,Y,Meta and return another modified X,Y,Meta
	1. Normalize all data as 
		1. Volume to 0-1
		2. Close --> 0-1
	2. For output Y data:
		1. Take only Close
		2. FutProfit5days
	
   
	"""
	import pandas as pd
	import numpy as np

	# next normalize the volume to 0-1
	Nsamples=X.shape[0]
	Tsteps=X.shape[1]
	Nfeat=X.shape[2]
	volumecols=['Volume']
	pricecols=['Close']
	colsX=list( Meta['MetaX']['columns'] )
	colsY=list( Meta['MetaY']['columns'] )
	FinalXcols=pricecols+volumecols
	FinalYcols=['FutProfit5days']
	
	Xn=None
	Yn=None
	Metan=None
	for i in range(Nsamples):
		dfX=pd.DataFrame(X[i,:,:],columns=colsX)
		dfY=pd.DataFrame(Y[i,:,:],columns=colsY)
		
		
		# clean up Y
		dfY.drop('Symbol',axis=1,inplace=True)
		
		dfY.drop(volumecols,axis=1,inplace=True)
		dfY.drop([cc for cc in pricecols if cc!='Close'],axis=1,inplace=True)
		
		Ydict={}
		dfY['ZeroPerf']=0
	
#         dfY['FutProfit5days']=-100*self.df['Close'].diff(periods=-5)/self.df['Close']
		dfY['Returns']=100*(dfY['Close']-dfY['Close'].iloc[0])/dfY['Close'].iloc[0]
		
		Ydict['FutProfit5days']=dfY[['Returns','ZeroPerf']].iloc[0:5].max(axis=1).round().max()
		Ydict['FutProfit10days']=dfY[['Returns','ZeroPerf']].iloc[0:10].max(axis=1).round().max()
		Ydict['FutProfit30days']=dfY[['Returns','ZeroPerf']].iloc[0:30].max(axis=1).round().max()
		Ydict['FutProfit60days']=dfY[['Returns','ZeroPerf']].iloc[0:60].max(axis=1).round().max()
		Ydict['FutProfit90days']=dfY[['Returns','ZeroPerf']].iloc[0:90].max(axis=1).round().max()
		
		Ydict['FutLoss5days']=dfY[['Returns','ZeroPerf']].iloc[0:5].min(axis=1).round().min()
		Ydict['FutLoss10days']=dfY[['Returns','ZeroPerf']].iloc[0:10].min(axis=1).round().min()
		Ydict['FutLoss30days']=dfY[['Returns','ZeroPerf']].iloc[0:30].min(axis=1).round().min()
		Ydict['FutLoss60days']=dfY[['Returns','ZeroPerf']].iloc[0:60].min(axis=1).round().min()
		Ydict['FutLoss90days']=dfY[['Returns','ZeroPerf']].iloc[0:90].min(axis=1).round().min()
		
		# clean up X
		dfX.drop('Symbol',axis=1,inplace=True)
		
		mxvol=dfX['Volume'].max()
		dfX['Volume']=dfX['Volume']/mxvol
		dfX['VolSMA10']=dfX['VolSMA10']/mxvol
		dfX['VolSMA20']=dfX['VolSMA20']/mxvol
		
		mxHigh=dfX['High'].max()
		mnLow=dfX['Low'].min()
		for cc in pricecols:
			dfX[cc]=(dfX[cc]-mnLow)/mxHigh
		
		XX=np.expand_dims( dfX[FinalXcols].astype(float).values   ,axis=0     )
		YY=np.expand_dims( np.array([int(Ydict[key]) for key in FinalYcols]),axis=0 )
		if Xn is None:
			Xn=XX
			Yn=YY
		else:
			Xn=np.vstack((Xn,XX))
			Yn=np.vstack((Yn,YY))
	
	Metan=Meta
	Metan['MetaX']['columns']=FinalXcols
	Metan['MetaY']['columns']=FinalYcols
	
	return Xn,Yn,Metan


@dtsclibs.register_compfunc(Group='Transformer',overwrite_if_exists=True)
def StandardizeData_CloseSMAVolSMA10(X,Y,Meta):
	"""
	A transformer function has to take X,Y,Meta and return another modified X,Y,Meta
	1. Normalize all data as 
		1. Volume to 0-1
		2. Prices --> also 0-1
	2. For output Y data:
		1. Take only Close
		2. Pull out best returns in first 5 days, 10 days, 30 days, 60 days, 90 days
		3. Pull out worst loss in first 5 days, 10 days, 30 days, 60 days, 90 days
	
   
	"""
	
	import pandas as pd
	import numpy as np

	# next normalize the volume to 0-1
	Nsamples=X.shape[0]
	Tsteps=X.shape[1]
	Nfeat=X.shape[2]
	volumecols=['Volume','VolSMA10']
	pricecols=['Close','SMA10']
	colsX=list( Meta['MetaX']['columns'] )
	colsY=list( Meta['MetaY']['columns'] )
	FinalXcols=pricecols+volumecols
	FinalYcols=['FutProfit5days','FutProfit10days','FutProfit30days','FutProfit60days','FutProfit90days']+['FutLoss5days',
									'FutLoss10days','FutLoss30days','FutLoss60days','FutLoss90days']
	
	Xn=None
	Yn=None
	Metan=None
	for i in range(Nsamples):
		dfX=pd.DataFrame(X[i,:,:],columns=colsX)
		dfY=pd.DataFrame(Y[i,:,:],columns=colsY)
		
		
		# clean up Y
		dfY.drop('Symbol',axis=1,inplace=True)
		
		dfY.drop(volumecols,axis=1,inplace=True)
		dfY.drop([cc for cc in pricecols if cc!='Close'],axis=1,inplace=True)
		
		Ydict={}
		dfY['ZeroPerf']=0
	
#         dfY['FutProfit5days']=-100*self.df['Close'].diff(periods=-5)/self.df['Close']
		dfY['Returns']=100*(dfY['Close']-dfY['Close'].iloc[0])/dfY['Close'].iloc[0]
		
		Ydict['FutProfit5days']=dfY[['Returns','ZeroPerf']].iloc[0:5].max(axis=1).round().max()
		Ydict['FutProfit10days']=dfY[['Returns','ZeroPerf']].iloc[0:10].max(axis=1).round().max()
		Ydict['FutProfit30days']=dfY[['Returns','ZeroPerf']].iloc[0:30].max(axis=1).round().max()
		Ydict['FutProfit60days']=dfY[['Returns','ZeroPerf']].iloc[0:60].max(axis=1).round().max()
		Ydict['FutProfit90days']=dfY[['Returns','ZeroPerf']].iloc[0:90].max(axis=1).round().max()
		
		Ydict['FutLoss5days']=dfY[['Returns','ZeroPerf']].iloc[0:5].min(axis=1).round().min()
		Ydict['FutLoss10days']=dfY[['Returns','ZeroPerf']].iloc[0:10].min(axis=1).round().min()
		Ydict['FutLoss30days']=dfY[['Returns','ZeroPerf']].iloc[0:30].min(axis=1).round().min()
		Ydict['FutLoss60days']=dfY[['Returns','ZeroPerf']].iloc[0:60].min(axis=1).round().min()
		Ydict['FutLoss90days']=dfY[['Returns','ZeroPerf']].iloc[0:90].min(axis=1).round().min()
		
		# clean up X
		dfX.drop('Symbol',axis=1,inplace=True)
		
		mxvol=dfX['Volume'].max()
		dfX['Volume']=dfX['Volume']/mxvol
		dfX['VolSMA10']=dfX['VolSMA10']/mxvol
		dfX['VolSMA20']=dfX['VolSMA20']/mxvol
		
		mxHigh=dfX['High'].max()
		mnLow=dfX['Low'].min()
		for cc in pricecols:
			dfX[cc]=(dfX[cc]-mnLow)/mxHigh
		
		XX=np.expand_dims( dfX[FinalXcols].astype(float).values   ,axis=0     )
		YY=np.expand_dims( np.array([int(Ydict[key]) for key in FinalYcols]),axis=0 )
		if Xn is None:
			Xn=XX
			Yn=YY
		else:
			Xn=np.vstack((Xn,XX))
			Yn=np.vstack((Yn,YY))
	
	Metan=Meta
	Metan['MetaX']['columns']=FinalXcols
	Metan['MetaY']['columns']=FinalYcols
	
	return Xn,Yn,Metan



@dtsclibs.register_compfunc(Group='Transformer',overwrite_if_exists=True)
def StandardizeData_Close01Volume01_X30_Y5prfbylss_interpcleaned(X,Y,Meta):
	"""
	A transformer function has to take X,Y,Meta and return another modified X,Y,Meta
	1. Normalize all data as 
		1. Close last 30 days --> 0-1
		2. Volume last 30 days --> 0-1
	2. For output Y data:
		0. Take next 5
		1. Take only Close
		2. FutProfit5days/(FutProfit5days+FutLoss5days)
	
   
	"""
	import pandas as pd
	import numpy as np

	# next normalize the volume to 0-1
	Nsamples=X.shape[0]
	
	Tsteps=X.shape[1]
	Nfeat=X.shape[2]

	volumecols=['Volume']
	pricecols=['Close']
	colsX=list( Meta['MetaX']['columns'] )
	colsY=list( Meta['MetaY']['columns'] )
	FinalXcols = pricecols+volumecols
	FinalYcols = ['Fut5days_Profit_BY_SumProfitLoss_Ratio']
	
	Xn=None
	Yn=None
	Metan=None
	for i in range(Nsamples):
		dfX=pd.DataFrame(X[i,:,:],columns=colsX)
		dfY=pd.DataFrame(Y[i,:,:],columns=colsY)
		
		dfX.index=range(len(dfX))
		dfY.index=range(len(dfY))


		# clean up Y
		dfY.drop('Symbol',axis=1,inplace=True)
		
		dfY.drop(volumecols,axis=1,inplace=True)
		dfY.drop([cc for cc in pricecols if cc!='Close'],axis=1,inplace=True)
		
		Ydict={}
		dfY['ZeroPerf']=0
	
#         dfY['FutProfit5days']=-100*self.df['Close'].diff(periods=-5)/self.df['Close']
		if dfY['Close'].iloc[0]==0:
			continue

		dfY['Returns']=100*(dfY['Close']-dfY['Close'].iloc[0])/dfY['Close'].iloc[0]
		profit=np.ceil( dfY[['Returns','ZeroPerf']].iloc[0:5].max(axis=1).max() )
		loss=np.ceil( dfY[['Returns','ZeroPerf']].iloc[0:5].min(axis=1).min() )

		if np.abs(profit) + np.abs(loss)==0:
			Ydict['Fut5days_Profit_BY_SumProfitLoss_Ratio'] = 0
		else:
			Ydict['Fut5days_Profit_BY_SumProfitLoss_Ratio'] = np.abs(profit)/( np.abs(profit) + np.abs(loss) )

		if pd.isnull(Ydict['Fut5days_Profit_BY_SumProfitLoss_Ratio']):
			continue

		# clean up X
		dfX.drop('Symbol',axis=1,inplace=True)
		
		mxvol=dfX['Volume'].max()
		if mxvol==0:
			continue

		dfX['Volume']=dfX['Volume']/mxvol
		
		mx=dfX['Close'].max()
		mn=dfX['Close'].min()

		if mx==0:
			continue

		dfX['Close']=(dfX['Close']-mn)/mx
		
		dfX=dfX[FinalXcols]

		NaNind=dfX[dfX.isnull().any(axis=1)].index
		if len(NaNind)>=len(dfX)/2:
			continue

		if pd.isnull( dfX.loc[0,'Close'] ):
			dfX.loc[0,'Close']=0
		if pd.isnull( dfX.loc[0,'Volume'] ):
			dfX.loc[0,'Volume']=0

		dfX=dfX.interpolate()

		XX=np.expand_dims( dfX.iloc[-30:][FinalXcols].astype(float).values   ,axis=0     )
		YY=np.expand_dims( np.array([int(Ydict[key]) for key in FinalYcols]),axis=0 )
		if Xn is None:
			Xn=XX
			Yn=YY
		else:
			Xn=np.vstack((Xn,XX))
			Yn=np.vstack((Yn,YY))
	
	Metan=Meta
	Metan['MetaX']['columns']=FinalXcols
	Metan['MetaY']['columns']=FinalYcols
	
	return Xn,Yn,Metan


@dtsclibs.register_compfunc(Group='Transformer',overwrite_if_exists=True)
def StandardizeData_Close01Volume01_X30_Y5prfbylss_interpcleaned_flatout(X,Y,Meta):
	"""
	A transformer function has to take X,Y,Meta and return another modified X,Y,Meta
	1. Normalize all data as 
		1. Close last 30 days --> 0-1
		2. Volume last 30 days --> 0-1
	2. For output Y data:
		0. Take next 5
		1. Take only Close
		2. FutProfit5days/(FutProfit5days+FutLoss5days)
	
   
	"""
	
	import pandas as pd
	import numpy as np

	# next normalize the volume to 0-1
	Nsamples=X.shape[0]
	
	Tsteps=X.shape[1]
	Nfeat=X.shape[2]

	volumecols=['Volume']
	pricecols=['Close']
	colsX=list( Meta['MetaX']['columns'] )
	colsY=list( Meta['MetaY']['columns'] )
	FinalXcols = pricecols+volumecols
	FinalYcols = ['Fut5days_Profit_BY_SumProfitLoss_Ratio']
	
	Xn=None
	Yn=None
	Metan=None
	for i in range(Nsamples):
		dfX=pd.DataFrame(X[i,:,:],columns=colsX).iloc[-30:]
		dfY=pd.DataFrame(Y[i,:,:],columns=colsY)
		
		dfX.index=range(len(dfX))
		dfY.index=range(len(dfY))
		
		# clean up Y
		dfY.drop('Symbol',axis=1,inplace=True)
		
		dfY.drop(volumecols,axis=1,inplace=True)
		dfY.drop([cc for cc in pricecols if cc!='Close'],axis=1,inplace=True)
		
		Ydict={}
		dfY['ZeroPerf']=0
	
#         dfY['FutProfit5days']=-100*self.df['Close'].diff(periods=-5)/self.df['Close']
		if dfY['Close'].iloc[0]==0:
			continue

		dfY['Returns']=100*(dfY['Close']-dfY['Close'].iloc[0])/dfY['Close'].iloc[0]
		profit=np.ceil( dfY[['Returns','ZeroPerf']].iloc[0:5].max(axis=1).max() )
		loss=np.ceil( dfY[['Returns','ZeroPerf']].iloc[0:5].min(axis=1).min() )

		if np.abs(profit) + np.abs(loss)==0:
			Ydict['Fut5days_Profit_BY_SumProfitLoss_Ratio'] = 0
		else:
			Ydict['Fut5days_Profit_BY_SumProfitLoss_Ratio'] = np.abs(profit)/( np.abs(profit) + np.abs(loss) )

		if pd.isnull(Ydict['Fut5days_Profit_BY_SumProfitLoss_Ratio']):
			continue



		# clean up X
		dfX.drop('Symbol',axis=1,inplace=True)
		
		mxvol=dfX['Volume'].max()
		if mxvol==0:
			continue

		dfX['Volume']=dfX['Volume']/mxvol
		
		
		mn=dfX['Close'].min()

		

		dfX['Close']=(dfX['Close']-mn)

		mx=dfX['Close'].max()
		if mx==0:
			continue

		dfX['Close']=dfX['Close']/mx

		dfX=dfX[FinalXcols]

		NaNind=dfX[dfX.isnull().any(axis=1)].index
		if len(NaNind)>=len(dfX)/2:
			continue


		if pd.isnull( dfX.loc[0,'Close'] ):
			dfX.loc[0,'Close']=0
		if pd.isnull( dfX.loc[0,'Volume'] ):
			dfX.loc[0,'Volume']=0

		if len(NaNind)>0:
			dfX=dfX.interpolate()


		XX=np.expand_dims( dfX[FinalXcols].astype(float).values.flatten(order='F')   ,axis=0     )
		YY=np.expand_dims( np.array(Ydict['Fut5days_Profit_BY_SumProfitLoss_Ratio']),axis=0 )
		if Xn is None:
			Xn=XX
			Yn=YY
		else:
			Xn=np.vstack((Xn,XX))
			Yn=np.vstack((Yn,YY))
	
	Metan=Meta
	Metan['MetaX']['columns']=FinalXcols
	Metan['MetaY']['columns']=FinalYcols
	
	Metan['MetaX']['shape']=Xn.shape
	Metan['MetaY']['shape']=Yn.shape

	return Xn,Yn,Metan


####################################################################################################
###########################                                #########################################
####################################################################################################

@dtsclibs.register_compfunc(Group='Transformer',overwrite_if_exists=True)
def StandardizeData_HLmeanVolumeSMA01_X30_Y5return_interpcleaned_flatout(X,Y,Meta):
	"""
	A transformer function has to take X,Y,Meta and return another modified X,Y,Meta
	1. Normalize all data as 
		1. (High+Low)/2 last 23 days --> 0-1
		2. Volume last 23 days --> 0-1
		3. 23 days of SMA 10,20,50,100,200 --> 0-1
		4. VolumeSMA10
		4. fill nans with interpolation
		5. flatten the data in order and return
	2. For output Y data:
		0. Take next 5
		1. Take only Close
		2. compute the best return in next 5 days
	
   
	"""
	import pandas as pd
	import numpy as np

	# next normalize the volume to 0-1
	Nsamples=X.shape[0]
	
	Tsteps=X.shape[1]
	Nfeat=X.shape[2]

	volumecols=['Volume','VolSMA10']
	pricecols=['HLmean','SMA10','SMA20','SMA50','SMA100','SMA200']
	colsX=list( Meta['MetaX']['columns'] )
	colsY=list( Meta['MetaY']['columns'] )
	FinalXcols = pricecols+volumecols
	FinalYcols = ['MaxReturn5days']
	
	Xn=None
	Yn=None
	Metan=None
	for i in range(Nsamples):
		dfX=pd.DataFrame(X[i,:,:],columns=colsX).iloc[-23:]
		dfY=pd.DataFrame(Y[i,:,:],columns=colsY)
		
		dfX.index=range(len(dfX))
		dfY.index=range(len(dfY))
		
		dfX['HLmean']=(dfX['High']+dfX['Low'])/2

		if dfX['HLmean'].max()<=2:
			continue



		# clean up Y
		dfY.drop('Symbol',axis=1,inplace=True)

		
		Ydict={}
		dfY['ZeroPerf']=0
	
#         dfY['FutProfit5days']=-100*self.df['Close'].diff(periods=-5)/self.df['Close']
		if dfY['Close'].iloc[0]==0:
			continue

		dfY['Returns']=100*(dfY['Close']-dfY['Close'].iloc[0])/dfY['Close'].iloc[0]
		ret=dfY['Returns'].iloc[0:5].max()

		if ret==0:
			Ydict['MaxReturn5days'] = 0
		else:
			Ydict['MaxReturn5days'] = ret

		if pd.isnull(Ydict['MaxReturn5days']):
			continue



		# clean up X
		dfX.drop('Symbol',axis=1,inplace=True)
		
		mxvol=dfX['Volume'].max()
		if mxvol==0:
			continue

		dfX=dfX[FinalXcols]

		dfX['Volume']=dfX['Volume']/mxvol
		dfX['VolSMA10']=dfX['VolSMA10']/mxvol
		
		mn=dfX[pricecols].min(axis=1).min()
		for cc in pricecols:
			dfX[cc]=(dfX[cc]-mn)	
		
		mx=dfX[pricecols].max(axis=1).max()
		if mx==0:
			continue

		for cc in pricecols:
			dfX[cc]=dfX[cc]/mx

		

		NaNind=dfX[dfX.isnull().any(axis=1)].index
		if len(NaNind)>=len(dfX)/2:
			continue

		for cc in FinalXcols:
			if pd.isnull( dfX.loc[0,cc] ):
				dfX.loc[0,cc]=0
		try:	
			if len(NaNind)>0:
				dfX=dfX.interpolate()
		except:
			dfX=dfX.fillna(0)

		# pdb.set_trace()

		XX=np.expand_dims( dfX[FinalXcols].astype(float).values.flatten(order='F')   ,axis=0     )
		YY=np.expand_dims( np.array(Ydict['MaxReturn5days']),axis=0 )
		if Xn is None:
			Xn=XX
			Yn=YY
		else:
			Xn=np.vstack((Xn,XX))
			Yn=np.vstack((Yn,YY))
	
	Metan=Meta
	Metan['MetaX']['columns']=FinalXcols
	Metan['MetaY']['columns']=FinalYcols
	
	Metan['MetaX']['shape']=Xn.shape
	Metan['MetaY']['shape']=Yn.shape

	return Xn,Yn,Metan








