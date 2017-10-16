import dataapp.libs as dtalibs
import dataapp.models as dtamd
import featureapp.models as ftamd
import stockapp.models as stkmd
import pandas as pd
import numpy as np
import dataapp.custommeta as cstmdata
import pdb




class DataManager(object):
	"""
	1. Pull in data from everywhere
	2. this is the main entry into all the raw data
	3. take in feature df and side concat
	4. Future if you get more fundamental data... join that too
	 
	"""
	
	max_cache=20 # maximum number of stocks for which to hold data

	def __init__(self,SymbolIds=[],RequiredCols=None,Append2ReqCols=[],DF=None):
		"""
		DF is a dict with keys as ids and values as dataframes of the objects
		"""
		if RequiredCols is None: 
			self.RequiredCols= cstmdata.RequiredCols
		else:
			self.RequiredCols=RequiredCols

		self.RequiredCols=list(set(self.RequiredCols+Append2ReqCols))

		self.SymbolIds=list( SymbolIds )
		self.stks={}


		# trading dates
		self.TradingDates=list(  dtalibs.getTradingdates() )

		# available columns in database
		self.FeatureCols=[f for f in ftamd.FeaturesMeta.objects.all().values_list('Featurelabel',flat=True).distinct()]
		self.StockMetaCols=[f.name for f in  stkmd.Stockmeta._meta.get_fields()]
		self.DataCols=[f.name for f in  dtamd.Stockprice._meta.get_fields()]



		for symbid in self.SymbolIds:
			self.stks[symbid]=self.Stockmeta.objects.get(id=symbid)


		if DF is not None:
			if set(DF.keys()) == set(SymbolIds):
				self.DF=DF
			else:
				raise Exception('SymbolIds and Keys  are not the same')
		else:
			self.DF={}


	@property
	def Stockmeta(self):
		return stkmd.Stockmeta
	
	
	def GetStockData(self,*args,**kwargs):
		return dtalibs.GetStockData(*args,**kwargs)
	
	
	def GetFeatures(self,*args,**kwargs):
		return dtalibs.GetFeatures(*args,**kwargs)

	def addindicators(self,*args,**kwargs):
		return dtalibs.addindicators(*args,**kwargs)


	def AddStockData(self):
		for symbid in self.SymbolIds:
			dd=self.GetStockData(Symbolids=[symbid])
			self.stockdata_columns=dd.columns
			self.DF[symbid]=dd

	def AddStockMetacols(self):
		self.stockmeta_columns=[]
		for symbid in self.SymbolIds:
			for reqcol in self.RequiredCols:
				if reqcol in self.StockMetaCols:
					val=getattr(self.Stockmeta.objects.get(id=symbid),reqcol )
					self.DF[symbid][reqcol]=val
					if reqcol=='Sector':
						self.DF[symbid]['SectorId']=stkmd.Sector.objects.get(Name=val).id
					if reqcol=='Industry':
						self.DF[symbid]['IndustryId']=stkmd.Industry.objects.get(Name=val).id

					self.stockmeta_columns.append(reqcol)

	def Addfeaturecols(self):
		featcols=list( set(self.RequiredCols) & set(self.FeatureCols) )
		for symbid in self.SymbolIds:
			dffeats=self.GetFeatures(Symbolids=[symbid])
			self.feat_columns=dffeats.columns
			self.DF[symbid]=dtalibs.merge_on_TSymbol(self.DF[symbid],dffeats)


	def AddIndicatorCols(self,cols=[]):
		IndicatorCols=[]
		for reqcol in self.RequiredCols+cols:
			if reqcol in cstmdata.StdIndicatorCols.keys():
				IndicatorCols.append( cstmdata.StdIndicatorCols[reqcol] )

		for symbid in self.SymbolIds:
			 if len(IndicatorCols)>0:
			 	self.DF[symbid]=self.addindicators(self.DF[symbid],IndicatorCols)
		

	def AddReqCols(self):
		self.AddStockData()
		self.AddStockMetacols()
		self.Addfeaturecols()
		self.AddIndicatorCols()


	def CreateTrainingDataSet(self,col2write,TFs,width_back=360,width_front=180):
		for symbid in self.SymbolIds:
			L=np.arange(width_back)
			R=np.arange(width_front);
			X=None
			Y=None
			Xflat=None
			Yflat=None

			Tadded=[]
			colflatX=[]
			colflatY=[]
			colX=[]
			colY=[]
			for T in TFs:	
				print T			
				indT=np.argwhere(self.DF[symbid].index==T)
				if len(indT)==0:
					continue
				else:
					indT=indT[0][0]
					Tadded.append(T)

				dfX=self.DF[symbid].iloc[indT-width_back-1:indT+1][col2write].copy()
				colX=dfX.columns

				if len(dfX)<width_back:
					dd=pd.DataFrame(columns=dfX.columns,index=range(width_back-len(dfX)))
					dfX=pd.concat([dd,dfX])

				# dfX=dfX[self.RequiredCols]
				colflatX=[]
				for cc in dfX.columns:
					colflatX=colflatX+[cc+'_'+str(i) for i in range(len(dfX)) ]


				pX=np.expand_dims(dfX.astype(float).values,axis=0)
				pXflat=np.expand_dims(dfX.astype(float).values.flatten(order='F') ,axis=0)  


				dfY=self.DF[symbid].iloc[indT:indT+width_front][col2write].copy()
				colY=dfY.columns

				if len(dfY)<width_front:
					dd=pd.DataFrame(columns=dfY.columns,index=range(width_front-len(dfY)))
					dfY=pd.concat([dfY,dd])

				
				# dfY=dfY[self.RequiredCols]
				colflatY=[]
				for cc in dfY.columns:
					colflatY=colflatY+[cc+'_'+str(i) for i in range(len(dfY)) ]

				pY=np.expand_dims(dfY.astype(float).values,axis=0)
				pYflat=np.expand_dims(dfY.astype(float).values.flatten(order='F') ,axis=0)  


				if X is None: 
					X=pX
					Y=pY
					Xflat=pXflat
					Yflat=pYflat
				else:
					X=np.vstack((X,pX))
					Y=np.vstack((Y,pY))
					Xflat=np.vstack((Xflat,pXflat))
					Yflat=np.vstack((Yflat,pYflat))




			Metaflat={'T':Tadded,'colflatX':colflatX,'colflatY':colflatY}
			Meta={'T':Tadded,'colX':colX,'colY':colY}
			yield (X,Y,Xflat,Yflat,Meta,Metaflat)

	def Iterbatchdata_Ordered(self,dfinstants_list,padding=None,roundT2dfdate=True):
		"""
		DataFrame input as
		dfinstants_list =[dfinstants,dfinstants,dfinstants .... ]
		dfinstants= [ df(Symbol, TF,width), ..., or df(Symbol, T0,width) ]
		return in same order
		padding True/False
		"""
		dfinstants_list=[dd for dd in dfinstants_list if dd is not None]

		AllSymbols=reduce( lambda x,y: x|y,map(lambda x: set(x['Symbol'].unique()),dfinstants_list) )
		Data=[]
		for i in range(len(dfinstants_list)):
			dfinstants_list[i].index=range(len(dfinstants_list[i]))
			Data.append({})

		for Symbol in AllSymbols:
			SymbId=self.Symbols2Ids[Symbol]
			df=self.PullStockdata(SymbId)
			df=self.AppendCols2df(SymbId,df)
			for i in range(len(dfinstants_list)):
				dfinstants=dfinstants_list[i]
				dfsymb=dfinstants[dfinstants['Symbol']==Symbol]

				for ind in dfsymb.index:
					width=dfsymb.loc[ind,'width']
					if 'TF' in dfsymb.columns and 'T0' in dfsymb.columns:
						raise Exception('Cannot have both TF and T0 in dfinstants')

					if 'TF' in dfsymb.columns:
						if isinstance(dfsymb.loc[ind,'TF'],basestring):
							TF=dtalibs.str2date( dfsymb.loc[ind,'TF'] )
						if roundT2dfdate:
							TFind=df.index[df.index<=TF][-1]
							if np.abs( (TFind-TF).days )<=3:
								ds=df.iloc[TFind-width:TFind]
							else:
								ds=pd.DataFrame()

						else:
							TFind=df.index[df.index==TF]
							if len(TFind)==0:
								ds=pd.DataFrame()
						
						Nd=len(ds)-width
						if Nd>0 and padding is not None:
							d={}
							for cc in ds.columns:
								d[cc]=[np.nan]*Nd
							dummyfill=pd.DataFrame(d)
							ds=pd.concat([ dummyfill , ds ])


					elif 'T0' in dfsymb.columns:
						if isinstance(dfsymb.loc[ind,'T0'],basestring):
							T0=dtalibs.str2date( dfsymb.loc[ind,'T0'] )
						if roundT2dfdate:
							T0ind=df.index[df.index>=T0][0]
							if np.abs( (TFind-TF).days )<=3:
								ds=df.iloc[T0ind:T0ind+width]
							else:
								ds=pd.DataFrame()
						else:
							T0ind=df.index[df.index==T0]
							if len(T0ind)==0:
								ds=pd.DataFrame()


						Nd=len(ds)-width
						if Nd>0 and padding is not None:
							d={}
							for cc in ds.columns:
								d[cc]=[np.nan]*Nd
							dummyfill=pd.DataFrame(d)
							ds=pd.concat([ ds, dummyfill ])



					Data[i][ind]=np.expand_dims(ds.values,axis=0)
		

		for i in range(len(dfinstants_list)):
			X=None
			for ind in dfinstants_list[i].index:
				if X is None:
					X=Data[i][ind]
				else:
					X=np.vstack((X,Data[i][ind]))

			Meta={'shape':X.shape,'dfinstants':dfinstants_list[i],'columns':self.RequiredCols}

			yield X,Meta