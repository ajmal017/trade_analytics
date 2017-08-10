from __future__ import unicode_literals
from __future__ import division

from django.db import models
import datetime
import pandas as pd
from django.db import connection
from multiselectfield import MultiSelectField
from django import forms
from django.utils.safestring import mark_safe
import django_tables2 as tables
from django.contrib.auth.models import User
import re
import os
import time



import pandas_datareader.data as web

import pdb




import CTA.StockDataManager as SDM


def CleanUpUser(user):

	username=str(user)
	if username=='AnonymousUser':
		username='@general@'
		user=User.objects.get(username=username)
	   
	else:
		username=str(user)
		

	return user,username

def LoadUpWatchlists_choices(user,username,loadgenalso=True):
	choices=[('None','Select')]

	if username=='@general@':
		Wuser=[]
	else:
		try:
			Wuser=Watchlist.objects.filter(user=user)
		except:
			Wuser=[]

	if loadgenalso==True:
		try:
			Wgen=Watchlist.objects.filter(user=User.objects.get(username='@general@') )
		except:
			Wgen=[]
	else:
		Wgen=[]

	wall=Watchlist.objects.get(watchlistname='All Symbols')
	choices=choices+[(str(wall.pk),str(wall.watchlistname))]
	choices=choices+[(str(w.pk),str(w.watchlistname)) for w in Wgen if w.watchlistname!='All Symbols']
	choices=choices+[(str('None'),str('-------'))]
	choices=choices+[(str(w.pk),str(w.watchlistname)) for w in Wuser]


	return choices

def GetStocks_selected(selected_watchlist_pk,symbs_str,user):
	symbs=[]
	try:
		symbs=re.compile(r'[:,\s\n]').split(symbs_str)
		symbs=list(set(symbs))
		symbs=[ss.upper() for ss in symbs if ss!='']
		# stocks1id=Stock.objects.filter(Symbol__in= symbs).values_list('pk',flat=True)
	except:
		pass

	# pdb.set_trace()
	# w=Watchlist.objects.get(pk=int(selected_watchlist_pk))
	# indvidstocks=Stock.objects.filter(Symbol__in=symbs)
	# if selected_watchlist_pk=='None' or selected_watchlist_pk==None or selected_watchlist_pk=='':
		# watchliststocks=[]
	# else:
		# watchliststocks=w.stocks.all()

	if selected_watchlist_pk=='None' or selected_watchlist_pk==None or selected_watchlist_pk=='':
		selected_watchlist_pk=[-1]
	else:
		selected_watchlist_pk=[int(selected_watchlist_pk)]


	stocks=Stock.objects.filter(models.Q(watchlist__pk__in=selected_watchlist_pk) | models.Q(Symbol__in=symbs)  )
		# W=Watchlist.objects.get(pk=int(selected_watchlist_pk))
	
	
	if stocks.count()==0:
		stocks=None
		stocks_str=None 
	else:   
		# stocks_str=[str(ss) for ss in stocks]
		stocks_str=stocks.values_list('Symbol',flat=True)
	
	return stocks,stocks_str 

def dictfetchall(cursor):
	"Return all rows from a cursor as a dict"
	columns = [col[0] for col in cursor.description]
	return [
		dict(zip(columns, row))
		for row in cursor.fetchall()
	]


def linkhref(link,text,newpage=True):
	if newpage==True:
		return '<a href="'+ link +'" target="_blank" >'+text+'</a>'
	else:
		return '<a href="'+ link +'">'+text+'</a>'

def UpdateWatchlist_withStockData():
		try:
			u=User.objects.get(username='@general@')
		except:
			u=User(username='@general@',email='n.adurthi@gmail.com',password='bablu0com')
			u.save()

		L=Stock.objects.values('Sector').distinct()
		for sec in L:
			print sec['Sector']
			if sec['Sector']!='nan':
				wlname='Sector: '+sec['Sector']
				try:
					if Watchlist.objects.filter(watchlistname=wlname).exists():
						w=Watchlist.objects.get(watchlistname=wlname)
					else:
						w=Watchlist(watchlistname=wlname)
						w.save()
				except:
					pdb.set_trace()

				# try:
				#     w=Watchlist.objects.get(watchlistname=wlname)
				# except:
				#     w=Watchlist(watchlistname=wlname)
				#     w.save()

				try:
					w.stocks.add(*Stock.objects.filter(Sector=sec['Sector']))
					w.user.add(u)
					w.save()
				except:
					print 'error with '+ sec['Sector']

		L=Stock.objects.values('Industry').distinct()

		for sec in L:
			print sec['Industry']
			if sec['Industry']!='nan':
				wlname='Industry: '+sec['Industry']
				if Watchlist.objects.filter(watchlistname=wlname).exists():
					w=Watchlist.objects.get(watchlistname=wlname)
				else:
					w=Watchlist(watchlistname=wlname)
					w.save()

				# try:
				#     w=Watchlist.objects.get(watchlistname=wlname)
				# except:
				#     w=Watchlist(watchlistname=wlname)
				#     w.save()
				try:
					w.stocks.add(*Stock.objects.filter(Industry=sec['Industry']))
					w.user.add(u)
					w.save()
				except:
					print 'error with '+ sec['Industry']


		return "All is well"

def LoadStockGroups():
	print os.getcwd()
	

	df=pd.read_csv('StockGroups - Copy 2.csv')
	df.columns
	df=df.fillna('nan')
	# df['Market Cap']=df['Market Cap'].where(pd.notnull(df), None).copy()
	df.index=range(len(df))
	for i in df.index:
		print [i,len(df)]
		if df.loc[i,'Market Cap']=='nan':
			df.loc[i,'Market Cap']=None

		stk=Stock(Company=df.loc[i,'Company'],Industry=df.loc[i,'Industry'],Sector=df.loc[i,'Sector'],status='Active',Marketcap=df.loc[i,'Market Cap'],Competitors=df.loc[i,'Competitors'].replace(' : ',','),Symbol=df.loc[i,'Symbol'],labels=df.loc[i,'label'].replace(':',',').replace(' ',''))
		try:
			stk.save()
		except:
			pdb.set_trace()

	labls=[]
	for stk in Stock.objects.all():    
		L=list(stk.labels)
		L=[ss for ss in L if ss!='']
		labls=labls+L
		if len(L)!=len(stk.labels):
			stk.labels=L
			stk.save()
			print stk

	return "All is well"
#--------------------MODELS----------------------------------------------------------------------------------------------------------

class Stock(models.Model):
	

	status=(('Active','Active'),('Inactive','Inactive'))
	Company=models.CharField(max_length=100,null=True,blank=True)
	Marketcap=models. DecimalField(max_digits=9,decimal_places=2,null=True,blank=True)
	Competitors=models.CharField(max_length=1100,null=True,blank=True)
	Symbol = models.CharField(max_length=6,null=True,blank=True)
	Sector = models.CharField(max_length=100,null=True,blank=True)
	Industry = models.CharField(max_length=100,null=True,blank=True)
	status=models.CharField(max_length=25,choices=status,null=True,blank=True)
	LastPriceUpdate= models.DateField(null=True)
	label_choices=( 
					('ETF','ETF'),
					('Stock','Stock'),
					('Gold','Gold'),
					('Silver','Silver'),
					('Oil','Oil'),
					('Inverse','Inverse'),
					('Copper','Copper'),
					('Entertainment','Entertainment'),
					('Uranium','Uranium'),
					('Coal','Coal'),
					('Index','Index'),

		)

	labels = MultiSelectField(choices=label_choices,blank=True)

	data=None

	def __str__(self):
		return self.Symbol

	def ClearData(self):
		if self.data is None:
			del self.data
			self.data=None
	def ReturnCleanedStockName(self):
		return self.Symbol.replace('^','e5').replace(' ','').replace('-','e9').replace('$','e3')

	def GetData(self,Fromdate=pd.datetime(2002,1,1),Todate=pd.datetime.today()):
		from django.conf import settings
		if self.data is None: 
			try:    
				df=pd.read_hdf(settings.DATABASES['StockDataH5']['NAME'],self.ReturnCleanedStockName())
			except:
				return pd.DataFrame()
			self.data=df.copy()
		else:
			df=self.data.copy()


		# df.index=pd.to_datetime(df['Date'])
		
		df=SDM.AppendVolMAs(df)
		df=SDM.AppendMAs(df)
		df=SDM.AppendMStd(df)
		df=SDM.AppendEMAs(df)
		df=SDM.AppendESTD(df)
		df=SDM.AppendReturns(df)
		df=SDM.AppendIndicator_SMAmaxDiff(df)
		df=SDM.AppendIndicator_AmpSMA10(df)

		if (Todate-df.index[-1]).days>5:
			print "Data for "+ self.Symbol+ " needs to be updated to the date "+ str(Todate)
			return df[Fromdate:Todate]
			# return df[(df.index>=Fromdate) & (df.index<=Todate)]
		else:
			return df[Fromdate:Todate]
			# return df[(df.index>=Fromdate) & (df.index<=Todate)]


	def GetData_mysql(self,Fromdate=pd.datetime(2002,1,1),Todate=pd.datetime.today()):
		if self.data is None:
			with connection.cursor() as dc:
				dc.execute("SHOW TABLES LIKE "+"'stockdata_"+self.ReturnCleanedStockName()+"';")
				if len( dictfetchall(dc) )==0:
					return pd.DataFrame()



			df=pd.read_sql("SELECT * FROM "+ "stockdata_"+self.ReturnCleanedStockName(), connection)
			self.data=df.copy()
		else:
			df=self.data.copy()


		df.index=pd.to_datetime(df['Date'])
		
		df=SDM.AppendVolMAs(df)
		df=SDM.AppendMAs(df)
		df=SDM.AppendMStd(df)
		df=SDM.AppendEMAs(df)
		df=SDM.AppendESTD(df)
		df=SDM.AppendReturns(df)
		df=SDM.AppendIndicator_SMAmaxDiff(df)
		df=SDM.AppendIndicator_AmpSMA10(df)

		if (Todate-df.index[-1]).days>5:
			print "Data for "+ self.Symbol+ " needs to be updated to the date "+ str(Todate)
			return df[Fromdate:Todate]
			# return df[(df.index>=Fromdate) & (df.index<=Todate)]
		else:
			return df[Fromdate:Todate]
			# return df[(df.index>=Fromdate) & (df.index<=Todate)]



	def GetData_retired(self,Fromdate=pd.datetime(2002,1,1).date(),Todate=pd.datetime.today().date()):
		from django.conf import settings
		try:
			df=pd.read_hdf(settings.DATABASES['StockDataH5']['NAME'],self.Symbol)        
		except:
			return pd.DataFrame()

		df=SDM.AppendVolMAs(df)
		df=SDM.AppendMAs(df)
		df=SDM.AppendMStd(df)
		df=SDM.AppendEMAs(df)
		df=SDM.AppendESTD(df)
		df=SDM.AppendReturns(df)
		df=SDM.AppendIndicator_SMAmaxDiff(df)
		df=SDM.AppendIndicator_AmpSMA10(df)

		if (Todate-df.index[-1].date()).days>5:
			print "Data for "+ self.Symbol+ " needs to be updated to the date "+ str(Todate)
			return df[Fromdate:Todate]
		else:
			return df[Fromdate:Todate]

	def UpdateData_slow(self, Fromdate=pd.datetime(2002,1,1),Todate=pd.datetime.today()):
		sttime=time.time()
		from django.conf import settings
		print "time for import setting ", time.time()-sttime

		sttime=time.time()
		try:
			# pdb.set_trace()
			df=pd.read_hdf(settings.DATABASES['StockDataH5']['NAME'],self.ReturnCleanedStockName())
			Fromdate=df.index[-1]
			datathere=True
		except:
			df=pd.DataFrame()
			datathere=False
		print "time for getting fromdate ", time.time()-sttime


		print Fromdate
		print Todate
		print (Todate-Fromdate).days
		if (Todate-Fromdate).days<1:
			print "No update required for stock "+self.Symbol
			del df
			return True

		sttime=time.time()
		try:
			print "Doawloding data First try"
			df=web.DataReader(self.Symbol, 'yahoo', Fromdate,Todate)
		except:
			# time.sleep(1)
			# try:
			# 	print "Doawloding data Second try"
			# 	df=web.DataReader(self.Symbol, 'yahoo', Fromdate,Todate)
			# except:
			print "*******Error with Stock "+self.Symbol
			return False
		print "time for downloading data fromdate ", time.time()-sttime

		
		if df.empty:
			print "Not enough data received..... may be the symbol changed recently"
			del df
			return False
			
		if datathere==False:
			# sttime=time.time()
			# df=SDM.AppendCandlePatterns(df)
			# print "time for candle patterns new set ", time.time()-sttime
			df.to_hdf(settings.DATABASES['StockDataH5']['NAME'],self.ReturnCleanedStockName())
			self.LastPriceUpdate= df.index[-1].date()
			del df
		else:
			DF=pd.read_hdf(settings.DATABASES['StockDataH5']['NAME'],self.ReturnCleanedStockName())
			if Fromdate in DF.index and Fromdate in df.index:
				df.drop(Fromdate,inplace=True)
			DF=pd.concat([DF,df])

			print "Updarted Data Fromdata 2 todate"
			DF.to_hdf(settings.DATABASES['StockDataH5']['NAME'],self.ReturnCleanedStockName())
			self.LastPriceUpdate= DF.index[-1].date()
			del DF



		self.save()

		print "Done updating Stock "+self.Symbol
		return True

	def UpdateData(self, Fromdate=pd.datetime(2002,1,1),Todate=pd.datetime.today()):
		sttime=time.time()
		from django.conf import settings
		print "time for import setting ", time.time()-sttime

		sttime=time.time()
		try:
			# pdb.set_trace()
			store=pd.HDFStore(settings.DATABASES['StockDataH5']['NAME'])
			nrows=store.get_storer(self.ReturnCleanedStockName()).nrows
			store.close()
			df=pd.read_hdf(settings.DATABASES['StockDataH5']['NAME'],self.ReturnCleanedStockName(),start=nrows-1,stop=nrows)
			Fromdate=df.index[-1]
			datathere=True
		except:
			df=pd.DataFrame()
			datathere=False
		print "time for getting fromdate ", time.time()-sttime


		print Fromdate
		print Todate
		print "Data there =",datathere
		print (Todate-Fromdate).days
		if (Todate-Fromdate).days<1:
			print "No update required for stock "+self.Symbol
			del df
			return True

		sttime=time.time()
		try:
			print "Doawloding data First try"
			df=web.DataReader(self.Symbol, 'yahoo', Fromdate,Todate)
		except:
			# time.sleep(1)
			# try:
			# 	print "Doawloding data Second try"
			# 	df=web.DataReader(self.Symbol, 'yahoo', Fromdate,Todate)
			# except:
			print "*******Error with Stock "+self.Symbol
			return False
		print "time for downloading data fromdate ", time.time()-sttime

		
		if df.empty:
			print "Not enough data received..... may be the symbol changed recently"
			del df
			return False
			
		if datathere==False:
			# sttime=time.time()
			# df=SDM.AppendCandlePatterns(df)
			# print "time for candle patterns new set ", time.time()-sttime
			df.to_hdf(settings.DATABASES['StockDataH5']['NAME'],self.ReturnCleanedStockName(),format='table')
			self.LastPriceUpdate= df.index[-1].date()
			del df
		else:
			store=pd.HDFStore(settings.DATABASES['StockDataH5']['NAME'])
			nrows=store.get_storer(self.ReturnCleanedStockName()).nrows
			store.close()
			DF=pd.read_hdf(settings.DATABASES['StockDataH5']['NAME'],self.ReturnCleanedStockName(),start=nrows-5,stop=nrows)
			for TT in DF.index:
				if TT in df.index:
					df.drop(TT,inplace=True)
			if df.empty==False:
				df.to_hdf(settings.DATABASES['StockDataH5']['NAME'],self.ReturnCleanedStockName(),format='table',append=True)
				self.LastPriceUpdate= df.index[-1].date()
			
			try:
				del DF
			except:
				pass
			try:
				del df
			except:
				pass
			


		self.save()

		print "Done updating Stock "+self.Symbol
		return True

	def UpdateData_mysql(self, Fromdate=pd.datetime(2002,1,1),Todate=pd.datetime.today()):
		from django.conf import settings

		with connection.cursor() as cc:
			if settings.DATABASES['default']['ENGINE']=='django.db.backends.sqlite3':
				cc.execute("CREATE TABLE IF NOT EXISTS "+ "stockdata_"+self.Symbol.replace(' ','').replace('-','') +" (Date text, Close real, Open real, High real, Low real, Volume real, CDL2CROWS integer, CDL3BLACKCROWS integer, CDL3INSIDE integer, CDL3LINESTRIKE integer,     CDL3OUTSIDE integer,        CDL3STARSINSOUTH integer,   CDL3WHITESOLDIERS integer,  CDLABANDONEDBABY integer,   CDLADVANCEBLOCK integer,CDLBELTHOLD integer,        CDLBREAKAWAY integer,       CDLCLOSINGMARUBOZU integer, CDLCONCEALBABYSWALL integer,CDLCOUNTERATTACK integer,   CDLDARKCLOUDCOVER integer,  CDLDOJI integer,   CDLDOJISTAR integer,        CDLDRAGONFLYDOJI integer,   CDLENGULFING integer,       CDLEVENINGDOJISTAR integer, CDLEVENINGSTAR integer,     CDLGAPSIDESIDEWHITE integer,CDLGRAVESTONEDOJI integer,  CDLHAMMER integer,          CDLHANGINGMAN integer,      CDLHARAMI integer,         CDLHARAMICROSS integer,    CDLHIGHWAVE integer,        CDLHIKKAKE integer,         CDLHIKKAKEMOD integer,      CDLHOMINGPIGEON integer,    CDLIDENTICAL3CROWS integer, CDLINNECK integer, CDLINVERTEDHAMMER integer,  CDLKICKING integer,         CDLKICKINGBYLENGTH integer, CDLLADDERBOTTOM integer,   CDLLONGLEGGEDDOJI integer,  CDLLONGLINE integer,   CDLMARUBOZU integer,   CDLMATCHINGLOW integer,  CDLMATHOLD integer,        CDLMORNINGDOJISTAR integer, CDLMORNINGSTAR integer,     CDLONNECK integer,          CDLPIERCING  integer,       CDLRICKSHAWMAN integer,     CDLRISEFALL3METHODS integer,CDLSEPARATINGLINES  integer,CDLSHOOTINGSTAR integer,    CDLSHORTLINE integer,      CDLSPINNINGTOP integer,   CDLSTALLEDPATTERN integer,  CDLSTICKSANDWICH integer,   CDLTAKURI integer,          CDLTASUKIGAP integer,       CDLTHRUSTING integer,       CDLTRISTAR  integer,    CDLUNIQUE3RIVER integer,  CDLUPSIDEGAP2CROWS integer, CDLXSIDEGAP3METHODS integer);")
			else:
				cc.execute("CREATE TABLE IF NOT EXISTS "+ "stockdata_"+self.Symbol.replace(' ','').replace('-','') +" (Date DATE, Close FLOAT, Open FLOAT, High FLOAT, Low FLOAT, Volume BIGINT, CDL2CROWS TINYINT, CDL3BLACKCROWS TINYINT, CDL3INSIDE TINYINT, CDL3LINESTRIKE TINYINT,     CDL3OUTSIDE TINYINT,        CDL3STARSINSOUTH TINYINT,   CDL3WHITESOLDIERS TINYINT,  CDLABANDONEDBABY TINYINT,   CDLADVANCEBLOCK TINYINT,CDLBELTHOLD TINYINT,        CDLBREAKAWAY TINYINT,       CDLCLOSINGMARUBOZU TINYINT, CDLCONCEALBABYSWALL TINYINT,CDLCOUNTERATTACK TINYINT,   CDLDARKCLOUDCOVER TINYINT,  CDLDOJI TINYINT,   CDLDOJISTAR TINYINT,        CDLDRAGONFLYDOJI TINYINT,   CDLENGULFING TINYINT,       CDLEVENINGDOJISTAR TINYINT, CDLEVENINGSTAR TINYINT,     CDLGAPSIDESIDEWHITE TINYINT,CDLGRAVESTONEDOJI TINYINT,  CDLHAMMER TINYINT,          CDLHANGINGMAN TINYINT,      CDLHARAMI TINYINT,         CDLHARAMICROSS TINYINT,    CDLHIGHWAVE TINYINT,        CDLHIKKAKE TINYINT,         CDLHIKKAKEMOD TINYINT,      CDLHOMINGPIGEON TINYINT,    CDLIDENTICAL3CROWS TINYINT, CDLINNECK TINYINT, CDLINVERTEDHAMMER TINYINT,  CDLKICKING TINYINT,         CDLKICKINGBYLENGTH TINYINT, CDLLADDERBOTTOM TINYINT,   CDLLONGLEGGEDDOJI TINYINT,  CDLLONGLINE TINYINT,   CDLMARUBOZU TINYINT,   CDLMATCHINGLOW TINYINT,  CDLMATHOLD TINYINT,        CDLMORNINGDOJISTAR TINYINT, CDLMORNINGSTAR TINYINT,     CDLONNECK TINYINT,          CDLPIERCING  TINYINT,       CDLRICKSHAWMAN TINYINT,     CDLRISEFALL3METHODS TINYINT,CDLSEPARATINGLINES  TINYINT,CDLSHOOTINGSTAR TINYINT,    CDLSHORTLINE TINYINT,      CDLSPINNINGTOP TINYINT,   CDLSTALLEDPATTERN TINYINT,  CDLSTICKSANDWICH TINYINT,   CDLTAKURI TINYINT,          CDLTASUKIGAP TINYINT,       CDLTHRUSTING TINYINT,       CDLTRISTAR  TINYINT,    CDLUNIQUE3RIVER TINYINT,  CDLUPSIDEGAP2CROWS TINYINT, CDLXSIDEGAP3METHODS TINYINT);")
					   
			try:
				# pdb.set_trace()
				cc.execute("SELECT * FROM "+ "stockdata_"+self.Symbol.replace(' ','').replace('-','') +" WHERE Date IN (SELECT max(Date) FROM "+ "stockdata_"+self.Symbol.replace(' ','').replace('-','') +") ;")
				Fromdate=dictfetchall(cc)[0]['Date']
				Fromdate=pd.to_datetime(Fromdate)
				datathere=True
			except:
				datathere=False


			print Fromdate
			print Todate
			print (Todate-Fromdate).days
			if (Todate-Fromdate).days<5:
				print "No update required for stock "+self.Symbol
				return True

			try:
				df=web.DataReader(self.Symbol, 'yahoo', Fromdate,Todate)
			except:
				time.sleep(5)
				try:
					df=web.DataReader(self.Symbol, 'yahoo', Fromdate,Todate)
				except:
					print "*******Error with Stock "+self.Symbol
					return False

			if len(df)<10:
				print "Not enough data received..... may be the symbol changed recently"
				return False
				
			if datathere==False:
				df=SDM.AppendCandlePatterns(df)
			else:
				# adding the pattern to last 30 days 
				DF=SDM.AppendCandlePatterns(df[(Todate-pd.DateOffset(30)) :Todate])
				df.loc[DF.index,:]=DF.copy()



			#as from date is already there in databse, remove it
			if datathere==True:
				if Fromdate in df.index:
					df.drop(Fromdate,inplace=True)

			candlecols=['CDL2CROWS' , 'CDL3BLACKCROWS' , 'CDL3INSIDE' , 'CDL3LINESTRIKE' ,     'CDL3OUTSIDE' ,        'CDL3STARSINSOUTH' ,   'CDL3WHITESOLDIERS' ,  'CDLABANDONEDBABY' ,   'CDLADVANCEBLOCK' ,'CDLBELTHOLD' ,        'CDLBREAKAWAY' ,       'CDLCLOSINGMARUBOZU' , 'CDLCONCEALBABYSWALL' ,'CDLCOUNTERATTACK' ,   'CDLDARKCLOUDCOVER' ,  'CDLDOJI' ,   'CDLDOJISTAR' ,        'CDLDRAGONFLYDOJI' ,   'CDLENGULFING' ,       'CDLEVENINGDOJISTAR' , 'CDLEVENINGSTAR' ,     'CDLGAPSIDESIDEWHITE' ,'CDLGRAVESTONEDOJI' ,  'CDLHAMMER' ,          'CDLHANGINGMAN',      'CDLHARAMI' ,         'CDLHARAMICROSS' ,    'CDLHIGHWAVE' ,        'CDLHIKKAKE' ,         'CDLHIKKAKEMOD' ,      'CDLHOMINGPIGEON' ,    'CDLIDENTICAL3CROWS' , 'CDLINNECK' , 'CDLINVERTEDHAMMER' ,  'CDLKICKING' ,         'CDLKICKINGBYLENGTH' , 'CDLLADDERBOTTOM' ,   'CDLLONGLEGGEDDOJI' ,  'CDLLONGLINE' ,   'CDLMARUBOZU' ,   'CDLMATCHINGLOW' ,  'CDLMATHOLD' ,        'CDLMORNINGDOJISTAR' , 'CDLMORNINGSTAR' ,     'CDLONNECK' ,          'CDLPIERCING'  ,       'CDLRICKSHAWMAN' ,     'CDLRISEFALL3METHODS' ,'CDLSEPARATINGLINES'  ,'CDLSHOOTINGSTAR' ,    'CDLSHORTLINE' ,      'CDLSPINNINGTOP' ,   'CDLSTALLEDPATTERN' ,  'CDLSTICKSANDWICH' ,   'CDLTAKURI' ,          'CDLTASUKIGAP' ,       'CDLTHRUSTING' ,       'CDLTRISTAR'  ,    'CDLUNIQUE3RIVER' ,  'CDLUPSIDEGAP2CROWS' , 'CDLXSIDEGAP3METHODS']

			if settings.DATABASES['default']['ENGINE']=='django.db.backends.sqlite3':
				data=[]
				for ind in df.index:
					pp=[ind.strftime("%Y-%m-%d"),df.loc[ind,'Close'], df.loc[ind,'Open'], df.loc[ind,'High'], df.loc[ind,'Low'], df.loc[ind,'Volume'] ]
					for col in candlecols:
						pp.append( round(df.loc[ind,col]) )
					data.append(tuple(pp) )

				qmarks=['?','?','?','?','?','?']+['?']*len(candlecols)
				qmarks='('+",".join(qmarks)+')'
				cc.execute("begin")
				cc.executemany("INSERT INTO "+ "stockdata_"+self.Symbol.replace(' ','').replace('-','') +" VALUES "+qmarks, data)
				cc.execute("commit")
			else:
				data=[]
				df['Date']=df.index.copy()
				df['Date']='"'+df['Date'].apply(lambda x: x.strftime("%Y-%m-%d"))+'"'
				
				for col in candlecols:
					df[col]=df[col].apply(lambda x: str(round(max(min(100,x), -100))))

				df=df[['Date','Close','Open','High','Low','Volume']+candlecols].astype(str)
				data='('+df.apply(lambda row: ",".join(row), axis=1)+')'
				data=data.tolist()
				data=",".join(data)
				cc.execute("INSERT INTO "+ "stockdata_"+self.Symbol.replace(' ','').replace('-','') +" (Date,Close,Open,High,Low,Volume,CDL2CROWS,CDL3BLACKCROWS,CDL3INSIDE,CDL3LINESTRIKE,CDL3OUTSIDE,CDL3STARSINSOUTH,CDL3WHITESOLDIERS,CDLABANDONEDBABY,CDLADVANCEBLOCK,CDLBELTHOLD,CDLBREAKAWAY,CDLCLOSINGMARUBOZU,CDLCONCEALBABYSWALL,CDLCOUNTERATTACK,CDLDARKCLOUDCOVER,CDLDOJI,CDLDOJISTAR,CDLDRAGONFLYDOJI,CDLENGULFING,CDLEVENINGDOJISTAR,CDLEVENINGSTAR,CDLGAPSIDESIDEWHITE,CDLGRAVESTONEDOJI,CDLHAMMER,CDLHANGINGMAN,CDLHARAMI,CDLHARAMICROSS,CDLHIGHWAVE,CDLHIKKAKE,CDLHIKKAKEMOD,CDLHOMINGPIGEON,CDLIDENTICAL3CROWS,CDLINNECK,CDLINVERTEDHAMMER,CDLKICKING,CDLKICKINGBYLENGTH,CDLLADDERBOTTOM,CDLLONGLEGGEDDOJI,CDLLONGLINE,CDLMARUBOZU,CDLMATCHINGLOW,CDLMATHOLD,CDLMORNINGDOJISTAR,CDLMORNINGSTAR,CDLONNECK,CDLPIERCING,CDLRICKSHAWMAN,CDLRISEFALL3METHODS,CDLSEPARATINGLINES,CDLSHOOTINGSTAR,CDLSHORTLINE,CDLSPINNINGTOP,CDLSTALLEDPATTERN,CDLSTICKSANDWICH,CDLTAKURI,CDLTASUKIGAP,CDLTHRUSTING,CDLTRISTAR,CDLUNIQUE3RIVER,CDLUPSIDEGAP2CROWS,CDLXSIDEGAP3METHODS ) VALUES  "+data+";")

		self.LastPriceUpdate= df.index[-1].date()
		self.save()

		print "Done updating Stock "+self.Symbol
		return True

	def DeleteData(self):
		with connection.cursor() as cc:
			cc.execute("DROP TABLE IF EXISTS "+ "stockdata_"+self.Symbol.replace(' ','').replace('-','')+";")
					   
	def UpdateData_retired(self, Fromdate=datetime.date(2002,1,1),Todate=datetime.date.today()):
		from django.conf import settings
		# with connection.cursor() as c:
		#     c.execute("CREATE TABLE IF NOT EXISTS "+ self.Symbol +" (Date text, Close real, Open real, High real, Low real, Volume real)")

		# cursor = connections['StockData'].cursor()
		# cursor.execute("CREATE TABLE IF NOT EXISTS "+ self.Symbol +" (Date text, Close real, Open real, High real, Low real, Volume real)")
		try:
			# df=pd.read_sql("SELECT * FROM "+ self.Symbol +" WHERE Date IN (SELECT max(Date) FROM "+ self.Symbol +") ", connections['StockData'])
			# Fromdate=self.price_set.all().order_by('Date').last().Date

			# cur=cursor.execute("SELECT * FROM "+ self.Symbol +" WHERE Date IN (SELECT max(Date) FROM "+ self.Symbol +") ")
			# Fromdate=datetime.datetime.strptime(dictfetchall(cur)[0]['Date'], "%Y-%m-%d").date()
			
			df=pd.read_hdf(settings.DATABASES['StockDataH5']['NAME'],self.Symbol)
			Fromdate=df.index[-1].date()
			datathere=True
		except:
			datathere=False
			pass
			
		print Fromdate
		print Todate
		print (Todate-Fromdate).days
		if (Todate-Fromdate).days<5:
			print "No update required for stock "+self.Symbol
			return True

		try:
			df=web.DataReader(self.Symbol, 'yahoo', Fromdate,Todate)
		except:
			time.sleep(5)
			try:
				df=web.DataReader(self.Symbol, 'yahoo', Fromdate,Todate)
			except:
				print "*******Error with Stock "+self.Symbol
				return False

		# for ind in df.index:
		#     date=ind.strftime("%Y-%m-%d")
		#     if self.price_set.filter(Date=date).exists()==False: 
		#         self.price_set.create(Close=df.loc[ind,'Close'],Open=df.loc[ind,'Open'],High=df.loc[ind,'High'],Low=df.loc[ind,'Low'],Volume=df.loc[ind,'Volume'],Date=date)
		
		# add the cndle pattern columns only if there no data to startwith
		if datathere==False:
			df=SDM.AppendCandlePatterns(df)
		else:
			# adding the pattern to last 30 days 
			DF=SDM.AppendCandlePatterns(df[(Todate-pd.DateOffset(30)).date() :Todate])
			df.loc[DF.index,:]=DF.copy()

		df.to_hdf(settings.DATABASES['StockDataH5']['NAME'],self.Symbol,format='table',append=True)

		self.LastPriceUpdate= df.index[-1].date()
		self.save()

		# data=[]
		# for ind in df.index:
		#     data.append((ind.strftime("%Y-%m-%d"),df.loc[ind,'Close'], df.loc[ind,'Open'], df.loc[ind,'High'], df.loc[ind,'Low'], df.loc[ind,'Volume']))
		# cursor.execute("begin")
		# cursor.executemany("INSERT INTO "+ self.Symbol +" VALUES (?,?,?,?,?,?)", data)
		# cursor.execute("commit")
		# cursor.close()

		print "Done updating Stock "+self.Symbol
		return True


def GetSectors():
	return Stock.objects.all().values_list('Sector',flat=True).distinct()

def GetIndustries():
	return Stock.objects.all().values_list('Sector',flat=True).distinct()

def GetStockData(symb,Fromdate=pd.datetime(2002,1,1),Todate=pd.datetime.today()):
	if Stock.objects.filter(Symbol=symb).exists()==True:
		return Stock.objects.get(Symbol=symb).GetData(Fromdate=Fromdate,Todate=Todate)
	else:
		return pd.DataFrame()
 
def GetStockMeta(symb):
	if Stock.objects.filter(Symbol=symb).exists()==True:
		return Stock.objects.get(Symbol=symb).values('Competitors','Sector','Industry','labels')
	else:
		return []

class Price(models.Model):
	Close=models.DecimalField(max_digits=9,decimal_places=2,null=True,blank=True)
	Open=models.DecimalField(max_digits=9,decimal_places=2,null=True,blank=True)
	High=models.DecimalField(max_digits=9,decimal_places=2,null=True,blank=True)
	Low=models.DecimalField(max_digits=9,decimal_places=2,null=True,blank=True)

	Volume=models.DecimalField(max_digits=15,decimal_places=2,null=True,blank=True)
	Date = models.DateField(null=False)

	stock=models.ForeignKey(Stock, on_delete=models.CASCADE)

	# def UpdateData(self, Fromdate=pd.datetime(2002,1,1),Todate=pd.datetime.today()):
	#     df=web.DataReader(self.stock.Symbol, 'yahoo', Fromdate,Todate)

	def __str__(self):
		return self.stock.Symbol+' '+str(self.Date)+' '+str(self.Close)

	class Meta:
		ordering = ["Date"]

# def Update(stock, Fromdate=pd.datetime(2002,1,1),Todate=pd.datetime.today()):
	
#     try:
#         df=web.DataReader(self.stock.Symbol, 'yahoo', Fromdate,Todate)
#         for ind in df.index:
#             date=ind.strftime("%Y-%m-%d") 
#             # p=Price(Close=df.loc[ind,'Close'],Open=df.loc[ind,'Open'],High=df.loc[ind,'High'],Low=df.loc[ind,'Low'],Volume=df.loc[ind,'Volume'],Date=date,stock=self.stock)
#             # p.save()
#             print [ind,df.loc[ind,'Close']]

#         return True
#     except:
#         return False




class Watchlist(models.Model):
	watchlistname=models.CharField(max_length=50,null=True)
	watchlist_descrip=models.CharField(max_length=1000,null=True,blank=True)
	user = models.ManyToManyField(User)
	stocks = models.ManyToManyField(Stock)
	created_at = models.DateTimeField(auto_now_add=True,null=True)
	updated_at = models.DateTimeField(auto_now=True,null=True)

	show = models.BooleanField(default=True)
	
	def __str__(self):
		return self.watchlistname


#--------------------FORMS----------------------------------------------------------------------------------------------------------

class UpdateStockData_form(forms.Form):
	symbol = forms.CharField(label='Enter the symbols (comma/space separated for multiple)',widget=forms.Textarea,required=False)
	symbol_list=forms.MultipleChoiceField(label='and/or Select multiple symbols',choices=[],required=False ,widget=forms.SelectMultiple(attrs={'size':'10','style':'width:150px;'}))

	watchlist = forms.ChoiceField(label='Select Watchlist', widget=forms.Select,choices=[])

	def __init__(self, *args, **kwargs):
		super(UpdateStockData_form, self).__init__(*args, **kwargs)
		
		self.fields['symbol_list'].choices = [(str(ss),str(ss)) for ss in Stock.objects.all().values_list('Symbol',flat=True).distinct()]
		self.fields['watchlist'].choices=[('None','None'),('All','All')]

		try:
			Wnaga=Watchlist.objects.filter(user=User.objects.get(username='nagavenkat')).values_list('watchlistname',flat=True)
			self.fields['watchlist'].choices=self.fields['watchlist'].choices+[(str(w),str(w)) for w in Wnaga]
		except:
			pass

		try:
			Wgen=Watchlist.objects.filter(user=User.objects.get(username='@general@')).values_list('watchlistname',flat=True)
			self.fields['watchlist'].choices=self.fields['watchlist'].choices+[(str(w),str(w)) for w in Wgen]
		except:
			pass

		self.symb=[]
	def process_stock_update(self,*args, **kwargs):
		# if 'watchlistname' in kwargs.keys():
		#     self.watchlistname=kwargs.pop('watchlistname')
		# else:
		#     self.watchlistname=None

		print self.cleaned_data['watchlist']
		print self.cleaned_data['symbol']
		print self.cleaned_data['symbol_list']


		symbols=[]
		if self.cleaned_data['symbol']!=None and self.cleaned_data['symbol']!='':
			symbols=symbols+re.compile(r'[:,\s\n]').split(self.cleaned_data['symbol'])

		if self.cleaned_data['symbol_list']!=None and self.cleaned_data['symbol_list']!='':
			symbols=symbols+self.cleaned_data['symbol_list']
		
		symbols=list(set(symbols))
		symbols=[ss.upper() for ss in symbols if ss!='']

		


		if self.cleaned_data['watchlist']!='None' and self.cleaned_data['watchlist']!=None and self.cleaned_data['watchlist']!='':

			if self.cleaned_data['watchlist']=='All':
				symbols=symbols+[str(ss) for ss in Stock.objects.all()]
			else:
				try:
					Wnaga=Watchlist.objects.get(user=User.objects.get(username='nagavenkat'),watchlistname=self.cleaned_data['watchlist'])
					symbols=symbols+[str(ss) for ss in Wnaga.stocks.all()]
				except:
					pass

				try:
					Wgen=Watchlist.objects.get(user=User.objects.get(username='@general@'),watchlistname=self.cleaned_data['watchlist'])
					symbols=symbols+[str(ss) for ss in Wgen.stocks.all()]
				except:
					pass

		stocks=[]
		for ss in symbols:
			try:
				stocks.append(Stock.objects.get(Symbol=ss))
			except:
				S=Stock(Symbol=ss)
				S.save()
				stocks.append(S)

		for si in range(len(stocks)):
			print [si,len(stocks)]
			stocks[si].UpdateData()



class ControlPanel_form(forms.Form):
	symbol = forms.CharField(label='Enter the symbols (comma/space separated for multiple)',widget=forms.Textarea,required=False)
	symbol_list=forms.MultipleChoiceField(label='and/or Select multiple symbols',choices=[],required=False ,widget=forms.SelectMultiple(attrs={'size':'10','style':'width:150px;'}))

	user_email = forms.EmailField(label='Enter your email to load your watchlists',required=False)
	user_name = forms.CharField(label='Enter your name to load your watchlists',required=False)
	create_user = forms.BooleanField(label='Create user if not exists?',required=False)
	
	watchlist_name = forms.CharField(label='Enter the watchlists name', max_length=100,required=False)
	create_watchlist = forms.BooleanField(label='Create the watchlist if it does not exist using the symbols selected above',required=False)
	watchlist_user_gen = forms.BooleanField(label=mark_safe('Assign the watchlist to the username/email above(if provided) <br />or leave it unmarked to make it a General watchlist'),required=False)

	
	watchlist = forms.ModelChoiceField(label='Select Watchlist',widget=forms.Select(attrs={'size':'5','style':'width:150px;'}),queryset=Watchlist.objects.all(),required=False)
	general_watchlists = forms.BooleanField(label='Also load general watchlists',required=False)
	update_stockdata_in_watchlists = forms.BooleanField(label='Update the Data for the Symbols/Watchlist',required=False)

	def __init__(self, *args, **kwargs):
		super(ControlPanel_form, self).__init__(*args, **kwargs)
		self.fields['symbol_list'].choices = [('-1','---')]+[(str(ss),str(ss)) for ss in Stock.objects.all.values_list('Symbol',flat=True).distinct()]





class CreateWatchlistForm(forms.Form):
	watchlist_name = forms.CharField(label='Enter a watchlists name', max_length=100)
	watchlist_descrip=forms.CharField(label='Describe the watchlist',widget=forms.Textarea(attrs={'style':'width:300px;height:50px'}), max_length=1000,required=False)

	symbol = forms.CharField(label='Enter the symbols (comma/space separated for multiple)',widget=forms.Textarea,required=False)
	symbol_list=forms.MultipleChoiceField(label='and/or Select multiple symbols',choices=[],required=False ,widget=forms.SelectMultiple(attrs={'size':'10','style':'width:150px;'}))
	
	stocks=[]
	def __init__(self, *args, **kwargs):
		super(CreateWatchlistForm, self).__init__(*args, **kwargs)
		self.fields['symbol_list'].choices = [('-1','---')]+[(str(ss),str(ss)) for ss in Stock.objects.all().values_list('Symbol',flat=True).distinct()]

	def process_watchlist(self,*args,**kwargs):
		username=kwargs.pop('username')
		if str(username)=='AnonymousUser':
			return False,"Please register to create a personal watchlists"

		if str(username)!='nagavenkat' and self.cleaned_data['watchlist_name']=='@general@':
			return False,"Watchlist name is not permitted"



		symbols=[]
		if self.cleaned_data['symbol']!=None and self.cleaned_data['symbol']!='':
			symbols=symbols+re.compile(r'[:,\s\n]').split(self.cleaned_data['symbol'])

		if self.cleaned_data['symbol_list']!=None and self.cleaned_data['symbol_list']!='':
			symbols=symbols+self.cleaned_data['symbol_list']
		
		symbols=list(set(symbols))
		symbols=[ss.upper() for ss in symbols if ss!='']

		stocks=[]
		for ss in symbols:
			try:
				stocks.append(Stock.objects.get(Symbol=ss))
			except:
				S=Stock(Symbol=ss)
				S.save()
				stocks.append(S)
		
		self.stocks=symbols



		try:
			W=Watchlist.objects.get(watchlistname=self.cleaned_data['watchlist_name'],user=username)
			return False,"Watchlist already exists, please modify it"
		except:
			w=Watchlist(watchlistname=self.cleaned_data['watchlist_name'],watchlist_descrip=self.cleaned_data['watchlist_descrip'])
			w.save()

		w.user.add(username)
		w.stocks.add(*stocks)
		w.save()

		return True,None

class Watchlist_amend_form(forms.Form):
	watchlist = forms.ChoiceField(label='Select Watchlist', widget=forms.Select,choices=[])
	
	def __init__(self, *args, **kwargs):
		self.username=kwargs.pop('username')
		if 'watchlistname' in kwargs.keys():
			self.watchlistname=kwargs.pop('watchlistname')
			watchlistname=self.watchlistname
		else:
			self.watchlistname=None
			watchlistname=self.watchlistname

		if str(self.username)=='AnonymousUser':
			self.watchlistname=None
			watchlistname=self.watchlistname
			username=None
			self.username=username

		super(Watchlist_amend_form, self).__init__(*args, **kwargs)

		try:
			W=Watchlist.objects.filter(user=self.username).values_list('watchlistname')
		except:
			W=[None]

		self.fields['watchlist'].choices=[(str(w),str(w)) for w in W]
		self.symbs=[]

		

		if self.watchlistname!=None:

			if str(self.username)!='nagavenkat' and self.watchlistname=='@general@':
				return False,"Watchlist name is not permitted"

			try:
				W=Watchlist.objects.get(user=self.username,watchlistname=self.watchlistname)
			except:
				return False,"Watchlist "+self.watchlistname+" is not present for user "+self.username

			symbs=W.stocks.all()

			symbs=[str(ss) for ss in symbs]
			print ", ".join(symbs)
			self.symbs=symbs

			self.fields['symbols_append']= forms.CharField(label='Append New Symbols (comma/space separated for multiple)',widget=forms.Textarea(attrs={'style':'width:300px;height:50px'})
													,required=False)

			for ss in symbs:
				self.fields['del_'+ss]=forms.BooleanField(label=ss,required=False,initial=False)

	def process_amend(self, *args, **kwargs):
		if str(self.username)=='AnonymousUser':
			return False,"Please register to ammend your personal watchlists"

		if str(self.username)!='nagavenkat' and self.watchlistname=='@general@':
			return False,"Watchlist name is not permitted"

		# W=Watchlist.objects.get(user=self.username,watchlistname=self.watchlistname)
		stocks_prev=self.symbs

		stocks_prev_str=[str(ss) for ss in stocks_prev]

		symbols_append_str=[]
		if self.cleaned_data['symbols_append']!=None and self.cleaned_data['symbols_append']!='':
			symbols_append_str=re.compile(r'[:,\s\n]').split(self.cleaned_data['symbols_append'])
		
		symbols_new_str=list( set(stocks_prev_str+symbols_append_str) )

		

		symbols_final_str=[]
		for ss in symbols_new_str:
			if 'del_'+ss in self.cleaned_data:
				if self.cleaned_data['del_'+ss]==True:
					print self.cleaned_data['del_'+ss] 
					pass
				else:
					symbols_final_str.append(ss.upper())
			else:
				symbols_final_str.append(ss.upper())

		
		symbols_final=[]
		for ss in symbols_final_str:
			try:
				S=Stock.objects.get(Symbol=ss)
				symbols_final.append(S)
			except:
				pass


		try:
			W=Watchlist.objects.get(watchlistname=self.watchlistname,user=self.username)
			watchlist_descrip=str(W.watchlist_descrip)
		except:
			return False,"Watchlist "+self.watchlistname+" is not present for user "+self.username

		W.delete()
		W=Watchlist(watchlistname=self.watchlistname,watchlist_descrip=watchlist_descrip)
		W.save()
		
		W.user.add(self.username)
		W.stocks.add(*symbols_final)
		W.save()

		return True,None

	def get_symbols_order(self):
		L=[]
		for ff in self.fields.keys():
			if 'del_' in ff:
				L.append((ff,ff.split('_')[1]))

		return L 

	def symbols_length_del(self):
		if len(self.symbs)>0:
			return True
		else:
			return False 



class Watchlist_view_form(forms.Form):
	watchlist = forms.ChoiceField(label='View Watchlist', widget=forms.Select,choices=[])
	
	def __init__(self, *args, **kwargs):
		
		
		if 'watchlistname' in kwargs.keys():
			self.watchlistname=kwargs.pop('watchlistname')
		else:
			self.watchlistname=None

		if 'user' in kwargs.keys():
			self.user=kwargs.pop('user')
			if str(self.user)=='AnonymousUser':
				self.username='AnonymousUser'
				self.user=User.objects.get(username='@general@')
			else:
				self.username=str(self.user)
		else:
			self.username='AnonymousUser'
			self.user=User.objects.get(username='@general@')

		super(Watchlist_view_form, self).__init__(*args, **kwargs)

		if self.username!='AnonymousUser' and self.username!='@general@':
			try:
				Wuser=Watchlist.objects.filter(user=self.user).values_list('watchlistname',flat=True)
				# Wuser=[str(w) for w in Wuser]
			except:
				Wuser=[]
			self.fields['watchlist'].choices=self.fields['watchlist'].choices+[(str(w),str(w)) for w in Wuser]

		try:
			Wgen=Watchlist.objects.filter(user=User.objects.get(username='@general@') ).values_list('watchlistname',flat=True)
			# Wgen=[str(w) for w in Wgen]
		except:
			Wgen=[]

		
		self.fields['watchlist'].choices=self.fields['watchlist'].choices+[(str('-------'),str('-------'))]
		self.fields['watchlist'].choices=self.fields['watchlist'].choices+[(str(w),str(w)) for w in Wgen]

		self.symbs=[]

		print "0---"*5
		print '*'+str(self.watchlistname)+'*'
		print '*'+str(self.user)+'*'

		if self.watchlistname!=None:

			try:
				W=Watchlist.objects.get(user=self.user,watchlistname=self.watchlistname)
			except:
				try:
					W=Watchlist.objects.get(user=User.objects.get(username='@general@'),watchlistname=self.watchlistname)
				except:
					return False,"Watchlist "+self.watchlistname+" is not present for user "+str(self.user)

			symbs=W.stocks.all()

			self.symbs=[str(ss) for ss in symbs]
			print ", ".join(self.symbs)


def BasicInitialize():
	import research.models as rmd
	import charting.models as chmd
	for cc in rmd.FeatureOperator.choices.keys():
		if rmd.FeatureOperator.objects.filter(operators=cc).exists()==False:
			FO=rmd.FeatureOperator(operators=cc)
			FO.save()
	for cc in rmd.FeatureUnit.choices.keys():
		if rmd.FeatureUnit.objects.filter(units=cc).exists()==False:
			FU=rmd.FeatureUnit(units=cc)
			FU.save()

	if rmd.SavedQueries.objects.filter(Queryname='StockMarket').exists()==False:
		SQ=rmd.SavedQueries(Queryname='StockMarket',Filjson='[]',window=360,Interval='D')
		SQ.save()		

	#  add All Symbols to watchlist
	genuser=User.objects.get(username='@general@')
	if Watchlist.objects.filter(watchlistname='All Symbols',watchlist_descrip='All the stocks',user=genuser).exists()==False:
		wth=Watchlist(watchlistname='All Symbols',watchlist_descrip='All the stocks')
		wth.save()
		wth.user.add(genuser)
		wth.stocks.add(*Stock.objects.all())
		wth.save()
		
	# dump the feature codes
	import research.featuremanager as featmng
	with featmng.featuremanager() as FM:
		FM.DumpFeatureCodes2file()

	# add basic chart props here 
	if chmd.StdChartProps.objects.filter(chartstylename='@default@',user=User.objects.get(username='@general@')).exists()==False:
		scp=chmd.StdChartProps(chartstylename='@default@')
		scp.save()
		scp.user.add(User.objects.get(username='@general@'))
		scp.save()	
		chartpropquery={}
		chartpropquery['ci']=['SMA10','SMA20','SMA50','SMA100','SMA200']
		chartpropquery['vi']=['VolSMA10','VolSMA20']
		chartpropquery['i']=[]
		chartpropquery['cp']=[]
		chartpropquery['ch']=[]
		chartpropquery['lt']=[]
		scp.UpdateChartProp(chartpropquery)
		scp.save()
	
	if chmd.StdChartProps.objects.filter(chartstylename='@defaultlinear@',user=User.objects.get(username='@general@')).exists()==False:

		scp=chmd.StdChartProps(chartstylename='@defaultlinear@')
		scp.save()
		scp.user.add(User.objects.get(username='@general@'))
		scp.save()	
		chartpropquery={}
		chartpropquery['ci']=['SMA10','SMA20','SMA50','SMA100','SMA200']
		chartpropquery['vi']=['VolSMA10','VolSMA20']
		chartpropquery['i']=[]
		chartpropquery['cp']=[]
		chartpropquery['ch']=[]
		chartpropquery['lt']=['top','mid','bottom']
		scp.UpdateChartProp(chartpropquery)
		scp.save()

	# Add the perf codes here
	if rmd.GeneralFeature.objects.filter(name='FutMXRtQt').exists()==False:
		#------------------
		GF=rmd.GeneralFeature(group ='Performance',name='FutMXRtQt',user=User.objects.get(username='@general@'),
				description=" The maximum quaterly performance i.e profit(positive)/loss(negative) possible T+3m assuming buy on T date"
				)      
		GF.save()
		GF.operators.add(*rmd.FeatureOperator.objects.filter(operators__in=['gt','gte','lt','lte'])  )
		GF.units.add(rmd.FeatureUnit.objects.get(units='%' ) )

		GF=rmd.GeneralFeature(group ='Performance',name='FutMNRtQt',user=User.objects.get(username='@general@'),
				description=" The minimum quaterly performance i.e profit(positive)/loss(negative) possible T+3m assuming buy on T date"
				)      
		GF.save()
		GF.operators.add(*rmd.FeatureOperator.objects.filter(operators__in=['gt','gte','lt','lte'])  )
		GF.units.add(rmd.FeatureUnit.objects.get(units='%' ) )

		#------------------
		GF=rmd.GeneralFeature(group ='Performance',name='FutMXRtHf',user=User.objects.get(username='@general@'),
				description=" The maximum half yearly performance i.e profit(positive)/loss(negative) possible T+6m assuming buy on T date"
				)      
		GF.save()
		GF.operators.add(*rmd.FeatureOperator.objects.filter(operators__in=['gt','gte','lt','lte'])  )
		GF.units.add(rmd.FeatureUnit.objects.get(units='%' ) )

		GF=rmd.GeneralFeature(group ='Performance',name='FutMNRtHf',user=User.objects.get(username='@general@'),
				description=" The minimum half yearly performance i.e profit(positive)/loss(negative) possible T+6m assuming buy on T date"
				)      
		GF.save()
		GF.operators.add(*rmd.FeatureOperator.objects.filter(operators__in=['gt','gte','lt','lte'])  )
		GF.units.add(rmd.FeatureUnit.objects.get(units='%' ) )

		#------------------
		GF=rmd.GeneralFeature(group ='Performance',name='FutMXRtAn',user=User.objects.get(username='@general@'),
				description=" The maximum annual performance i.e profit(positive)/loss(negative) possible T+1y assuming buy on T date"
				)      
		GF.save()
		GF.operators.add(*rmd.FeatureOperator.objects.filter(operators__in=['gt','gte','lt','lte'])  )
		GF.units.add(rmd.FeatureUnit.objects.get(units='%' ) )

		GF=rmd.GeneralFeature(group ='Performance',name='FutMNRtAn',user=User.objects.get(username='@general@'),
				description=" The minimum annual performance i.e profit(positive)/loss(negative) possible T+1y assuming buy on T date"
				)      
		GF.save()
		GF.operators.add(*rmd.FeatureOperator.objects.filter(operators__in=['gt','gte','lt','lte'])  )
		GF.units.add(rmd.FeatureUnit.objects.get(units='%' ) )

		
		#------------------
		GF=rmd.GeneralFeature(group ='Performance',name='PastMXRtQt',user=User.objects.get(username='@general@'),
				description=" The maximum quaterly performance i.e profit(positive)/loss(negative) in T-3m assuming sell on T date"
				)      
		GF.save()
		GF.operators.add(*rmd.FeatureOperator.objects.filter(operators__in=['gt','gte','lt','lte'])  )
		GF.units.add(rmd.FeatureUnit.objects.get(units='%' ) )

		GF=rmd.GeneralFeature(group ='Performance',name='PastMNRtQt',user=User.objects.get(username='@general@'),
				description=" The minimum quaterly performance i.e profit(positive)/loss(negative) in T-3m assuming sell on T date"
				)      
		GF.save()
		GF.operators.add(*rmd.FeatureOperator.objects.filter(operators__in=['gt','gte','lt','lte'])  )
		GF.units.add(rmd.FeatureUnit.objects.get(units='%' ) )

		#------------------
		GF=rmd.GeneralFeature(group ='Performance',name='PastMXRtHf',user=User.objects.get(username='@general@'),
				description=" The maximum half yearly performance i.e profit(positive)/loss(negative) in T-6m assuming sell on T date"
				)      
		GF.save()
		GF.operators.add(*rmd.FeatureOperator.objects.filter(operators__in=['gt','gte','lt','lte'])  )
		GF.units.add(rmd.FeatureUnit.objects.get(units='%' ) )

		GF=rmd.GeneralFeature(group ='Performance',name='PastMNRtHf',user=User.objects.get(username='@general@'),
				description=" The minimum half yearly performance i.e profit(positive)/loss(negative) in T-6m assuming sell on T date"
				)      
		GF.save()
		GF.operators.add(*rmd.FeatureOperator.objects.filter(operators__in=['gt','gte','lt','lte'])  )
		GF.units.add(rmd.FeatureUnit.objects.get(units='%' ) )

		#------------------
		GF=rmd.GeneralFeature(group ='Performance',name='PastMXRtAn',user=User.objects.get(username='@general@'),
				description=" The maximum half yearly performance i.e profit(positive)/loss(negative) in T-1y assuming sell on T date"
				)      
		GF.save()
		GF.operators.add(*rmd.FeatureOperator.objects.filter(operators__in=['gt','gte','lt','lte'])  )
		GF.units.add(rmd.FeatureUnit.objects.get(units='%' ) )

		GF=rmd.GeneralFeature(group ='Performance',name='PastMNRtAn',user=User.objects.get(username='@general@'),
				description=" The minimum half yearly performance i.e profit(positive)/loss(negative) in T-1y assuming sell on T date"
				)      
		GF.save()
		GF.operators.add(*rmd.FeatureOperator.objects.filter(operators__in=['gt','gte','lt','lte'])  )
		GF.units.add(rmd.FeatureUnit.objects.get(units='%' ) )

#-------------------TABLES-----------------------------------------------------------------------------------------------------------

	
class StockTable(tables.Table):
	class Meta:
		model = Stock




