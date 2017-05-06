from __future__ import division
import utility.models as utmd
# import stockapp.models as stkmd
# import dataapp.models as dtamd
import dataapp.libs as dtalibs
import pandas as pd


class AveragePrice(utmd.index):
	"""
	Take the average price of all the stocks in the group
	"""
	
	def __init__(self,*args,**kwargs):
		super(AveragePrice,self).__init__(*args,**kwargs)

		self.register(description="Average Close of Group",name="AverageClose",label="AvgClose",resulttype=pd.DataFrame,
						scale=['absolute','%'],operations=['<','>','<=','>=','!=','between'],computefeatures=True)
		self.register(description="Volume Average Close of Group",name="VolAvgClose",label="VolAvgClose",resulttype=pd.DataFrame,
						scale=['absolute','%'],operations=['<','>','<=','>=','!=','between'],computefeatures=True)
		

	def compute(self,*args,**kwargs):
		Fromdate=kwargs.get('Fromdate',pd.datetime(2002,1,1).date() )
		Todate=kwargs.get('Todate',pd.datetime.today().date() )
		grpstks_ids=kwargs.get('grpstks_ids',None)

		
		df=dtalibs.GetStockData(grpstks_ids,Fromdate,Todate,'concat')

		dd=df.groupby('Date').agg('mean').reset_index()
		self.setvalue("AvgClose",dd)
		
		# still need to implement
		df['VolClose']=df['Close']*(df['Volume']/df['Volume'].sum()  )
		dv=df[['Date','VolClose']].groupby('Date').agg('np.sum').reset_index()
		self.setvalue("VolAvgClose",dv)
		


