import pandas as pd
import dataapp.data_download.yqd as yqd
import stockapp.models as stkmd
import dataapp.models as dtamd

class DataDownloadManager_Impl(object):
	def __init__(self,stk,compute_status_obj=None):
		self.stk=stk
		self.compute_status_obj=compute_status_obj
		self.Todate=pd.datetime.today().date()

		if self.stk.Lastdate is None:
			self.Fromdate=pd.datetime(2002,1,1).date()
		else:
			self.Fromdate=self.stk.Lastdate

	def run_compute_status(self):
		if self.compute_status_obj is not None:
			self.compute_status_obj.save_running_byId(self.compute_status_obj.Id,Msg='')

	def success_compute_status(self,Msg=''):
		if self.compute_status_obj is not None:
			self.compute_status_obj.save_success_byId(self.compute_status_obj.Id,Msg=Msg)
	def fail_compute_status(self,Msg=''):
		if self.compute_status_obj is not None:
			self.compute_status_obj.save_fail_byId(self.compute_status_obj.Id,Msg=Msg)


	def pre_download_check(self):
		pass
	def downloaddata(self):
		pass
	def post_download_check(self):
		pass
	def update_data(self):
		pass


class DataDownloadManager(DataDownloadManager_Impl)
	def pre_download_check(self):
		
		if self.stk.LastPriceUpdate==self.Todate:
			print "skipping ",self.stk," as LastpriceUpdate is today "
			F={'status':'NoUpdateRequired','Todate':self.Todate,'Fromdate':self.Fromdate}
		else:
			F={'status':'UpdateRequired','Todate':self.Todate,'Fromdate':self.Fromdate}


		if self.Todate.dayofweek>=5:
			print "Today is weekend so no download ",self.stk
			F={'status':'NoUpdateRequired','Todate':self.Todate,'Fromdate':self.Fromdate}

		return F

	def downloaddata(self):
		try:
			df=yqd.load_yahoo_quote(self.stk.Symbol,self.Fromdate.strftime('%Y%m%d'), self.Todate.strftime('%Y%m%d'))
			return {'df':df,'status':'Success'}
		except:
			print "error downloading ",self.Symbol, " for input dates ",self.Fromdate,self.Todate
			return {'df':None,'status':'Fail'}


	def update_data(self):

		print "Working on ",self.stk.Symbol," ",self.stk.id
		

		if stk.Update==False:
			return

		

		UpCk=predownloadcheck(stk)

		if UpCk['status']=='UpdateRequired':
			self.run_compute_status()
			DD=DownloadData(stk.Symbol, Fromdate,Todate)
			if DD['status']=='Success':
				df=DD['df']
			else:
				self.fail_compute_status()
				stk.LastPriceUpdate=self.Todate
				stk.save()
				return 

			df=StockDataFrame_sanitize(df,standardize=False)

			self.save_df2db(df)

			self.success_compute_status()
			print "Updated data for ", self.stk.Symbol, " downloaded ", len(df)
			

	def save_df2db(self,df)
		df=df[df.index>self.stk.Lastdate]
		
		objs=[]
		for ind in df.index:
			objs.append( dtamd.Stockprice(Close=df.loc[ind,'Close'], Open=df.loc[ind,'Open'] ,
										 High=df.loc[ind,'High'],Low=df.loc[ind,'Low'],
										 Volume=df.loc[ind,'Volume'],Date=ind,Symbol=stk.Symbol,Symbol_id=stk.id)  )


		dtamd.Stockprice.objects.bulk_create(objs)


		if self.stk.Startdate is None:
			self.stk.Startdate=df.index[0]

		if df.index[0] < self.stk.Startdate:
			self.stk.Startdate=df.index[0]

		if self.stk.Lastdate is None:
			self.stk.Lastdate=df.index[-1]

		if df.index[-1] > self.stk.Lastdate:
			self.stk.Lastdate=df.index[-1]


		stk.LastPriceUpdate=self.Todate
		self.stk.save()
		



