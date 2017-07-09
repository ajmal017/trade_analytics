# -*- coding: utf-8 -*-
"""
Created on Thu Jan 22 14:36:53 2015

@author: nagnanamus

* Extract feautures from windowed data
* Make a new DatFrame with  columns

shiftby, windowlength , WindowEndDate, len(HorzSlope), len(UPslope), No.UpInflectPts,
MaxUpSlope, NoPPVgt2PPV, NoPPVgt3PPV,NoPPVgt4PPV,NoPPVgt5PPV, lenb/nMaxPPV, OCHLratioMaxPPV, 
Close, Volume, Symbol
FutReturnQuart, FutReturnHalf , FutReturnAnnual,  FutMaxReturnQuart 
,  FutMaxReturnHalf ,  FutMaxReturnAnnual , NoGapUps , NoGapDowns, MaxGapUp, 
NoCandleAboveSMA10,NoCandleAboveSMA20,  No10gt20gt50gt100gt200


* Start from the latest date
* windows = 1month, 3month, 6month, 1year, 2 years
* shift by = 5 days (1 week)
* all windows have same reference date (end date as we start from latest date)
"""
from __future__ import division
# from matplotlib import pyplot as plt
import json
import numpy as np
import sys
import time
import os.path
import CTA.GenConfig as GC
import CTA.StockDataManager as SDM  
import CTA.TableManager as TM
import pandas as pd
import scipy.stats
import os
import multiprocessing as mp
from functools import partial
import matplotlib.pyplot as plt
import pdb

output = mp.Queue()



    
with open( GC.PathDict['PatternsDict'] ) as data_file:    
    pattdict = json.load(data_file)        


# generate the correlation template plots

for P in pattdict.keys():
   fname=os.path.join(GC.PathDict['PatternsDict_plots'],P+'.png')    
   if os.path.isfile(fname)==False:
       plt.figure()
       plt.plot(pattdict[P]['X'],pattdict[P]['Y'])
       plt.savefig(fname)
       plt.close()



tubes={
        'Tw005_th0':{'w':0.05,'th':0},  'Tw01_th0':{'w':0.1,'th':0},  'Tw02_th0':{'w':0.2,'th':0},
        'Tw005_th30':{'w':0.05,'th':30},'Tw01_th30':{'w':0.1,'th':30},'Tw02_th30':{'w':0.2,'th':30},
        'Tw005_th45':{'w':0.05,'th':45},'Tw01_th45':{'w':0.1,'th':45},'Tw02_th45':{'w':0.2,'th':45},
        'Tw005_th60':{'w':0.05,'th':60},'Tw01_th60':{'w':0.1,'th':60},'Tw02_th60':{'w':0.2,'th':60},
        'Tw005_th75':{'w':0.05,'th':75},'Tw01_th75':{'w':0.1,'th':75},'Tw02_th75':{'w':0.2,'th':75},

        'Tw005_thm30':{'w':0.05,'th':-30},'Tw01_thm30':{'w':0.1,'th':-30},'Tw02_thm30':{'w':0.2,'th':-30},
        'Tw005_thm45':{'w':0.05,'th':-45},'Tw01_thm45':{'w':0.1,'th':-45},'Tw02_thm45':{'w':0.2,'th':-45},
        'Tw005_thm60':{'w':0.05,'th':-60},'Tw01_thm60':{'w':0.1,'th':-60},'Tw02_thm60':{'w':0.2,'th':-60},
        'Tw005_thm75':{'w':0.05,'th':-75},'Tw01_thm75':{'w':0.1,'th':-75},'Tw02_thm75':{'w':0.2,'th':-75},
       
       }

#,ShiftBys=GC.ShiftBy_std
# do it for a particular dates for particular stocks
def GetPattCorrTube_RefDate(Refdates,windows=GC.windows_std,symb=None,saveit=['NoSave','Reoptimize']):
#    HDFleaftag=GC.PathDict['PattCorrTubeName_leaftag']
#    HDFtablink=GC.PathDict['PattCorrTubelink_bydate']
    
    Features=pd.DataFrame()
    
    STDO=SDM.StockDataOperations()    
    if symb in None:
        symb=STDO.MeaningFullStocks_forComputation()
    
    if isinstance(symb, list)==False:
        sys.exit('Need a list of symbols')
    				
    i=0 
    for tt in Refdates:  
        HDFtabname=GC.PathDict['PattCorrTubeName_bydate'](tt)
        
        for sym in symb:
            for window in windows:
                TT=SDM.GetWindowTfs(tt,window)
                t0=TT[0]
                tf=TT[1]
                print([sym,window,t0,tf])
                try:
                    D=STDO.GetStockData(sym,Fdate=t0 ,Tdate=tf)
                    y=D['Close'].values
                    t=( D.index-pd.datetime(2002,1,1) ).days
                        

                    dd={'Symbol':sym,'RefDateTf':tf,'RefDateT0':t0,'window':window}   
                    dd.update(GetCorrs(t,y)  )
                    dd.update(GetPattCorrTube(t,y)  )
                    
                    
                    Features=pd.concat([Features,pd.DataFrame(dd,index=[i])])
    
                    i=i+1
                except:
                    print("error with "+sym+" for time "+str(tf)+" and "+str(t0))
        if 'Save' in saveit:
            TM.ConcatDataFrame2Table_windows(HDFtablink,HDFtabname,HDFleaftag,PattCorrTubeTable,opt=0,pc=0,RoOptmize=False) 
                        
            Features=pd.DataFrame()

    if 'ReturnFrame' in saveit:
        return Features
    else:            
        return "Done" 
    
    

def GetCorrs_Tubes(DF):
    yc=DF['Close'].values
    yo=DF['Open'].values
   
    t=( DF.index-pd.datetime(2002,1,1) ).days
    dd={}   
    dd.update(GetCorrs(t,yc)  )
    dd.update(GetPattCorrTube(t,yc,yo)  )       
    return dd
    
def GetCorrs(t,y):
    y=np.array(y)
    t=np.array(t)
    y=y-min(y)
    t=t-min(t)
    
    y=y/max(y)
    t=t/max(t)
    
    dd={}
    
    for P in pattdict.keys():
        c2=pattdict[P]['Y']
        t2=pattdict[P]['X']         
        y2=np.interp(t,t2,c2)    
        p=scipy.stats.pearsonr(y,y2)
        dd[P]=round(p[0]*100)

        
    return dd    
    
def GetPattCorrTube(t,yc,yo):
    dd={}    
    for tb in tubes.keys():
        dd[tb]=GettubeStr(tubes[tb]['w'],t,yc,yo,th=tubes[tb]['th'])
    return dd
    
def LoadPattTubes(DF):
    T=DF.index.copy()
    t=( T-pd.datetime(2002,1,1) ).days
    yc=DF['Close'].values.copy()
    yo=DF['Open'].values.copy()
    
    ymin=min( np.minimum(yo,yc) )
    yc=yc-ymin
    yo=yo-ymin

    ymax=max( np.maximum(yo,yc) )
    yc=yc/ymax
    yo=yo/ymax

    ymn=np.minimum(yo,yc)
    ymx=np.maximum(yo,yc)

    # pdb.set_trace()

    tmin=min(t)
    t=t-tmin
    tmax=max(t)
    t=t/tmax
      
    starttime=time.time()
    for tb in tubes.keys():
        DF.loc[:,tb+'_top']=np.nan
        DF.loc[:,tb+'_bottom']=np.nan 

        w=tubes[tb]['w']
        th=tubes[tb]['th']

        th=th*np.pi/180
        
        m=np.tan(th)
        if m==0:
            a=0
        else:   
            a=w/np.sin(th)

        ss=np.arange(w,1.1+0.05,0.05)
        Ttop=np.array([np.nan]*len(DF))
        Tbottom=np.array([np.nan]*len(DF))
        cnt=0
        cntindx=[]
        for i in ss:
            if m==0:
                Tbtm=np.array([i-w]*len(t))
                Tup=np.array([i]*len(t))
            else:
                Tbtm=m*(t-i+w) 
                Tup=m *(t+a-i+w)
            #finding the longest stretch
            Y=pd.DataFrame({'Ymn':ymn,'Ymx':ymx,'No.':range(len(yc)), 'Tup':Tup, 'Tbtm':Tbtm  })
            Y.index=DF.index
            YT=Y[ ( Y['Ymx']>=Y['Tbtm']) & ( Y['Ymn']<=Y['Tup'])   ].copy()
            if len(YT)>=2:
                p=YT['No.'].values
                np.append(p,p[-1]+2000)
                q=0
                Q=[]
                idx=[YT.index[0]]
                grpidx=[]
                for jk in range(1,len(p)):
                    if p[jk]-p[jk-1]<=3:
                        q=q+1
                        # idx.append( YT[YT['No.']==p[jk-1]].index[0] )
                        idx.append( YT.index[jk-1] )
                    else:
                        Q.append(q)
                        q=0
                        grpidx.append(idx)
                        idx=[ YT.index[jk] ]

                Q=np.array(Q)
                if len(Q>0):
                    n=max(Q)
                    L=grpidx[np.argmax(Q)]
                else:
                    n=0



            else:
                n=0

            if n>cnt:
                cnt=n
                cntindx=L
                DF[tb+'_top']=Tup*ymax+ymin
                DF[tb+'_bottom']=Tbtm*ymax+ymin
                try:
                    indrmv=set(DF.index)-set(DF.loc[L[0]:L[-1]].index)
                except:
                    pdb.set_trace()
                DF.loc[indrmv,tb+'_top']=np.nan
                DF.loc[indrmv,tb+'_bottom']=np.nan  
        
        print tb +" cnt = "+str(cnt) 

            # pdb.set_trace()
            # ymxend=Y['Ymx'].iloc[-1]
            # ymnend=Y['Ymn'].iloc[-1]
            # if ymxend>=Tbtm[-1] and ymnend<= Tup[-1]:
            #     YT=Y[ ( Y['Ymx']>=Y['Tbtm']) & ( Y['Ymn']<=Y['Tup'])]
            #     if len(YT)>=2:
            #         # print "-------++++++"*10
                    
            #         # p=YT['No.'].values
            #         # np.append(p,p[-1]+2000)
            #         failed=0
            #         for pj in reversed(range(1,len(ymn))):
            #             if ymx[pj]>=Tbtm[pj] and ymn[pj]<= Tup[pj]:
            #                 failed=0
            #             else:
            #                 failed=failed+1

            #             if failed>=4:
            #                 break
            #         pn=len(ymn)-pj
            #     else:
            #         pn=0        
            # else:
            #     pn=0
                
            

            # if pn>0:
            #     DF.loc[DF.index[pj:],tb+'_top']=Tup[pj:]*ymax+ymin
            #     DF.loc[DF.index[pj:],tb+'_bottom']=Tbtm[pj:]*ymax+ymin 
            #     DF.loc[DF.index[0:pj],tb+'_top']=np.nan
            #     DF.loc[DF.index[0:pj],tb+'_bottom']=np.nan
            
                
        
        # if tb=='Tw02_th0':
        #     pdb.set_trace()
        # DF['No.']=range(len(DF))
        # ind=DF[ ( (DF['Close']>DF[tb+'_top']) & (DF['Open']>DF[tb+'_top']) )  |  ( (DF['Close']<DF[tb+'_bottom']) & (DF['Open']<DF[tb+'_bottom']) ) ].index 
        
        # # DF.loc[ind,tb+'_top']=np.nan
        # # DF.loc[ind,tb+'_bottom']=np.nan
        # DF.loc[ind,'No.']=np.nan
        # p=[]
        # L=[]
        # S=DF[pd.notnull(DF['No.'])][ ['No.','Close' ]].copy()
        # # pdb.set_trace()
        # for i in range(1,len(S)):

        #     if S.loc[S.index[i],'No.']-S.loc[S.index[i-1],'No.']<=3:
        #         p.append(S.index[i-1])
        #     else:
        #         L.append(p)
        #         p=[]


        # M=0
        # ps=-1

        # for i in range(len(L)):
        #     if len(DF.loc[L[i]])>M:
        #         M=len(DF.loc[L[i]])
        #         ps=i

        # if len(L)==0:
        #     pass    
        # else:
        #     ind=DF.loc[L[ps][0]:L[ps][-1]].index
        #     try:
        #         DF.loc[ set(DF.index) - set(ind) , tb+'_top']=np.nan
        #         DF.loc[ set(DF.index) - set(ind) , tb+'_bottom']=np.nan
        #     except:
        #         pdb.set_trace()

    print "time taken is "+str(time.time()-starttime)
    return DF



    
#th is the degree of rotattion
# w is width and y is the data between 0 and 1 
# t is also between 0 and 1     
# th is in degrees       
def GettubeStr(w,t,yc,yo,th) :
    yc=np.array(yc)
    yo=np.array(yo)
    t=np.array(t)

    ymin=min( np.minimum(yo,yc) )
    

    yc=yc-ymin
    yo=yo-ymin
    t=t-min(t)
    
    ymax=max( np.maximum(yo,yc) )

    yc=yc/ymax
    yo=yo/ymax
    t=t/max(t)
    
    ymn=np.minimum(yo,yc)
    ymx=np.maximum(yo,yc)

    th=th*np.pi/180
    
    m=np.tan(th)
    if m==0:
        a=0
    else:	
        a=w/np.sin(th)

   
    s=np.arange(w,1.1+0.05,0.05)
    cnt=0
    for i in s:
        if m==0:
            Tbtm=np.array([i-w]*len(t))
            Tup=np.array([i]*len(t))
        else:
            Tbtm=m*(t-i+w) 
            Tup=m *(t+a-i+w)
        #finding the longest stretch
        Y=pd.DataFrame({'Ymn':ymn,'Ymx':ymx,'No.':range(len(yc)), 'Tup':Tup, 'Tbtm':Tbtm  })
        YT=Y[ ( Y['Ymx']>=Y['Tbtm']) & ( Y['Ymn']<=Y['Tup'])   ]
        if len(YT)>=2:
            # print "-------++++++"*10
            # pdb.set_trace()
            p=YT['No.'].values
            np.append(p,p[-1]+2000)
            q=0
            Q=[0]
            for jk in range(1,len(p)):
                if p[jk]-p[jk-1]<=3:
                    q=q+1
                else:
                    Q.append(q)
                    q=0
                    

            n=max(Q)
        else:
            n=0
        if n>cnt:
            cnt=n
        
    return cnt


def GetFutPastPerf(Df_plus_minus_1y,t0,tf):
    FeatureDict={}
    # All the reference is from tf or T date
    # get the returns, buy date is the reference end date of window

    Df_plus_quart=  Df_plus_minus_1y[tf:(tf+pd.DateOffset(90))]
    Df_plus_half=   Df_plus_minus_1y[tf:(tf+pd.DateOffset(180))]
    Df_plus_ann=    Df_plus_minus_1y[tf:(tf+pd.DateOffset(360))]

    Df_minus_quart=  Df_plus_minus_1y[(tf-pd.DateOffset(90)):tf]
    Df_minus_half=   Df_plus_minus_1y[(tf-pd.DateOffset(180)):tf]
    Df_minus_ann=    Df_plus_minus_1y[(tf-pd.DateOffset(360)):tf]

    # maxret=max(100*(Dfquart['Close'].values-clref)/clref)
    if len(Df_plus_quart)>50:
        FeatureDict['FutMXRtQt']=min([ round( max( 100*( Df_plus_quart['Close']-Df_plus_quart['Close'].iloc[0] )/Df_plus_quart['Close'].iloc[0] ) ) , 999 ])
        FeatureDict['FutMNRtQt']=max([ round( min( 100*( Df_plus_quart['Close']-Df_plus_quart['Close'].iloc[0] )/Df_plus_quart['Close'].iloc[0] ) ), -999 ])
    else:
        FeatureDict['FutMXRtQt']=np.nan
        FeatureDict['FutMNRtQt']=np.nan

    if len(Df_plus_half)>100:    
        FeatureDict['FutMXRtHf']=min([ round( max( 100*( Df_plus_half['Close']-Df_plus_half['Close'].iloc[0] )/Df_plus_half['Close'].iloc[0] ) ) , 999 ])
        FeatureDict['FutMNRtHf']=max([ round( min( 100*( Df_plus_half['Close']-Df_plus_half['Close'].iloc[0] )/Df_plus_half['Close'].iloc[0] ) ), -999 ])
    else:
        FeatureDict['FutMXRtHf']=np.nan
        FeatureDict['FutMNRtHf']=np.nan

    if len(Df_plus_ann)>230:
        FeatureDict['FutMXRtAn']=min([ round( max( 100*( Df_plus_ann['Close']-Df_plus_ann['Close'].iloc[0] )/Df_plus_ann['Close'].iloc[0] ) ) , 999 ])
        FeatureDict['FutMNRtAn']=max([ round( min( 100*( Df_plus_ann['Close']-Df_plus_ann['Close'].iloc[0] )/Df_plus_ann['Close'].iloc[0] ) ), -999 ])
    else:
        FeatureDict['FutMXRtAn']=np.nan
        FeatureDict['FutMNRtAn']=np.nan

        # ## Getting the past perfformance
    if len(Df_minus_quart)>50:
        FeatureDict['PastMXRtQt']=min([ round( max( 100*( Df_minus_quart['Close'].iloc[-1] -Df_minus_quart['Close'] )/Df_minus_quart['Close'] ) ) , 999 ])
        FeatureDict['PastMNRtQt']=max([ round( min( 100*( Df_minus_quart['Close'].iloc[-1] -Df_minus_quart['Close'] )/Df_minus_quart['Close'] ) ), -999 ])
    else:
        FeatureDict['PastMXRtQt']=np.nan
        FeatureDict['PastMNRtQt']=np.nan

    if len(Df_minus_half)>100:    
        FeatureDict['PastMXRtHf']=min([ round( max( 100*( Df_minus_half['Close'].iloc[-1]-Df_minus_half['Close'] )/Df_minus_half['Close'] ) ) , 999 ])
        FeatureDict['PastMNRtHf']=max([ round( min( 100*( Df_minus_half['Close'].iloc[-1]-Df_minus_half['Close'] )/Df_minus_half['Close'] ) ), -999 ])
    else:
        FeatureDict['PastMXRtHf']=np.nan
        FeatureDict['PastMNRtHf']=np.nan

    if len(Df_minus_ann)>230:
        FeatureDict['PastMXRtAn']=min([ round( max( 100*( Df_minus_ann['Close'].iloc[-1]-Df_minus_ann['Close'] )/Df_minus_ann['Close'] ) ) , 999 ])
        FeatureDict['PastMNRtAn']=max([ round( min( 100*( Df_minus_ann['Close'].iloc[-1]-Df_minus_ann['Close'] )/Df_minus_ann['Close'] ) ) , -999 ])
    else:
        FeatureDict['PastMXRtAn']=np.nan
        FeatureDict['PastMNRtAn']=np.nan



    return FeatureDict


# you can now extract the wedge patterns from the top and bottom trends

def ExtractLinearPatterns(DF):
    FeatureDict={}
    # DF['LinFittop']
    # DF['LinFitMid']
    # DF['LinFitbottom']

    # DF['LinSlptop']
    # DF['LinSlpMid']
    # DF['LinSlpbottom']

    DF['No.']=range(0,len(DF))
    DF['Slpdiff']=DF['LinSlpbottom']-DF['LinSlptop']
    df=DF[DF['Slpdiff']>0]
    M=[]
    w=df['LinFittop'].iloc[0]-df['LinFitbottom'].iloc[0]
    for i in range(1,len(df)):
        if df['No.'].iloc[i]-df['No.'].iloc[i-1]<=2:
            pass
        else:
            s=df['LinFittop'].iloc[i-1]-df['LinFitbottom'].iloc[i-1]
            M.append(s*100/w)
            w=s

    if len(M)>0:
        FeatureDict['WidthRatio']=min([ round( max(M) ),999])
    else:
        FeatureDict['WidthRatio']=np.nan



    return FeatureDict


def GetCandlePatterns(DF):
    FeatureDict={}
    for cp in GC.CandlePatterns.keys():
        FeatureDict[cp]=len( DF[DF[cp]!=0])

    return FeatureDict

# Extract all the features and put them in a dictionary   
# Df is the full dataframe   
#t0 anf tf are the datetime objects of the window of concern   
def Extractfeatrues(Df):
    Df['Date']=Df.index
    Df['No.']=range(0,len(Df))

    FeatureDict={}
#==============================================================================
#         FeatureDict['(W28)MX2MXV']=np.nan 
#==============================================================================
 
    FeatureDict['CNDLS'] =len(Df)
    
    # clref=Df.iloc[-1]['Close']
    # op=Df['Open'].values
    # cl=Df['Close'].values
    Dfmax=Df[['Open','Close']].max(axis=1)
    Dfmin=Df[['Open','Close']].min(axis=1)

    
    #Number of Relative volumnes greater than 2
    FeatureDict['RV15']=len(Df[Df['VolRel10']>=1.5])
    #Number of Relative volumnes greater than 4
    FeatureDict['RV2']=len(Df[Df['VolRel10']>=2])
    #Number of Relative volumnes greater than 6
    FeatureDict['RV3']=len(Df[Df['VolRel10']>=3])
    #Number of Relative volumnes greater than 8
    FeatureDict['RV4']=len(Df[Df['VolRel10']>=4])
    #max value of Relative volume
    FeatureDict['MXRV']=Df['VolRel10'].max()
    
    
	
    #number of days between the first two maximum relative volumes
    ds=Df[pd.notnull(Df['VolRel10'])].copy()
    ds.sort_values(by=['VolRel10'],ascending=False,inplace=True)
    #FeatureDict['(W09)MX2MXRV']=np.abs((ds.index[-1]-ds.index[-2]).days)    # in days
    FeatureDict['MX2MXRV']=np.abs(ds['No.'].iloc[0]-ds['No.'].iloc[1])     # in candles  
    
   
    #candle squeeze at this point : Measure 1
    h=ds.iloc[0]['High']
    l=ds.iloc[0]['Low']
    o=ds.iloc[0]['Open']
    c=ds.iloc[0]['Close']
    
    if np.abs(o-c)==0:
        FeatureDict['SQZ1MXRV']=np.nan
    else:
        FeatureDict['SQZ1MXRV']=(h-l)/np.abs(o-c)

    #Number of candle Gap ups and Gap downs
    gapups=Dfmin.iloc[1:]-Dfmax.iloc[0:-1]  # current min - prev max
    gapdowns=Dfmin.iloc[0:-1]-Dfmax.iloc[1:] # prev min - current max
    FeatureDict['GPUP']=len(gapups[gapups>=0])
    FeatureDict['GPDN']=len(gapdowns[gapdowns>0])
	
    gapupspct=(Dfmin.iloc[1:]-Dfmax.iloc[0:-1])/Dfmax.iloc[0:-1]
    gapdownspct=(Dfmin.iloc[0:-1]-Dfmax.iloc[1:])/Dfmin.iloc[0:-1]	
	
    if len(gapupspct[gapupspct>=0])==0: 
        FeatureDict['MXGPUP']=np.nan
    else:
        FeatureDict['MXGPUP']=100*max(gapupspct[gapupspct>=0])
        
    if len(gapdownspct[gapdownspct>=0])==0:
        FeatureDict['MXGPDN']=np.nan
    else:
        FeatureDict['MXGPDN']=100*max(gapdownspct[gapdownspct>=0])

    #Totoal number of candles above SMA10 (no need to be consiquetive)
    Dfabove10=Dfmax-Df['SMA10']
    FeatureDict['SMA10']=len(Dfabove10[Dfabove10>=0])
    
    #Totoal number of candles above SMA20 (no need to be consiquetive)
    Dfabove20=Dfmax-Df['SMA20']
    FeatureDict['SMA20']=len(Dfabove20[Dfabove20>=0])
    
    #Total number days for which  SMA10 > SMA20 >SMA50 > SMA100 > SMA200(no need to be consiquetive)
    Dfabove102050100200=Df[(Df['SMA10'] >= Df['SMA20']) & (Df['SMA20'] >= Df['SMA50']) & (Df['SMA50'] >= Df['SMA100']) & (Df['SMA100'] >= Df['SMA200'])].copy()
    FeatureDict['SMA1251020']=len(Dfabove102050100200)
    
   
    
    #Total number days for which  SMA50 > SMA100 > SMA200(no need to be consiquetive)
    Dfabove50100200=Df[(Df['SMA50'] >= Df['SMA100']) & (Df['SMA100'] >= Df['SMA200'])].copy()    
    FeatureDict['SMA51020']=len(Dfabove50100200)
    
    Dfabove2050=Df[(Df['SMA20'] >= Df['SMA50'])].copy() 
    FeatureDict['SMA25']=len(Dfabove2050)
    
    # Dfabove102050100200['diff']=Dfabove102050100200['No.'].diff(periods=1)
    # Dfabove102050100200['diff']=Dfabove102050100200['diff'].apply(lambda x : 0 if int(np.abs(x))!=1 else 1).copy()
    # Dfabove102050100200['diffdiff']=Dfabove102050100200['diff'].diff(periods=1)
    # x=[]
    # cnt=0
    # for i in range(len(Dfabove102050100200)):
    #     if Dfabove102050100200['diffdiff']==1:
    #         cnt=cnt+1

    #     if Dfabove102050100200['diffdiff']==-1:
    #         x.append(cnt)
    #         cnt=0



    #Total number days for which  SMA10 > SMA20 >SMA50 > SMA100 > SMA200(needs to be consiquetive!!!!)
    cnt=0
    x=[0]
    for i in range(1,len(Dfabove102050100200)):
        if np.abs(Dfabove102050100200['No.'].iloc[i]-Dfabove102050100200['No.'].iloc[i-1])==1:
            cnt=cnt+1    
        else:
            x.append(cnt)
            cnt=0
    if cnt>0:
        x.append(cnt)
        cnt=0

    FeatureDict['Rly1251020']=max(x)
    #Min distance(in days) of the nearest rally of SMA10 > SMA20 >SMA50 > SMA100 > SMA200(needs to be consiquetive!!!!)
    FeatureDict['Rly2Rf1251020']=x[-1]
    
    
    #Total number days for which  SMA50 > SMA100 > SMA200(needs to be consiquetive!!!!)
    cnt=0
    x=[0]
    for i in range(1,len(Dfabove50100200)):
        if np.abs((Dfabove50100200['No.'].iloc[i]-Dfabove50100200['No.'].iloc[i-1]))==1:
            cnt=cnt+1    
        else:
            x.append(cnt)
            cnt=0
    if cnt>0:
        x.append(cnt)
        cnt=0

    FeatureDict['Rly51020']=max(x)
    #Min distance(in days) of the nearest rally of SMA50 > SMA100 > SMA200(needs to be consiquetive!!!!)
    FeatureDict['Rly2Rf51020'] =x[-1]       
         
    #Total number days for which  SMA20 > SMA50 (needs to be consiquetive!!!!)
    cnt=0
    x=[0]
    for i in range(1,len(Dfabove2050.index)):
        if np.abs(Dfabove2050['No.'].iloc[i]-Dfabove2050['No.'].iloc[i-1])==1:
            cnt=cnt+1    
        else:
            x.append(cnt)
            cnt=0
    if cnt>0:
        x.append(cnt)
        cnt=0

    FeatureDict['Rly25'] =max(x)

    ds=Df[pd.notnull(Df['Volume'])].sort_values(by='Volume',ascending=False)    
    FeatureDict['MX2MXV']=np.abs(ds['No.'].iloc[0]-ds['No.'].iloc[1])
    
    return FeatureDict

# Given the data for the window Df and TrendLines, get all the features 
# possible and put it into dict     
def ExtractLinearTrendfeatrues(Df,Trends):
    #df=Df.copy
    #for ss in Df.columns:
    #    df = df[np.isfinite(df[ss])]
    
    FeatureDict={}
    FeatureDict['Chgpts']=np.nan
    FeatureDict['FltRly']=np.nan
    FeatureDict['UpRly']=np.nan
    FeatureDict['FN2PChgpts']=np.nan
    FeatureDict['MXSLChg']=np.nan
    FeatureDict['FltRV15']=np.nan
    FeatureDict['FltRV2']=np.nan
    FeatureDict['FltRV3']=np.nan         
    FeatureDict['URV15']=np.nan  
    FeatureDict['URV2']=np.nan
    FeatureDict['URV3']=np.nan
    FeatureDict['FltR20V15']=np.nan
    FeatureDict['FltR20V2']=np.nan
    FeatureDict['FltR20V3']=np.nan
    FeatureDict['CNDLS'] =np.nan
    FeatureDict['Fltlen']=np.nan
    FeatureDict['Uplen']=np.nan
    
    
    try:
        fltnorm=GC.FLATNESS_NORMS(window)
    except:
        fltnorm=0.35
        
    Trend_flat=Trends[ Trends['Slpnorm'].abs()<=fltnorm ].copy()
    Trend_up=Trends[ Trends['Slpnorm'].abs()>fltnorm ].copy()
    Trend_dwn=Trends[ Trends['Slpnorm']<-fltnorm ].copy()

    Df_flat=pd.DataFrame()
    for ind in Trend_flat.index: 
        Df_flat=pd.concat( [Df_flat,Df[ Trend_flat.loc[ind,'X0date']:Trend_flat.loc[ind,'Xfdate']  ] ] )
    
    Df_up=pd.DataFrame()
    for ind in Trend_up.index: 
        Df_up=pd.concat( [Df_up,Df[ Trend_up.loc[ind,'X0date']:Trend_up.loc[ind,'Xfdate']  ] ] )

    Df_dwn=pd.DataFrame()
    for ind in Trend_dwn.index: 
        Df_dwn=pd.concat( [Df_dwn,Df[ Trend_dwn.loc[ind,'X0date']:Trend_dwn.loc[ind,'Xfdate']  ] ] )

    FeatureDict['Chgpts']=len(Trends)
    
    # Rally length of flat ... 
    FeatureDict['Fltlen']=len(Df_flat)
    FeatureDict['Uplen']=len(Df_up)

    #flat rally 
    #FeatureDict['(L02)FltRly']= max(MaxFltRally)
    if len(Trend_flat)>0:
        FeatureDict['FltRly']= (Trend_flat['Xfdate']-Trend_flat['X0date']).apply(lambda x: x.days).max()
    else:
        FeatureDict['FltRly']=np.nan
        
    #Rally length of upward... any slope > 0
    #FeatureDict['(L03)UpRly']= max(MaxUplenRally)   # in #days
    if len(Trend_flat)>0:
        FeatureDict['UpRly']= (Trend_up['Xfdate']-Trend_up['X0date']).apply(lambda x: x.days).max()
    else:
        FeatureDict['UpRly']=np.nan
            
    # FeatureDict['UpRly']= max(MaxUpcndlsRally)  # in #candles
    
    # of neg/flat to +ve change points
    slpnrms=Trends['Slpnorm'].copy().values

    slpnrms[np.abs(slpnrms)<=fltnorm]=0
    slpnrms[slpnrms<-fltnorm]=-1
    slpnrms[slpnrms>fltnorm]=1

    slpnrms_diff=np.diff(slpnrms)

    if len(slpnrms_diff)==0:
        FeatureDict['FN2PChgpts']=0
    else:    
        FeatureDict['FN2PChgpts']= len( slpnrms_diff[np.where(slpnrms_diff==1)] ) 
    
    
    FeatureDict['MXSLChg']=round( Trends['Slpnorm'].diff().abs().max() ,2 )
    
    FeatureDict['FltRV15']= len(Df_flat[Df_flat['VolRel10']>=1.5])
    FeatureDict['FltRV2']= len(Df_flat[Df_flat['VolRel10']>=2])
    FeatureDict['FltRV3']= len(Df_flat[Df_flat['VolRel10']>=3])
    
    # Flat region volume spikes (use VolRel20)
    FeatureDict['FltR20V15']= len(Df_flat[Df_flat['VolRel20']>=1.5])
    FeatureDict['FltR20V2']= len(Df_flat[Df_flat['VolRel20']>=2])
    FeatureDict['FltR20V3']= len(Df_flat[Df_flat['VolRel20']>=3])
    

    FeatureDict['URV15']=len(Df_up[Df_up['VolRel10']>=1.5])
    FeatureDict['URV2']=len(Df_up[Df_up['VolRel10']>=2])
    FeatureDict['URV3']=len(Df_up[Df_up['VolRel10']>=3])
    
    return FeatureDict


def GetTFeatures(DF):
    FeatureDict={}

    FeatureDict['Price']=DF['Close'].iloc[-1]
    FeatureDict['Volume']=DF['Volume'].iloc[-1]
    FeatureDict['RVSMA10']=DF['VolRel10'].iloc[-1]
    FeatureDict['RVSMA20']=DF['VolRel20'].iloc[-1]
    
    FeatureDict['MarketCap']=np.nan
    
    FeatureDict['ConsecutiveGreen']=np.nan
    FeatureDict['ConsecutiveRed']=np.nan
    FeatureDict['ConsecutiveSMA10']=np.nan
    FeatureDict['ConsecutiveSMA20']=np.nan

    return FeatureDict



class LineBuilder:
    def __init__(self, pp):
        self.pp = pp
        self.line = pp[0]
        self.xs = []#list(line.get_xdata())
        self.ys = []#list(line.get_ydata())
        self.Xstates=[]
        self.Ystates=[]
        self.XYstates={}
        self.cnt=1
        self.xy=[]
        self.cid = pp[0].figure.canvas.mpl_connect('button_press_event', self)
        #self.cidpress = pp[1].figure.canvas.mpl_connect('key_press_event', self)
        print('LOL')
        with open('PatternTemplates.txt', 'r') as outfile:
           self.XYstates=json.load(outfile) 
           for i in range(100):
               if 'P'+str(i) not in self.XYstates.keys():
                   self.cnt=i
                   break
        print('Next will be saved at '+'P'+str(self.cnt))
        
    def __call__(self, event):
        print ('click', event)
        if event.inaxes!=self.line.axes: 
            print ('returning')            
            return
        if event.button==1:
            self.xs.append(event.xdata)
            self.ys.append(event.ydata)
            self.xy.append([event.xdata,event.ydata])
            self.line.set_data(self.xs, self.ys)
            self.line.figure.canvas.draw()
        if event.button==3:
            print ('Finished this state going to next one')
            self.Xstates.append(self.xs)
            self.Ystates.append(self.ys)
            self.XYstates['P'+str(self.cnt)]={'X':self.xs,'Y':self.ys}
            self.xy=[]
            self.xs = []
            self.ys = []
        if event.button==2:
            print('lol')
            with open('PatternTemplates.txt', 'w') as outfile:
                json.dump(self.XYstates, outfile, sort_keys=True,indent=50)        
                
def Drawpattern():
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.set_title('click to build line segments')
    ax.set_xlim([0, 1])
    ax.set_ylim([0, 1])
    line = ax.plot([0], [0])  # empty line
    linebuilder = LineBuilder(line)
    plt.show()
    
if __name__ == '__main__':
    STDO=SDM.StockDataOperations()    
    Shiftby=20
    Refdates=SDM.GetRefDates(20,Tlb=pd.datetime(2006,1,1),Tub=STDO.stocks_latest_date)
    
    start_time = time.time()
    pool = mp.Pool(processes=2)
    results = [pool.apply_async(partial(GetPattCorrTube_RefDate,Refdates=[Refdates[i]],norm='Yes',saveit=True), args=()) for i in range(0,len(Refdates))]
    output = [p.get() for p in results]
    print("--- %s seconds ---" % (time.time() - start_time))
    
    
	#print(output)

                