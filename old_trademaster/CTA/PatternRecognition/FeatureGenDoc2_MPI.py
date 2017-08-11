# -*- coding: utf-8 -*-
"""
Created on Tue Feb 10 20:35:30 2015

@author: nagnanamus
Generate the features and store them
"""

from __future__ import division
from mpi4py import MPI

import os.path

comm = MPI.COMM_WORLD
MPIsize = comm.Get_size()
MPIrank = comm.Get_rank()
MPIname = MPI.Get_processor_name()

import CompTechAnalysis.StockData_Manager.StockDataManager as SDM  
import CompTechAnalysis.StockData_Analysis.FeaturesExtraction as fe
import CompTechAnalysis.Pattern_recos_models.PatternReco_FlatStocks as pflat
from CompTechAnalysis.GenConfig import CreateConfigFile
import CompTechAnalysis.Stock_Doc_Gen.DataDocGenerators as ddg

import pandas as pd
import json 
import time


PathDict={'StockData_daily':'Data/StockData_daily.h5',
          'StockData_weekly':'Data/StockData_weekly.h5',
          'StockData_monthly':'Data/StockData_monthly.h5',
          'LinearFitPlotDataPath':'Plots/LinearTrendChannels/',
          'LinearFitFeatures':'Plots/LinearTrendChannels/MASTERFEATURE.h5'}
   
#PathDict={'StockData_daily':'/home/nag/Copy/python-finance/Data/StockData_daily.h5',
#          'StockData_weekly':'/home/nag/Copy/python-finance/Data/StockData_weekly.h5',
#          'StockData_monthly':'/home/nag/Copy/python-finance/Data/StockData_monthly.h5',
#          'LinearFitPlotDataPath':'/home/nag/Copy/python-finance/Plots/LinearTrendChannels/',
#          'LinearFitFeatures':'/home/nag/Copy/python-finance/Plots/LinearTrendChannels/MASTERFEATURE.h5'}
          
time.sleep(MPIrank*0.05)
if not os.path.isfile("config.txt"):          
    CreateConfigFile(PathDict)

df=SDM.LoadStockGroups()



#%% Cleaning the Stockdone, RunLsit and Error lists
LinFitComputeDoneList=json.load(open('LinFitComputeDoneList.txt','r'))
LinFitComputeDoneList['StockDoneList']=[]
LinFitComputeDoneList['RunList']=[]
LinFitComputeDoneList['ErrorList']=[]

for cnt in range(0,len(df.index)) :
    ss=df.iloc[cnt]['Symbol']        
    if os.path.isfile(PathDict['LinearFitPlotDataPath']+'AllFeaturesData_'+ss+'.h5'):
        LinFitComputeDoneList['StockDoneList'].append(ss)
        
json.dump(LinFitComputeDoneList, open('LinFitComputeDoneList.txt','w'))

#%%
STDO=SDM.StockDataOperations()
SL3=[]
SG3=[]
SL2=[]
SG2=[]
for cnt in range(0,len(df.index)) :
    ss=df.iloc[cnt]['Symbol']     
    stks={ss:[[2006,1,1],[]]} 
    try:    
        DFF=STDO.PullDataSymbolsSet(stks)
        DF=DFF[ss]
        if (DF.index[-1]-DF.index[0]).days<750 or len(DF[DF['Close']<3].index)>0.5*len(DF.index) or len(DF[DF['Volume']<5000].index)>0.5*len(DF.index) or  len(DF[DF['Volume']==0].index)>10 or len(DF[DF['Close']==0].index)>10 or len(DF[DF['Close']<=1].index)>0.25*len(DF.index) :
            SL3.append(ss)
        else:
            SG3.append(ss)
        if (DF.index[-1]-DF.index[0]).days<750 or len(DF[DF['Close']<2].index)>0.5*len(DF.index) or len(DF[DF['Volume']<5000].index)>0.5*len(DF.index) or  len(DF[DF['Volume']==0].index)>10 or len(DF[DF['Close']==0].index)>10 or  len(DF[DF['Close']<=1].index)>0.25*len(DF.index) :
            SL2.append(ss)
        else:
            SG2.append(ss)    
    except:
        SL2.append(ss)
        SL3.append(ss)

#%%  Go thru each stock


if os.path.isfile("LinFitComputeDoneList.txt") and MPIrank == 0: 
    LinFitComputeDoneList=json.load(open('LinFitComputeDoneList.txt','r'))
elif MPIrank == 0:
    LinFitComputeDoneList={'StockDoneList':[],'ErrorList':[],'RunList':[]}

TempList={'StockDoneList':[],'ErrorList':[],'RunList':[]}

STDO=SDM.StockDataOperations()

# Number of stocks per processor
Nstocks =10

MPIdata=[[]]*MPIsize 
jj=0
if MPIrank == 0:
    
    pp=[]      
    for cnt in range(0,len(df.index)) :
        ss=df.iloc[cnt]['Symbol']        
        try:
            flg=False
            for mp in MPIdata:
                if ss in mp:
                    flg=True
            if (ss not in LinFitComputeDoneList['StockDoneList']) and (ss not in pp) and (ss not in LinFitComputeDoneList['ErrorList'] ) and (ss not in LinFitComputeDoneList['RunList'] ) and flg==False:
                stks={ss:[[2006,1,1],[]]} 
                DFF=STDO.PullDataSymbolsSet(stks)
                DF=DFF[ss]
                if (DF.index[-1]-DF.index[0]).days<750 or len(DF[DF['Close']<3].index)>0.5*len(DF.index) or len(DF[DF['Volume']<5000].index)>0.5*len(DF.index) or  len(DF[DF['Volume']==0].index)>10 or len(DF[DF['Close']==0].index)>10 or len(DF[DF['Close']<=1].index)>10:
                    print ss+' is below the $3 threshold or 5000 vol threshold or $1 or 0Vol or 0Close or has < 750 days data'
                    LinFitComputeDoneList['ErrorList'] .append(ss) 
                    continue
                pp.append(ss)
		LinFitComputeDoneList['RunList'].append(ss)
        except:
            print str(cnt)+' Stock is having error' 
            LinFitComputeDoneList['ErrorList'] .append(ss)            
            
        if len(pp)>=Nstocks:
            MPIdata[jj]=pp
            jj=jj+1
            pp=[]
            if jj>=MPIsize:
                break
    if len(pp)>0 and jj<MPIsize:
        MPIdata[jj]=pp
else:
   MPIdata = None


    
STDO.CloseDataFiles()
MPIdata = comm.scatter(MPIdata, root=0)

if MPIrank==0:
    json.dump(LinFitComputeDoneList, open('LinFitComputeDoneList.txt','w'))

if MPIrank<20:   
    time.sleep(MPIrank*1)
else:
    time.sleep(MPIrank*0.1)

if not isinstance(MPIdata, list):
    MPIdata=[MPIdata]
for ss in MPIdata:
    print 'Processor '+str(MPIrank)+' of node '+str(MPIname)+ ' is working on '+ss+' of list '+ str(MPIdata)    
    try:
	
        start_time = time.time()
        STDO=SDM.StockDataOperations() #year,month,day
        #stks={ss:[[2005,1,1],[2015,2,1]]} 
        stks={ss:[[2006,1,1],[]]} 
        DFF=STDO.PullDataSymbolsSet(stks)
        DF=DFF[ss].copy()
        STDO.CloseDataFiles()
        
        TC=pflat.TrendChannels(DF,'Close',ss,PathDict['LinearFitPlotDataPath'])
        
        window=120
        ShiftBy=20
        TC.IntervalWindowChannelFitting(window,ShiftBy,NormalizeFeatwindow='No')
        dd120=fe.GenerateFeatureTable(DF,ss,ShiftBy,window,Normalize2window='No')
        ds120=TC.LinearFeatureFrame
        TC.MatplotlibIntervalWindowChannelFitting(formattype='png')
        print ss+': Done with 120 window'
        
        
        window=180
        ShiftBy=20
        TC.IntervalWindowChannelFitting(window,ShiftBy,NormalizeFeatwindow='No')
        dd180=fe.GenerateFeatureTable(DF,ss,ShiftBy,window,Normalize2window='No')
        ds180=TC.LinearFeatureFrame
        TC.MatplotlibIntervalWindowChannelFitting(formattype='png')
        print ss+': Done with 180 window'
        
        window=360
        ShiftBy=20
        TC.IntervalWindowChannelFitting(window,ShiftBy,NormalizeFeatwindow='No')
        dd360=fe.GenerateFeatureTable(DF,ss,ShiftBy,window,Normalize2window='No')
        ds360=TC.LinearFeatureFrame    
        TC.MatplotlibIntervalWindowChannelFitting(formattype='png')
        print ss+': Done with 360 window'
        
        window=720
        ShiftBy=20
        TC.IntervalWindowChannelFitting(window,ShiftBy,NormalizeFeatwindow='No')
        dd720=fe.GenerateFeatureTable(DF,ss,ShiftBy,window,Normalize2window='No')
        ds720=TC.LinearFeatureFrame    
        TC.MatplotlibIntervalWindowChannelFitting(formattype='png')
        print ss+': Done with 720 window'
        
        dd=pd.concat([dd120,dd180,dd360,dd720])
        ds=pd.concat([ds120,ds180,ds360,ds720])
    	
        TC.SaveTrendIntervalWindowChannelFits()
        
        gg=pd.concat([dd,ds],axis=1)
        gg=gg.T.drop_duplicates().T
        
        print 'Saving Features of '+ss
        MASTERFEATURE = pd.HDFStore(PathDict['LinearFitPlotDataPath']+'AllFeaturesData_'+ss+'.h5')
        #MASTERFEATURE[ss+'/BasicFeatures']=dd
        #MASTERFEATURE[ss+'/LinearFeatures']=ds
        #MASTERFEATURE[ss+'/CombinedFeatures']=gg
        MASTERFEATURE['Features']=gg
        MASTERFEATURE.close()        
        
        TC.PackandRemoveSymbPicFolder()
        
        TempList['StockDoneList'].append(ss)
        
        print ss+': Done !!! in '+str(time.time() - start_time)+' seconds'
        
    except:
        print ss+' Feature+LinearFeature Error *****************************************************'    
        TempList['ErrorList'].append(ss)



recdata=TempList
recdata = comm.gather(recdata, root=0)

if MPIrank == 0:
   LinFitComputeDoneList=json.load(open('LinFitComputeDoneList.txt','r'))
   for i in range(0,MPIsize):
      LinFitComputeDoneList['StockDoneList']=LinFitComputeDoneList['StockDoneList']+recdata[i]['StockDoneList']
      LinFitComputeDoneList['ErrorList'] =LinFitComputeDoneList['ErrorList'] +recdata[i]['ErrorList']
   LinFitComputeDoneList['StockDoneList']=list(set(LinFitComputeDoneList['StockDoneList']))
   LinFitComputeDoneList['ErrorList'] =list(set(LinFitComputeDoneList['ErrorList'] ))
   for sp in LinFitComputeDoneList['StockDoneList']:
      if sp in LinFitComputeDoneList['RunList']:
          LinFitComputeDoneList['RunList'].remove(sp)
   for sp in LinFitComputeDoneList['ErrorList']:
      if sp in LinFitComputeDoneList['RunList']:
          LinFitComputeDoneList['RunList'].remove(sp)
   json.dump(LinFitComputeDoneList, open('LinFitComputeDoneList.txt','w'))
      
else:
    recdata=None
   
#%% HTML DOC generation
#if MPIrank == 0:
#    ddg=reload(ddg)
#    MASTERFEATURE = pd.HDFStore(PathDict['LinearFitFeatures'])
#
#    # Regular Table and Plots
#    ddg.GenerateHTMLDOC_PlotsTable_type2(PathDict['LinearFitPlotDataPath'],MASTERFEATURE['All'])
#
#    # Plot all the charts side by side
#    ddg.GenerateHTMLDOC_Plots_SideBySide(PathDict['LinearFitPlotDataPath'],MASTERFEATURE['All'],RowSize=3)
#    
#    #Table Plots and input form
#    ddg.GenerateHTMLDOC_PlotsTableForms2Google_type1(PathDict['LinearFitPlotDataPath'],MASTERFEATURE['All'])
#   
#   
   
   
