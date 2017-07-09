from __future__ import division
import numpy as np
import pandas as pd
import logging
logger = logging.getLogger(__name__)

def GetFeatureTestData():
	from . import tasks
	from . import models as md
	import stockdata.models as stkmd

	Symbol='TSLA'
	logger.warning('TSLA is chosen')
	stks=stkmd.Stock.objects.get(Symbol=Symbol)
	T=pd.datetime(2012,12,1)
	window=360
	Interval='D'
	if md.LinearTrends.objects.filter(Symbol=stks,T=T.strftime("%Y-%m-%d"),window=window,Interval=Interval).exists()==False:
		tasks.GenLinTrendsCustomFeats('TSLA',T,window,Interval,[])

	t0=T-pd.DateOffset(360)
	# Dfpm1y=stks.GetData(Fromdate=(t0-pd.DateOffset(90)),Todate=(T+pd.DateOffset(360)) )
	DF= stks.GetData(Fromdate=t0,Todate=T )
	DF['No']=range(len(DF))

	Dlin=md.LinearTrends.objects.get(Symbol=stks,T=T.strftime("%Y-%m-%d"),window=window,Interval=Interval)
	TrendsMid=Dlin.GetMidTrends()
	TrendsTop=Dlin.GetTopTrends()
	TrendsBottom=Dlin.GetBottomTrends()   
	

	import CTA.PatternRecognition.LinearTrendFit as LTF

	DF['LinFitTop'],DF['LinSlpTop']=LTF.GetLineFromTrends_algo2(TrendsTop,DF)
	DF['LinFitMid'],DF['LinSlpMid']=LTF.GetLineFromTrends_algo2(TrendsMid,DF)
	DF['LinFitBottom'],DF['LinSlpBottom']=LTF.GetLineFromTrends_algo2(TrendsBottom,DF)

	return t0,T,window,Interval,Symbol,TrendsMid, TrendsTop, TrendsBottom, DF

class featuremanager():
	evaldata={}
	testdata={}
	def __init__(self):
		import os
		from django.conf import settings
		self.featdumpfile=os.path.join( settings.BASE_DIR,'research' ,'FeaturesCode.py' )
		self.feattestfile=os.path.join( settings.BASE_DIR,'research' ,'feattestfile.py' )
		
		self.commonmodules=['import pandas as pd',
			'import numpy as np',
			'from stockdata.models import GetSectors,GetIndustries,GetStockData,GetStockMeta',
			'from research.featuremanager import Rallylength',
			]


	def __enter__(self):
		return self

	def __exit__(self, exc_type, exc_value, traceback):
		try:
			del self.evaldata
		except:
			pass
		try:
			del self.testdata
		except:
			pass

	
	def LoadEvalData(self,df,TrendsMid,  TrendsTop,  TrendsBottom):
		if len(self.evaldata)==0:
			self.evaldata={  
						'df':df,
						'T':len(df),
						'DebugOutput':{},
						'TrendsMid':TrendsMid,
						'TrendsBottom':TrendsBottom,
						'TrendsTop':TrendsTop
						}
			del df
			del TrendsMid
			del TrendsTop
			del TrendsBottom

	def LoadTestData(self):
		from . import models as md
		if len(self.testdata)==0:
			t0, T, window, Interval, Symbol, TrendsMid,  TrendsTop,  TrendsBottom,  df=GetFeatureTestData()
			self.testmeta={'t0':t0,'T':T,'window':window,'Interval':Interval,'Symbol':Symbol}
			self.testdata={  
						'df':df,
						'T':len(df),
						'DebugOutput':{},
						'TrendsMid':TrendsMid,
						'TrendsBottom':TrendsBottom,
						'TrendsTop':TrendsTop
						}

			del df
			del TrendsMid
			del TrendsTop
			del TrendsBottom

		ss= {  
					'df':self.testdata['df'].copy(),
					'T':len(self.testdata['df']),
					'DebugOutput':{},
					'TrendsMid':self.testdata['TrendsMid'].copy(),
					'TrendsBottom':self.testdata['TrendsBottom'].copy(),
					'TrendsTop':self.testdata['TrendsTop'].copy()
					}
		
		return ss

	def LoadFeatureModule(self):
		import importlib
		self.mod=importlib.import_module('research.FeaturesCode')
		
	def EvalFeatures(self,featname):
		featfunc=getattr(self.mod, featname)
		return featfunc(self.evaldata)

	def TestFeatures(self,featname):
		featfunc=getattr(self.mod, featname)
		return featfunc(self.testdata)

	def GetFeaturefunctions(self):
		pass

	def GetEmptyFeatCode_str(self,name):
		return 'def '+name+'(data):\r\n\t#numpy available as np\r\n\t#pandas available as pd\r\n\t# No other module can be used\r\n\tT=data["T"]\r\n\tdf=data["df"]\r\n\tTrendsMid=data["TrendsMid"]\r\n\tTrendsTop=data["TrendsTop"]\r\n\tTrendsBottom=data["TrendsBottom"]\r\n\t# Use data["DebugOutput"] to show output for debugging\r\n\t'

	def process_feature_code(data,code_str,name):
		import research.FeaturesCode as FC
	
		# code=compile(code_str,'<string>','exec')
		# exec(code)
		x= eval('FC.'+name+'(data)')
		if np.isnan(x)==True:
			x=None
		return x

	def CheckFeaturecode_str(self,name,code_str):
		from multiprocessing import Pool
		import importlib
		import time

		for ss in ['__','import','builtin','write','os.','os ','sys.','sys ','write','open','close','with','system','set','get']:
			if ss in code_str:
				return (False,'Feature code cannot contain "'+ss+'"',None)

		if 'def '+name+'(data):' not in code_str:
			return (False,'Feature function code should have '+'def '+name+'(df):',None)

		if 'return' not in code_str:
			return (False,'Feature function code should return a value '+'def '+name+'(df):',None)

		errs=(ZeroDivisionError,NameError,IndentationError,TabError,SystemError,SystemExit,TypeError,UnboundLocalError,UnicodeError,EOFError)
		
		with open(self.feattestfile,'w') as featfile:
			import py_compile
			ss=self.commonmodules
			ss="\n".join(ss)+'\n'
			ss=ss+'\n\n'
			featfile.write("%s" % ss+code_str)
		py_compile.compile(self.feattestfile)
		mod=importlib.import_module('.feattestfile')
		func=getattr(mod, name)
		# try:
		# 	code=compile(code_str,'<string>','exec')
		# except errs as e:
		# 	return (False,e,None)
		# else:
		# 	return (False,'error in compile code',None)

		# exec(code)


		starttime=time.time()

		kpp = Pool(1)
		import sys
		try:
			data=self.LoadTestData()
			res = kpp.apply_async(func,[data,] )
			kpp.close()
			x=res.get(timeout=2)
		except OSError as err:
			return (False, "OS error: {0}".format(err),None)
			print()
		except ValueError:
			return (False, "value error",None)
		except errs as e:
			return (False,e,None)
		except:
			return (False, "Unexpected error: "+str(sys.exc_info()[0]),None)

		#  CHecking if user changed any data
		if data['df'].equal(self.testdata['df'])==False:
			return (False, 'df cannot be changed' , None )
		if data['T']!=self.testdata['T']:
			return (False, 'T cannot be changed' , None )
		if data['TrendsMid'].equal(self.testdata['TrendsMid'])==False:
			return (False, 'TrendsMid cannot be changed' , None )
		if data['TrendsBottom'].equal(self.testdata['TrendsBottom'])==False:
			return (False, 'TrendsBottom cannot be changed' , None )
		if data['TrendsTop'].equal(self.testdata['TrendsTop'])==False:
			return (False, 'TrendsTop cannot be changed' , None )

		print "time taken is "+str(time.time()-starttime)
		import json
		if type(x[0])==int or type(x[0])==float:
			return (True, 'Feature Computed' , json.dumps(x,indent=4) )
		else:
			return (False, 'Feature function should return float or int',None)
		# except:
		# 	return (False,'error in running code',None)

	
	
	def DumpFeatureCodes2file(self):
		
		from . import models as md
		import py_compile
		ss=self.commonmodules
		ss="\n".join(ss)+'\n'
		ss=ss+'\n\n'

		for feat in md.GeneralFeature.objects.all():
			ss=ss+'# Id: '+str(feat.pk)+'\n'  
			ss=ss+'# User: '+str(feat.user)+'\n'  
			ss=ss+'# Name: '+feat.name+'\n'
			ss=ss+'# Group: '+feat.group+'\n'
			ss=ss+'# Description: '+str(feat.description).replace('\n','\n# ')+'\n'
			ss=ss+'# Created at: '+str(feat.created_at)+'\n'
			ss=ss+'# Updated at: '+str(feat.updated_at)+'\n'
			ss=ss+str(feat.code)
			ss=ss+'\n\n'+'#---'*30+'\n\n'

		with open( self.featdumpfile,'w') as featfile:
			featfile.write("%s" % ss)
		py_compile.compile(self.featdumpfile)

	def ReadCustomFeatures_UpdateFeaturesDB():
		from . import CustomFeatures as CF
		from . import models as md
		import inspect
		members=inspect.getmembers(CF)
		for mm in members:
			if inspect.isfunction(mm[1]):
				src=inspect.getsource(mm[1])
				funcname=mm[1].__name__
				comments=inspect.getcomments(mm[1])
				
				# Id:
				# User: @general@
				# Name: Close
				# Group: Price
				# Description: Close Price at T
				# Operators: gt,lt,gte,lte,equalto
				# Units: None
				# Created at:
				# Updated at:
				dd={'user':None,'name':None,'group':None,'description':None,'units':None,'operators':None}
				for cc in comments.split('\n'):
					if '# User:' in cc:
						dd['user']=cc.replace('# User:' ,'')
						if dd['user'][0]=='':
							dd['user']=dd['user'][1:]
					if '# Name:' in cc:
						dd['name']=cc.replace('# Name:' ,'')
						if dd['name'][0]=='':
							dd['name']=dd['name'][1:]
					if '# Group:' in cc:
						dd['group']=cc.replace('# Group:' ,'')
						if dd['group'][0]=='':
							dd['group']=dd['group'][1:]
					if '# Description:' in cc:
						dd['description']=cc.replace('# Description:' ,'')
						if dd['description'][0]=='':
							dd['description']=dd['description'][1:]
					if '# Operators:' in cc:
						dd['operators']=cc.replace('# Operators:' ,'')
						dd['operators']=dd['operators'].replace(' ','').split(',')

					if '# Units:' in cc:
						dd['units']=cc.replace('# Units:' ,'')
						dd['units']=dd['units'].replace(' ','').split(',')

				#only load feature if it does not exist with the name
				if md.GeneralFeature.objects.filter(name=funcname)==False:
					GF=md.GeneralFeature(name=funcname,user=dd['user'],group=dd['group'],description=dd['description'],code=src)
					GF.operators.add(*md.FeatureOperator.objects.filter(operators__in=dd['operators']))
					GF.units.add(*md.FeatureUnit.objects.filter(units__in=dd['units']))
					GF.save()





# tol is tolerance for tol number of days. so even though it misses out for tol days it still counts as consecutive
def Rallylength(x,tol=2):
	if len(x)==0:
		return [[]]
	if len(x)==1:
		return [[x]]
		
	x=np.array(x)
	x=np.append(x,x[-1]+1)

	Q=[]
	cnt=0
	j=0
	for i in range(1,len(x)):
		if x[i]-x[i-1]<=tol:
			cnt=cnt+1
			pass
		else:
			Q.append(x[j:i])
			j=i
			cnt=0
		# print x[i]
	if cnt>0:
		Q.append(x[j:i])
	return Q