# -*- coding: utf-8 -*-
"""
Created on Fri Jun 20 13:19:46 2014
This code is used to update the stock data of given stock symbols
Pull the required stock data into variable
Highly dependent on pandas

@author: Nagnanamus

Learn: 
    * Pandas
    * Finviz Data Manipulation
    * Plotting data Matplotlib+ Bokeh
    * Analyst recos
    * Downloading data and organizing it
    

"""
from __future__ import division
try:
    from urllib.request import urlopen
except:
    from urllib2 import urlopen

import time
from time import sleep
import os.path
import os
import pandas_datareader.data as web

import datetime
import numpy as np
import pandas as pd
import sys
from . import GenConfig as GC
from . import TableManager as TM  
from . import PlotingManager as pltmag
try:
    import talib
except:
    print 'talib not available'

    
from sqlalchemy import create_engine
import sqlalchemy.types as sqltyp
from sqlalchemy.dialects.mysql import TINYINT,BIGINT,VARCHAR,DATE,DECIMAL,FLOAT,SMALLINT



def chunkinator(l, n):
    """ Yield successive n-sized chunks from l.
    """
    for i in range(0, len(l), n):
        yield l[i:i+n]
     
        
def ImportDailyData(fy,fm,fd,ty,tm,td,symb):
    f = web.DataReader(symb, 'yahoo', datetime.datetime(fy, fm, fd), datetime.datetime(ty, tm, td))
    return f


def AppendVolMAs(df):
    df['VolSMA10']=df.Volume.rolling(window = 10).mean()
    df['VolRel10']=df.Volume/df['VolSMA10']
    
    df['VolSMA20']=df.Volume.rolling(window = 20).mean()
    df['VolRel20']=df.Volume/df['VolSMA20']

    df['VolSTD10']=df.Volume.rolling(window = 10).std()
    df['VolSTD20']=df.Volume.rolling(window = 20).std()
    df['VolEMA10']=df.Volume.ewm(span=10).mean()
    df['VolEMA20']=df.Volume.ewm(span=20).mean()
    
    return df

# SMAs     
def AppendMAs(df):

    df['SMA10']=df.Close.rolling(window = 10).mean()        
    df['SMA20']=df.Close.rolling(window = 20).mean() 
    df['SMA50']=df.Close.rolling(window = 50).mean()               
    df['SMA100']=df.Close.rolling(window = 100).mean()                                   
    df['SMA200']=df.Close.rolling(window = 200).mean()   
    
    return df

def AppendMStd(df):
    
    df['STD10']=df.Close.rolling(window = 10).std()    
    df['STD20']=df.Close.rolling(window = 20).std()
    df['STD50']=df.Close.rolling(window = 50).std()              
    df['STD100']=df.Close.rolling(window = 100).std()                                  
    df['STD200']=df.Close.rolling(window = 200).std() 
    
    return df
    
def AppendEMAs(df):
    df['EMA10']=df.Close.ewm(span=10).mean()
    df['EMA20']=df.Close.ewm(span=20).mean() 
    df['EMA50']=df.Close.ewm(span=50).mean()               
    df['EMA100']=df.Close.ewm(span=100).mean()                                   
    df['EMA200']=df.Close.ewm(span=200).mean()    
    
    return df   


def AppendESTD(df):
    
    df['ESTD10']=df.Close.ewm(span=10).std()    
    df['ESTD20']=df.Close.ewm(span=20).std()
    df['ESTD50']=df.Close.ewm(span=50).std()               
    df['ESTD100']=df.Close.ewm(span=100).std()                                   
    df['ESTD200']=df.Close.ewm(span=200).std()             
    
    return df

def AppendReturns(df):
    
    df['Return']=(df.Close-df.Close.shift(1))/df.Close.shift(1) 
    df['ReturnSMA10']=df.Return.rolling(window = 10).mean()        
    df['ReturnSMA20']=df.Return.rolling(window = 10).mean()
    
    return df


def AppendIndicator_SMAmaxDiff(df):
    df['SMAmaxDiff']=np.zeros(len(df))

    ind=df[ (df['SMA10']> df['SMA20']) & (df['SMA20'] > df['SMA50'])  ].index
    df.loc[ind,'SMAmaxDiff']=df.loc[ind,'SMA10']-df.loc[ind,'SMA20']

    ind=df[ (df['SMA10']> df['SMA50']) & (df['SMA50'] > df['SMA20'])  ].index
    df.loc[ind,'SMAmaxDiff']=df.loc[ind,'SMA10']-df.loc[ind,'SMA50']

    ind=df[ (df['SMA20']> df['SMA10']) & (df['SMA10'] > df['SMA50'])  ].index
    df.loc[ind,'SMAmaxDiff']=df.loc[ind,'SMA20']-df.loc[ind,'SMA50']

    ind=df[ (df['SMA20']> df['SMA50']) & (df['SMA50'] > df['SMA10'])  ].index
    df.loc[ind,'SMAmaxDiff']=-( df.loc[ind,'SMA20']-df.loc[ind,'SMA10'] )

    ind=df[ (df['SMA50']> df['SMA10']) & (df['SMA10'] > df['SMA20'])  ].index
    df.loc[ind,'SMAmaxDiff']=-( df.loc[ind,'SMA50']-df.loc[ind,'SMA20'] )

    ind=df[ (df['SMA50']> df['SMA20']) & (df['SMA20'] > df['SMA10'])  ].index
    df.loc[ind,'SMAmaxDiff']=-( df.loc[ind,'SMA50']-df.loc[ind,'SMA10'] )

    
    return df

def AppendIndicator_AmpSMA10(df):
    df['AmpSMA10']=df.apply(lambda row: (row['Open']+row['Close'])/2-row['SMA10'], axis=1)

    return df

def AppendCandlePatterns(df):
    for ss in GC.CandlePatterns.keys():
        myString = 'talib.'+ss+"(df['Open'].values,df['High'].values,df['Low'].values,df['Close'].values)"
        df[ss]= eval(myString)
        df[ss]=df[ss].astype(int)

    return df
################################################################################################
class StockDataOperations:
    """
    -Class to handle the manipulations of the data
    -Automatically loads the data
    By defaulkt pull daily data: otherwise specify if daily, weekly or monthly
    """
    def __init__(self):
        self.TodayDate=datetime.datetime.today()
        self.t0=datetime.datetime(2002,1,1)

        self.stocks=[]

    def Initialize_Config(self):
    
        configs=GC.GetConfigs()
        #self.StockGroups=pd.HDFStore(PathDict['StockGroups'])['StockGroups']
        tdate=pd.datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)
        flg=0
        if 'Stock_List_Updated_Date' not in configs:
            configs['Stock_List_Updated_Date']='2002-01-01'
            flg=1
        
        self.stocks=self.getstocklist()    
        if pd.datetime.strptime(configs['Stock_List_Updated_Date'], "%Y-%m-%d") < tdate:
            pd.DataFrame(self.stocks).to_csv(GC.PathDict['AllStocksList'],header=False,index=False)
            configs['Stock_List_Updated_Date']=tdate.strftime("%Y-%m-%d")
            flg=1
         
        if 'Stock_Data_Updated_Date' not in configs:
            configs['Stock_Data_Updated_Date']='2002-01-01'
            flg=1

        if pd.datetime.strptime(configs['Stock_Data_Updated_Date'], "%Y-%m-%d") < tdate:    
            df1=self.GetStockData('TSLA')
            df2=self.GetStockData('AAPL')
            self.stocks_data_latest_date=min([max(df1.index),max(df2.index)])
            configs['Stock_Data_Latest_Date']=self.stocks_data_latest_date.strftime("%Y-%m-%d")
            configs['Stock_Data_Updated_Date']=tdate.strftime("%Y-%m-%d")
            flg=1    
        else:
            self.stocks_data_latest_date=pd.datetime.strptime(configs['Stock_Data_Latest_Date'], "%Y-%m-%d")                
            
            
        if flg==1:
            GC.Update_Configs(configs)
            print('Updating Configs')

    def getstocklist(self):
        db = MS.connect(host="127.0.0.1",user=GC.PathDict['mysqluser'], passwd=GC.PathDict['mysqlpass'],db=GC.PathDict['StockData_mysql_dbname'])
        cur=db.cursor()
        cur.execute("SHOW TABLES")
        self.stocks=[ss[0] for ss in cur.fetchall()]
        db.close()
        return self.stocks

    def MeaningFullStocks_forComputation(self):
        S=[]
        for ss in self.stocks:
            DF=self.GetStockData(ss,Fdate=datetime.datetime(2006,1,1))
            if len(ss)>4 or (DF.index[-1]-DF.index[0]).days<750 or len(DF[DF['Close']<3].index)>0.5*len(DF.index) or len(DF[DF['Volume']<5000].index)>0.5*len(DF.index) or  len(DF[DF['Volume']==0].index)>10 or len(DF[DF['Close']==0].index)>10 or len(DF[DF['Close']<=1].index)>10 or self.SanitityStock_Check(stock=ss)==False:
                print(ss+' is below the $3 threshold or 5000 vol threshold or $1 or 0Vol or 0Close or has < 750 days data')
            else:
                S.append(ss)
        return S        
        
    def SanitityStock_Check(self,stock=None,DF=None):

        if stock is not None:
            df=self.GetStockData(stock)
        elif DF is not None:
            df=DF
        else:
            sys.exit('Need To provide a stock or the data for santity check')        
        #check 1:
        df['CD']=df['Close'] - df['Close'].shift(1)
        df['VD']=df['Volume'] - df['Volume'].shift(1)
        if len(df[df['CD']==0])/len(df)>0.1 or len(df[df['VD']==0])/len(df) >0.1:
            print('Failed consecutive difference value test')
            return False
        elif len(df[pd.isnull(df['Close'])])/len(df)>0.05 or len(df[pd.isnull(df['Volume'])])/len(df) >0.05:
            print('NaN test failed')
            return False
        else:
            return True

    def UpdateStockGroups(self):
        StockGroups=pd.read_csv(GC.PathDict['StockGroups'])
        StockGroups.index=range(0,len(StockGroups))        
        for i in StockGroups.index:
            
            time.sleep(1)
            stock=StockGroups.loc[i,'Symbol']
            print([stock,str(i),str(len(StockGroups))])            
            if pd.isnull(StockGroups.loc[i,'Industry']) and pd.isnull(StockGroups.loc[i,'Sector']):             
                Sec,Ind=GetSectorIndustry(stock)
                StockGroups.loc[i,'Sector']=Sec
                StockGroups.loc[i,'Industry']=Ind
            C=GetCompetitors(stock)
            if len(C)>0:
                StockGroups.loc[i,'Competitors']=", ".join(C)
                
        StockGroups.to_csv(GC.PathDict['StockGroups'],index=False)    

            
    def ImportYahooData(self,symb,Fdate,Tdate):
        sleep(0.5)
        return web.DataReader(symb, 'yahoo', Fdate,Tdate)

    def GetStockData(self,symb,Fdate=datetime.datetime(2002,1,1) ,Tdate=datetime.datetime.today(),dbname=None):
        if dbname==None:
            engine = create_engine('mysql+mysqldb://'+GC.PathDict['mysqluser']+':'+GC.PathDict['mysqlpass']+'@127.0.0.1/'+GC.PathDict['StockData_mysql_dbname'])
        else:
            engine = create_engine('sqlite:///'+dbname)

        # store=pd.HDFStore(GC.PathDict['GetStockDataFile'](symb))
        # df=store['Daily'] 
        df=pd.read_sql(symb,engine)
        df.index=df['Date']

        df=AppendMAs(df)
        df=AppendMStd(df)
        df=AppendEMAs(df)
        df=AppendESTD(df)
        df=AppendVolMAs(df)
        df=AppendReturns(df)
        
        # store.close()
        return df[Fdate:Tdate] 
    
    

    def PlotStocks_windows(self,symb,tf,window=360,plotconfig=pltmag.plotconfig_std,plotdeploy=pltmag.plotdeploy_std,dbname=None):
        if type(tf) is str:
            tf=pd.datetime.strptime(tf, '%Y-%m-%d')
            
        t0=GetWindowTfs(tf,window)[0]
        df=self.GetStockData(symb,Fdate=t0 ,Tdate=tf,dbname=dbname) #
        plotconfig[0]['title']= symb+' W:'+str(window)+' S:'+' Tf:'+tf.strftime("%Y-%m-%d")
        pltmag.PlotCandle(df,plotconfig,plotdeploy)
        

    def UpdateData(self,symbs=None,dbname=None):
        if dbname==None:
            engine = create_engine('mysql+mysqldb://'+GC.PathDict['mysqluser']+':'+GC.PathDict['mysqlpass']+'@127.0.0.1/'+GC.PathDict['StockData_mysql_dbname'])
        else:
            engine = create_engine('sqlite:///'+dbname)


        configs=GC.GetConfigs()
        if 'Stock_List_Error' not in configs:        
            configs['Stock_List_Error']=[]
        
        flg=0
        if symbs==None:
            symbs=self.stocks

        if type(symbs) is not list:
            symbs=[symbs]

        for symb in symbs:
            print(symb)
            if symb in self.stocks:
                if symb in configs['Stock_List_Error']:
                    print('Stock is in Stock_List_Error')
                    continue
                
                df=self.GetStockData(symb,self.t0,self.TodayDate)
                
                if self.SanitityStock_Check(DF=df)==True:
                    if (self.TodayDate-df.index[-1]).days>3:
                        f=self.ImportYahooData(symb,df.index[-1],self.TodayDate)
                        
                        if self.SanitityStock_Check(DF=f)==True:                         
                            f,mm=TM.CleanUpDataFrame(f)
                            df.to_sql(symb,engine,flavor='mysql',if_exists='append',index=True,index_label='Date')
                            print('Update in first try')
                        else: #try again
                            f=self.ImportYahooData(symb,df.index[-1],self.TodayDate)
                            
                            if self.SanitityStock_Check(DF=f)==True:
                                f,mm=TM.CleanUpDataFrame(f)
                                df.to_sql(symb,engine,flavor='mysql',if_exists='append',index=True,index_label='Date')
                                print('Updated in Second try')
                            else:
                                print('Sanity check failed to update')
                                configs['Stock_List_Error'].append(symb)
                                flg=1
                    else:
                        print('No need to update as it is already latest')

                else: # replace
                    print('Sanity Check Failed on existing data so replacing')
                    df=self.ImportYahooData(symb,self.t0,self.TodayDate)
                    if self.SanitityStock_Check(DF=df)==True:
                        df.to_sql(symb,engine,flavor='mysql',if_exists='append',index=True,index_label='Date',dtype={'Date':sqltyp.Date,'Open':sqltyp.Float,'Close':sqltyp.Float,'High':sqltyp.Float,'Low':sqltyp.Float,'Adj_Close':sqltyp.Float,'Volume':sqltyp.BigInteger})
                        print('Replaced !!!!')
                    else:
                        #second try
                        df=self.ImportYahooData(symb,self.t0,self.TodayDate)
                        if self.SanitityStock_Check(DF=df)==True:
                            df.to_sql(symb,engine,flavor='mysql',if_exists='append',index=True,index_label='Date',dtype={'Date':sqltyp.Date,'Open':sqltyp.Float,'Close':sqltyp.Float,'High':sqltyp.Float,'Low':sqltyp.Float,'Adj_Close':sqltyp.Float,'Volume':sqltyp.BigInteger})
                            print('Replaced on second try!!!!')
                        else:
                            print('Sanity check failed on the replacement')
                            configs['Stock_List_Error'].append(symb)
                            flg=1
            
            else:
                
                try:
                    df=self.ImportYahooData(symb,self.t0,self.TodayDate)
                    df,mm=TM.CleanUpDataFrame(df)
                    df.to_sql(symb,engine,if_exists='replace',index=True,index_label='Date')
                except:
                    print("Error = "+symb)

                    
            
            
        if flg==1:
            print('Updating Configs')
            GC.Update_Configs(configs)

    #Pulls only daily Data
    def PullDataSymbolsSet(self,symbs):
        #                       year,month,day 
        #symbs eg is {'AAPL':[Fdate,Tdate],'TSLA':[None,Tdate]}        
        df={};  
        for sym in symbs.keys():
            if symbs[sym][0]==None:
                Fdate=self.t0
            if symbs[sym][1]==None:
                Tdate=self.TodayDate
                
            ss=self.GetStockData(self,sym,Fdate ,Tdate)   
            df.update({sym:ss})

        return df                    
        
    def GetFilteredListofStocks(self,pdT0=datetime.datetime(2002,1,1),pdTf=datetime.datetime.today()):
        SS=[]
        for i in range(0,len(self.stocks)) : #len(SymbList.index)
            ss=self.stocks[i]        
            try:
                DF=self.GetStockData(self,ss,pdT0 ,pdTf)   
                if (DF.index[-1]-DF.index[0]).days<750 or len(DF[DF['Close']<3].index)>0.5*len(DF.index) or len(DF[DF['Volume']<5000].index)>0.5*len(DF.index) or  len(DF[DF['Volume']==0].index)>50 or len(DF[DF['Close']==0].index)>50 or len(DF[DF['Close']<=1].index)>50:            
                    print (ss+' is below the $3 threshold or 5000 vol threshold or $1 or 0Vol or 0Close or has < 750 days data')
                else:
                    SS.append(ss)               
            except:
                print ('Something wrong with getting data for '+ss)
        return SS




def GetSectorIndustry(stock):
    try:
        with urlopen('http://finviz.com/quote.ashx?t='+stock,timeout=10) as response:
            html = str(response.read() )
            ss='screener.ashx?v=111&f='
            L=html[html.find(ss):html.find(ss)+200]
            pp='class="tab-link">'
            Sector=L[L.find(pp)+len(pp):L.find('|')]
            Sector=Sector[:Sector.find('</a>')]
            if Sector[0]==' ':
                Sector=Sector[1:]
            if Sector[-1]==' ':
                Sector=Sector[:-1]
                
            LL=L[L.find('|'): ]    
            Industry=LL[LL.find(pp)+len(pp):LL.find('</a>')]
            if Industry[0]==' ':
                Industry=Industry[1:]
            if Sector[-1]==' ':
                Industry=Industry[:-1]    
    except:
        print('Could not get secto and industry from finviz for '+stock)
        Sector=np.nan
        Industry=np.nan
    
    print('SecotIndistry='+str(Sector)+' '+str(Industry))
    return Sector,Industry
        
        
def GetCompetitors(stock):
    try:
        with urlopen('https://finance.yahoo.com/q/co?s='+stock+'+Competitors',timeout=10) as response:
            html = str(response.read() )
            ss='Direct Competitor Comparison'
            L=html[html.find(ss):html.find(ss)+1200]
            n=1        
            while n>0:
                n1=L.find('<')
                n2=L.find('>')
                n=min([n1,n2])
                if n<0:
                    break
                L=L.replace(L[n1:n2+1],' ')
                n=min([n1,n2])
            L=L.replace('&nbsp;','')
            L=L.split(' ')
            L=[pp for pp in L if pp!='']
            L=L[L.index('Comparison')+1: L.index('PVT1') ]
            
    except:
        L=[]
        print('Could not get yahoo competitors for '+stock)
    try:            
        with urlopen('http://www.nasdaq.com/symbol/'+stock.lower()+'/competitors',timeout=10) as response:
            html = str(response.read() )
            ss='<div class="genTable thin">'
            n1=html.find(ss)
            n2=html[n1:].find('</div>')
            tab=html[n1+len(ss):n1+n2]
            tab=tab.replace('\\r',' ').replace('\\n',' ').replace('\r',' ').replace('\r',' ').replace('\t',' ').replace('\\t',' ')
            df=pd.read_html(tab)
            df=df[0]
            for ss in df.columns:
                if 'Company'.lower() in ss.lower():
                    DF=df[ss]
                    break
            S=list(DF)
            for i in range(0,len(S)):
                n1=S[i].find(':')
                S[i]=S[i][:n1]
                for j in reversed(range(0,len(S[i]))):
                    if S[i][j].islower() or S[i][j]=='.':
                        S[i]=S[i][j+1:]
                        break
    except:
        S=[]
        print('Could not get nasdaq competitors for '+stock)
    
    print('Competitors='+str(L+S))            
    return(list(set(L+S)))



