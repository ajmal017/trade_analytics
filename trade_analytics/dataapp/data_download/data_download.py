





###########################  Download stock data  ######################################

def predownloadcheck(stk):
	Todate=pd.datetime.today().date()

	if stk.Lastdate is None:
		Fromdate=pd.datetime(2002,1,1).date()
	else:
		Fromdate=stk.Lastdate


	if stk.LastPriceUpdate==pd.datetime.today().date():
		print "skipping ",stk," as LastpriceUpdate is today "
		return {'status':'Success','Todate':Todate,'Fromdate':Fromdate}
	else:
		return {'status':'Run','Todate':Todate,'Fromdate':Fromdate}


	if Todate.dayofweek>=5:
		print "Today is weekend so no download ",stk
		return {'status':'Success','Todate':Todate,'Fromdate':Fromdate}

	if (Todate-Fromdate).days<1:
		print "Already updated ",stk
		return {'status':'Success','Todate':Todate,'Fromdate':Fromdate}
	else:
		return {'status':'Run','Todate':Todate,'Fromdate':Fromdate}



def DownloadData(Symbol, Fromdate,Todate):
	try:
		df=web.DataReader(Symbol, 'yahoo', Fromdate,Todate)
		return {'df':df,'status':'Success'}
	except:
		print "error downloading ",Symbol, " for input dates ",Fromdate,Todate
		return {'df':None,'status':'Fail'}



def postdownloadcheck(stk,dfStartdate,dfLastdate):
	if stk.Lastdate is not None:
		if dfLastdate<=stk.Lastdate:
			print "skipping ",stk," as it is already uptodate "
			return {'status':'Success'}
		elif dfStartdate<=stk.Lastdate:
			print stk," download data has overlap "
			return {'status':'Overlap'}
		else:
			return {'status':'Run'}
	else:
		return {'status':'Run'}

def UpdatePriceData(Symbols_ids,*args,**kwargs):
	"""Update stock price data for given symbol ids

		Args:
			Symbols ids from db / Symbol strings,
			- args have to be json serializable for multiprocessing

	"""
	semaphore=kwargs.get('semaphore',None)
	if semaphore:
		semaphore.acquire()

	stocks=stkmd.Stockmeta.objects.filter(id__in=Symbols_ids)

	for stk in stocks:
		print "Working on ",stk.Symbol," ",stk.id
		comstat=stkmd.ComputeStatus_Stockdownload.objects.get(Status='ToDo',Symbol=stk)
		comstat.Status='Run'
		comstat.save()

		if stk.Update==False:
			print "skipping as update was set to False"
			comstat.Status='Success'
			comstat.save()
			stk.LastPriceUpdate=pd.datetime.today().date()
			stk.save()
			continue

		UpCk=predownloadcheck(stk)
		if UpCk['status']=='Success':
			comstat.Status='Success'
			comstat.save()
			stk.LastPriceUpdate=pd.datetime.today().date()
			stk.save()
			continue
		else:
			Fromdate=UpCk['Fromdate']
			Todate=UpCk['Todate']



		if stk.Derived:
			DD=ComputeIndex(stk, Fromdate,Todate)
		else:
			DD=DownloadData(stk.Symbol, Fromdate,Todate)


		if DD['status']=='Success':
			df=DD['df']
		else:
			comstat.Status='Fail'
			comstat.save()
			stk.LastPriceUpdate=pd.datetime.today().date()
			stk.save()
			continue

		df=StockDataFrame_sanitize(df,standardize=False)

		UpCk=postdownloadcheck(stk,df.index[0],df.index[-1])
		if UpCk['status']=='Success':
			stk.LastPriceUpdate=pd.datetime.today().date()
			stk.save()
			comstat.Status='Success'
			comstat.save()
			continue
		elif UpCk['status']=='Overlap':
			df=df[df.index>stk.Lastdate]


		objs=[]
		for ind in df.index:
			objs.append( dtamd.Stockprice(Close=df.loc[ind,'Close'], Open=df.loc[ind,'Open'] ,
										 High=df.loc[ind,'High'],Low=df.loc[ind,'Low'],
										 Volume=df.loc[ind,'Volume'],Date=ind,Symbol=stk.Symbol,Symbol_id=stk.id)  )


		# use a lock/semaphore if required
		if kwargs.get('lock',None):
			with kwargs['lock']:
				dtamd.Stockprice.objects.bulk_create(objs)
		else:
			dtamd.Stockprice.objects.bulk_create(objs)

		stk.LastPriceUpdate=pd.datetime.today().date()

		if stk.Startdate is None:
			stk.Startdate=df.index[0]

		if df.index[0]<stk.Startdate:
			stk.Startdate=df.index[0]

		if stk.Lastdate is None:
			stk.Lastdate=df.index[-1]

		if df.index[-1]>stk.Lastdate:
			stk.Lastdate=df.index[-1]



		stk.save()
		comstat.Status='Success'
		comstat.save()

		print "Updated data for ", stk, " downloaded ", len(df)

	if semaphore:
		semaphore.release()
