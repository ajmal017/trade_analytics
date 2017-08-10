# -*- coding: utf-8 -*-
"""
Created on Mon May  4 14:06:30 2015

@author: nagnanamus
"""
from __future__ import division
try:
    from mpi4py import MPI
    comm = MPI.COMM_WORLD
    MPIsize = comm.Get_size()
    MPIrank = comm.Get_rank()
    MPIname = MPI.Get_processor_name()
except:
    print('MPI not there ')
    
    
import sys
   
import os.path
import CompTechAnalysis.StockData_Manager.StockDataManager as SDM  
import CompTechAnalysis.StockData_Analysis.FeaturesExtraction as fe
import CompTechAnalysis.Pattern_recos_models.PatternReco_FlatStocks as pflat
from CompTechAnalysis.GenConfig import CreateConfigFile,GetConfig
import CompTechAnalysis.Stock_Doc_Gen.DataDocGenerators as ddg

import pandas as pd
import json 
import time
import numpy as np
import scipy
# import matplotlib
# import matplotlib.pylab as plt
from itertools import combinations,tee
import itertools
import os
from os import listdir
from os.path import isfile, join

import multiprocessing
from multiprocessing import Pool
from subprocess import call

import subprocess as sbp
import sqlalchemy as sqlal    

#==============================================================================
# PathDict={'StockData_daily':'/home/nagnanamus/Copy/python-finance/Data/StockData_daily.h5',
#           'StockData_weekly':'/home/nagnanamus/Copy/python-finance/Data/StockData_weekly.h5',
#           'StockData_monthly':'/home/nagnanamus/Copy/python-finance/Data/StockData_monthly.h5',
#           'LinearFitPlotDataPath':'/home/nagnanamus/Copy/python-finance/Plots/LinearTrendChannels/',
#           'CORRELATIONTABLE':'/home/nagnanamus/Copy/python-finance/Data/CORRELATIONTABLE.h5'
#           'LinearFitFeatures':'/home/nagnanamus/Copy/python-finance/Plots/LinearTrendChannels/MASTERFEATURE.h5'}
#==============================================================================
   
   
# respect if the length of the two datas are not exactly the same
# trasform to [0,1] and the recalculate data by interpolation
#and then calculate the correlation 
def GetCorr(df1,df2):
    
    return 1
# Get the correlation table to up to date
def makeCorrTable(S1List,S2List,pdT0=pd.datetime(2006,1,1),ShiftBy=20,window=120):
    #FileDict=GetConfig()
    #CORRELATIONTABLE = pd.HDFStore(FileDict['CORRELATIONTABLE'])  
    pdTf=pd.datetime.today()
    corrtable=pd.DataFrame(columns={'Stock1','Stock2','corr','RefDate','window','shiftby'})
    STDO=SDM.StockDataOperations()    
    i=0

    while i>=0:
        #(ss1,DF1,i)=SDM.GetStdStockSet(pdT0,pdTf,i)
        ss1=S1List[i]
        DD=STDO.PullDataSymbolsSet({ss1:[[pdT0.year,pdT0.month,pdT0.day],[]]})  
        DF1=DD[ss1]
        i=i+1
        j=0
        while j>=0:
            #(ss2,DF2,j)=SDM.GetStdStockSet(pdT0,pdTf,j)
            ss2=S2List[j]
            DD=STDO.PullDataSymbolsSet({ss2:[[pdT0.year,pdT0.month,pdT0.day],[]]})  
            DF2=DD[ss2]
            j=j+1
            
            if ss1==ss2:
                continue
            df=corrtable[corrtable['Stock1']==ss1]
            if not df[df['Stock2']==ss2].empty:
                continue
            df=corrtable[corrtable['Stock2']==ss1]
            if not df[df['Stock1']==ss2].empty:
                continue
            print(str(i)+'_'+ss1+' and '+str(j)+'_'+ss2)
            
            TT1=SDM.GenerateWindowsShiftby(DF1.index,window,ShiftBy)
            TT2=SDM.GenerateWindowsShiftby(DF2.index,window,ShiftBy)
            if len(TT1)>len(TT2):
                TT=TT1
            else:
                TT=TT2
                    
            for tt in TT:
             t0=tt[0]
             tf=tt[1]
             c1=DF1[t0:tf].Close.values
             c2=DF2[t0:tf].Close.values
             
             t1=np.array(range(0,len(DF1[t0:tf].index)))
             t2=np.array(range(0,len(DF2[t0:tf].index)))
             
             if np.abs(len(c1)-len(c2))>max(4,2*window/100) or len(c2)<10 or len(c1)<10:            
                 continue
             
             t=np.linspace(0,1,200)
             
             c1=c1-min(c1)
             c1=c1/max(c1)
             t1=t1-min(t1)
             t1=t1/max(t1)
             y1=np.interp(t,t1,c1)   
                 
             c2=c2-min(c2)
             c2=c2/max(c2)
             t2=t2-min(t2)
             t2=t2/max(t2)
             y2=np.interp(t,t2,c2)    
             
             
             p=scipy.stats.pearsonr(y1,y2)
             d={'Stock1':ss1,'Stock2':ss2,'corr':p[0],'RefDate':tf,'window':window,'shiftby':ShiftBy}
             corrtable=corrtable.append(pd.DataFrame(d,index=[0]))
    
    corrtable.index=range(0,len(corrtable.index))   
    return corrtable      
    #CORRELATIONTABLE['CORRELATIONTABLE']=corrtable    



             
def GetCorrelation(ss1,ss2,pdT0,pdTf,window,ShiftBy,DF1=pd.DataFrame(),DF2=pd.DataFrame()):
    corrtable=pd.DataFrame(columns={'Stock1','Stock2','corr','RefDateTf','RefDateT0','window','shiftby'})
    
    if DF1.empty or DF2.empty:
        STDO=SDM.StockDataOperations()    
        DD=STDO.PullDataSymbolsSet({ss1:[[pdT0.year,pdT0.month,pdT0.day],[]]})  
        DF1=DD[ss1]
        DD=STDO.PullDataSymbolsSet({ss2:[[pdT0.year,pdT0.month,pdT0.day],[]]})  
        DF2=DD[ss2]
        STDO.CloseDataFiles()
        
        
    TT=SDM.GenerateGeneralWindowsShiftby(window,ShiftBy)
         
    for tt in TT:
        t0=tt[0]
        tf=tt[1]
        
        
        
        c1=DF1[t0:tf].Close.values
        c2=DF2[t0:tf].Close.values
             
        t1=np.array(range(0,len(DF1[t0:tf].index)))
        t2=np.array(range(0,len(DF2[t0:tf].index)))
             
        #if np.abs(len(c1)-len(c2))>max(4,2*window/100) or len(c2)<10 or len(c1)<10:            
        #    continue
        if len(c2)<0.9*SDM.GetWindowAvgTradeDays(window) or len(c1)<0.9*SDM.GetWindowAvgTradeDays(window):            
            continue
        
        SDM.GetWindowAvgTradeDays(window)
        #if (tf-DF1[t0:tf].index[-1]).days>5 or (tf-DF2[t0:tf].index[-1]).days>5:
        #    continue
        
        t=np.linspace(0,1,200)
             
        c1=c1-min(c1)
        c1=c1/max(c1)
        t1=t1-min(t1)
        t1=t1/max(t1)
        y1=np.interp(t,t1,c1)   
                 
        c2=c2-min(c2)
        c2=c2/max(c2)
        t2=t2-min(t2)
        t2=t2/max(t2)
        y2=np.interp(t,t2,c2)    
             
             
        p=scipy.stats.pearsonr(y1,y2)
        d={'Stock1':ss1,'Stock2':ss2,'corr':p[0],'RefDateTf':tf,'RefDateT0':t0,'window':window,'shiftby':ShiftBy}
        corrtable=corrtable.append(pd.DataFrame(d,index=[0]))    
        
    
    return corrtable          
             
             
             
def UpdateCorrelations(SS,fileprepend='None'):
    PathDict=GetConfig()
    pdT0=PathDict['pdT0']
    pdTf=PathDict['pdTf']
    SS=list(SS)
    for ss in SS:
        ss1=ss[0]
        ss2=ss[1]
        print ('working on '+ss1+' and '+ss2  )
        corrtable=pd.DataFrame()
        try:
            start_time = time.time()
            
            window=120
            ShiftBy=20
            corrtable120=GetCorrelation(ss1,ss2,pdT0,pdTf,window,ShiftBy)
            print ('Done with 120 window')
                    
                    
            window=180
            ShiftBy=20
            corrtable180=GetCorrelation(ss1,ss2,pdT0,pdTf,window,ShiftBy)
            print ('Done with 180 window')
                    
            window=360
            ShiftBy=20
            corrtable360=GetCorrelation(ss1,ss2,pdT0,pdTf,window,ShiftBy)
            print ('Done with 360 window')
                    
            window=720
            ShiftBy=20
            corrtable720=GetCorrelation(ss1,ss2,pdT0,pdTf,window,ShiftBy)
            print ('Done with 720 window')
                    
            corrtable=pd.concat([corrtable,corrtable120,corrtable180,corrtable360,corrtable720])
            
                      
            print (ss1+'+'+ss2+': Done !!! in '+str(time.time() - start_time)+' seconds')
            
            #corrtable.to_csv(PathDict['CORRELATIONDATALINK']+'CORR_'+ss1+'_'+ss2+'.csv')
                    
        except:
            print (ss1+'+'+ss2+' Feature+LinearFeature Error *****************************************************'    )
            
        if fileprepend=='None':
            tt=pd.datetime.today().strftime("%Y_%m_%d_%H_%M_%S")
        else:
            tt=fileprepend
            
        GenerateUpdateCorrelation_HDF5_byRefdate(File=None,CorrTable=corrtable,AlphaBetFile=tt)  


                 
    

# HDF5 MAIN TABLE
def CombineUpdateCorrelationTables():
    print('yes')



# HDF5 small tables by date and window
def GenerateUpdateCorrelation_HDF5_byRefdate(File=None,CorrTable=pd.DataFrame(),ftags=None,desttag='',OptTables='No',Compress='No',lenid=[]):
    ErredFiles=[]
    min_itemsizes={'Stock1': 8,'Stock2':8}    
    PathDict=GetConfig()
    #corrtable=pd.DataFrame(columns={'Stock1','Stock2','corr','RefDateTf','RefDateT0','window','shiftby'}) 
    #d={'Stock1':ss1,'Stock2':ss2,'corr':p[0],'RefDateTf':tf,'RefDateT0':t0,'window':window,'shiftby':ShiftBy}
    if File==None:    
        onlyfiles = [ f for f in listdir(PathDict['CORRELATIONDATALINK_bydate']) if isfile(join(PathDict['CORRELATIONDATALINK_bydate'],f)) and 'CORR_' not in f ]
    else:
        onlyfiles=list(File)
    
    if ftags==None:
        print('ftags to work on not provided')
    else:
        #if isinstance(ftags, basestring):
        if type(ftags)==str:
            ftags=[ftags]
            fs=[]
            for ss in onlyfiles:
                for tg in ftags:
                    if ss.find(tg) >=0:
                        fs.append(ss)
        onlyfiles=fs
    
    if desttag=='':
        print('No destination tag provided... so using master dest tag')
        Afs=''
    else:
        Afs=desttag+'_'
        
        
        
    if not CorrTable.empty:
        onlyfiles=['DirectTable']
        
        
    #creating the tables and the dictionary of hdf5 files
    window=120
    ShiftBy=20        
    TT=SDM.GenerateGeneralWindowsShiftby(window,ShiftBy)   
    Allthetables120={}
    Allthetables180={}
    Allthetables360={}
    Allthetables720={}
    
    dd=pd.DataFrame(columns={'Stock1','Stock2','corr','RefDateTf','RefDateT0','window','shiftby'})   
    Dumbtabfnames={}
    
    if OptTables.lower()=='Yes'.lower() or OptTables.lower()=='No'.lower():
        Allthetables={}
    
    for tt in TT:
        tf=tt[1]
        
        
        if OptTables.lower()=='Yes'.lower():
            tab=pd.HDFStore(PathDict['CORRELATIONDATALINK_bydate']+Afs+'CORR_'+tf.strftime("%Y-%m-%d")+'.h5')  
            
            Allthetables120[tf]=pd.DataFrame(columns={'Stock1','Stock2','corr','RefDateTf','RefDateT0','window','shiftby'})
            Allthetables180[tf]=pd.DataFrame(columns={'Stock1','Stock2','corr','RefDateTf','RefDateT0','window','shiftby'})
            Allthetables360[tf]=pd.DataFrame(columns={'Stock1','Stock2','corr','RefDateTf','RefDateT0','window','shiftby'})
            Allthetables720[tf]=pd.DataFrame(columns={'Stock1','Stock2','corr','RefDateTf','RefDateT0','window','shiftby'})
        
            tab.append('CORR120',dd,data_columns = True,index=False,format='table',min_itemsize=min_itemsizes)
            tab.append('CORR180',dd,data_columns = True,index=False,format='table',min_itemsize=min_itemsizes)
            tab.append('CORR360',dd,data_columns = True,index=False,format='table',min_itemsize=min_itemsizes)
            tab.append('CORR720',dd,data_columns = True,index=False,format='table',min_itemsize=min_itemsizes)
            Allthetables[tf]=tab
            
        elif OptTables.lower()=='No'.lower():
            tab=pd.HDFStore(PathDict['CORRELATIONDATALINK_bydate']+Afs+'CORR_'+tf.strftime("%Y-%m-%d")+'.h5') 
            
            Allthetables120[tf]=pd.DataFrame(columns={'Stock1','Stock2','corr','RefDateTf','RefDateT0','window','shiftby'})
            Allthetables180[tf]=pd.DataFrame(columns={'Stock1','Stock2','corr','RefDateTf','RefDateT0','window','shiftby'})
            Allthetables360[tf]=pd.DataFrame(columns={'Stock1','Stock2','corr','RefDateTf','RefDateT0','window','shiftby'})
            Allthetables720[tf]=pd.DataFrame(columns={'Stock1','Stock2','corr','RefDateTf','RefDateT0','window','shiftby'})
                
            tab.append('CORR120',dd,index=False,format='table',min_itemsize=min_itemsizes)
            tab.append('CORR180',dd,index=False,format='table',min_itemsize=min_itemsizes)
            tab.append('CORR360',dd,index=False,format='table',min_itemsize=min_itemsizes)
            tab.append('CORR720',dd,index=False,format='table',min_itemsize=min_itemsizes)
            Allthetables[tf]=tab
            
        elif OptTables.lower()=='Dumb'.lower():
            
            Dumbtabfnames[tf]=PathDict['CORRELATIONDATALINK_bydate']+Afs+'CORR_'+tf.strftime("%Y-%m-%d")+'.h5'
            Allthetables120[tf]=pd.DataFrame(columns={'Stock1','Stock2','corr','RefDateTf','RefDateT0','window','shiftby'})
            Allthetables180[tf]=pd.DataFrame(columns={'Stock1','Stock2','corr','RefDateTf','RefDateT0','window','shiftby'})
            Allthetables360[tf]=pd.DataFrame(columns={'Stock1','Stock2','corr','RefDateTf','RefDateT0','window','shiftby'})
            Allthetables720[tf]=pd.DataFrame(columns={'Stock1','Stock2','corr','RefDateTf','RefDateT0','window','shiftby'})
            
      
    onlyfiles.sort()
    if len(lenid)==0:
        print('doing all the files as no length para supplied')
    else:
        onlyfiles=onlyfiles[ lenid[0] :lenid[1]  ]
        print('doing only ' + str(lenid[0])+' to '+str(lenid[1]) + ' of the sorted set of files')
        
    kk=0     
    for ff in onlyfiles:
        kk=kk+1
        print(ff+' '+str(kk)+' of '+str(len(onlyfiles)))
        
        if ff=='DirectTable':
            corrtable=CorrTable
            if corrtable.empty:
                continue
            
        elif '.csv' in ff:
            try:
                corrtable=pd.read_csv(PathDict['CORRELATIONDATALINK']+ff,dtype={'Stock1': object,'Stock2': object,'corr':np.float16,'window':np.int32,'shiftby':np.int32},parse_dates=['RefDateT0','RefDateTf'])
            except:
                print(ff+' has error')
                ErredFiles.append(ff)
                continue
            
        elif '.h5' in ff:
            try:
                stre=pd.HDFStore(PathDict['CORRELATIONDATALINK_bydate']+ff)
                corrtable=pd.DataFrame()
                for sks in stre.keys():
                    sks=sks[1:]
                    try:
                        corrtable=pd.concat([corrtable,stre[sks]])
                    except:
                        print('Leaf '+sks+' of tag file '+ff+' has error dude... have fun!!!')
                print('The length of this sub-corr table with '+str(len(stre.keys())) +' is : '+str(len(corrtable)))    
                stre.close()
                    
            except:
                print(ff+' has error')
                ErredFiles.append(ff)
                continue            
            
        corrtable=corrtable[['Stock1','Stock2','corr','RefDateTf','RefDateT0','window','shiftby']]     
        corrtable.index=range(0,len(corrtable.index))
#        for i in range(0,len(corrtable.index)):    
#            corrtable.loc[i,'RefDateTf']=corrtable.loc[i,'RefDateTf'].replace(hour=0, minute=0, second=0)
#            corrtable.loc[i,'RefDateT0']=corrtable.loc[i,'RefDateT0'].replace(hour=0, minute=0, second=0)
            
        
        window=120
        ShiftBy=20        
        TT=SDM.GenerateGeneralWindowsShiftby(window,ShiftBy)
        
        for tt in TT:
            tf=tt[1]
            tf1=tf - pd.DateOffset(8)
            tf2=tf + pd.DateOffset(8)
            ds=corrtable[(corrtable['RefDateTf']>tf1) & (corrtable['RefDateTf']<tf2)].copy() 
            
            if ds.empty:
                continue      

            ds['RefDateTf']=tf

            dx=ds[ds['window']==120]
            if not dx.empty:
                Allthetables120[tf]=pd.concat([Allthetables120[tf],dx])
                
            dx=ds[ds['window']==180]
            if not dx.empty:
                Allthetables180[tf]=pd.concat([Allthetables180[tf],dx])                
            
            dx=ds[ds['window']==360]
            if not dx.empty:
                Allthetables360[tf]=pd.concat([Allthetables360[tf],dx])
            
            dx=ds[ds['window']==720]
            if not dx.empty:
                Allthetables720[tf]=pd.concat([Allthetables720[tf],dx])
            
            #print(ff+' appended for window 120 on '+tf.strftime("%Y-%m-%d"))            
        


        if np.remainder(kk,5)==0:
            for tt in TT:
                tf=tt[1]
                Allthetables120[tf]['RefDateTf']=Allthetables120[tf]['RefDateTf'].astype('datetime64[ns]')     
                Allthetables120[tf]['RefDateT0']=Allthetables120[tf]['RefDateT0'].astype('datetime64[ns]')
                Allthetables120[tf]['window']=Allthetables120[tf]['window'].astype('int32')
                Allthetables120[tf]['shiftby']=Allthetables120[tf]['shiftby'].astype('int32')
                Allthetables120[tf]['corr']=Allthetables120[tf]['corr'].astype('float16') 
                Allthetables120[tf]['Stock1']=Allthetables120[tf]['Stock1'].astype('str') 
                Allthetables120[tf]['Stock2']=Allthetables120[tf]['Stock2'].astype('str') 
            
                Allthetables180[tf]['RefDateTf']=Allthetables180[tf]['RefDateTf'].astype('datetime64[ns]')     
                Allthetables180[tf]['RefDateT0']=Allthetables180[tf]['RefDateT0'].astype('datetime64[ns]')
                Allthetables180[tf]['window']=Allthetables180[tf]['window'].astype('int32')
                Allthetables180[tf]['shiftby']=Allthetables180[tf]['shiftby'].astype('int32')
                Allthetables180[tf]['corr']=Allthetables180[tf]['corr'].astype('float16') 
                Allthetables180[tf]['Stock1']=Allthetables180[tf]['Stock1'].astype('str') 
                Allthetables180[tf]['Stock2']=Allthetables180[tf]['Stock2'].astype('str') 
            
                Allthetables360[tf]['RefDateTf']=Allthetables360[tf]['RefDateTf'].astype('datetime64[ns]')     
                Allthetables360[tf]['RefDateT0']=Allthetables360[tf]['RefDateT0'].astype('datetime64[ns]')
                Allthetables360[tf]['window']=Allthetables360[tf]['window'].astype('int32')
                Allthetables360[tf]['shiftby']=Allthetables360[tf]['shiftby'].astype('int32')
                Allthetables360[tf]['corr']=Allthetables360[tf]['corr'].astype('float16') 
                Allthetables360[tf]['Stock1']=Allthetables360[tf]['Stock1'].astype('str') 
                Allthetables360[tf]['Stock2']=Allthetables360[tf]['Stock2'].astype('str') 
            
                Allthetables720[tf]['RefDateTf']=Allthetables720[tf]['RefDateTf'].astype('datetime64[ns]')     
                Allthetables720[tf]['RefDateT0']=Allthetables720[tf]['RefDateT0'].astype('datetime64[ns]')
                Allthetables720[tf]['window']=Allthetables720[tf]['window'].astype('int32')
                Allthetables720[tf]['shiftby']=Allthetables720[tf]['shiftby'].astype('int32')
                Allthetables720[tf]['corr']=Allthetables720[tf]['corr'].astype('float16') 
                Allthetables720[tf]['Stock1']=Allthetables720[tf]['Stock1'].astype('str') 
                Allthetables720[tf]['Stock2']=Allthetables720[tf]['Stock2'].astype('str') 
                
                if OptTables.lower()=='Yes'.lower():
                    Allthetables[tf].append('CORR120',Allthetables120[tf],data_columns = True,index=False,format='table',min_itemsize=min_itemsizes)
                    Allthetables[tf].append('CORR180',Allthetables180[tf],data_columns = True,index=False,format='table',min_itemsize=min_itemsizes)
                    Allthetables[tf].append('CORR360',Allthetables360[tf],data_columns = True,index=False,format='table',min_itemsize=min_itemsizes)
                    Allthetables[tf].append('CORR720',Allthetables720[tf],data_columns = True,index=False,format='table',min_itemsize=min_itemsizes)
                
                elif OptTables.lower()=='No'.lower():  
                    Allthetables[tf].append('CORR120',Allthetables120[tf],index=False,format='table',min_itemsize=min_itemsizes)
                    Allthetables[tf].append('CORR180',Allthetables180[tf],index=False,format='table',min_itemsize=min_itemsizes)
                    Allthetables[tf].append('CORR360',Allthetables360[tf],index=False,format='table',min_itemsize=min_itemsizes)
                    Allthetables[tf].append('CORR720',Allthetables720[tf],index=False,format='table',min_itemsize=min_itemsizes)
                
                elif OptTables.lower()=='Dumb'.lower():            
                    Allthetables120[tf].to_hdf(Dumbtabfnames[tf],'CORR120',format='table',mode='a',append=True)
                    Allthetables180[tf].to_hdf(Dumbtabfnames[tf],'CORR180',format='table',mode='a',append=True)
                    Allthetables360[tf].to_hdf(Dumbtabfnames[tf],'CORR360',format='table',mode='a',append=True)
                    Allthetables720[tf].to_hdf(Dumbtabfnames[tf],'CORR720',format='table',mode='a',append=True)
            
                Allthetables120[tf]=pd.DataFrame(columns={'Stock1','Stock2','corr','RefDateTf','RefDateT0','window','shiftby'})
                Allthetables180[tf]=pd.DataFrame(columns={'Stock1','Stock2','corr','RefDateTf','RefDateT0','window','shiftby'})
                Allthetables360[tf]=pd.DataFrame(columns={'Stock1','Stock2','corr','RefDateTf','RefDateT0','window','shiftby'})
                Allthetables720[tf]=pd.DataFrame(columns={'Stock1','Stock2','corr','RefDateTf','RefDateT0','window','shiftby'})
            
    

    for tt in TT:
        tf=tt[1]
        Allthetables120[tf]['RefDateTf']=Allthetables120[tf]['RefDateTf'].astype('datetime64[ns]')     
        Allthetables120[tf]['RefDateT0']=Allthetables120[tf]['RefDateT0'].astype('datetime64[ns]')
        Allthetables120[tf]['window']=Allthetables120[tf]['window'].astype('int32')
        Allthetables120[tf]['shiftby']=Allthetables120[tf]['shiftby'].astype('int32')
        Allthetables120[tf]['corr']=Allthetables120[tf]['corr'].astype('float16') 
        Allthetables120[tf]['Stock1']=Allthetables120[tf]['Stock1'].astype('str') 
        Allthetables120[tf]['Stock2']=Allthetables120[tf]['Stock2'].astype('str') 
            
        Allthetables180[tf]['RefDateTf']=Allthetables180[tf]['RefDateTf'].astype('datetime64[ns]')     
        Allthetables180[tf]['RefDateT0']=Allthetables180[tf]['RefDateT0'].astype('datetime64[ns]')
        Allthetables180[tf]['window']=Allthetables180[tf]['window'].astype('int32')
        Allthetables180[tf]['shiftby']=Allthetables180[tf]['shiftby'].astype('int32')
        Allthetables180[tf]['corr']=Allthetables180[tf]['corr'].astype('float16') 
        Allthetables180[tf]['Stock1']=Allthetables180[tf]['Stock1'].astype('str') 
        Allthetables180[tf]['Stock2']=Allthetables180[tf]['Stock2'].astype('str') 
            
        Allthetables360[tf]['RefDateTf']=Allthetables360[tf]['RefDateTf'].astype('datetime64[ns]')     
        Allthetables360[tf]['RefDateT0']=Allthetables360[tf]['RefDateT0'].astype('datetime64[ns]')
        Allthetables360[tf]['window']=Allthetables360[tf]['window'].astype('int32')
        Allthetables360[tf]['shiftby']=Allthetables360[tf]['shiftby'].astype('int32')
        Allthetables360[tf]['corr']=Allthetables360[tf]['corr'].astype('float16') 
        Allthetables360[tf]['Stock1']=Allthetables360[tf]['Stock1'].astype('str') 
        Allthetables360[tf]['Stock2']=Allthetables360[tf]['Stock2'].astype('str') 
            
        Allthetables720[tf]['RefDateTf']=Allthetables720[tf]['RefDateTf'].astype('datetime64[ns]')     
        Allthetables720[tf]['RefDateT0']=Allthetables720[tf]['RefDateT0'].astype('datetime64[ns]')
        Allthetables720[tf]['window']=Allthetables720[tf]['window'].astype('int32')
        Allthetables720[tf]['shiftby']=Allthetables720[tf]['shiftby'].astype('int32')
        Allthetables720[tf]['corr']=Allthetables720[tf]['corr'].astype('float16') 
        Allthetables720[tf]['Stock1']=Allthetables720[tf]['Stock1'].astype('str') 
        Allthetables720[tf]['Stock2']=Allthetables720[tf]['Stock2'].astype('str') 
                
        if OptTables.lower()=='Yes'.lower():
            Allthetables[tf].append('CORR120',Allthetables120[tf],data_columns = True,index=False,format='table',min_itemsize=min_itemsizes)
            Allthetables[tf].append('CORR180',Allthetables180[tf],data_columns = True,index=False,format='table',min_itemsize=min_itemsizes)
            Allthetables[tf].append('CORR360',Allthetables360[tf],data_columns = True,index=False,format='table',min_itemsize=min_itemsizes)
            Allthetables[tf].append('CORR720',Allthetables720[tf],data_columns = True,index=False,format='table',min_itemsize=min_itemsizes)
        elif OptTables.lower()=='No'.lower():    
            Allthetables[tf].append('CORR120',Allthetables120[tf],index=False,format='table',min_itemsize=min_itemsizes)
            Allthetables[tf].append('CORR180',Allthetables180[tf],index=False,format='table',min_itemsize=min_itemsizes)
            Allthetables[tf].append('CORR360',Allthetables360[tf],index=False,format='table',min_itemsize=min_itemsizes)
            Allthetables[tf].append('CORR720',Allthetables720[tf],index=False,format='table',min_itemsize=min_itemsizes)
        
        elif OptTables.lower()=='Dumb'.lower():            
            Allthetables120[tf].to_hdf(Dumbtabfnames[tf],'CORR120',format='table',mode='a',append=True)
            Allthetables180[tf].to_hdf(Dumbtabfnames[tf],'CORR180',format='table',mode='a',append=True)
            Allthetables360[tf].to_hdf(Dumbtabfnames[tf],'CORR360',format='table',mode='a',append=True)
            Allthetables720[tf].to_hdf(Dumbtabfnames[tf],'CORR720',format='table',mode='a',append=True)
                    
        Allthetables120[tf]=pd.DataFrame(columns={'Stock1','Stock2','corr','RefDateTf','RefDateT0','window','shiftby'})
        Allthetables180[tf]=pd.DataFrame(columns={'Stock1','Stock2','corr','RefDateTf','RefDateT0','window','shiftby'})
        Allthetables360[tf]=pd.DataFrame(columns={'Stock1','Stock2','corr','RefDateTf','RefDateT0','window','shiftby'})
        Allthetables720[tf]=pd.DataFrame(columns={'Stock1','Stock2','corr','RefDateTf','RefDateT0','window','shiftby'})
    
    
    if OptTables.lower()=='Yes'.lower() or OptTables.lower()=='No'.lower():      
        for tf in Allthetables.keys():
            if OptTables.lower()=='Yes'.lower():
                Allthetables[tf].create_table_index('CORR120', optlevel=9, kind='full')
                Allthetables[tf].create_table_index('CORR180', optlevel=9, kind='full')
                Allthetables[tf].create_table_index('CORR360', optlevel=9, kind='full')
                Allthetables[tf].create_table_index('CORR720', optlevel=9, kind='full')  
                
            Allthetables[tf].close()
            
    if Compress.lower()=='Yes'.lower():
        onlyfiles = [ f for f in listdir(PathDict['CORRELATIONDATALINK_bydate']) if isfile(join(PathDict['CORRELATIONDATALINK_bydate'],f)) and 'CORR_' in f and '.h5' in f ]
        if desttag=='':
            print('Compressing all files as no dest tag is propagated..!!')
        else:
            onlyfiles=[f for f in onlyfiles if desttag in f]        
                
        kk=1        
        for ff in onlyfiles: 
            ot=-1
            print('packing file '+ff+' or no. '+str(kk)+' of '+str(len(onlyfiles)))
            kk=kk+1
            orgfl=PathDict['CORRELATIONDATALINK_bydate']+ff
            tpfl=PathDict['CORRELATIONDATALINK_bydate']+ff+"_temp_"+str(kk)+".h5"
            ot=sbp.call(["ptrepack","--chunkshape=50000","--propindexes","--complevel=9","--complib=blosc",orgfl,tpfl],stderr=sbp.STDOUT)
            if ot==0:
                sbp.call(["rm",orgfl],stderr=sbp.STDOUT)
                sbp.call(["mv",tpfl,orgfl],stderr=sbp.STDOUT)
            else:
                print('Could not pretpack the file so deleting the temp one')
                if os.path.isfile(tpfl):
                    sbp.call(["rm",tpfl],stderr=sbp.STDOUT)
                
    for ss in ErredFiles:
        print(ss+' has error')
    

    return ErredFiles    

# HDF5 small tables by date and window
def ConcateCorrelation_HDF5_byRefdate(desttag='', ftags=None,OptTables='No',Compress='No'):
    
    min_itemsizes={'Stock1': 8,'Stock2':8}    
    PathDict=GetConfig()
    onlyfiles = [ f for f in listdir(PathDict['CORRELATIONDATALINK_bydate']) if isfile(join(PathDict['CORRELATIONDATALINK_bydate'],f)) and '.h5' in f ]
    
    if desttag=='':
        desttag=''
    else:
        desttag=desttag+'_'
            
    TT=SDM.GenerateGeneralWindowsShiftby(120,20)   
    for tt in TT:          
        tf=tt[1]
        FF=[ss for ss in onlyfiles if tf.strftime("%Y-%m-%d") in ss]
                
        fs=[]
        if ftags==None:
            fs=[f for f in FF if '_CORR_2' in f or '_CORR_1' in f or '_CORR_3' in f]
            #print('No tags for the files: Concatenating all temp files')     
        else:
            #if isinstance(ftags, basestring):
            if type(ftags)==str:
                ftags=[ftags]
            for ss in FF:
                for tg in ftags:
                    if ss.find(tg) >=0:
                        fs.append(ss)
			

        fs=list(set(fs))
        fs.sort()
        print(' ')
        print('Working with the following files at time '+tf.strftime("%Y-%m-%d"))
        for sf in fs:        
            print(sf)
        
        
        Mfilename=PathDict['CORRELATIONDATALINK_bydate']+desttag+'CORR_'+tf.strftime("%Y-%m-%d")+'.h5'
        Masterfile=pd.HDFStore(Mfilename)

        for ff in fs:
            #print('Concatenating .. '+ff)
            try:
                sfile=pd.HDFStore(PathDict['CORRELATIONDATALINK_bydate']+ff)            
                if '/CORR120' in sfile.keys():
                    dd=sfile['CORR120']
                    #dd.drop_duplicates(subset=['Stock1','Stock2','RefDateTf','RefDateT0','window','shiftby'],inplace=True)
                    
                    if OptTables.lower()=='Yes'.lower():                                        
                        Masterfile.append('CORR120',dd,data_columns = True,index=False,format='table',min_itemsize=min_itemsizes,chunksize=25000)
                    else:
                        Masterfile.append('CORR120',dd,index=False,format='table',min_itemsize=min_itemsizes,chunksize=25000)
                
                if '/CORR180' in sfile.keys():    
                    dd=sfile['CORR180']
                    #dd.drop_duplicates(subset=['Stock1','Stock2','RefDateTf','RefDateT0','window','shiftby'],inplace=True)                    
                    if OptTables.lower()=='Yes'.lower():                                        
                        Masterfile.append('CORR180',dd,data_columns = True,index=False,format='table',min_itemsize=min_itemsizes,chunksize=25000)
                    else:
                        Masterfile.append('CORR180',dd,index=False,format='table',min_itemsize=min_itemsizes,chunksize=25000)
                
                if '/CORR360' in sfile.keys():           
                    dd=sfile['CORR360']
                    #dd.drop_duplicates(subset=['Stock1','Stock2','RefDateTf','RefDateT0','window','shiftby'],inplace=True)                    
                    if OptTables.lower()=='Yes'.lower():                                        
                        Masterfile.append('CORR360',dd,data_columns = True,index=False,format='table',min_itemsize=min_itemsizes,chunksize=25000)
                    else:    
                        Masterfile.append('CORR360',dd,index=False,format='table',min_itemsize=min_itemsizes,chunksize=25000)
                        
                if '/CORR720' in sfile.keys():            
                    dd=sfile['CORR720']
                    #dd.drop_duplicates(subset=['Stock1','Stock2','RefDateTf','RefDateT0','window','shiftby'],inplace=True)
                    
                    if OptTables.lower()=='Yes'.lower():                                        
                        Masterfile.append('CORR720',dd,data_columns = True,index=False,format='table',min_itemsize=min_itemsizes,chunksize=25000)
                    else:
                        Masterfile.append('CORR720',dd,index=False,format='table',min_itemsize=min_itemsizes,chunksize=25000)
                sfile.close()
            except:
                print('Error in file ' + ff)
                
 
                
        #if OptTables.lower()=='Yes'.lower():
        Masterfile.create_table_index('CORR120', optlevel=9, kind='full')
        Masterfile.create_table_index('CORR180', optlevel=9, kind='full')
        Masterfile.create_table_index('CORR360', optlevel=9, kind='full')
        Masterfile.create_table_index('CORR720', optlevel=9, kind='full')
        
        for ss in Masterfile.keys():
            dd=Masterfile[ss[1:]]
            if dd.empty:
                del Masterfile[ss[1:]]
        if len(Masterfile.keys())==0:
            Masterfile.close()
            print('Nothing in '+ Mfilename + ' so removing it')
            os.remove(Mfilename)
        else:
            Masterfile.close()
        
        if Compress.lower()=='Yes'.lower():
            ot=-1
            if os.path.isfile(Mfilename): 
                print('packing file '+Mfilename)
                orgfl=Mfilename
                tpfl=Mfilename[0:-3]+'_temp.h5'
                ot=sbp.call(["ptrepack","--chunkshape=50000","--propindexes","--complevel=9","--complib=blosc",orgfl,tpfl],stderr=sbp.STDOUT)
                if ot==0:
                    sbp.call(["rm",orgfl],stderr=sbp.STDOUT)
                    sbp.call(["mv",tpfl,orgfl],stderr=sbp.STDOUT)
                else:
                    print('Could not pretpack the file so deleting the temp one')
                    if os.path.isfile(tpfl): 
                        sbp.call(["rm",tpfl],stderr=sbp.STDOUT)
                    
                

# HDF5 small tables by date and window
def DeleteTempCorrFiles_bydate(ftgs=None):

    PathDict=GetConfig()
    onlyfiles = [ f for f in listdir(PathDict['CORRELATIONDATALINK_bydate']) if isfile(join(PathDict['CORRELATIONDATALINK_bydate'],f)) ]
    if ftgs==None:
        fs=[f for f in onlyfiles if '_CORR_2' in f or '_CORR_1' in f or '_CORR_3' in f]
    else:
        #if isinstance(ftgs, basestring):
        if type(ftgs)==str:    
            ftgs=[ftgs]
        fs=[]
        for ss in onlyfiles:
            for tg in ftgs:
                if ss.find(tg) >=0:
                    fs.append(ss)
    for ff in fs:
        print('deleting the taged files .. '+ff)
        os.remove(PathDict['CORRELATIONDATALINK_bydate']+ff)            
            
        
# the table is a NxN table with correlations
# Create Tables for 120,180,360,720 separately
# SQL small tables
def GenerateUpdateCorrelation_SQLdatabases_byRefdate():
    engine = sqlal.create_engine('mysql+mysqldb://...', pool_recycle=3600)

     

        
    
    

#%% THIS SECTION IS TO RUNLIKE A SCRIPT AND UPDATE ALL THE CORRELATION TABLES    
if __name__ == '__main__':
    PathDict=GetConfig()
    
    sys.argv[1]
    
    
    # Update HDF5 files by date
    if sys.argv[1]=='-u':
                
        store=pd.HDFStore('CORRLISTSTATUS.h5')
        dd=store['CorrList']
        DD=dd[dd['Status']=='-'][['Stock1','Stock2']]
        inds=DD.index
        DD=list(DD.values)
                
        if sys.argv[2]=='-MPI':
            print('Using MPI')
            
            Npairs=1500
            
            MPIdata=[[]]*MPIsize       
            
            pdTf=pd.datetime.today()
            pdT0=pd.datetime(2006,1,1)
            pdT00=pd.datetime(2002,1,1)
            ShiftBy=20
            
            i=0
            Slist=[]
            if MPIrank == 0:
                onlyfiles = [ f for f in listdir(PathDict['CORRELATIONDATALINK']) if isfile(join(PathDict['CORRELATIONDATALINK'],f)) ]
                
 
                j=0
                p=0
                totcnt=0
                while p<len(MPIdata):        
                    k=Npairs
                    lb=j        
                    ub=j+k
                    if ub>len(DD):
                        ub=len(DD)
                    MPIdata[p]=DD[lb:ub]
                    totcnt=totcnt+len(DD[lb:ub])
                    j=j+k
                    p=p+1
                if j<len(DD):
                    MPIdata[-1]=MPIdata[-1]+DD[j:]
                    totcnt=totcnt+len(DD[j:])
                    
                dd.loc[inds[0:totcnt],'Status']='Done'
                store['CorrList']=dd
                store.close()
            else:
                MPIdata = None
                
            MPIdata = comm.scatter(MPIdata, root=0)


            if MPIrank<20:   
                time.sleep(MPIrank*5)
            else:
                time.sleep(MPIrank*1)

            tt=pd.datetime.today().strftime("%Y_%m_%d_%H_%M_%S")
            UpdateCorrelations(MPIdata,fileprepend=tt)
            
                

            recdata=tt
            recdata = comm.gather(recdata, root=0)
            
            if MPIrank == 0:
                ffs=[]
                for i in range(0,MPIsize):
                   ffs.append(recdata[i])
                   print(recdata[i])
            else:
                recdata=None
        
        
        
                
        elif sys.argv[2]=='-M':
            print('Using MultiProcessings')
            n=int(len(DD)/100)
            SM=SDM.chunkinator(DD, n)
            
            p = Pool(n)
            print('Updating the Correlation')
            start_time = time.time() 
            p.map(UpdateCorrelations, SM)
            print("Correlation Update took = " % (time.time() - start_time))
        
        # Updating the Status list
        elif sys.argv[2]=='-U':
            UpdateCorrStatusList()
            
            
    # Concat HDF5 files by date
    if sys.argv[1]=='-C':
        ConcateCorrelation_HDF5_byRefdate()
        
    # delete temp files
    if sys.argv[1]=='-D':
        DeleteTempCorrFiles()
   
