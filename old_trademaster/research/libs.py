from __future__ import division
from django.template import Context, Template
import copy
import stockdata.models as stkmd
from . import models as md
import pandas as pd
from django.utils.safestring import mark_safe
import logging
logger = logging.getLogger(__name__)
import numpy as np
from django.db import connection
from memory_profiler import profile
from django.db.models import Q
import pdb
import gc
from sqlalchemy import create_engine
from django.conf import settings

def per20(x):
	return np.percentile(x,20)
def per50(x):
	return np.percentile(x,50)
def per80(x):
	return np.percentile(x,80)



def render_tag(Catlist,pk,T,user,window,Symbol,Interval):
	CC=list(Catlist)
	for ci in range(len(CC)):
		if md.Grading.objects.filter(Category__pk=CC[ci]['id'],user=user,T=T,window=window,Symbol=stkmd.Stock.objects.get(Symbol=Symbol),Interval=Interval).exists()==True:
			CC[ci]['checked']=True
		else:
			CC[ci]['checked']=False


	Categories=copy.deepcopy(CC)

	tt=Template("""
		<form id="form_{{pk}}" action="" method="post">
			<div id="disp_{{pk}}"></div>
			<div style="width:300px;height:300px;overflow-x:scroll ; overflow-y: scroll;" >
				<input type="hidden" name="Symbol" value={{Symbol}}>
				<input type="hidden" name="window" value={{window}}>
				<input type="hidden" name="Interval" value={{Interval}}>
				<input type="hidden" name="T" value={{T|date:"c"}}>
				<table border=1 style=" text-align: left;border: 1px solid black;border-collapse: collapse;">
				{% for meta in Categories %}
					<tr>
					{% if meta.checked %}
						{% if meta.gencat %}
							<td> <input type="checkbox" name="cat{{meta.id}}" value="1" checked> </td>  <td><font color="blue"> {{meta.name}} </font> </td>
						{% else %}
							<td> <input type="checkbox" name="cat{{meta.id}}" value="1" checked> </td>  <td> {{meta.name}}  </td>
						{% endif %}
					{% else %}
						{% if meta.gencat %}
							<td> <input type="checkbox" name="cat{{meta.id}}" value="1"> </td>          <td><font color="blue"> {{meta.name}}  </font></td>
						{% else %}
							<td> <input type="checkbox" name="cat{{meta.id}}" value="1"> </td>          <td> {{meta.name}}  </td>
						{% endif %}
					{% endif %}
					</tr>
				{% endfor %}
				</table>
				<p align="center"> <input onclick="submittagfunc('form_{{record.pk}}','disp_{{record.pk}}')" type="button" name="tag_submit" value="Submit" /> </p>
			</div>
		</form>

	""")
	return tt.render(Context({"pk":pk,
								'T':T,
								'user':user,
								'window':window,
								'Symbol':Symbol,
								'Interval':Interval, 
								"Categories":Categories }))


# #Fpk# is form pk
# #Symbol#
# #window#
# #Interval#
# #T# 2001-1-1
def render_tag_str(Cats,GG,row,user):


	tt="""
		<form id="form_#Fpk#" action="" method="post">
			<div id="disp_#Fpk#"></div>
			<div style="width:300px;height:300px;overflow-x:scroll ; overflow-y: scroll;" >
				<input type="hidden" name="Symbol" value=#Symbol#>
				<input type="hidden" name="window" value=#window#>
				<input type="hidden" name="Interval" value=#Interval#>
				<input type="hidden" name="user" value=#user#>
				<input type="hidden" name="T" value=#T#>

				<table border=1 style=" text-align: left;border: 1px solid black;border-collapse: collapse;">
	""".replace('#user#',user.username).replace('#Symbol#',row['Symbol']).replace('#window#',str(row['window']) ).replace('#Interval#',row['Interval']).replace('#Fpk#',str(row['No']) ).replace('#T#',row['T'].strftime("%Y-%m-%d") )
	
	# pdb.set_trace()

	for cc in Cats:
		ss="<tr>\n"
		gg=GG.filter(Category=cc,Symbol__Symbol=row['Symbol'],T=row['T'],Interval=row['Interval'],window=row['window']  )
		if gg.count()>0:
			for ch in md.GradingChoices:
				if gg[0].Grade==ch[0]:
					ss=ss+'<td>' +str(ch[0])+'<input type="checkbox" name="cat'+str(cc.pk)+'" value="'+ str(ch[0])+'" checked> </td>  '
				else:
					ss=ss+'<td>' +str(ch[0])+'<input type="checkbox" name="cat'+str(cc.pk)+'" value="'+ str(ch[0])+'" > </td>  '
		else:
			for ch in md.GradingChoices:
				ss=ss+'<td>' +str(ch[0])+'<input type="checkbox" name="cat'+str(cc.pk)+'" value="'+ str(ch[0])+'" > </td>  '
		ss=ss+	'<td><font color="blue"> '+ cc.name+' </font> </td>\n'
		ss=ss+'</tr>'

		tt=tt+ss
	tt=tt+"""
				</table>

				<p align="center"> <input onclick="submittagfunc('form_#Fpk#','disp_#Fpk#')" type="button" name="tag_submit" value="Submit" /> </p>
			</div>
		</form></script>




	""".replace('#user#',user.username).replace('#Symbol#',row['Symbol']).replace('#window#',str(row['window']) ).replace('#Interval#',row['Interval']).replace('#Fpk#',str(row['No']) ).replace('#T#',row['T'].strftime("%Y-%m-%d") )
	return mark_safe(tt.replace('\n','').replace('\t',''))


def render_tag_str_fast(dfCats,dfGG,row,username):


	tt="""
		<form id="form_#Fpk#" action="" method="post">
			<div id="disp_#Fpk#"></div>
			<div style="width:300px;height:300px;overflow-x:scroll ; overflow-y: scroll;" >
				<input type="hidden" name="Symbol" value=#Symbol#>
				<input type="hidden" name="window" value=#window#>
				<input type="hidden" name="Interval" value=#Interval#>
				<input type="hidden" name="user" value=#user#>
				<input type="hidden" name="T" value=#T#>

				<table border=1 style=" text-align: left;border: 1px solid black;border-collapse: collapse;">
	""".replace('#user#',username).replace('#Symbol#',row['Symbol']).replace('#window#',str(row['window']) ).replace('#Interval#',row['Interval']).replace('#Fpk#',str(row['No']) ).replace('#T#',row['T'].strftime("%Y-%m-%d") )
	
	# pdb.set_trace()

	for ind in dfCats.index:
		ss="<tr>\n"
		# gg=GG.filter(Category=cc,Symbol__Symbol=row['Symbol'],T=row['T'],Interval=row['Interval'],window=row['window']  )
		gg=dfGG[(dfGG['Symbol__Symbol']==row['Symbol']) & (dfGG['Category__pk']==dfCats.loc[ind,'pk']) & (dfGG['T']==row['T']) & (dfGG['Interval']==row['Interval']) & (dfGG['window']==row['window'])]
		if len(gg)>0:
			for ch in md.GradingChoices:
				if gg.iloc[0]['Grade']==ch[0]:
					ss=ss+'<td>' +str(ch[0])+'<input type="checkbox" name="cat'+str(dfCats.loc[ind,'pk'])+'" value="'+ str(ch[0])+'" checked> </td>  '
				else:
					ss=ss+'<td>' +str(ch[0])+'<input type="checkbox" name="cat'+str(dfCats.loc[ind,'pk'])+'" value="'+ str(ch[0])+'" > </td>  '
		else:
			for ch in md.GradingChoices:
				ss=ss+'<td>' +str(ch[0])+'<input type="checkbox" name="cat'+str(dfCats.loc[ind,'pk'])+'" value="'+ str(ch[0])+'" > </td>  '
		ss=ss+	'<td><font color="blue"> '+ dfCats.loc[ind,'name']+' </font> </td>\n'
		ss=ss+'</tr>'

		tt=tt+ss
	tt=tt+"""
				</table>

				<p align="center"> <input onclick="submittagfunc('form_#Fpk#','disp_#Fpk#')" type="button" name="tag_submit" value="Submit" /> </p>
			</div>
		</form></script>




	""".replace('#user#',username).replace('#Symbol#',row['Symbol']).replace('#window#',str(row['window']) ).replace('#Interval#',row['Interval']).replace('#Fpk#',str(row['No']) ).replace('#T#',row['T'].strftime("%Y-%m-%d") )
	return mark_safe(tt.replace('\n','').replace('\t',''))





def GenrateAdvanced_Filter_Colm_Options(user):
	genfeats=md.GeneralFeature.objects.filter(user__username='@general@')
	if str(user)!='@general@':
		userfeats=md.GeneralFeature.objects.filter(user=user)
	else:
		userfeats=[]


	GroupOptions=[{'value':'None',"text":'Select','connectedto':[]}]+[{'value':grp,"text":'(G) '+grp,'connectedto':[]} for grp in genfeats.values_list('group',flat=True).distinct()]+[{'value':grp,"text":grp,'connectedto':[]} for grp in userfeats.values_list('group',flat=True).distinct()]
	FeatOptions=[{'value':'None',"text":'Select','connectedto':[]}]+[{'value':str(ss.pk)+'^'+ss.name,"text":'(G) '+ss.name,'connectedto':[ss.group]} for ss in genfeats]+[{'value':str(ss.pk)+'^'+ss.name,"text":ss.name,'connectedto':[ss.group]} for ss in userfeats]

	FeatExtraInput=["corsymb"]
	commusers=list(set(['@general@',str(user)]))

	OperatorOptions=[{'value':'None',"text":'Select','connectedto':['None']}]
	for op in md.FeatureOperator.objects.all():
		cnt=[]
		GFs=md.GeneralFeature.objects.filter(user__username__in=commusers,operators=op) 
		for gf in GFs:
			cnt.append(str(gf.pk)+'^'+gf.name)
		OperatorOptions.append( {'value': op.operators, 'text': op.choices[op.operators],'connectedto':cnt} )

	UnitOptions=[{'value':'None',"text":'Select','connectedto':['None']}]
	for un in md.FeatureUnit.objects.all():
		cnt=[]
		GFs=md.GeneralFeature.objects.filter(user__username__in=commusers,units=un) 
		for gf in GFs:
			cnt.append(str(gf.pk)+'^'+gf.name)
		UnitOptions.append(  {'value': un.units, 'text': un.choices[un.units],'connectedto':cnt} )

	

	

	GroupColm=GroupOptions+[{'value':'Charts',"text":'Charts','connectedto':[]}]

	FeatColm=FeatOptions+[  {'value':'^Chart1y',"text":'1y Chart','connectedto':['Charts']},
							{'value':'^Chart6m',"text":'6m Chart','connectedto':['Charts']},
							{'value':'^Chart1y6m',"text":'1y Chart+6m','connectedto':['Charts']}]
 
	return {'GroupOptions':GroupOptions,
			'FeatOptions': FeatOptions,
			'FeatExtraInput': FeatExtraInput, 
			'FeatExtraInput': FeatExtraInput, 
			'OperatorOptions': OperatorOptions,
			'UnitOptions': UnitOptions,
			'GroupColm':GroupColm,
			'FeatColm':FeatColm}


def GetHistoricalQueryTdate(T,T0):
	if T==T0:
		TT=[T]
	else:
		S=pd.date_range(T0, T, freq='W-MON')
		TT=[]
		for t in S:
			TT.append(t.date())
		if T not in TT:
			TT.append(T)

	return TT


# query always starts on window feature objects  GeneralFeatureValue
def SQLquery_Q(Q,filjson,window):
	# stkmd.Stock.objects.get(Symbol='TSLA')
	SQLquery_sts=filjson
	for qp in SQLquery_sts:
		featid=qp[1].split('^')[0]
		extrainput=qp[2]
		opt=qp[3]
		val=qp[4]
		unit=qp[5]
		# change the val to number of candles unit 
		if unit=='%_window':
			val= str( int( ( int(val)/100) * int(window)  )  )

		Q=eval('Q.filter(generalfeaturevalue__gfeature__pk='+featid+',generalfeaturevalue__value__'+opt+'='+val+')')     
	
	return Q

# query always starts on window feature objects  GeneralFeatureValue
def SQLquery_Q_fast(QQ,QCMF,filjson,window):
	# stkmd.Stock.objects.get(Symbol='TSLA')
	# feat_len=GeneralFeature.objects.get(name='CNDLS')
	SQLquery_sts=filjson
	# QCMF=set( CombinesFeaturesEntry.objects.values_list('pk',flat=True) )
	# QCMF=set( range(CombinesFeaturesEntry.objects.all().count()+5) )
	# QCMF=set( Q.values_list("gfeatentry__pk",flat=True) )
	for qp in SQLquery_sts:
		featid=qp[1].split('^')[0]
		extrainput=qp[2]
		opt=qp[3]
		val=qp[4]
		unit=qp[5]
		# change the val to number of candles unit 
		if unit=='%_window':
			val= str( int( ( int(val)/100) * int(window)  )  )

		# pdb.set_trace()	
		L=eval('QQ.filter(gfeature_id='+featid+',value__'+opt+'='+val+').values_list("gfeatentry_id",flat=True).distinct("gfeatentry_id")') 
		# if len(L)>0:
		QCMF=QCMF& set( L  )
	
	QCMF=list( QCMF )
	if len(QCMF)>0:
		QQ=QQ.filter(gfeatentry_id__in=QCMF)
	
	return QQ,QCMF


# query always starts on window feature objects  GeneralFeatureValue
def SQLquery_Q_rawsql(GFV,CFE,GF,filjson,window):
	CFE_pk=list(CFE.values_list('pk',flat=True))
	if filjson!=None and len(filjson)!=0:
		SQLquery_sts=filjson
		FF=[]
		for qp in SQLquery_sts:
			featid=qp[1].split('^')[0]
			extrainput=qp[2]
			opt=md.FeatureOperator.choices_sql[ qp[3] ] 
			val=qp[4]
			unit=qp[5]
			# change the val to number of candles unit 
			if unit=='%_window':
				val= str( int( ( int(val)/100) * int(window)  )  )

			FF.append('( SELECT gfeatentry_id FROM research_generalfeaturevalue WHERE (gfeature_id = '+featid+' and value '+opt+' '+val+') )')

		FF=" INTERSECT ".join(FF)
		FF='( '+FF+' )'
		# pdb.set_trace()
		if len(CFE_pk)==1:
			FF='SELECT gfeatentry_id,gfeature_id,value FROM research_generalfeaturevalue WHERE ((gfeatentry_id IN '+FF+') and (gfeatentry_id = '+str(CFE_pk[0])+'))'
		else:
			FF='SELECT gfeatentry_id,gfeature_id,value FROM research_generalfeaturevalue WHERE ((gfeatentry_id IN '+FF+') and (gfeatentry_id IN '+str(tuple(CFE_pk))+'))'
		# pdb.set_trace()
		dfv=pd.read_sql(FF,connection)
	else:
		if len(CFE_pk)==1:
			FF='SELECT gfeatentry_id,gfeature_id,value FROM research_generalfeaturevalue WHERE gfeatentry_id = '+str(CFE_pk[0])
		else:
			FF='SELECT gfeatentry_id,gfeature_id,value FROM research_generalfeaturevalue WHERE gfeatentry_id IN '+str(tuple(CFE_pk))
		dfv=pd.read_sql(FF,connection)


	if dfv.empty:
		return pd.DataFrame()

	dfv['gfeature_id']=dfv['gfeature_id'].astype(int)
	dfv['gfeatentry_id']=dfv['gfeatentry_id'].astype(int)
	dfv['value']=dfv['value'].astype(float)

	CFE_pk=dfv['gfeatentry_id'].tolist()
	
	dfcf=pd.DataFrame(list( CFE.filter(pk__in=CFE_pk).values('pk','T','window','Interval',
																 'Symbol__Symbol',
																'Symbol__Sector',
																'Symbol__Industry') )).rename(columns={'pk':'gfeatentry_id',
																										'Symbol__Symbol':'Symbol',
																										'Symbol__Sector':'Sector',
																										'Symbol__Industry':'Industry'})
	if dfcf.empty:
		return pd.DataFrame()
	dfcf['T']=dfcf['T'].astype(pd.datetime)
	dfcf['T']=dfcf['T'].apply(lambda x: pd.to_datetime(x,format="%Y-%m-%d").date())
	dfcf['gfeatentry_id']=dfcf['gfeatentry_id'].astype(int)
	dfcf['window']=dfcf['window'].astype(int)
	dfcf['Symbol']=dfcf['Symbol'].astype(str)
	dfcf['Interval']=dfcf['Interval'].astype(str)
	dfcf['Sector']=dfcf['Sector'].astype(str)
	dfcf['Industry']=dfcf['Industry'].astype(str)
	dfcf.index=range(len(dfcf))

	# get all the feature values
	

	dfgf=pd.DataFrame(list( GF.values('pk','name') )).rename(columns={'pk':'gfeature_id'})
	dfgf['gfeature_id']=dfgf['gfeature_id'].astype(int)
	dfgf['name']=dfgf['name'].astype(str)


	# pdb.set_trace()

	dd=pd.merge(dfv,dfgf,how='left',on=['gfeature_id'])
	dd.drop('gfeature_id',axis=1,inplace=True)

	dc=pd.merge(dd,dfcf,how='left',on=['gfeatentry_id'])
	dc.drop('gfeatentry_id',axis=1,inplace=True)

	df=pd.pivot_table(dc,index=['T','Symbol','window','Interval','Industry','Sector'],
			  columns='name',values='value',aggfunc=np.max).reset_index()

	df=df.round(decimals=2)
	df.index=range(len(df))

	del dfcf
	del dfv
	del dfgf
	del dd
	del dc
	gc.collect()

	return df






class MasterFeatureTableManager():
	def __init__(self):
		dbname=settings.DATABASES['default']['NAME']
		username=settings.DATABASES['default']['USER']
		password=settings.DATABASES['default']['PASSWORD']
		host=settings.DATABASES['default']['HOST']
		ss='postgresql://#username#:#password#@#host#:5432/#dbname#'
		ss=ss.replace('#username#',username)
		ss=ss.replace('#password#',password)
		ss=ss.replace('#host#',host)
		ss=ss.replace('#dbname#',dbname)
		self.engine = create_engine(ss)
		self.tbname='research_mastercombinedentry'

		sql="SELECT EXISTS(SELECT * FROM information_schema.tables WHERE table_schema = 'public' AND table_name = '"+self.tbname+"');"
		df=pd.read_sql(sql,self.engine)
		self.TableExists=df.iloc[0]['exists']

	def updatetable(self,dfupload):
		dfupload.index=range(len(dfupload))

		if self.TableExists==False:
			dfupload.to_sql(self.tbname,self.engine,if_exists='append',index=False,chunksize=10000)
			return True
		else:
			cols=list(dfupload.columns)
			colexists=self.GetColumns()
			

			if set(cols)==set(colexists):
				print "colms are the same so do nothing"
			elif len(set(cols)-set(colexists))>0:
				print "input dataframe has additional colmns ......adding them"
				newcols=list( set(cols)-set(colexists) )
				for colname in newcols:
					coltype=self.GetPostgresColType(dfupload,colname)
					self.AddColumn(colname,coltype)
					print "added column : "+colname+" with coltype : "+coltype
			elif len(set(colexists)-set(cols))>0:
				print "there are more columns in the database table.... so adding them to the dataframe"
				newcols=list( set(colexists)-set(cols) )
				for colname in newcols:
					dfupload[colname]=np.nan
					print "added column : "+colname+" to dataframe "

			else:
				print "This case is impossible"

			

			dfindexexist=self.GetIndex()
			dfupload['index']=dfupload['T'].apply(lambda x: x.strftime("%Y-%m-%d"))+'_'+dfupload['Symbol']+'_'+dfupload['window'].astype(str)+'_'+dfupload['Interval']

			newindex=list(set(dfupload['index'].tolist())-set(dfindexexist['index'].tolist()))
			dfupload_new=dfupload[dfupload['index'].isin(newindex)]
			dfupload_old=dfupload[~dfupload['index'].isin(newindex)]

			if dfupload_new.empty:
				print "No new entries"
			else:
				print "pushing up the new entries"
				dfupload_new.drop('index', axis=1, inplace=True)
				dfupload_new.to_sql(self.tbname,self.engine,if_exists='append',index=False,chunksize=10000)

			if dfupload_old.empty:
				print "No old entries "
			else:
				print "Updating the existing entries ...done by first pulling all the old data into memory"
				oldindex=dfupload_old['index'].tolist()
				dfold=self.GetQuery_INDEX(oldindex)
				dfold['index']=dfold['T'].apply(lambda x: x.strftime("%Y-%m-%d"))+'_'+dfold['Symbol']+'_'+dfold['window'].astype(str)+'_'+dfold['Interval']
				
				dfold=dfold[ sorted(dfold.columns) ]
				dfupload_old=dfupload_old[ sorted(dfupload_old.columns) ]

				dfold.sort_values(by=['index'],inplace=True)
				dfupload_old.sort_values(by=['index'],inplace=True)
				
				dfold.index=range(len(dfold))
				dfupload_old.index=range(len(dfupload_old))
				

				for cc in dfupload_old.columns:
					dfold[cc]=dfold[cc].astype( dfupload_old[cc].dtype )

				# pdb.set_trace()

				if dfold.shape!=dfupload_old.shape:
					print "Something wrong... shapes do not match"
					return False

				if dfold.equals(dfupload_old)==True:
					print 'old data looks the same as new data... no update required for old data'
					return True
				else:
					print " if new data has nans... do not update that entry"
					for ind in dfold.index:
						for cc in dfold.columns:
							if dfupload_old.loc[ind,cc] is not None and pd.isnull(dfupload_old.loc[ind,cc])==False:
								 dfold.loc[ind,cc]=dfupload_old.loc[ind,cc]

					# pdb.set_trace()

					self.DeleteQuery_INDEX(oldindex)
					dfold.drop('index', axis=1, inplace=True)
					dfold.to_sql(self.tbname,self.engine,if_exists='append',index=False,chunksize=10000)
					print "done old data update"




	def GetPostgresColType(self,df,colname):
		import collections
		import datetime
		dfcoltype=list(df[colname].apply(lambda x: type(x)))
		counter=dict(collections.Counter(dfcoltype))
		m=-1
		ky=-1
		for key,value in counter.items():
			if value>m:
				ky=key
				m=value
		if ky==pd.datetime or ky==datetime.datetime or ky==datetime.datetime.date or ky == type(pd.datetime(2015,1,1)) or ky == type(pd.datetime(2015,1,1).date()):
			return 'date'
		elif ky==str or ky==unicode:
			n=max(list(df[colname].apply(lambda x: len(x))))
			return 'varchar('+str(2*n)+')'
		elif ky==int:
			return 'integer'
		elif ky==float:
			return 'decimal'
		else:
			return 'decimal'
	def AddColumn(self,colname,coltype):
		sql='ALTER TABLE '+self.tbname+' ADD "'+str(colname)+'" '+coltype+';'
		df=pd.read_sql(sql,self.engine)
		return df

	def GetQuery(self,sql):
		if self.TableExists==False:
			return pd.DataFrame()

		df=pd.read_sql(sql,self.engine)
		return df
	
	def GetAlldata(self,LIMIT=None):
		if self.TableExists==False:
			return pd.DataFrame()
		if LIMIT==None:
			sql='SELECT * FROM '+self.tbname+';'
		else:
			sql='SELECT * FROM '+self.tbname+' LIMIT '+str(LIMIT)+';'

		df=pd.read_sql(sql,self.engine)
		return df

	def GetQuery_T(self,T):
		if self.TableExists==False:
			return pd.DataFrame()
		Tstr=T.strftime("%Y-%m-%d")
		sql='SELECT * FROM '+self.tbname+' where "T"::date=\''+Tstr+'\' ;'
		df=pd.read_sql(sql,self.engine)
		return df

	def GetQuery_INDEX(self,INDEXlist):
		if self.TableExists==False:
			return pd.DataFrame()
		INDEXlist=[str(ss) for ss in INDEXlist]

		sql='SELECT  FROM '+self.tbname
		if len(INDEXlist)==0:
			return pd.DataFrame()
		elif len(INDEXlist)==1:
			sql='SELECT * FROM '+self.tbname+' where ("T"::text || \'_\' || "Symbol"::text || \'_\' || "window"::text || \'_\' || "Interval"::text = \''+ str(INDEXlist[0])+'\');'
		else:
			sql='SELECT *FROM '+self.tbname+' where ("T"::text || \'_\' || "Symbol"::text || \'_\' || "window"::text || \'_\' || "Interval"::text IN '+ str(tuple(INDEXlist))+');'
		df=pd.read_sql(sql,self.engine)
		return df

	def DeleteQuery_INDEX(self,INDEXlist):
		if self.TableExists==False:
			return pd.DataFrame()
		
		INDEXlist=[str(ss) for ss in INDEXlist]

		if len(INDEXlist)==0:
			return pd.DataFrame()
		elif len(INDEXlist)==1:
			sql='DELETE FROM '+self.tbname+' where ("T"::text || \'_\' || "Symbol"::text || \'_\' || "window"::text || \'_\' || "Interval"::text = \''+ str(INDEXlist[0])+'\');'
		else:
			sql='DELETE FROM '+self.tbname+' where ("T"::text || \'_\' || "Symbol"::text || \'_\' || "window"::text || \'_\' || "Interval"::text IN '+ str(tuple(INDEXlist))+');'
		# df=pd.read_sql(sql,self.engine)
		cursor=self.engine.connect()
		cursor.execute(sql)
		cursor.close()
		return True

	def GetColumns(self):
		if self.TableExists==False:
			return []
		sql='SELECT * FROM '+self.tbname+' LIMIT 10;'
		df=pd.read_sql(sql,self.engine)
		return list(df.columns)

	def DeleteTable(self):
		if self.TableExists==False:
			return True
		sql='DROP TABLE '+self.tbname+';'
		cursor=self.engine.connect()
		cursor.execute(sql)
		cursor.close()
		# df=pd.read_sql(sql,self.engine)
		return True


	def GetIndex(self):
		if self.TableExists==False:
			return None
		sql='SELECT "T"::text || \'_\' || "Symbol"::text || \'_\' || "window"::text || \'_\' || "Interval"::text AS INDEX FROM '+self.tbname+' ;'
		df=pd.read_sql(sql,self.engine)
		return df
		

	def CheckIfTableExists(self):
		sql="SELECT EXISTS(SELECT * FROM information_schema.tables WHERE table_schema = 'public' AND table_name = '"+self.tbname+"');"
		df=pd.read_sql(sql,self.engine)
		self.TableExists=df.iloc[0]['exists']
		return self.TableExists

	def GetSummarybyDate(self):
		sql="""SELECT 'SELECT "T" AS "Tdate", ' || string_agg('count(' || quote_ident(attname) || ')' || ' AS ' || quote_ident(attname), ', ')
		    || 'FROM '   || attrelid::regclass || ' GROUP BY "T"'
		FROM   pg_attribute
		WHERE  attrelid = 'research_mastercombinedentry'::regclass
		AND    attnum  >= 1           -- exclude tableoid & friends (neg. attnum)
		AND    attisdropped is FALSE  -- exclude deleted columns
		GROUP  BY attrelid;"""
		df=self.GetQuery(sql)
		sql=df[df.columns[0]].iloc[0]
		df=self.GetQuery(sql)
		df.sort_values(by=['Tdate'],inplace=True)
		df.index=range(len(df))
		df.drop('T',axis=1,inplace=True)
		df.rename(columns={'Tdate':'T'},inplace=True)
		return df

# query always starts on window feature objects  GeneralFeatureValue
def SQLquery_Q_master(CFE_fil,filjson,window):
	MFT=MasterFeatureTableManager()
	# sql='SELECT "T"::text || \'_\' || "Symbol"::text || \'_\' || "window"::text || \'_\' || "Interval"::text AS INDEX FROM research_combinesfeaturesentry ;'
	# CFE_index=pd.read_sql(sql,connection)
	# CFE_index=CFE_index['index'].tolist()
	# CFE_index=pd.DataFrame(list(CFE.values('T','Symbol__Symbol','window','Interval')))
	# CFE_index['index']=CFE_index['T'].apply(lambda x: x.strftime("%Y-%m-%d"))+'_'+CFE_index['Symbol__Symbol']+'_'+CFE_index['window'].astype(str)+'_'+CFE_index['Interval']
	# CFE_index=[str(ss) for ss in CFE_index['index']]
	if filjson!=None and len(filjson)!=0:
		SQLquery_sts=filjson
		FF=[]
		for qp in SQLquery_sts:
			featid=qp[1].split('^')[0]
			featname=md.GeneralFeature.objects.get(pk=int(featid)).name
			extrainput=qp[2]
			opt=md.FeatureOperator.choices_sql[ qp[3] ] 
			val=qp[4]
			unit=qp[5]
			# change the val to number of candles unit 
			if unit=='%_window':
				val= str( int( ( int(val)/100) * int(window)  )  )

			FF.append('"'+featname+'"' +' '+opt+' '+val)
		# if len(CFE_index)==0:
		# 	pass
		# elif len(CFE_index)==1:
		# 	FF.append('"T"::text || \'_\' || "Symbol"::text || \'_\' || "window"::text || \'_\' || "Interval"::text = '+str(CFE_index[0]))
		# else:
		# 	FF.append('"T"::text || \'_\' || "Symbol"::text || \'_\' || "window"::text || \'_\' || "Interval"::text IN '+str(tuple(CFE_index)))
		# pdb.set_trace()
		F2=FF+CFE_fil
		F3=[str(ff) for ff in F2]
		F4=" and ".join(F3)
		F5='SELECT * FROM '+MFT.tbname+' WHERE ( '+F4+' );'
		df=MFT.GetQuery(F5)
	else:
		FF=[]

		F2=CFE_fil
		F3=[str(ff) for ff in F2]
		F4=" and ".join(F3)
		F5='SELECT * FROM '+MFT.tbname+' WHERE ( '+F4+' );'
		df=MFT.GetQuery(F5)

		# if len(FF)>0:
		# 	FF=str(FF)
		# 	FF='SELECT * FROM '+MFT.tbname+' WHERE ( '+FF+' );'
		# 	df=MFT.GetQuery(FF)
		# else:
		# 	FF='SELECT * FROM '+MFT.tbname+';'
		# 	df=MFT.GetQuery(FF)


	return df





def ComputeStatus(onT=pd.datetime.today().date(),TT=[]):
	if md.ComputeStatusDF.objects.filter(DFname='ComputeStatus',T=onT).exists():	
		CSDF=md.ComputeStatusDF.objects.get(DFname='ComputeStatus',T=onT)
	else:
		CSDF=md.ComputeStatusDF(DFname='ComputeStatus',T=onT)


	import stockdata.models as stkmd
	dfstock=pd.DataFrame(list(stkmd.Stock.objects.all().values('LastPriceUpdate','id'))).rename(columns={'LastPriceUpdate':'T'})
	dfstock=dfstock[['id','T']].groupby('T').agg('count').reset_index()
	dfstock.rename(columns={'id':'#Updated Stocks'},inplace=True)

	LT=pd.DataFrame(list(md.LinearTrends.objects.all().values('T','Symbol_id') ))
	dfLinTrend=LT[['T','Symbol_id']].groupby('T').agg('count').reset_index()
	dfLinTrend.rename(columns={'Symbol_id':'#LT'},inplace=True)

	dfALL=pd.merge(dfstock,dfLinTrend,how='outer',on=['T']).round()
	del dfstock
	del dfLinTrend
	del LT

	if len(TT)==0:
		TT=md.CombinesFeaturesEntry.objects.all().values_list('T',flat=True).distinct().order_by('T')
	DD=pd.DataFrame()
	window=360
	Interval='D'
	kk=1
	n=len(TT)
	for T in TT:
		print T,kk,n
		kk=kk+1
		CFE=md.CombinesFeaturesEntry.objects.filter(T=T,window=window,Interval=Interval)
		GF=md.GeneralFeature.objects.all()
		GFV=md.GeneralFeatureValue.objects.all()
		if CFE.count()==0:
			print "No CFE objects for this date = "+T.strftime("%Y-%m-%d")
			continue
		df=SQLquery_Q_rawsql(GFV,CFE,GF,None,window)
		try:
			DD=pd.concat([DD,df])
		except:
			pdb.set_trace()

		del df
		del CFE
		del GF
		del GFV

	DD.index=range(len(DD))
	DD=DD.groupby('T').agg('count').reset_index()

	df=pd.merge(dfALL,DD,how='outer',on=['T']).round()
	del dfALL
	del DD
	dfALL=df

	dfALL.sort_values(by=['T'],inplace=True)


	CSDF.uploadDF(df)
	CSDF.save()


	return df

def MasterQueryUpdate(TT=[],window=360,Interval='D'):
	MFT=MasterFeatureTableManager()
	kk=1
	if len(TT)==0:
		TT=md.CombinesFeaturesEntry.objects.all().values_list('T',flat=True).distinct().order_by('T')

	n=len(TT)
	for T in TT:
		print T,kk,n
		kk=kk+1
		CFE=md.CombinesFeaturesEntry.objects.filter(T=T,window=window,Interval=Interval)
		GF=md.GeneralFeature.objects.all()
		GFV=md.GeneralFeatureValue.objects.all()
		if CFE.count()==0:
			print "No CFE objects for this date = "+T.strftime("%Y-%m-%d")
			continue
		df=SQLquery_Q_rawsql(GFV,CFE,GF,None,window)
		if df.empty:
			print "No SQL_raw query returned for date = "+T.strftime("%Y-%m-%d")
			continue
		MFT.updatetable(df)
		del df


	return df


def ComputeStatus_master(onT=pd.datetime.today().date(),TT=[]):
	MFT=MasterFeatureTableManager()
	if md.ComputeStatusDF.objects.filter(DFname='ComputeStatus',T=onT).exists():	
		CSDF=md.ComputeStatusDF.objects.get(DFname='ComputeStatus',T=onT)
	else:
		CSDF=md.ComputeStatusDF(DFname='ComputeStatus',T=onT)


	import stockdata.models as stkmd
	dfstock=pd.DataFrame(list(stkmd.Stock.objects.all().values('LastPriceUpdate','id'))).rename(columns={'LastPriceUpdate':'T'})
	dfstock=dfstock[['id','T']].groupby('T').agg('count').reset_index()
	dfstock.rename(columns={'id':'#Updated Stocks'},inplace=True)

	LT=pd.DataFrame(list(md.LinearTrends.objects.all().values('T','Symbol_id') ))
	dfLinTrend=LT[['T','Symbol_id']].groupby('T').agg('count').reset_index()
	dfLinTrend.rename(columns={'Symbol_id':'#LT'},inplace=True)

	dfALL=pd.merge(dfstock,dfLinTrend,how='outer',on=['T']).round()
	del dfstock
	del dfLinTrend
	del LT

	if len(TT)==0:
		TT=md.CombinesFeaturesEntry.objects.all().values_list('T',flat=True).distinct().order_by('T')
	DD=pd.DataFrame()
	df=MFT.GetSummarybyDate()
	for T in TT:
		DD=pd.concat([DD,df[df['T']==T]])

	DD.index=range(len(DD))
	del df
	df=pd.merge(dfALL,DD,how='outer',on=['T']).round()
	del dfALL
	del DD
	dfALL=df

	dfALL.sort_values(by=['T'],inplace=True)


	CSDF.uploadDF(df)
	CSDF.save()


	return df