from __future__ import division
from datascience.ML.MLmodels  import *
import datascience.libs as dtsclibs
import dataapp.libs as dtalibs
import datascience.models as dtscmd
import pdb
import pandas as pd
import numpy as np
	
filename=__name__.split('.')[-1]

####################################################################################################
#################### ------------ Base Creators-------------- ##################################
####################################################################################################

def CreateStockData_base_X1y_Y3m_TFMonday_from2010(SymbolId,Mode):
	Trange=pd.date_range(start=pd.datetime(2010,1,1),end=pd.datetime.today(),freq='W-MON') 
	return dtalibs.CreateStockData_base(SymbolId,Trange,Mode)




####################################################################################################
#################### ------------ Some Data Transformers-------------- ##################################
####################################################################################################


def StandardizeData_HLmeanVolumeSMA01_X30_Y5return_interpcleaned_flatout(X,Y=None,Meta):
	"""
	A transformer function has to take X,Y,Meta and return another modified X,Y,Meta
	0. Implement contraints on input
		1. fail on not satisfying constraint
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
		dfX.index=range(len(dfX))
		
		if len(dfX)<23:
			print "need 23 time steps of data, only :",len(dfX)," provided"
			continue

		if len(set(['High','Low','Volume','VolSMA10']) & set(dfX.columns))==0:
			print "required columns not there"
			continue

		mxvol=dfX['Volume'].max()
		if mxvol==0:
			continue
		dfX['Volume']=dfX['Volume']/mxvol
		dfX['VolSMA10']=dfX['VolSMA10']/mxvol

		dfX['HLmean']=(dfX['High']+dfX['Low'])/2
		if dfX['HLmean'].max()<=2:
			continue

		
		dfX=dfX[FinalXcols]
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
			print "skipping too many NaNs"
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
		
		if Xn is None:
			Xn=XX
		else:
			Xn=np.vstack((Xn,XX))


		if Y is not None:
			dfY=pd.DataFrame(Y[i,:,:],columns=colsY)
			dfY.index=range(len(dfY))
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

			YY=np.expand_dims( np.array(Ydict['MaxReturn5days']),axis=0 )
			
			if Yn is None:
				Yn=YY
			else:
				Yn=np.vstack((Yn,YY))
		

		
	if Xn.shape[0]==0:
		raise Exception('No data samples in this set')

	Metan=Meta
	Metan['MetaX']['columns']=FinalXcols
	Metan['MetaY']['columns']=FinalYcols
	
	Metan['MetaX']['shape']=Xn.shape
	Metan['MetaY']['shape']=Yn.shape

	return Xn,Yn,Metan








