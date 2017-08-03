# -*- coding: utf-8 -*-
"""
Created on Fri Dec 12 14:23:53 2014

@author: nagnanamus

Strategy 1:
* Recognize all flat stocks
* divide into windows 30,60,90, 120, 150, 180, 210, 240, 270 (~1 year)
* Shift window by 10 days
* Normalized tubes ([0,1]) widths: 10% , 20%  30% , 50% , 75%  
* 

Strategy 2: 
* Same window concept
* Build Normalized Templates ([0,1])
* Check correlations and sort

Strategy 3:
* just check the 10,20,50,100,200-day returns (performance)  (not SMA) 
* check the std 

Strategy 4:
* Relative Volume

Strategy 5:
* Tight squeeze and volume action
* Channel fitting
"""

from __future__ import division

import numpy as np
import pandas as pd
# import matplotlib.pyplot as plt
import sys
import CTA.GenConfig as GC
import CTA.PlotingManager as pltmag

import CTA.PatternRecognition.CustomClustering as ccp
import CTA.TableManager as TM  
import time
import multiprocessing as mp
import os
   
import pdb
#%%

def GetLineFromTrends(Trends,df):
    T=GC.Dates2days(df.index)
    L=[]
    M=[]
    for tt in T:
        indxx=np.nan
        for ind in Trends.index:
            if tt>=Trends.loc[ind,'X0'] and tt<=Trends.loc[ind,'Xf']:
                indxx=ind
                break


        if np.isnan(indxx):
            L.append(L[-1])
            M.append(M[-1])
        else:
            pk=np.interp(tt, [ Trends.loc[indxx,'X0'] , Trends.loc[indxx,'Xf'] ], [ Trends.loc[indxx,'Y0'] , Trends.loc[indxx,'Yf'] ] )
            L.append( pk  )
            M.append( Trends.loc[indxx,'Slp'] )
    
    M=np.array(M)
    L=np.array(L)
    return L,M

def GetLineFromTrends_algo2(Trends,df):
    L=[]
    M=[]
    if Trends.empty==False:
        for ind in df.index:
            dT=Trends[(ind>=Trends['X0date']) & (ind<=Trends['Xfdate'])]
            if dT.empty==False:
                indxx=dT.index[0]
                Tm=GC.Dates2days([ind])[0]
                L.append( Trends.loc[indxx,'Slp']*(Tm-Trends.loc[indxx,'X0'])+Trends.loc[indxx,'Y0'] )
                M.append( Trends.loc[indxx,'Slp'] )
            else:
                dT=Trends[(ind>=Trends['Xfdate']) & (ind<=Trends['X0date'])]
                if dT.empty==False:
                    indxx=dT.index[0]
                    Tm=GC.Dates2days([ind])[0]
                    L.append( Trends.loc[indxx,'Slp']*(Tm-Trends.loc[indxx,'X0'])+Trends.loc[indxx,'Y0'] )
                    M.append( Trends.loc[indxx,'Slp'] )
                else:
                    L.append(L[-1])
                    M.append(M[-1])
    if len(L)==0:
        L= np.empty(len(df.index)) * np.nan
    else:
        L=np.array(L)

    if len(M)==0:
        M = np.empty(len(df.index)) * np.nan
    else:
        M=np.array(M)
        
    return L,M

# vlambda is the penalty in cvx trend fitting 
#  NchannelStrength is the min length of a channel   
# T is in days
def LinTrendfitcvx(df,weights=None,method='mid',PLOT='No',InterpRes=100,vlambda=15,vlambda_bias=20,NchannelStrength=10):
    Y=df.values
    T=GC.Dates2days(df.index)
    
    miny=min(Y)
    mint=min(T)
    
    y=Y-min(Y)
    t=T-min(T)
    
    maxy=max(y)
    maxt=max(t)
    
    y=y/float( max(y) )
    t=t/float( max(t) )
    
    
    
    N=InterpRes
    yintp=np.interp(np.linspace(0,1,N),t,y)   
    tintp=np.linspace(0,1,N)
    
    if weights==None:
        weights=np.ones(len(yintp))
    else:
        weights=np.interp(np.linspace(0,1,N),t,weights)
    
    if method=='mid':    
        xval=ccp.OptTrendFit_cvx(yintp,vlambda,weights)
    elif method=='bottom':
        xval=ccp.OptBottomTrendFit_cvx(yintp,vlambda,vlambda_bias,weights)
    elif method=='top':
        xval=ccp.OptTopTrendFit_cvx(yintp,vlambda,vlambda_bias,weights)

    slp=np.transpose((xval[1:]-xval[0:-1]))
    slp=slp[0]
    slp=slp-min(slp)
    slp=slp/max(slp)
    slp=np.insert(slp,0,slp[0])

    ss=ccp.KmeansClustering_1Ddata_algo1(np.transpose([slp]),MinGrpSize=NchannelStrength)
    ssclust=ss[0]    
    sslab=ss[1]
    opt_slopes=len(ssclust)
    
    Slopes=np.zeros(slp.size)    
    for j in range(0,opt_slopes):
            Slopes[sslab==j]=ssclust[j]

    # now space sluster each slope cluster
    xx=xval.transpose()[0]

    Trends=pd.DataFrame()
    indxx=0
    for j in range(0,opt_slopes):
        pp=np.argwhere(sslab==j)
        pp=np.transpose(pp)[0]
        ppgrps=ccp.ConsecutiveClustering_1Ddata_algo1(pp)
        for k in ppgrps:

            t0=maxt*tintp[k[0]]+mint
            tf=maxt*tintp[k[-1]]+mint
            y0=maxy*xx[k[0]]+miny
            yf=maxy*xx[k[-1]]+miny
            m=(yf-y0)/(tf-t0)

            Trends=pd.concat([Trends, pd.DataFrame({'X0norm':tintp[k[0]],
                                                            'Xfnorm':tintp[k[-1]],
                                                            'Y0norm':xx[k[0]],
                                                            'Yfnorm':xx[k[-1]],
                                                            'Slpnorm':ssclust[j][0],
                                                            
                                                            'X0':t0,
                                                            'Xf':tf,
                                                            'Y0':y0,
                                                            'Yf':yf,
                                                            'Slp':m,

                                                            'X0date':GC.days2Dates([t0])[0],
                                                            'Xfdate':GC.days2Dates([tf])[0],

                                                            },index=[indxx]) ] )  

            indxx=indxx+1

    

    Trends.sort_values(by=['X0'],inplace=True)
    Trends.index=range(len(Trends))

    L=[]
    for tt in T:
        indxx=np.nan
        for ind in Trends.index:
            if tt>=Trends.loc[ind,'X0'] and tt<=Trends.loc[ind,'Xf']:
                indxx=ind
                break
        if np.isnan(indxx):
            L.append(L[-1])
        else:
            try:    
                pk=np.interp(tt, [ Trends.loc[indxx,'X0'] , Trends.loc[indxx,'Xf'] ], [ Trends.loc[indxx,'Y0'] , Trends.loc[indxx,'Yf'] ] )
            except:
                pdb.set_trace()

            L.append( pk  )
    

    L=np.array(L)

    if PLOT=='Yes':
        plt.rc('text', usetex=True)
        plt.rc('font', family='serif')
        font = {'family' : 'normal',
                'weight' : 'normal',
                'size'   : 16}
        plt.rc('font', **font)

        # Plot estimated trend with original signal.
        plt.figure(figsize=(10, 6))
        plt.plot(T, Y, 'k:', linewidth=1.0)

        for ind in Trends.index:
            plt.plot([Trends.loc[ind,'X0'],Trends.loc[ind,'Xf'] ], [Trends.loc[ind,'Y0'],Trends.loc[ind,'Yf'] ] , 'b', linewidth=2.0)
        plt.show()
        
    return [Trends,L]
     
     
def Linefitcvx(df,weights=None,method='mid',PLOT='No',InterpRes=100,vlambda=15,vlambda_bias=20,NchannelStrength=10):
    Y=df.values
    T=GC.Dates2days(df.index)
    
    miny=min(Y)
    mint=min(T)
    
    y=Y-min(Y)
    t=T-min(T)
    
    maxy=max(y)
    maxt=max(t)
    
    y=y/float( max(y) )
    t=t/float( max(t) )
    
    
    
    N=InterpRes
    yintp=np.interp(np.linspace(0,1,N),t,y)   
    tintp=np.linspace(0,1,N)
    
    if weights==None:
        weights=np.ones(len(yintp))
    else:
        weights=np.interp(np.linspace(0,1,N),t,weights)
    
    if method=='bottom':    
        xval=ccp.OptLineFit_cvx(yintp,tintp,method,vlambda_bias,weights)
    elif method=='top':
        xval=ccp.OptLineFit_cvx(yintp,tintp,method,vlambda_bias,weights)


    mnorm=xval[0]
    cnorm=xval[1]

    Lnorm=mnorm*t+cnorm
    L=Lnorm*maxy+miny    


    if PLOT=='Yes':
        plt.rc('text', usetex=True)
        plt.rc('font', family='serif')
        font = {'family' : 'normal',
                'weight' : 'normal',
                'size'   : 16}
        plt.rc('font', **font)

        # Plot estimated trend with original signal.
        plt.figure(figsize=(10, 6))
        plt.plot(T, Y, 'k:', linewidth=1.0)

        plt.plot([Trends.loc[ind,'X0'],Trends.loc[ind,'Xf'] ], [Trends.loc[ind,'Y0'],Trends.loc[ind,'Yf'] ] , 'b', linewidth=2.0)
        plt.show()
        
    return [Trends,L]
 
