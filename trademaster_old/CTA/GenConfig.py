# -*- coding: utf-8 -*-
"""
Created on Wed Feb 18 16:14:52 2015

@author: nagnanamus
"""
from __future__ import division
import yaml
import collections
import json
import pandas as pd
import numpy as np
import os
from pathlib import Path
from collections import OrderedDict
import sys
from sqlalchemy.dialects.mysql import TINYINT,BIGINT,VARCHAR,DATE,DECIMAL,FLOAT,SMALLINT,DATE,INTEGER

#%%  Side ways concatenation options
opt_std={
      0:'Just append below, ignore the extra columns',
      1:'Side concat if index same, add remaining indicies at bottom, keep the extra columns',
      2:'Side concat if index same, add remaining indicies at bottom, ignore extra columns',    
      3:'Side concat if index same, leave remaining indicies, keep extra columns',
      4:'Side concat if index same, leave remaining indicies, ignore extra columns'
      }

def GetWindowAvgTradeDays(window):
    if window==120:
        return 84
    if window==180:
        return 125    
    if window==360:
        return 250  
    if window==720:
        return 495          


def GetWindowTfs(Tf,window):
    t0=Tf-pd.DateOffset(window)
    return [t0,Tf]
    
def GetRefDates(ShiftBy,Tlb=pd.datetime(2006,1,1),Tub=None):
    pdDatest0=pd.datetime(2002,1,15)    
    tdy=pd.datetime.today()    
    if Tub==None:
        Tub=tdy
    TTF=[]
    tf=pdDatest0 
    if tf>=Tlb and tf<=Tub:
        TTF.append(tf)
        
    while tf<=tdy:
        tt=tf+pd.DateOffset(ShiftBy)
        if tt.dayofweek==5:
            tt=tt-pd.DateOffset(1)
        if tt.dayofweek==6:
            tt=tt-pd.DateOffset(2)
        if tt>=Tlb and tt<=Tub:    
            TTF.append(tt)
        tf=tf+pd.DateOffset(ShiftBy)
        
    return TTF



def GetClosestRefdate(tf,ShiftBy):
    
        
    TF=GetRefDates(ShiftBy)
    mn=1000000
    mp=tf
    for i in range(0,len(TF)):
        t=np.abs((TF[i]-tf).days)
        if t<mn:
            mn=t
            mp=TF[i]

    return mp
    

    
def GenerateGeneralWindowsShiftby(window,ShiftBy):
    
        
    TF=GetRefDates(ShiftBy)
    pdDatesIndex=[]
    for i in range(0,len(TF)):
        t0=TF[i]-pd.DateOffset(window)
        pdDatesIndex.append([t0,TF[i]])
    
    return pdDatesIndex      


def Dates2str(dates,fmt="%Y-%m-%d"): # "%b %d\n %Y"

    dd=[]    
    for ind in range(len(dates)):
        dd.append(  dates[ind].strftime(fmt)  )
    
    return np.array(dd)

def Dates2days(dates):

    dd=[]    
    for ind in range(len(dates)):
        dd.append( ( dates[ind] - pd.datetime(2002,1,1)).days )
    
    return np.array(dd)

def days2Dates(days):

    dd=[]    
    for ind in range( len(days) ):
        dd.append( pd.datetime(2002,1,1) + pd.DateOffset( days[ind] ) )
    
    return np.array(dd)


#%%
windows_std=[120,180,360,720]
ShiftBy_std=[20]

# FLATNESS_NORMS={720:0.3,
#                 360:0.35,
#                 180:0.45,
#                 120:0.45}

FLATNESS_NORMS=lambda window: np.interp(window,[720,360,180,120],[0.3,0.35,0.45,0.45])

#TODO: DO it
FeatureTableDescription= {
         'RefDateTf': { 
               'astype':'datetime64[ns]' ,
               'mysqldtype':DATE, 
               'webcode':'F1', 
               'short':  "Ref. Window End Date" , 
               'long': "The moving window is referenced by its ending date" ,
               'table':['Features','LinearFits'],
               'Disp':'Yes',
               'FilterDisp':'No',
               'SortDisp':'Yes'
               },

         'RefDateT0' : { 
               'astype':'datetime64[ns]' ,
               'mysqldtype':DATE,  
               'webcode':'F2', 
               'short':  "Ref. Window Start Date" , 
               'long': "The stock price data of the moving window is completely determined by its starting and ending date",
               'table':['Features','LinearFits'] ,
               'Disp':'No',
               'FilterDisp':'No',
               'SortDisp':'No'
               },

         'Symbol' : {   
               'astype':'str',  
               'mysqldtype':VARCHAR(5), 
               'min_itemsize': 10, 
               'webcode':'F3', 
               'short':  "Symbol" ,
               'long': "Ticker or symbol of the stock" ,
               'table':['Features','LinearFits'],
               'Disp':'Yes',
               'FilterDisp':'No',
               'SortDisp':'No'
               },

         'window' : {   
               'astype':'int32',  
               'mysqldtype':INTEGER, 
               'webcode':'F4', 
               'short':  "Window length" , 
               'long': "Length of the moving window",
               'table':['Features','LinearFits'] ,
               'Disp':'No',
               'FilterDisp':'No',
               'SortDisp':'No'
               },

         'Days2epoch' : {  
               'astype':'int32',
               'mysqldtype':INTEGER, 
               'webcode':'F8', 
               'short':  "# Rel. Vol. >1.5" , 
               'long': "The number of candles in the current window with relative volume (with respect to 10-day simple moving volume average) greater than 1.5" ,
               'table':['Features'] ,
               'Disp':'Yes',
               'FilterDisp':'Yes',
               'SortDisp':'Yes'
               },

         'RV2_10SMA' : {
               'astype':'int32',
               'mysqldtype':INTEGER, 
               'webcode':'F9', 
               'short':  "# Rel. Vol. >2" , 
               'long': "The number of candles in the current window with relative volume (with respect to 10-day simple moving volume average) greater than 2",
               'table':['Features']  ,
               'Disp':'Yes',
               'FilterDisp':'Yes',
               'SortDisp':'Yes'
               },

         'RV3' : {
               'astype':'int32',
               'mysqldtype':INTEGER, 
               'webcode':'F10', 
               'short':  "# Rel. Vol. >3" , 
               'long': "The number of candles in the current window with relative volume (with respect to 10-day simple moving volume average) greater than 3" ,
               'table':['Features'] ,
               'Disp':'Yes',
               'FilterDisp':'Yes',
               'SortDisp':'Yes'
               },

         'RV4' : {
               'astype':'int32',
               'mysqldtype':INTEGER, 
               'webcode':'F11', 
               'short':  "# Rel. Vol. >4" , 
               'long': "The number of candles in the current window with relative volume (with respect to 10-day simple moving volume average) greater than 4" ,
               'table':['Features'] ,
               'Disp':'Yes',
               'FilterDisp':'Yes',
               'SortDisp':'Yes'
               },

         'MXRV' : {  
               'astype':'float16' ,
               'mysqldtype':FLOAT ,
               'webcode':'F12', 
               'short':  "Maximum Rel. Vol." , 
               'long': "The maximum relative volume (with respect to 10-day simple moving volume average) in the current window" ,
               'table':['Features'] ,
               'Disp':'Yes',
               'FilterDisp':'Yes',
               'SortDisp':'Yes'
               },

         'FutMXRtQt' : {
               'astype':'float16' ,
               'mysqldtype':FLOAT,
               'webcode':'F13', 
               'short':  "Max. future 3mon return" , 
               'long': "The maximum possible return in the period (End date+ 3 months) " ,
               'table':['Features'] ,
               'Disp':'Yes',
               'FilterDisp':'Yes',
               'SortDisp':'Yes'
               },

         'FutMXRtHf' : {
               'astype':'float16' ,
               'mysqldtype':FLOAT,
               'webcode':'F14', 
               'short':  "Max. future 6mon return" , 
               'long': "The maximum possible return in the period (End date+ 6 months) " ,
               'table':['Features'] ,
               'Disp':'Yes',
               'FilterDisp':'Yes',
               'SortDisp':'Yes'
               },

         'FutMXRtAn' : {
               'astype':'float16' ,
               'mysqldtype':FLOAT,
               'webcode':'F15', 
               'short':  "Max. future 1y return" , 
               'long': "The maximum possible return in the period (End date+ 1y) " ,
               'table':['Features'] ,
               'Disp':'Yes',
               'FilterDisp':'Yes',
               'SortDisp':'Yes'
               },
        
         'MX2MXRV' :  {
               'astype':'int32',
               'mysqldtype':INTEGER,
               'webcode':'F16', 
               'short':  "# days, Max.-Max. Rel. Vol." , 
               'long': "The number of days between the first 2 maximum relative volumes (10-day volume SMA)" ,
               'table':['Features'] ,
               'Disp':'Yes',
               'FilterDisp':'Yes',
               'SortDisp':'Yes'
               },
         
         'SQZ1MXRV' : {
               'astype':'float16',
               'mysqldtype':FLOAT ,
               'webcode':'F17', 
               'short':  "Candle Squeeze 1" , 
               'long': " (C-O)/(H-L) at Max Rel. Vol." ,
               'table':['Features'] ,
               'Disp':'Yes',
               'FilterDisp':'Yes',
               'SortDisp':'Yes'
               },
        
         'SQZ2MXRV' : {
               'astype':'float16' ,
               'mysqldtype':FLOAT,
               'webcode':'F18', 
               'short':  "Candle Squeeze 2" , 
               'long': " Mean[(C-O)/(H-L)] at Max Rel. Vol." ,
               'table':['Features'] ,
               'Disp':'Yes',
               'FilterDisp':'Yes',
               'SortDisp':'Yes'
               },
        
         'GPUP' :  {
               'astype':'int32',
               'mysqldtype':INTEGER,
               'webcode':'F19', 
               'short':  "# of Gap-Ups" , 
               'long': " The number of gap ups in the current window" ,
               'table':['Features'] ,
               'Disp':'Yes',
               'FilterDisp':'Yes',
               'SortDisp':'Yes'
               },
  
         'GPDN' :  {
               'astype':'int32',
               'mysqldtype':INTEGER,
               'webcode':'F20', 
               'short':  "# of Gap-Downs" , 
               'long': " The number of gap downs in the current window" ,
               'table':['Features'] ,
               'Disp':'Yes',
               'FilterDisp':'Yes',
               'SortDisp':'Yes'
               },

         'MXGPUP' :  {
               'astype':'float16' ,
               'mysqldtype':FLOAT,
               'webcode':'F21', 
               'short':  "Max. Gap-Up" , 
               'long': " The maximum gap up in the current window" ,
               'table':['Features'] ,
               'Disp':'Yes',
               'FilterDisp':'Yes',
               'SortDisp':'Yes'
               },

         'MXGPDN' :  {
               'astype':'float16' ,
               'mysqldtype':FLOAT,
               'webcode':'F22', 
               'short':  "Max. Gap-Down" , 
               'long': " The maximum gap down in the current window" ,
               'table':['Features'] ,
               'Disp':'Yes',
               'FilterDisp':'Yes',
               'SortDisp':'Yes'
               },

         'CDLMA10' :{
               'astype':'int32',
               'mysqldtype':INTEGER,
               'webcode':'F23', 
               'short':  "#Candles C > SMA10" , 
               'long': " The number of candles with close price above the 10-day simple moving average" ,
               'table':['Features'] ,
               'Disp':'Yes',
               'FilterDisp':'Yes',
               'SortDisp':'Yes'
               },

         'CDLMA20' : {
               'astype':'int32',
               'mysqldtype':INTEGER,
               'webcode':'F24', 
               'short': "#Candles C > SMA20" , 
               'long': " The number of candles with close price above the 20-day simple moving average",
               'table':['Features']  ,
               'Disp':'Yes',
               'FilterDisp':'Yes',
               'SortDisp':'Yes'
               },

         'SMA1251020' : {
               'astype':'int32',
               'mysqldtype':INTEGER,
               'webcode':'F25', 
               'short':  "#Candles SMA10 > SMA20 > SMA50 > SMA100 > SMA200" , 
               'long': " The number of candles that satisfy SMA10 > SMA20 > SMA50 > SMA100 > SMA200" ,
               'table':['Features'] ,
               'Disp':'Yes',
               'FilterDisp':'Yes',
               'SortDisp':'Yes'
         },

         'SMA51020' :  {
               'astype':'int32',
               'mysqldtype':INTEGER,
               'webcode':'F26', 
               'short':  "#Candles: SMA50 > SMA100 > SMA200" , 
               'long': " The number of candles that satisfy SMA50 > SMA100 > SMA200" ,
               'table':['Features'] ,
               'Disp':'Yes',
               'FilterDisp':'Yes',
               'SortDisp':'Yes'
         },

         'Rly1251020' :{
               'astype':'int32',
               'mysqldtype':INTEGER,
               'webcode':'F27', 
               'short':  "#Consecutive Candles with SMA 10 > 20 > 50 > 100 > 200" , 
               'long': " The number of consecutive candles that satisfy SMA10 > SMA20 > SMA50 > SMA100 > SMA200",
               'table':['Features']  ,
               'Disp':'Yes',
               'FilterDisp':'Yes',
               'SortDisp':'Yes'
         },

         'Rly2Rf1251020' : {
               'astype':'int32',
               'mysqldtype':INTEGER,
               'webcode':'F28', 
               'short':  "#Consecutive Candles from End Date with SMA 10 > 20 > 50 > 100 > 200" , 
               'long': " The number of consecutive candles starting from the end date of the current window that satisfy SMA10 > SMA20 > SMA50 > SMA100 > SMA200" ,
               'table':['Features'] ,
               'Disp':'Yes',
               'FilterDisp':'Yes',
               'SortDisp':'Yes'
         },

         'Rly51020' :  {
               'astype':'int32',
               'mysqldtype':INTEGER,
               'webcode':'F29', 
               'short':  "#Consecutive Candles: SMA 50 > 100 > 200" , 
               'long': " The number of consecutive candles of the current window that satisfy  SMA50 > SMA100 > SMA200" ,
               'table':['Features'] ,
               'Disp':'Yes',
               'FilterDisp':'Yes',
               'SortDisp':'Yes'
         },

         'Rly2Rf51020' : {
               'astype':'int32',
               'mysqldtype':INTEGER,
               'webcode':'F30', 
               'short':  "#Consecutive Candles from End Date with SMA  50 > 100 > 200" , 
               'long': " The number of consecutive candles starting from the end date of the current window that satisfy  SMA50 > SMA100 > SMA200" ,
               'table':['Features'] ,
               'Disp':'Yes',
               'FilterDisp':'Yes',
               'SortDisp':'Yes'
         },

         'FutMXDDHf': {
               'astype':'float16' ,
               'mysqldtype':FLOAT,
               'webcode':'F31', 
               'short':  "Max. future 6mon draw-down" , 
               'long': "The maximum possible draw down in the period (End date+ 6 months) " ,
               'table':['Features'] ,
               'Disp':'Yes',
               'FilterDisp':'Yes',
               'SortDisp':'Yes'
         },

         'MA25': {
               'astype':'int32',
               'mysqldtype':INTEGER,
               'webcode':'F32', 
               'short':  "# Candles:  SMA20 > SMA50 " , 
               'long': "The  number of candles with SMA20 > SMA50 " ,
               'table':['Features'] ,
               'Disp':'Yes',
               'FilterDisp':'Yes',
               'SortDisp':'Yes'
         },

         'Rly25':{
               'astype':'int32',
               'mysqldtype':INTEGER,
               'webcode':'F33', 
               'short':  "# Consecutive Candles:  SMA20 > SMA50 " , 
               'long': "The  number of consecutive candles with SMA20 > SMA50 " ,
               'table':['Features'] ,
               'Disp':'Yes',
               'FilterDisp':'Yes',
               'SortDisp':'Yes'
         },

         'MX2MXV' : {
               'astype':'int32',
               'mysqldtype':INTEGER,
               'webcode':'F34', 
               'short':  "# days: First 2 max volumes" , 
               'long': "The  number of days between the first 2 maximum volumes" ,
               'table':['Features'] ,
               'Disp':'Yes',
               'FilterDisp':'Yes',
               'SortDisp':'Yes'
         },

         'CNDLS': {
               'astype':'int32',
               'mysqldtype':INTEGER,
               'webcode':'F35', 
               'short':  "# Candles" , 
               'long': "The number of candles in the window" ,
               'table':['Features'] ,
               'Disp':'Yes',
               'FilterDisp':'Yes',
               'SortDisp':'Yes'
         },
       
         'Chgpts' : {
               'astype':'int32',
               'mysqldtype':INTEGER,
               'webcode':'F36', 
               'short':  "# Change points" , 
               'long': "The number of change points in the Linear-Fitting of the data in the window" ,
               'table':['Features'] ,
               'Disp':'Yes',
               'FilterDisp':'Yes',
               'SortDisp':'Yes'
         },

         'FltRly' : {
               'astype':'int32',
               'mysqldtype':INTEGER,
               'webcode':'F37', 
               'short':  "# days: Flat trend" , 
               'long': "The number of days in the flat region (from Linear-Fit Algorithm)" ,
               'table':['Features'] ,
               'Disp':'Yes',
               'FilterDisp':'Yes',
               'SortDisp':'Yes'
         },

         'UpRly' : {
               'astype':'int32',
               'mysqldtype':INTEGER,
               'webcode':'F38', 
               'short':  "# days: Upward region" , 
               'long': "The number of days in the upward region (from Linear-Fit Algorithm)" ,
               'table':['Features'] ,
               'Disp':'Yes',
               'FilterDisp':'Yes',
               'SortDisp':'Yes'
         },

         'FN2PChgpts' : {
               'astype':'int32',
               'mysqldtype':INTEGER,
               'webcode':'F39', 
               'short':  "# positive change points" , 
               'long': "The number of change points(from Linear-Fit Algorithm) where the slope changes from negative to positive" ,
               'table':['Features'] ,
               'Disp':'Yes',
               'FilterDisp':'Yes',
               'SortDisp':'Yes'
         },

         'MXSLChg' : {
               'astype':'float16' ,
               'mysqldtype':FLOAT,
               'webcode':'F40', 
               'short':  "Max. change in Slope" , 
               'long': "The maximum change in the slope of linear trends(from Linear-Fit Algorithm)" ,
               'table':['Features'] ,
               'Disp':'Yes',
               'FilterDisp':'Yes',
               'SortDisp':'Yes'
         },

         'FltRV15' : {
               'astype':'int32',
               'mysqldtype':INTEGER,
               'webcode':'F41', 
               'short':  "# Rel. Vols > 1.5 in Flat trend" , 
               'long': "The number of days with relative volume greater than 1.5 (10-day vol SMA) in the flat trend region (from Linear-Fit Algorithm)" ,
               'table':['Features'] ,
               'Disp':'Yes',
               'FilterDisp':'Yes',
               'SortDisp':'Yes'
         },

         'FltRV2' :  {
               'astype':'int32',
               'mysqldtype':INTEGER,
               'webcode':'F42', 
               'short':  "# Rel. Vols > 2 in Flat trend" , 
               'long': "The number of days with relative volume greater than 2 (10-day vol SMA) in the flat trend region (from Linear-Fit Algorithm)",
               'table':['Features']  ,
               'Disp':'Yes',
               'FilterDisp':'Yes',
               'SortDisp':'Yes'
         },

         'FltRV3' : {
               'astype':'int32',
               'mysqldtype':INTEGER,
               'webcode':'F43', 
               'short':  "# Rel. Vols > 3 in Flat trend" , 
               'long': "The number of days with relative volume greater than 3 (10-day vol SMA) in the flat trend region (from Linear-Fit Algorithm)" ,
               'table':['Features'] ,
               'Disp':'Yes',
               'FilterDisp':'Yes',
               'SortDisp':'Yes'
         },
         
         'URV15' : {
               'astype':'int32',
               'mysqldtype':INTEGER,
               'webcode':'F44', 
               'short':  "# Rel. Vols > 1.5 in Upward trend" , 
               'long': "The number of days with relative volume greater than 1.5 (10-day vol SMA) in the Upward trend region (from Linear-Fit Algorithm)" ,
               'table':['Features'] ,
               'Disp':'Yes',
               'FilterDisp':'Yes',
               'SortDisp':'Yes'
         },
  
         'URV2' :{
               'astype':'int32',
               'mysqldtype':INTEGER,
               'webcode':'F45', 
               'short':  "# Rel. Vols > 2 in Upward trend" , 
               'long': "The number of days with relative volume greater than 2 (10-day vol SMA) in the Upward trend region (from Linear-Fit Algorithm)" ,
               'table':['Features'] ,
               'Disp':'Yes',
               'FilterDisp':'Yes',
               'SortDisp':'Yes'
         },

         'URV3' :{
               'astype':'int32',
               'mysqldtype':INTEGER,
               'webcode':'F46', 
               'short':  "# Rel. Vols > 3 in Upward trend" , 
               'long': "The number of days with relative volume greater than 3 (10-day vol SMA) in the Upward trend region (from Linear-Fit Algorithm)" ,
               'table':['Features'] ,
               'Disp':'Yes',
               'FilterDisp':'Yes',
               'SortDisp':'Yes'
         },
  
         'FltR20V15' : {
               'astype':'int32',
               'mysqldtype':INTEGER,
               'webcode':'F47', 
               'short':  "#Rel.Vols(20SMA) > 1.5 : Flat trend" , 
               'long': "The number of days with relative volume greater than 1.5 (20-day vol SMA) in the flat trend region (from Linear-Fit Algorithm)" ,
               'table':['Features'] ,
               'Disp':'Yes',
               'FilterDisp':'Yes',
               'SortDisp':'Yes'
         },
         
         'FltR20V2' : {
               'astype':'int32',
               'mysqldtype':INTEGER,
               'webcode':'F48', 
               'short':  "#Rel.Vols(20SMA) > 2 : Flat trend" , 
               'long': "The number of days with relative volume greater than 2 (20-day vol SMA) in the flat trend region (from Linear-Fit Algorithm)" ,
               'table':['Features'] ,
               'Disp':'Yes',
               'FilterDisp':'Yes',
               'SortDisp':'Yes'
         },
         
         'FltR20V3' : {
               'astype':'int32',
               'mysqldtype':INTEGER,
               'webcode':'F49', 
               'short':  "#Rel.Vols(20SMA) > 3 : Flat trend" , 
               'long': "The number of days with relative volume greater than 3 (20-day vol SMA) in the flat trend region (from Linear-Fit Algorithm)" ,
               'table':['Features'] ,
               'Disp':'Yes',
               'FilterDisp':'Yes',
               'SortDisp':'Yes'
         },
         
         'Fltlen' : {
               'astype':'int32',
               'mysqldtype':INTEGER,
               'webcode':'F50', 
               'short':  "# days in Flat trend" , 
               'long': "The number of days in the flat trend region (from Linear-Fit Algorithm)" ,
               'table':['Features'] ,
               'Disp':'Yes',
               'FilterDisp':'Yes',
               'SortDisp':'Yes'
         },
         
         'Uplen' :{
               'astype':'int32',
               'mysqldtype':INTEGER,
               'webcode':'F51', 
               'short':  "# days in Upward trend" , 
               'long': "The number of days in the Upward trend region (from Linear-Fit Algorithm)" ,
               'table':['Features'] ,
               'Disp':'Yes',
               'FilterDisp':'Yes',
               'SortDisp':'Yes'
         },

         'P1': {
               'astype':'int32',
               'mysqldtype':INTEGER,
               'webcode':'P6',
               'short':  "Pattern 1" , 
               'long': "Linear Up pattern correlation",
               'table':'PattCorrtube',
               'Disp':'Yes',
               'FilterDisp':'Yes',
               'SortDisp':'Yes' 
         },

         'P2': {
               'astype':'int32',
               'mysqldtype':INTEGER,
               'webcode':'P7',
               'short':  "Pattern 2" , 
               'long': "Linear Up pattern correlation delayed",
               'table':'PattCorrtube' ,
               'Disp':'Yes',
               'FilterDisp':'Yes',
               'SortDisp':'Yes'
         },

         'P3': {
               'astype':'int32',
               'mysqldtype':INTEGER,
               'webcode':'P8',
               'short':  "Pattern 3" , 
               'long': "Round bottom pattern correlation",
               'table':'PattCorrtube' ,
               'Disp':'Yes',
               'FilterDisp':'Yes',
               'SortDisp':'Yes'
         },

         'P4': {
               'astype':'int32',
               'mysqldtype':INTEGER,
               'webcode':'P9',
               'short':  "Pattern 4" , 
               'long': "Up and flat pattern pattern correlation",
               'table':'PattCorrtube' ,
               'Disp':'Yes',
               'FilterDisp':'Yes',
               'SortDisp':'Yes'
         },

         'P5': {
               'astype':'int32',
               'mysqldtype':INTEGER,
               'webcode':'P10',
               'short':  "Pattern 5" , 
               'long': "V bottom pattern correlation",
               'table':'PattCorrtube' ,
               'Disp':'Yes',
               'FilterDisp':'Yes',
               'SortDisp':'Yes'
         },

         'P6': {
               'astype':'int32',
               'mysqldtype':INTEGER,
               'webcode':'P11',
               'short':  "Pattern 6" , 
               'long': "V up pattern correlation",
               'table':'PattCorrtube' ,
               'Disp':'Yes',
               'FilterDisp':'Yes',
               'SortDisp':'Yes'
         },

         'P7': {
               'astype':'int32',
               'mysqldtype':INTEGER,
               'webcode':'P12',
               'short':  "Pattern 7" , 
               'long': "Measured up pattern correlation",
               'table':'PattCorrtube' ,
               'Disp':'Yes',
               'FilterDisp':'Yes',
               'SortDisp':'Yes'
         },

         'P8': {
               'astype':'int32',
               'mysqldtype':INTEGER,
               'webcode':'P13',
               'short':  "Pattern 8" , 
               'long': "W below pattern correlation",
               'table':'PattCorrtube' ,
               'Disp':'Yes',
               'FilterDisp':'Yes',
               'SortDisp':'Yes'
         },
 
         'P9': {
               'astype':'int32',
               'mysqldtype':INTEGER,
               'webcode':'P14',
               'short':  "Pattern 9" , 
               'long': "Stair case pattern correlation",
               'table':'PattCorrtube' ,
               'Disp':'Yes',
               'FilterDisp':'Yes',
               'SortDisp':'Yes'
         },

         'Tw01_th0': {
               'astype':'int32',
               'mysqldtype':INTEGER,
               'webcode':'P15',
               'short':   "Tube: W=0.1,0deg" , 
               'long': "Tube Strength with width 0.1(norm) and inclined at angle 0 degrees ",
               'table':'PattCorrtube',
               'Disp':'Yes',
               'FilterDisp':'Yes',
               'SortDisp':'Yes' 
         },

         'Tw01_th30': {
               'astype':'int32',
               'mysqldtype':INTEGER,
               'webcode':'P16',
               'short':  "Tube: W=0.1,30deg" , 
               'long':  "Tube Strength with width 0.1(norm) and inclined at angle 30 degrees ",
               'table':'PattCorrtube',
               'Disp':'Yes',
               'FilterDisp':'Yes',
               'SortDisp':'Yes' 
         },

         'Tw01_th45': {
               'astype':'int32',
               'mysqldtype':INTEGER,
               'webcode':'P17',
               'short':  "Tube: W=0.1,45deg" , 
               'long':  "Tube Strength with width 0.1(norm) and inclined at angle 45 degrees ",
               'table':'PattCorrtube',
               'Disp':'Yes',
               'FilterDisp':'Yes',
               'SortDisp':'Yes' 
         },

         'Tw01_th60': {
               'astype':'int32',
               'mysqldtype':INTEGER,
               'webcode':'P18',
               'short':  "Tube: W=0.1,60deg" , 
               'long':  "Tube Strength with width 0.1(norm) and inclined at angle 60 degrees ",
               'table':'PattCorrtube',
               'Disp':'Yes',
               'FilterDisp':'Yes',
               'SortDisp':'Yes' 
         },

         'Tw01_th75': {
               'astype':'int32',
               'mysqldtype':INTEGER,
               'webcode':'P19',
               'short':  "Tube: W=0.1,75deg" , 
               'long':  "Tube Strength with width 0.1(norm) and inclined at angle 75 degrees ",
               'table':'PattCorrtube',
               'Disp':'Yes',
               'FilterDisp':'Yes',
               'SortDisp':'Yes' 
         },

         'Tw02_th0': {
               'astype':'int32',
               'mysqldtype':INTEGER,
               'webcode':'P20',
               'short':  "Tube: W=0.2,0deg" , 
               'long':  "Tube Strength with width 0.2(norm) and inclined at angle 0 degrees ",
               'table':'PattCorrtube' ,
               'Disp':'Yes',
               'FilterDisp':'Yes',
               'SortDisp':'Yes'
         },

         'Tw02_th30': {
               'astype':'int32',
               'mysqldtype':INTEGER,
               'webcode':'P21',
               'short': "Tube: W=0.2,30deg" , 
               'long': "Tube Strength with width 0.2(norm) and inclined at angle 30 degrees ",
               'table':'PattCorrtube',
               'Disp':'Yes',
               'FilterDisp':'Yes',
               'SortDisp':'Yes' 
         },

         'Tw02_th45': {
               'astype':'int32',
               'mysqldtype':INTEGER,
               'webcode':'P22',
               'short': "Tube: W=0.2,45deg" , 
               'long': "Tube Strength with width 0.2(norm) and inclined at angle 45 degrees ",
               'table':'PattCorrtube',
               'Disp':'Yes',
               'FilterDisp':'Yes',
               'SortDisp':'Yes' 
         },

         'Tw02_th60': {
               'astype':'int32',
               'mysqldtype':INTEGER,
               'webcode':'P23',
               'short': "Tube: W=0.2,60deg" , 
               'long': "Tube Strength with width 0.2(norm) and inclined at angle 60 degrees ",
               'table':'PattCorrtube',
               'Disp':'Yes',
               'FilterDisp':'Yes',
               'SortDisp':'Yes' 
         },

         'Tw02_th75': {
               'astype':'int32',
               'mysqldtype':INTEGER,
               'webcode':'P24',
               'short': "Tube: W=0.2,75deg" , 
               'long': "Tube Strength with width 0.2(norm) and inclined at angle 75 degrees ",
               'table':'PattCorrtube',
               'Disp':'Yes',
               'FilterDisp':'Yes',
               'SortDisp':'Yes' 
         },

         'Tw03_th0': {
               'astype':'int32',
               'mysqldtype':INTEGER,
               'webcode':'P25',
               'short':  "Tube: W=0.3,0deg" , 
               'long':  "Tube Strength with width 0.3(norm) and inclined at angle 0 degrees ",
               'table':'PattCorrtube' ,
               'Disp':'Yes',
               'FilterDisp':'Yes',
               'SortDisp':'Yes'
         },

         'Tw03_th30': {
               'astype':'int32',
               'mysqldtype':INTEGER,
               'webcode':'P26',
               'short': "Tube: W=0.3,30deg" , 
               'long': "Tube Strength with width 0.3(norm) and inclined at angle 30 degrees ",
               'table':'PattCorrtube',
               'Disp':'Yes',
               'FilterDisp':'Yes',
               'SortDisp':'Yes' 
         },

         'Tw03_th45': {
               'astype':'int32',
               'mysqldtype':INTEGER,
               'webcode':'P27',
               'short': "Tube: W=0.3,45deg" , 
               'long': "Tube Strength with width 0.3(norm) and inclined at angle 45 degrees ",
               'table':'PattCorrtube',
               'Disp':'Yes',
               'FilterDisp':'Yes',
               'SortDisp':'Yes' 
         },

         'Tw03_th60': {
               'astype':'int32',
               'mysqldtype':INTEGER,
               'webcode':'P28',
               'short': "Tube: W=0.3,60deg" , 
               'long': "Tube Strength with width 0.3(norm) and inclined at angle 60 degrees ",
               'table':'PattCorrtube',
               'Disp':'Yes',
               'FilterDisp':'Yes',
               'SortDisp':'Yes' 
         },

         'Tw03_th75': {
               'astype':'int32',
               'mysqldtype':INTEGER,
               'webcode':'P29',
               'short': "Tube: W=0.3,75deg" , 
               'long': "Tube Strength with width 0.3(norm) and inclined at angle 75 degrees ",
               'table':'PattCorrtube',
               'Disp':'Yes',
               'FilterDisp':'Yes',
               'SortDisp':'Yes' 
         },



   'LineT0' : {   
         'astype':'datetime64[ns]' , 
         'mysqldtype':DATE,
         'webcode':'L3', 
         'short':  "Linear trend start Date" , 
         'long': "The start date of the Linear trend segment (from Linear-Fit Algorithm) in the window. The number of segments in the window is given by LineInd, the index of the line" ,
         'table':['LinearFits'] ,
         'Disp':'Yes',
         'FilterDisp':'Yes',
         'SortDisp':'Yes'
         },

   'LineT1' : {   
         'astype':'datetime64[ns]' , 
         'mysqldtype':DATE,
         'webcode':'L4', 
         'short':  "Linear trend end Date" , 
         'long': "The end date of the Linear trend segment (from Linear-Fit Algorithm) in the window. The number of segments in the window is given by LineInd, the index of the line" ,
         'table':['LinearFits'] ,
         'Disp':'Yes',
         'FilterDisp':'Yes',
         'SortDisp':'Yes'
         },

   'NormLineT0' : {  
         'astype':'float16' , 
         'mysqldtype':FLOAT,
         'webcode':'L5', 
         'short':  "Linear trend x0-coord" , 
         'long': "The starting x coordinate of the Linear trend segment (from Linear-Fit Algorithm) in the normalized window. The number of segments in the window is given by LineInd, the index of the line" ,
         'table':['LinearFits'] ,
         'Disp':'Yes',
         'FilterDisp':'Yes',
         'SortDisp':'Yes'
         },

   'NormLineT1' : {  
         'astype':'float16' ,
         'mysqldtype':FLOAT,
         'webcode':'L6', 
         'short':  "Linear trend x1-coord" , 
         'long': "The ending x coordinate of the Linear trend segment (from Linear-Fit Algorithm) in the normalized window. The number of segments in the window is given by LineInd, the index of the line" ,
         'table':['LinearFits'] ,
         'Disp':'Yes',
         'FilterDisp':'Yes',
         'SortDisp':'Yes'
         },



   'NormLineSlp' : { 
         'astype':'float16' ,
         'mysqldtype':FLOAT,
         'webcode':'L9', 
         'short':  "Normalized Slope : Linear trend" , 
         'long': "The slope of the Linear trend segment (from Linear-Fit Algorithm) in the normalized window. The number of segments in the window is given by LineInd, the index of the line",
         'table':['LinearFits'] ,
         'Disp':'Yes',
         'FilterDisp':'Yes',
         'SortDisp':'Yes' 
         },

   'NormLineC1' : {  
         'astype':'float16' ,
         'mysqldtype':FLOAT, 
         'webcode':'L10', 
         'short':  "Linear trend y1-coord" , 
         'long': "The ending y coordinate of the Linear trend segment (from Linear-Fit Algorithm) in the normalized window. The number of segments in the window is given by LineInd, the index of the line" ,
         'table':['LinearFits'] ,
         'Disp':'Yes',
         'FilterDisp':'Yes',
         'SortDisp':'Yes'
         },

   'NormLineC0' : {  
         'astype':'float16' ,
         'mysqldtype':FLOAT, 
         'webcode':'L11', 
         'short':  "Linear trend y0-coord" , 
         'long': "The starting x coordinate of the Linear trend segment (from Linear-Fit Algorithm) in the normalized window. The number of segments in the window is given by LineInd, the index of the line" ,
         'table':['LinearFits'] ,
         'Disp':'Yes',
         'FilterDisp':'Yes',
         'SortDisp':'Yes'
         },

   'LineSlp' :{   
         'astype':'float16' , 
         'mysqldtype':FLOAT, 
         'webcode':'L12', 'short':  "Slope : Linear trend" , 
         'long': "The slope of the Linear trend segment (from Linear-Fit Algorithm) in the window. The number of segments in the window is given by LineInd, the index of the line",'table':'LinFitData' ,
         'table':['LinearFits'] ,         
         'Disp':'Yes',
         'FilterDisp':'Yes',
         'SortDisp':'Yes'
         },

   'LineInd' :{   
         'astype':'int32',
         'mysqldtype':INTEGER, 
         'webcode':'L13', 
         'short':  "Linear Trend Index" ,                            
         'long': "All the linear segments from the Linear-Fit algorithm are identified by their index: index of 2.5 implies that this the 2nd line segment of the 5 segments in the window",
         'table':['LinearFits'],                          
         'Disp':'No',                       
         'FilterDisp':'No',
         'SortDisp':'No' 
         },

   'LineC1' :{ 
         'astype':'float16' , 
         'mysqldtype':FLOAT, 
         'webcode':'L14', 
         'short':  "Linear trend start Close price" , 
         'long': "The starting close price of the Linear trend segment (from Linear-Fit Algorithm) in the window. The number of segments in the window is given by LineInd, the index of the line" ,
         'table':['LinearFits'] ,
         'Disp':'Yes',
         'FilterDisp':'Yes',
         'SortDisp':'Yes'
         },

   'LineC0' :{ 
         'astype':'float16' , 
         'mysqldtype':FLOAT, 
         'webcode':'L15', 
         'short':  "Linear trend end Close price" , 
         'long': "The ending close price of the Linear trend segment (from Linear-Fit Algorithm) in the window. The number of segments in the window is given by LineInd, the index of the line",
         'table':['LinearFits'] ,
         'Disp':'Yes',            
         'FilterDisp':'Yes',
         'SortDisp':'Yes' 
         },


   'Stock1':  {
      'astype':'str', 
      'mysqldtype':VARCHAR(6),
      'min_itemsize': 10,
      'webcode':'C1',
      'short':  "Symbol 1" , 
      'long': "Ticker/Symbol of the first Stock in the correlation pair" ,
      'table':['CORR'] ,
      'Disp':'No',
      'FilterDisp':'No',
      'SortDisp':'No'
      },

 'Stock2': {
      'astype':'str',
      'mysqldtype':VARCHAR(6), 
      'min_itemsize': 10,
      'webcode':'C2',
      'short':  "Symbol 2" , 
      'long': "Ticker/Symbol of the second Stock in the correlation pair" ,
      'table':['CORR'] ,
      'Disp':'No',
      'FilterDisp':'No',
      'SortDisp':'No'
      },

 'corr': {
      'astype':'float16' , 
      'mysqldtype':INTEGER,
      'webcode':'C3',
      'short':  "correlation" , 
      'long': "Correlation of the pair Ticker 1 and Ticker 2 with same window" ,
      'table':['CORR'] ,
      'Disp':'No',
      'FilterDisp':'No',
      'SortDisp':'No'
      },



   'Open':  {
      'astype':'float16', 
      'mysqldtype':FLOAT, 
      'webcode':'Y1',
      'short':  "Open" , 
      'long': "Open price of candle" ,
      'table':['StockData'] ,
      'Disp':'No',
      'FilterDisp':'No',
      'SortDisp':'No'
      },

 'High': {
      'astype':'float16', 
      'mysqldtype':FLOAT, 
      'webcode':'Y2',
      'short':  "Close" , 
      'long': "High price of candle" ,
      'table':['StockData'] ,
      'Disp':'No',
      'FilterDisp':'No',
      'SortDisp':'No'
      },

 'Low': {
      'astype':'float16' , 
      'mysqldtype':FLOAT, 
      'webcode':'Y3',
      'short':  "Low" , 
      'long':   "Low price of candle" ,
      'table':['StockData'] ,
      'Disp':'No',
      'FilterDisp':'No',
      'SortDisp':'No'
      },

 'Close': {
      'astype':'float16', 
      'mysqldtype':FLOAT,
      'webcode':'Y4',
      'short':  "Close" , 
      'long': "Close price of candle",
      'table':['StockData'] ,
      'Disp':'No',
      'FilterDisp':'No',
      'SortDisp':'No' 
      },

 'Volume': {
      'astype':'int64', 
      'mysqldtype':FLOAT,
      'webcode':'Y5',
      'short':  "Volume" ,
      'long':"Volume",
      'table':['StockData']  ,
      'Disp':'No',
      'FilterDisp':'No',
      'SortDisp':'No'
      },

 'Adj_Close':  {
      'astype':'float16' , 
      'mysqldtype':FLOAT, 
      'webcode':'Y6',
      'short':  "Adj Close" , 
      'long': "Last close price" ,
      'table':['StockData'] ,
      'Disp':'No',
      'FilterDisp':'No',
      'SortDisp':'No'
      },
 


'Industry': {
   'astype':'str',
   'mysqldtype':VARCHAR(20),
   'webcode':'A1',
   'short': 'Industry', 
   'long': 'Industry',
   'table':['StockGroups'] ,
   'Disp':'Yes',
   'FilterDisp':'No',
   'SortDisp':'No'
   },

 'Sector': {
   'astype':'str',
   'mysqldtype':VARCHAR(20),
   'webcode':'A2',
   'short': 'Sector', 
   'long': 'Sector',
   'table':['StockGroups'] ,
   'Disp':'Yes',
   'FilterDisp':'No',
   'SortDisp':'No'
   },

 'Stock_ETF': {
   'astype':'str',
   'mysqldtype':VARCHAR(10),
   'webcode':'A3',
   'short': 'Stock/ETF', 
   'long': 'Stock/ETF',
   'table':['StockGroups'] ,
   'Disp':'Yes',
   'FilterDisp':'No',
   'SortDisp':'No'
   }



             }
            



MasterColumnDict={}
MasterColumnDict.update(FeatureTableDescription) 

ColumnRenamersDict={'Adj Close':'Adj_Close'}
            
#%%                      
min_itemsizes={'Stock1': 8,'Stock2':8,'Symbol': 8,'Stock': 8,'Status':8,'Symbol': 8,'Active':8,'ETF/Stock':8,
               'ETF_Stock':8}

TablesNames=['StockData','StockGroups','Features','CORR','LinearFits']

CORR_table_tags=['Stock1','Stock2','window','shiftby','RefDateTf']
Common_table_tags=['Symbol','window','shiftby','RefDateTf']

#%%
CTApath=[str(Path(__file__).resolve().parents[1])]

DataPath=CTApath+['Data']
MiscDataPath=CTApath+['Misc-Data']
PlotPath=CTApath+['Plots']


         
PathDict=         {
                  'StockStatusList':os.path.join(*(DataPath+['StockSTATUSlist.h5'])),
                                                  
                  # 'DataLink':os.path.join(*(DataPath+['Stocks'])),
                  # 'GetStockDataFile': lambda x: os.path.join(*(DataPath+['Stocks']+ [x[0],x+'.h5'])),  
                  'mysql':{
                           'user':'nagavenkat',
                           'pass':'bablu0com'
                           },
                  
                  'StockData':{
                              'mysql':{
                                       'dbname':'StockData',
                                       'tbname':'Just the name of the stock'
                                       }
                              },

                  'StockGroups':{
                                 'mysql':{
                                          'dbname':'StockGroups',
                                          'tbname':'StockGroups'
                                          }
                                 }, 

                  'StockGroups_csv':os.path.join(*(MiscDataPath+['StockGroups.csv'])), 

                  'AllStocksList':os.path.join(*(MiscDataPath+['AllStocksList.csv'])),

                  'ColmCodes':os.path.join(*(MiscDataPath+['ColmCodes.txt'])),

                  'ConFigFile':os.path.join(*(MiscDataPath+['CTA-Config.yaml'])),
                  
                  'Features': {
                              'mysql':{
                                       'dbname':'Features',
                                       'tbname':lambda tf:'Features_'+tf.strftime("%Y_%m_%d") 
                                       }
                              },

                  'LinearFits': {
                              'mysql':{
                                       'dbname':'LinearFits',
                                       'tbname':lambda tf:'LinearFits_'+tf.strftime("%Y_%m_%d") 
                                       }
                              },

                  'CORR': {
                              'mysql':{
                                       'dbname':'CORR',
                                       'tbname':lambda tf:'CORR_'+tf.strftime("%Y_%m_%d") 
                                       }
                              },
                                                      
                  'LinFitPlot':{
                                 'link': lambda symb,wind,shift,Tf: os.path.join(*(PlotPath+['LinearTrend_plots']+[os.path.join('LinPlot_'+Tf.strftime("%Y-%m-%d"),str(int(wind)),str(symb)[0],'LinearTrendFit_'+str(symb)+'_'+str(int(wind))+'_'+str(int(shift))+'_'+Tf.strftime("%Y-%m-%d")+".png")])) ,                   
                                 'filename': lambda symb,wind,shift,Tf: 'LinearTrendFit_'+str(symb)+'_'+str(wind)+'_'+str(shift)+'_'+Tf.strftime("%Y-%m-%d")
                  } ,       

                  # previous stuff
                  'Featurelink_bydate':os.path.join(*(DataPath+['FitFeatureData','Features_byRefdate'])),
                  'FeaturesName_bydate': lambda x: 'FeatureData_'+x.strftime("%Y-%m-%d")+'.h5',
                  'FeaturesName_leaftag': 'FeatureData',
                  'Features_tabname': 'FeatureData',
				  
                  'LinearFitDatalink_bydate':os.path.join(*(DataPath+['LinearFitFeatureData','LinearFits_byRefdate'])),
                  'LinearFitDataName_bydate': lambda x: 'LinerFitData_'+x.strftime("%Y-%m-%d")+'.h5',
		            'LinearFitDataName_leaftag': 'LinFitData' ,
                  'LinearFitData_tabname': 'LinFitData' ,
				  
                  'CorrelationDatalink_bydate':os.path.join(*(DataPath+['CorrelationData','CorrelationData_byRefdate'])),
                  'CorrelationDataName_bydate': lambda x: 'CORR_'+x.strftime("%Y-%m-%d")+'.h5',
                  'CorrelationDataName_leaftag': 'CORR',
                  'CorrelationData_tabname': 'CORR',

                  
                  'PattCorrTubelink_bydate':os.path.join(*(DataPath+['PattCorrtubeData','PattCorrtube_byRefdate'])),
                  'PattCorrTubeName_bydate': lambda x: 'PattCorrtube_'+x.strftime("%Y-%m-%d")+'.h5',
                  'PattCorrTubeName_leaftag': 'PattCorrtube',
                  'PattCorrTubeName_tabname': 'PattCorrtube',
                  
                  
                  'web-app-flask': os.path.join(*(CTApath+['web-app-flask'])),
                  
                  'PatternsDict':os.path.join(*(CTApath+['CTA','PatternRecognition','PatternTemplates.txt'])),
                  'PatternsDict_plots':os.path.join(*(CTApath+['CTA','PatternRecognition'])),

                  'pdTf':pd.datetime.today(),
                  'pdT0':pd.datetime(2006,1,1),
                  'pdT00':pd.datetime(2002,1,1)
                  
                  }


# with open(PathDict['ColmCodes'], 'w') as fp:
#     json.dump(dd, fp)
    
#%%
def GeneratePath(ppstr=None):
    if os.path.isdir(ppstr)==False:
        os.makedirs(ppstr)    
    return ppstr
        
        
def GetConfigs():
    fname=PathDict['ConFigFile']
    if os.path.isfile(fname)==False:
        configs= collections.OrderedDict()
        configs['Author']='Nagavenkat Adurthi'
        configs['Description']="""This is the configuraton file that describes all the parameters used in the simulation  and also the current status of the data"""
        configs['File Created on']= pd.datetime.today().strftime("%Y-%m-%d")

        with open(fname, 'w') as stream:
            try:
                stream.write(yaml.dump(configs, width=100, indent=4) )
            except yaml.YAMLError as exc:
                print(exc)
            
    with open(fname, 'r') as stream:
        try:
            configs=yaml.load(stream)
        except yaml.YAMLError as exc:
            sys.exit(exc)
    return configs
    
def Update_Configs(configs):
    fname=PathDict['ConFigFile']
    with open(fname, 'w') as stream:
        try:
            stream.write(yaml.dump(configs, width=100, indent=4) )
        except yaml.YAMLError as exc:
            print(exc)
        

Gold_stocks=['GSV',
'DRD',
'MUX',
'GSS',
'SA',
'RIC',
'HMY',
'KGC',
'SBGL',
'AKG',
'NG',
'NEM',
'ABX',
'BAA',
'BTG',
'NGD',
'AUY',
'MGH',
'SAND',
'AGI',
'GFI',
'EGI',
'GG',
'KGJI',
'RGLD',
'GORO',
'EGO',
'TRX',
'XPL',
'LODE',
'PPP',
'PGLC',
'TGD',
'VGZ',
'AAU',
'AU',
'IAG',
'XRA',
'AEM',
'FNV',
'THM',
'GOLD',
'NEM',
'ABX',
'BAA',
'BTG',
'NGD',
'AUY',
'MGH',
'SAND',
'AGI',
'GFI',
'EGI',
'GG',
'KGJI',
'RGLD',
'GORO',
'EGO',
'TRX',
'XPL',
'LODE',
'PPP',
'PGC',
'TG'
]

CandlePatterns={
'CDL2CROWS' :           'Two Crows',
'CDL3BLACKCROWS'    :   'Three Black Crows',
'CDL3INSIDE'         :  'Three Inside Up/Down',
'CDL3LINESTRIKE'     :  'Three-Line Strike',
'CDL3OUTSIDE'        :  'Three Outside Up/Down',
'CDL3STARSINSOUTH'   :  'Three Stars In The South',
'CDL3WHITESOLDIERS'  :  'Three Advancing White Soldiers',
'CDLABANDONEDBABY'   :  'Abandoned Baby',
'CDLADVANCEBLOCK'    :  'Advance Block',
'CDLBELTHOLD'        :  'Belt-hold',
'CDLBREAKAWAY'       :  'Breakaway',
'CDLCLOSINGMARUBOZU' :  'Closing Marubozu',
'CDLCONCEALBABYSWALL':  'Concealing Baby Swallow',
'CDLCOUNTERATTACK'   :  'Counterattack',
'CDLDARKCLOUDCOVER'  :  'Dark Cloud Cover',
'CDLDOJI'            :  'Doji',
'CDLDOJISTAR'        :  'Doji Star',
'CDLDRAGONFLYDOJI'   :  'Dragonfly Doji',
'CDLENGULFING'       :  'Engulfing Pattern',
'CDLEVENINGDOJISTAR' :  'Evening Doji Star',
'CDLEVENINGSTAR'     :  'Evening Star',
'CDLGAPSIDESIDEWHITE':  'Up/Down-gap side-by-side white lines',
'CDLGRAVESTONEDOJI'   : 'Gravestone Doji',
'CDLHAMMER'           : 'Hammer',
'CDLHANGINGMAN'       : 'Hanging Man',
'CDLHARAMI'           : 'Harami Pattern',
'CDLHARAMICROSS'      : 'Harami Cross Pattern',
'CDLHIGHWAVE'         : 'High-Wave Candle',
'CDLHIKKAKE'         :  'Hikkake Pattern',
'CDLHIKKAKEMOD'      :  'Modified Hikkake Pattern',
'CDLHOMINGPIGEON'    :  'Homing Pigeon',
'CDLIDENTICAL3CROWS' :  'Identical Three Crows',
'CDLINNECK'          :  'In-Neck Pattern',
'CDLINVERTEDHAMMER'  :  'Inverted Hammer',
'CDLKICKING'         :  'Kicking',
'CDLKICKINGBYLENGTH' :  'Kicking - bull/bear determined by the longer marubozu',
'CDLLADDERBOTTOM'    :  'Ladder Bottom',
'CDLLONGLEGGEDDOJI'  :  'Long Legged Doji',
'CDLLONGLINE'        :  'Long Line Candle',
'CDLMARUBOZU'        :  'Marubozu',
'CDLMATCHINGLOW'     :  'Matching Low',
'CDLMATHOLD'         :  'Mat Hold',
'CDLMORNINGDOJISTAR' :  'Morning Doji Star',
'CDLMORNINGSTAR'     :  'Morning Star',
'CDLONNECK'          :  'On-Neck Pattern',
'CDLPIERCING'        :  'Piercing Pattern',
'CDLRICKSHAWMAN'     :  'Rickshaw Man',
'CDLRISEFALL3METHODS':  'Rising/Falling Three Methods',
'CDLSEPARATINGLINES'  : 'Separating Lines',
'CDLSHOOTINGSTAR'     : 'Shooting Star',
'CDLSHORTLINE'        : 'Short Line Candle',
'CDLSPINNINGTOP'      : 'Spinning Top',
'CDLSTALLEDPATTERN'   : 'Stalled Pattern',
'CDLSTICKSANDWICH'    : 'Stick Sandwich',
'CDLTAKURI'           : 'Takuri (Dragonfly Doji with very long lower shadow)',
'CDLTASUKIGAP'        : 'Tasuki Gap',
'CDLTHRUSTING'        : 'Thrusting Pattern',
'CDLTRISTAR'          : 'Tristar Pattern',
'CDLUNIQUE3RIVER'     : 'Unique 3 River',
'CDLUPSIDEGAP2CROWS'  : 'Upside Gap Two Crows',
'CDLXSIDEGAP3METHODS' : 'Upside/Downside Gap Three Methods'
}



