from __future__ import unicode_literals
from __future__ import division
from django.db import models
import tempfile
import os
import pandas as pd
pd.set_option('display.max_colwidth', -1)
from django.core.validators import RegexValidator
from django.core.files import File
from django.contrib.auth.models import User
import stockdata.models as stkmd
import charting.models as chrtmd
from django.contrib.postgres.fields import ArrayField
from django.utils.safestring import mark_safe
import logging
logger = logging.getLogger(__name__)
from django.contrib.postgres.fields import JSONField



# these are basically questions such as 
# Sold to fast
# Decieved by news or friend
# Actually the news helped me
# Bought it by goind through Query 1
# Did my research on fundamental analysis and then bought it
# etc etc ............

# Questions can be like
# Did you check the fundamentals
# Did 

# Journal is your study journal ... your real trades 
# Buy trades
# Sell trades
# Holding or waiting
# long trades
# Short Trades

# Grade is for training data
# Cup and Handle Pattern



class Category(models.Model):
	user = models.ForeignKey(User,on_delete=models.CASCADE)
	name = models.CharField(max_length=100)
	description=models.CharField(max_length=500,null=True,blank=True)
	Type=models.CharField(max_length=1,choices=[('J','Journal'),('G','Grade'),('Q','Question')],null=True,blank=True)
	ParentCategory=models.ForeignKey('self', blank=True, null=True,on_delete=models.CASCADE)

	def __str__(self):
		return str(self.user)+ ' : ' +str(self.Type)+ ' : ' +str(self.name)

GradingChoices=[('-1','Negative/Bad/No'),('0','Neutral/OK/Maybe'),('1','Positive/Good/Yes')]

class Grading(models.Model):
	user = models.ForeignKey(User,on_delete=models.CASCADE)
	Category=models.ForeignKey(Category, blank=True, null=True,on_delete=models.CASCADE)
	T= models.DateField(null=False)
	window=models.DecimalField(max_digits=4,decimal_places=0,null=True,blank=True)
	Symbol=models.ForeignKey(stkmd.Stock, on_delete=models.CASCADE)
	Interval = models.CharField(max_length=1, choices=chrtmd.intervals)
	Grade= models.CharField(max_length=5, choices=GradingChoices,null=True,blank=True)
	notes=models.CharField(max_length=100,null=True,blank=True)
	CustomImage=models.ImageField(max_length=200,null=True,blank=True)
	created_at = models.DateTimeField(auto_now_add=True,null=True)
	updated_at = models.DateTimeField(auto_now=True,null=True)

	def __str__(self):
		return str(self.user)+ ' : ' +str(self.Category)+ ' : ' +str(self.Symbol)+ ' : ' +str(self.T)+ ' : ' +  str(self.window) + ' : ' +str(self.Interval)



class SavedQueries(models.Model):
	Queryname=models.CharField(max_length=100,null=True)
	Querydescription=models.CharField(max_length=500,null=True)
	watchlist=models.ForeignKey(stkmd.Watchlist,on_delete=models.CASCADE,null=True)
	user = models.ForeignKey(User,on_delete=models.CASCADE,null=True)
	Coljson=models.CharField(max_length=500,null=True)
	Filjson=models.CharField(max_length=800,null=True)

	window=models.DecimalField(max_digits=4,decimal_places=0,null=True,blank=True)
	Interval = models.CharField(max_length=1, choices=chrtmd.intervals)

	
	
	created_at = models.DateTimeField(auto_now_add=True,null=True)
	updated_at = models.DateTimeField(auto_now=True,null=True)

	def __str__(self):
		return str(self.Queryname)

	
def QueryDF_path(instance, filename):
	pth=os.path.join('Query_DF', instance.T.strftime("%Y-%m-%d"),instance.DFname+'_'+str(instance.savedquery.pk) +'.h5' )
	return pth

class SavedQueries_DF(models.Model):
	savedquery=models.ForeignKey(SavedQueries,on_delete=models.CASCADE)
	T= models.DateField(null=False)
	DFname=models.CharField(max_length=100,null=True)
	QueryDF = models.FileField(upload_to=QueryDF_path,null=True)

	created_at = models.DateTimeField(auto_now_add=True,null=True)
	updated_at = models.DateTimeField(auto_now=True,null=True)


	def uploadDF(self,DF):
		tmpfl = tempfile.NamedTemporaryFile(suffix='.h5',delete=False)
		DF.to_hdf(tmpfl.name,'table')
		temp = open(tmpfl.name, 'r')
		self.QueryDF = File(temp)
		self.save() 
		temp.close()

	def readDF(self):
		from django.conf import settings
		pp=self.QueryDF.url
		if pp[0]=='/':
			pp=pp[1:]
		
		path=os.path.join(settings.MEDIA_ROOT.replace('media',''),pp)
		DF=pd.read_hdf(path,'table')
		return DF

def image_path(instance, filename):
	return os.path.join('Query_plots',instance.T.strftime("%Y-%m-%d") ,instance.plotname+'_'+str(instance.savedquery.pk)+'.png')

class SavedQueries_plots(models.Model):
	savedquery=models.ForeignKey(SavedQueries,on_delete=models.CASCADE)
	T= models.DateField(null=False)
	plotname=models.CharField(max_length=100,null=True)
	plotsize=JSONField(null=True)
	image = models.ImageField(upload_to=image_path)

	created_at = models.DateTimeField(auto_now_add=True,null=True)
	updated_at = models.DateTimeField(auto_now=True,null=True)

	def uploadfig2file(self,fig):
		# convert dict to json and save
		tf = tempfile.NamedTemporaryFile(suffix='.png',delete=False)
		fig.savefig(tf.name,bbox_inches='tight',transparent=True, format='png')
		temp = open(tf.name, 'r')
		self.image = File(temp)
		self.save() 
		temp.close()

	def GetcleanedURL(self):
		ss=self.image.url
		sk=ss.split('?')[0]
		if '.png' in ss and '.png' not in sk:
			sk=sk+'.png'
		return mark_safe(sk) 

	def GetImage(self,width="300px",height="200px",mode='lazy'):
		if mode=='lazy':
			return mark_safe('<img class="lazy" data-original="'+self.GetcleanedURL()+'" style="width:'+width+';height:'+height+';">')             
		else:
			return mark_safe('<img src="'+self.GetcleanedURL()+'" style="width:'+width+';height:'+height+';">') 



def ComputeStatusDF_path(instance, filename):
	pth=os.path.join('ComputeStatusDF', instance.T.strftime("%Y-%m-%d"),instance.DFname +'.h5' )
	return pth

class ComputeStatusDF(models.Model):
	T= models.DateField(null=False)
	DFname=models.CharField(max_length=100,null=True)
	DF = models.FileField(upload_to=ComputeStatusDF_path,null=True)

	created_at = models.DateTimeField(auto_now_add=True,null=True)
	updated_at = models.DateTimeField(auto_now=True,null=True)


	def uploadDF(self,DF):
		tmpfl = tempfile.NamedTemporaryFile(suffix='.h5',delete=False)
		DF.to_hdf(tmpfl.name,'table')
		temp = open(tmpfl.name, 'r')
		self.DF = File(temp)
		self.save() 
		temp.close()

	def readDF(self):
		from django.conf import settings
		pp=self.DF.url
		if pp[0]=='/':
			pp=pp[1:]
		path=os.path.join(settings.MEDIA_ROOT.replace('media',''),pp)
		DF=pd.read_hdf(path,'table')
		return DF


def GeneralFile_path(instance, filename):
	pth=os.path.join('GeneralFile', instance.T.strftime("%Y-%m-%d"),str(instance.name) +str(instance.extn) )
	return pth

class GeneralFile(models.Model):
	T= models.DateField(null=False)
	name=models.CharField(max_length=100,null=True)
	F = models.FileField(upload_to=GeneralFile_path,null=True)
	extn=models.CharField(max_length=5,null=True)

	created_at = models.DateTimeField(auto_now_add=True,null=True)
	updated_at = models.DateTimeField(auto_now=True,null=True)

	
	def uploadDF2csv(self,DF):
		tmpfl = tempfile.NamedTemporaryFile(suffix='.csv',delete=False)
		self.extn='.csv'
		DF.to_csv(tmpfl.name,chunksize=10000,index=False)
		temp = open(tmpfl.name, 'r')
		self.F = File(temp)
		self.save() 
		temp.close()

	def uploadDF2csv_recursive(self,DF,header=True):
		if hasattr(self, 'tmpflrec')==False:
			self.tmpflrec = tempfile.NamedTemporaryFile(suffix='.csv',delete=False)
		self.extn='.csv'
		DF.to_csv(self.tmpflrec.name,chunksize=10000,index=False,mode='a',header=header)


	def uploadDF2csv_recursive_finalize(self):
		self.extn='.csv'
		temp = open(self.tmpflrec.name, 'r')
		self.F = File(temp)
		self.save() 
		temp.close()

	def GetcleanedCSVURL(self):
		ss=self.F.url
		sk=ss.split('?')[0]
		if '.csv' in ss and '.csv' not in sk:
			sk=sk+'.csv'
		return mark_safe(sk)

	def readcsv2DF(self):
		from django.conf import settings
		pp=self.F.url
		if pp[0]=='/':
			pp=pp[1:]
		
		path=os.path.join(settings.MEDIA_ROOT.replace('media',''),pp)
		DF=pd.read_csv(path,index=False)
		return DF

	def DeleteFileIfexists(self):
		if bool(self.F)==False or self.F==None:
			return
		else:
			from django.conf import settings
			pp=self.F.url
			if pp[0]=='/':
				pp=pp[1:]
			
			if self.extn not in pp:
				pp=pp+self.extn

			ppath=os.path.join(settings.MEDIA_ROOT.replace('media',''),pp)
			if os.path.isfile(ppath):
				import subprocess as sbp
				sbp.check_output(['rm',ppath])
				self.F=None
				self.save()


	def uploadfig2file(self,fig):
		# convert dict to json and save
		tf = tempfile.NamedTemporaryFile(suffix='.png',delete=False)
		fig.savefig(tf.name,bbox_inches='tight',transparent=True, format='png')
		temp = open(tf.name, 'r')
		self.F = File(temp)
		self.extn='.png'
		self.save() 
		temp.close()

	def GetcleanedURL(self):
		ss=self.F.url
		sk=ss.split('?')[0]
		if '.png' in ss and '.png' not in sk:
			sk=sk+'.png'
		return mark_safe(sk) 

	def GetImage(self,width="300px",height="200px",mode='lazy'):
		if mode=='lazy':
			return mark_safe('<img class="lazy" data-original="'+self.GetcleanedURL()+'" style="width:'+width+';height:'+height+';">')             
		else:
			return mark_safe('<img src="'+self.GetcleanedURL()+'" style="width:'+width+';height:'+height+';">') 


	def uploadDF(self,DF):
		tmpfl = tempfile.NamedTemporaryFile(suffix='.h5',delete=False)
		self.extn='.h5'
		DF.to_hdf(tmpfl.name,'table')
		temp = open(tmpfl.name, 'r')
		self.F = File(temp)
		self.save() 
		temp.close()

	def readDF(self):
		from django.conf import settings
		pp=self.F.url
		if pp[0]=='/':
			pp=pp[1:]
		
		path=os.path.join(settings.MEDIA_ROOT.replace('media',''),pp)
		DF=pd.read_hdf(path,'table')
		return DF


class LinearTrends(models.Model):
	window=models.DecimalField(max_digits=4,decimal_places=0,null=True,blank=True)
	T= models.DateField(null=False)
	Symbol=models.ForeignKey(stkmd.Stock, on_delete=models.CASCADE)
	Interval = models.CharField(max_length=1, choices=chrtmd.intervals)
	created_at = models.DateTimeField(auto_now_add=True,null=True)
	updated_at = models.DateTimeField(auto_now=True,null=True)
	
	LinearTrendsJsonStr_top=models.TextField(null=True,blank=True)
	LinearTrendsJsonStr_mid=models.TextField(null=True,blank=True)
	LinearTrendsJsonStr_bottom=models.TextField(null=True,blank=True)

	def UpdateTrends(self,top=None,mid=None,bottom=None):
		if top is not None:
			self.LinearTrendsJsonStr_top=top.to_json(orient='index',date_unit='ms') 
		if mid is not None:
			self.LinearTrendsJsonStr_mid=mid.to_json(orient='index',date_unit='ms')
		if bottom is not None:
			self.LinearTrendsJsonStr_bottom=bottom.to_json(orient='index',date_unit='ms')

	def GetTopTrends(self):
		if self.LinearTrendsJsonStr_top is not None:
			TrendTop=pd.read_json(self.LinearTrendsJsonStr_top,orient='index')
			TrendTop['Xfdate']=pd.to_datetime(TrendTop['Xfdate'],unit='ms')
			TrendTop['X0date']=pd.to_datetime(TrendTop['X0date'],unit='ms')
		else:
			TrendTop=pd.DataFrame()

		return TrendTop

	def GetMidTrends(self):
		if self.LinearTrendsJsonStr_mid is not None:
			TrendMid=pd.read_json(self.LinearTrendsJsonStr_mid,orient='index')
			TrendMid['Xfdate']=pd.to_datetime(TrendMid['Xfdate'],unit='ms')
			TrendMid['X0date']=pd.to_datetime(TrendMid['X0date'],unit='ms')
		else:
			TrendMid=pd.DataFrame()

		return TrendMid

	def GetBottomTrends(self):
		if self.LinearTrendsJsonStr_bottom is not None:
			TrendBottom=pd.read_json(self.LinearTrendsJsonStr_bottom,orient='index')
			TrendBottom['Xfdate']=pd.to_datetime(TrendBottom['Xfdate'],unit='ms')
			TrendBottom['X0date']=pd.to_datetime(TrendBottom['X0date'],unit='ms')
		else:
			TrendBottom=pd.DataFrame()

		return TrendBottom

	def __str__(self):
		return str(self.Symbol)+ ' : ' +str(self.T)+ ' : ' +  str(self.window) + ' : ' +str(self.Interval)

class FeatureOperator(models.Model):
	choices={	'gt':'greater than',
				'lt':'less than',
				'gte':'greater than or equal to',
				'lte':'less than or equal to',
				'equalto':'equal to',
				'contains':'contains'}
	choices_sql={	'gt':'>',
					'lt':'<',
					'gte':'>=',
					'lte':'<=',
					'equalto':'=',
					'contains':'LIKE'}
	operators=models.CharField(max_length=15, choices=[(key,value) for key,value in choices.items()]  )

	def __str__(self):
		return str(self.operators)


class FeatureUnit(models.Model):
	choices={'candles':'#candles','%_window':'% of window','%':'%','None':'None' }       
	units=models.CharField(max_length=15, choices=[(key,value) for key,value in choices.items()]  )

	def __str__(self):
		return str(self.units)

PerfFeats=['FutMNRtQt','FutMNRtHf','FutMNRtAn','PastMNRtQt','PastMNRtHf','PastMNRtAn','FutMXRtQt','FutMXRtHf','FutMXRtAn','PastMXRtQt','PastMXRtHf','PastMXRtAn' ]
FutPerfFeats=[ ['FutMNRtQt','FutMXRtQt'],['FutMNRtHf','FutMXRtHf'],['FutMNRtAn','FutMXRtAn'] ]
PastPerfFeats=[ ['PastMNRtQt','PastMXRtQt'],['PastMNRtHf','PastMXRtHf'],['PastMNRtAn','PastMXRtAn'] ]


class GeneralFeature(models.Model):
	alphanumeric = RegexValidator(r'^[a-zA-Z][_0-9a-zA-Z]*$', 'Should Begin with alphabet and alphanumeric characters or "_" are allowed later on.')
	user = models.ForeignKey(User,on_delete=models.CASCADE)
	code =models.TextField( null=True)
	name =models.CharField(max_length=50,null=True, validators=[alphanumeric])
	
	operators= models.ManyToManyField(FeatureOperator) 
	units=models.ManyToManyField( FeatureUnit)

	group =models.CharField(max_length=50,null=True)
	description =models.CharField(max_length=200,null=True)

	created_at = models.DateTimeField(auto_now_add=True,null=True)
	updated_at = models.DateTimeField(auto_now=True,null=True)

	def __str__(self):
		return str(self.user)+ ' : '  + str(self.name)+ ' : '  + str(self.group)




class CombinesFeaturesEntry(models.Model):
	window=models.DecimalField(max_digits=4,decimal_places=0,null=True,blank=True)
	T= models.DateField(null=False)
	Symbol=models.ForeignKey(stkmd.Stock, on_delete=models.CASCADE)
	Interval = models.CharField(max_length=1, choices=chrtmd.intervals)

	def __str__(self):
		return str(self.Symbol)+ ' : ' +str(self.T)+ ' : '  + str(self.window)+ ' : '  + str(self.Interval)


class GeneralFeatureValue(models.Model):
	gfeatentry=models.ForeignKey(CombinesFeaturesEntry, on_delete=models.CASCADE,db_index=True)
	gfeature=models.ForeignKey(GeneralFeature, on_delete=models.CASCADE,db_index=True)
	value=models.DecimalField(max_digits=5,decimal_places=2,null=True,blank=True,db_index=True)

	def __str__(self):
		return str(self.gfeatentry)+ ' : '  + str(self.value)



class WatchlistPerf(models.Model):
	T= models.DateField(null=False)
	watchlist=models.ForeignKey(stkmd.Watchlist, on_delete=models.CASCADE)

	
	PastMNRtAn_per20=models.DecimalField(max_digits=3,decimal_places=0,null=True,blank=True)
	PastMNRtAn_per50=models.DecimalField(max_digits=3,decimal_places=0,null=True,blank=True)
	PastMNRtAn_per80=models.DecimalField(max_digits=3,decimal_places=0,null=True,blank=True)
	PastMNRtHf_per20=models.DecimalField(max_digits=3,decimal_places=0,null=True,blank=True)
	PastMNRtHf_per50=models.DecimalField(max_digits=3,decimal_places=0,null=True,blank=True)
	PastMNRtHf_per80=models.DecimalField(max_digits=3,decimal_places=0,null=True,blank=True)
	PastMNRtQt_per20=models.DecimalField(max_digits=3,decimal_places=0,null=True,blank=True)
	PastMNRtQt_per50=models.DecimalField(max_digits=3,decimal_places=0,null=True,blank=True)
	PastMNRtQt_per80=models.DecimalField(max_digits=3,decimal_places=0,null=True,blank=True)
	PastMXRtAn_per20=models.DecimalField(max_digits=3,decimal_places=0,null=True,blank=True)
	PastMXRtAn_per50=models.DecimalField(max_digits=3,decimal_places=0,null=True,blank=True)
	PastMXRtAn_per80=models.DecimalField(max_digits=3,decimal_places=0,null=True,blank=True)
	PastMXRtHf_per20=models.DecimalField(max_digits=3,decimal_places=0,null=True,blank=True)
	PastMXRtHf_per50=models.DecimalField(max_digits=3,decimal_places=0,null=True,blank=True)
	PastMXRtHf_per80=models.DecimalField(max_digits=3,decimal_places=0,null=True,blank=True)
	PastMXRtQt_per20=models.DecimalField(max_digits=3,decimal_places=0,null=True,blank=True)
	PastMXRtQt_per50=models.DecimalField(max_digits=3,decimal_places=0,null=True,blank=True)
	PastMXRtQt_per80=models.DecimalField(max_digits=3,decimal_places=0,null=True,blank=True)

	def __str__(self):
		return str(self.watchlist)+ ' : ' +str(self.T)
