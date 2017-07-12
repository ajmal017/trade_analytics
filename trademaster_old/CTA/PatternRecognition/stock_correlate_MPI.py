# -*- coding: utf-8 -*-
"""
Created on Tue Feb 10 20:35:30 2015

@author: nagnanamus
Generate the features and store them
"""

from __future__ import division
from mpi4py import MPI

import os.path
import sys
comm = MPI.COMM_WORLD
MPIsize = comm.Get_size()
MPIrank = comm.Get_rank()
MPIname = MPI.Get_processor_name()

import CompTechAnalysis.StockData_Manager.StockDataManager as SDM  
import CompTechAnalysis.StockData_Analysis.FeaturesExtraction as fe
import CompTechAnalysis.Pattern_recos_models.PatternReco_FlatStocks as pflat
import CompTechAnalysis.Pattern_recos_models.stock_correlate as stkcorr
from CompTechAnalysis.GenConfig import CreateConfigFile
import CompTechAnalysis.Stock_Doc_Gen.DataDocGenerators as ddg

import pandas as pd
import json 
import time
from itertools import combinations,tee
import itertools
import socket

from os import listdir
from os.path import isfile, join



if sys.platform in ['win32','win64']:
    PathDict={'StockStatusList':'C:\\Users\\Nagnanamus\\Copy\\python-finance\\StockSTATUSlist.h5',
              'StockData_daily':'C:\\Users\\Nagnanamus\\Copy\\python-finance\\Data\\StockData_daily.h5',
              'StockData_weekly':'C:\\Users\\Nagnanamus\\Copy\\python-finance\\Data\\StockData_weekly.h5',
              'StockData_monthly':'C:\\Users\\Nagnanamus\\Copy\\python-finance\\Data\\StockData_monthly.h5',   
              'CorrelationMasterTable':'C:\\Users\\Nagnanamus\\Copy\\python-finance\\Data\\MASTERCORRELATIONDATA.h5',
              'CORRELATIONDATALINK':'C:\\Users\\Nagnanamus\\Copy\\python-finance\\Data\\CorrelationData\\CorrelationData_raw\\',
              'CORRELATIONDATALINK_bydate':'C:\\Users\\Nagnanamus\\Copy\\python-finance\\Data\\CorrelationData\\CorrelationData_byRefdate\\',
              'LinearFitMasterFeaturesTable':'C:\\Users\\Nagnanamus\\Copy\\python-finance\\Data\\MASTERLINEARFEATURE.h5',
              'LinearFitMasterFitDataTable':'C:\\Users\\Nagnanamus\\Copy\\python-finance\\Data\\MASTERLINEARFITDATA.h5',              
              'LinearFitPlotslink':'C:\\Users\\Nagnanamus\\Copy\\python-finance\\Plots\\LinearTrendChannels\\',
              'LinearFitDatalink':'C:\\Users\\Nagnanamus\\Copy\\python-finance\\Data\\LinearFitFeatureData\\LinearFits\\',
              'LinearFitDatalink_bydate':'C:\\Users\\Nagnanamus\\Copy\\python-finance\\Data\\LinearFitFeatureData\\LinearFits\\LinearFitsByDate\\',
              'LinearFitFeaturelink':'C:\\Users\\Nagnanamus\\Copy\\python-finance\\Data\\LinearFitFeatureData\\LinearFeatures\\',       
              'LinearFitFeaturelink_bydate':'C:\\Users\\Nagnanamus\\Copy\\python-finance\\Data\\LinearFitFeatureData\\LinearFeatures\\LinearFeaturesByDate\\',
              'LinearFitFeaturesName':'AllFeaturesData_',
              'LinearFitDataName':'LinerFitWindowDict_',
              'LinearFitPlotname':'LinearTrendFit_',
              'CORRELATIONTABLEname':'CORR_',
              'pdTf':pd.datetime.today(),
              'pdT0':pd.datetime(2006,1,1),
              'pdT00':pd.datetime(2002,1,1)}



elif 'nagnanamus' in socket.getfqdn():
    PathDict={'StockStatusList':'/home/nagnanamus/Copy/python-finance/StockSTATUSlist.h5',
              'StockData_daily':'/home/nagnanamus/Copy/python-finance/Data/StockData_daily.h5',
              'StockData_weekly':'/home/nagnanamus/Copy/python-finance/Data/StockData_weekly.h5',
              'StockData_monthly':'/home/nagnanamus/Copy/python-finance/Data/StockData_monthly.h5',   
              'CorrelationMasterTable':'/home/nagnanamus/Copy/python-finance/Data/MASTERCORRELATIONDATA.h5',
              'CORRELATIONDATALINK':'/home/nagnanamus/Copy/python-finance/Data/CorrelationData/CorrelationData_raw/',
              'CORRELATIONDATALINK_bydate':'/home/nagnanamus/Copy/python-finance/Data/CorrelationData/CorrelationData_byRefdate/',
              'LinearFitMasterFeaturesTable':'/home/nagnanamus/Copy/python-finance/Data/MASTERLINEARFEATURE.h5',
              'LinearFitMasterFitDataTable':'/home/nagnanamus/Copy/python-finance/Data/MASTERLINEARFITDATA.h5',              
              'LinearFitPlotslink':'/home/nagnanamus/Copy/python-finance/Plots/LinearTrendChannels/',
              'LinearFitDatalink':'/home/nagnanamus/Copy/python-finance/Data/LinearFitFeatureData/LinearFits/',
              'LinearFitDatalink_bydate':'/home/nagnanamus/Copy/python-finance/Data/LinearFitFeatureData/LinearFits/LinearFitsByDate/',
              'LinearFitFeaturelink':'/home/nagnanamus/Copy/python-finance/Data/LinearFitFeatureData/LinearFeatures/',       
              'LinearFitFeaturelink_bydate':'/home/nagnanamus/Copy/python-finance/Data/LinearFitFeatureData/LinearFeatures/LinearFeaturesByDate/',
              'LinearFitFeaturesName':'AllFeaturesData_',
              'LinearFitDataName':'LinerFitWindowDict_',
              'LinearFitPlotname':'LinearTrendFit_',
              'CORRELATIONTABLEname':'CORR_',
              'pdTf':pd.datetime.today(),
              'pdT0':pd.datetime(2006,1,1),
              'pdT00':pd.datetime(2002,1,1)}

elif 'ccr' in socket.getfqdn():
    PathDict={'StockStatusList':'StockSTATUSlist.h5',
              'StockData_daily':'Data/StockData_daily.h5',
              'StockData_weekly':'Data/StockData_weekly.h5',
              'StockData_monthly':'Data/StockData_monthly.h5',   
              'CorrelationMasterTable':'Data/MASTERCORRELATIONDATA.h5',
              'CORRELATIONDATALINK':'Data/CorrelationData/CorrelationData_raw/',
              'CORRELATIONDATALINK_bydate':'Data/CorrelationData/CorrelationData_byRefdate/',
              'LinearFitMasterFeaturesTable':'Data/MASTERLINEARFEATURE.h5',
              'LinearFitMasterFitDataTable':'Data/MASTERLINEARFITDATA.h5',              
              'LinearFitPlotslink':'Plots/LinearTrendChannels/',
              'LinearFitDatalink':'Data/LinearFitFeatureData/LinearFits/',
              'LinearFitDatalink_bydate':'Data/LinearFitFeatureData/LinearFits/LinearFitsByDate/',
              'LinearFitFeaturelink':'Data/LinearFitFeatureData/LinearFeatures/',       
              'LinearFitFeaturelink_bydate':'Data/LinearFitFeatureData/LinearFeatures/LinearFeaturesByDate/',
              'LinearFitFeaturesName':'AllFeaturesData_',
              'LinearFitDataName':'LinerFitWindowDict_',
              'LinearFitPlotname':'LinearTrendFit_',
              'CORRELATIONTABLEname':'CORR_',
              'pdTf':pd.datetime.today(),
              'pdT0':pd.datetime(2006,1,1),
              'pdT00':pd.datetime(2002,1,1)}
          
         
   
#PathDict={'StockData_daily':'/home/nag/Copy/python-finance/Data/StockData_daily.h5',
#          'StockData_weekly':'/home/nag/Copy/python-finance/Data/StockData_weekly.h5',
#          'StockData_monthly':'/home/nag/Copy/python-finance/Data/StockData_monthly.h5',
#          'LinearFitPlotDataPath':'/home/nag/Copy/python-finance/Plots/LinearTrendChannels/',
#          'LinearFitFeatures':'/home/nag/Copy/python-finance/Plots/LinearTrendChannels/MASTERFEATURE.h5'}
          
time.sleep(MPIrank*0.05)
        
CreateConfigFile(PathDict)


#STDO=SDM.StockDataOperations()
#%%  Go thru each stock



Npairs=2


MPIdata=[[]]*MPIsize 

pdTf=pd.datetime.today()
pdT0=pd.datetime(2006,1,1)
pdT00=pd.datetime(2002,1,1)
ShiftBy=20
#TT=SDM.GenerateGeneralWindowsShiftby(120,20)

i=0
Slist=[]
if MPIrank == 0:
    #onlyfiles = [ f for f in listdir(PathDict['CORRELATIONDATALINK']) if isfile(join(PathDict['CORRELATIONDATALINK'],f)) ]
    #print('ok')
    #Slist=STDO.GetFilteredListofStocks(pdT00,pdT0,pdTf)
    #L=combinations(Slist, 2)   
    #SS=list(L)
    tf=pd.datetime.today()
    tf1=tf - pd.DateOffset(15)
    store=pd.HDFStore(PathDict['StockStatusList'])
    dd=store['CorrStatus']
    DD=dd[dd['LastUpdated']<=tf1][['Stock1','Stock2']]
    if DD.empty:
        DD=[]
    else:
        inds=DD.index
        DD=list(DD.values)
	
          
    if len(DD)>0:        
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
        if j+Npairs>=len(DD):
            MPIdata[-1]=MPIdata[-1]+DD[j:]
            totcnt=totcnt+len(DD[j:])
            
        dd.loc[inds[0:totcnt],'LastUpdated']=pd.datetime.today().replace(hour=0, minute=0, second=0,microsecond=0)
        


else:
   MPIdata = None


#STDO.CloseDataFiles()

    
    
MPIdata = comm.scatter(MPIdata, root=0)


if MPIrank<20:   
    time.sleep(MPIrank*5)
else:
    time.sleep(MPIrank*1)

corrtable=pd.DataFrame()

for ss in MPIdata:
    ss1=ss[0]
    ss2=ss[1]
    print ('Processor '+str(MPIrank)+' of node '+str(MPIname)+ ' is working on '+ss1+' and '+ss2  )
    try:
	
        start_time = time.time()

        window=120
        ShiftBy=20
        corrtable120=stkcorr.GetCorrelation(ss1,ss2,pdT0,pdTf,window,ShiftBy)
        print ('Done with 120 window')
        
        
        window=180
        ShiftBy=20
        corrtable180=stkcorr.GetCorrelation(ss1,ss2,pdT0,pdTf,window,ShiftBy)
        print ('Done with 180 window')
        
        window=360
        ShiftBy=20
        corrtable360=stkcorr.GetCorrelation(ss1,ss2,pdT0,pdTf,window,ShiftBy)
        print ('Done with 360 window')
        
        window=720
        ShiftBy=20
        corrtable720=stkcorr.GetCorrelation(ss1,ss2,pdT0,pdTf,window,ShiftBy)
        print ('Done with 720 window')
        
        corrtable=pd.concat([corrtable,corrtable120,corrtable180,corrtable360,corrtable720])

          
        print (ss1+'+'+ss2+': Done !!! in '+str(time.time() - start_time)+' seconds')

        #corrtable.to_csv(PathDict['CORRELATIONDATALINK']+'CORR_'+ss1+'_'+ss2+'.csv')
        
    except:
        print (ss1+'+'+ss2+' Feature+LinearFeature Error *****************************************************'    )

 
tt=pd.datetime.today().strftime("%Y_%m_%d_%H_%M_%S")

if not corrtable.empty:
    stkcorr.GenerateUpdateCorrelation_HDF5_byRefdate(File=None,CorrTable=corrtable,AlphaBetFile=tt)    

print('ALl done on processor')
recdata=tt
recdata = comm.gather(recdata, root=0)
print('Sending data to 0th processor')

if MPIrank == 0:
    ffs=[]
    for i in range(0,MPIsize):
       ffs.append(recdata[i])
       print('done tags .. '+recdata[i])
    #create a new tag and concat all... delete the previous tags   
    desttag=pd.datetime.today().strftime("%Y_%m_%d_%H_%M_%S")   
    stkcorr.ConcateCorrelation_HDF5_byRefdate(desttag=desttag, ftags=ffs)   
    
    store['CorrStatus']=dd
    store.close()
else:
    recdata=None
