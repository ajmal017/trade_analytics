# -*- coding: utf-8 -*-
"""
plotting_manager.py 

Handles plottings dedicated for stocks

* Bokeh Plots for stocks
* Matplotlib plots for stocks
* Make html files and pdfs from pweave

"""
from __future__ import division
import urllib
import imghdr
import matplotlib
matplotlib.use('Agg', force=True)
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter, WeekdayLocator,DayLocator, MONDAY
from matplotlib.patches import Circle, Rectangle
from matplotlib.collections import PolyCollection
from matplotlib.colors import colorConverter
import matplotlib.finance
from matplotlib.finance import candlestick_ohlc
from PIL import Image
import time
import subprocess as sbp
from math import pi
import pandas as pd
import mpld3
import time
import bokeh
from bokeh.plotting import *
from bokeh.resources import CDN
from bokeh.embed import components
from bokeh.io import output_file, show, vplot
try:
    from cStringIO import StringIO
except:
    from StringIO import StringIO

import CTA.GenConfig as GC

import os.path
import numpy as np

import pdb

#pd.options.display.mpl_style = 'default'
from matplotlib.dates import num2date

CDN_script_bokeh="""
<link
    href="http://cdn.pydata.org/bokeh/release/bokeh-0.10.0.min.css"
    rel="stylesheet" type="text/css">
<script src="http://cdn.pydata.org/bokeh/release/bokeh-0.10.0.min.js"></script>
"""


def SMAcolors(cc):
    if '10+' in cc+'+':
        return 'b'
    if '20+' in cc+'+':
        return 'r'
    if '50+' in cc+'+':
        return 'g'
    if '100+' in cc+'+':
        return 'b--'    
    if '200+' in cc+'+':
        return 'r--'
        

plotconfig_std= {'bokeh':False,
                'fig':{'size':(20,15)}, 
                      'subfig':[    
                         { 
                         'title':'Symbol',
                         'size':(10,15),   # has effect only for bokeh
                         'rowspan':2,
                         'Chart':'Price',
                         'type':'Candle',
                         'Dflines':{
                                   'MA10':{'norm':False,'c':'b','w':2},
                                   'MA20':{'norm':False,'c':'r','w':2},
                                   'MA50':{'norm':False,'c':'g','w':2},
                                   'MA100':{'norm':False,'c':'b--','w':3},
                                   'MA200':{'norm':False,'c':'r--','w':3}
                                   }
                                   
                         #'Customlines':[{'Xtype':'dates','X':[1,2,3],'Y':[3,2,1],'c':'r--','w':2}],
                         #'Circles':[{'Xtype':'dates','X0':3,'Y0':4,'R':1,'c':'g','w':2}]
                         },

                         {   
                         'title':'Volume',  
                         'size':(10,7),   # has effect only for bokeh
                         'rowspan':1,
                         'Chart':'Volume',
                         'type':'Bar',
                         'Dflines':{
                                   'VolMA10':{'norm':False,'c':'b','w':2},
                                   'VolMA20':{'norm':False,'c':'r','w':2}
                                    }
                         },

                         # {   
                         # 'title':'STD',
                         # 'size':(10,7),   # has effect only for bokeh
                         # 'rowspan':1,
                         # 'Chart':None,
                         # 'type':None,
                         # 'Dflines':{
                         #           'STD10':{'norm':True,'c':'b','w':2}
                         #           }
                         # },
                         
                         # {   
                         # 'title':'Amp SMA',
                         # 'size':(10,7),   # has effect only for bokeh
                         # 'rowspan':1,
                         # 'Chart':None,
                         # 'type':None,
                         # 'Dflines':{
                         #           'AmpSMA10':{'norm':True,'c':'b','w':2}
                         #           }
                         # },
                         
                         # {   
                         # 'title':'Max-Min SMA',
                         # 'size':(10,7),   # has effect only for bokeh
                         # 'rowspan':1,
                         # 'Chart':None,
                         # 'type':None,
                         # 'Dflines':{
                         #           'SMAmaxDiff':{'norm':True,'c':'b','w':2}
                         #           }
                         # }
                         
                         
                         
                         
                              ]
                     }


plotdeploy_std={
                          'show':False,
                          'save':True,
                          'mpld3':False,
                          'bokeh':False,
                          'savepath':None,
                          'ClosePlot':True,
                          'ImageCompress':False,
                          'XtremeImageCompress':False
                          }




# plotconfig =[{'title':'SymbName','Dim':[height,width],'Candle':[],'SMA':[10,20,50,100,200],'EMA':[10,20,50,100,200]}, .....
#             {'title':'SymbName','Dim':[height,width],'Vol':[],'VolSMA':[10,20,50,100,200],     }]
# a list of dictionaries, each dictionary is for 1 figure
# if SAVE=filename ... it will save the fig to the filename         
def PlotCandle(Df,plotconfig,plotdeploy,Q):
    candle_width=1
    fac=1.2*candle_width
    # Df['index']=Df.index
    # Df['Daysindex']=Df['index'].apply( lambda x: matplotlib.dates.date2num(x) )

    daysnum=GC.Dates2days(Df.index)
    daysnum=daysnum*fac



    dates=list(Df.index)
    datestrs=GC.Dates2str(dates,fmt="%b-%d-%Y")

    mids = (Df.Open + Df.Close)/2
    spans = abs(Df.Close-Df.Open)

    inc = Df.Close > Df.Open
    dec = Df.Open > Df.Close
    w = 12*60*60*1000 # half day in ms
 
    yrs=Df.index.year


    # a=zip(Df['Daysindex'].tolist(),Df['Open'].tolist(),Df['Close'].tolist(),Df['High'].tolist(),Df['Low'].tolist())
    # o=Df['Open'].tolist()
    # c=Df['Close'].tolist()
    # Df['Volume'].tolist()

    # tt=Df['Daysindex'].tolist()

    # get the total number of rows
    gridrows=0
    for cnt in range(len(plotconfig['subfig'])):
        gridrows=gridrows+plotconfig['subfig'][cnt]['rowspan']

    # fig, ax = plt.subplots(len(plotconfig),sharex=True,figsize=(10, 7))
    if plotdeploy['bokeh']==False:
        fig, ax = plt.subplots(len(plotconfig['subfig']),sharex=True,figsize=plotconfig['fig']['size'])
        bokehpp=[]*len(plotconfig['subfig'])
        
    rr=0
    
    for cnt in range(len(plotconfig['subfig'])):
        if plotdeploy['bokeh']==True:
            bokehpp[cnt]=figure(x_axis_type = "datetime",tools="pan,wheel_zoom,box_zoom,reset,previewsave,crosshair",
                   name="candlestick", plot_height=plotconfig['subfig'][cnt]['size'][0], plot_width=plotconfig['subfig'][cnt]['size'][1])
            bokehpp[cnt].title = plotconfig['subfig'][cnt]['title']
        else:
            ax[cnt]=plt.subplot2grid((gridrows,1), (rr,0),rowspan=plotconfig['subfig'][cnt]['rowspan'],axisbg='w',sharex=ax[0])
            ax[cnt].set_title(plotconfig['subfig'][cnt]['title'])
            ax[cnt].grid()

        rr=rr+plotconfig['subfig'][cnt]['rowspan']

        if plotconfig['subfig'][cnt]['Chart'] == 'Price':
            if plotconfig['subfig'][cnt]['type'] == 'Candle':
                if plotdeploy['bokeh']==False:
                    # matplotlib.finance.candlestick_ochl(ax[cnt], a,width=0.8,colorup='g', colordown='r',alpha=0.4);
                    ax[cnt]=candleplot(ax[cnt],Df,daysnum,width=candle_width,alpha=0.8)
                elif plotdeploy['bokeh']==True:
                    bokehpp[cnt].segment(Df.date, Df.High, Df.date, Df.Low, color='black')
                    bokehpp[cnt].rect(Df.date[inc], mids[inc], w, spans[inc], fill_color="white", line_color="green")
                    bokehpp[cnt].rect(Df.date[dec], mids[dec], w, spans[dec], fill_color="red", line_color="red")
                    bokehpp[cnt].title =bokehpp[cnt].title +' '+str(min(Df.index))[0:11]+' to ' +str(max(Df.index))[0:11]


        if 'Dflines' in plotconfig['subfig'][cnt].keys():
            for cc in plotconfig['subfig'][cnt]['Dflines'].keys():
                w=plotconfig['subfig'][cnt]['Dflines'][cc]['w']
                c=plotconfig['subfig'][cnt]['Dflines'][cc]['c']
                ppp=Df[cc].values
                if plotconfig['subfig'][cnt]['Dflines'][cc]['norm']==True:
                    ppp=ppp-min(ppp)
                    ppp=ppp/max(ppp)
    
                if plotdeploy['bokeh']==False:
                    ax[cnt].plot(daysnum,ppp,c, alpha=0.5,linewidth=w)
                elif plotdeploy['bokeh']==True:
                    bokehpp[cnt].line(Df.index, ppp, line_color=c,alpha=0.5,linewidth=w)


        if 'Customlines' in plotconfig['subfig'][cnt].keys():
            for i in range(len( plotconfig['subfig'][cnt]['Customlines'] )):
                X=plotconfig['subfig'][cnt]['Customlines'][i]['X']

                if plotconfig['subfig'][cnt]['Customlines'][i]['Xtype']=='dates':
                    Xdays_fac=GC.Dates2days(X)*fac
                    X_fac=GC.days2Dates(Xdays_fac)
                else:
                    Xdays_fac=X*fac
                    X_fac=GC.days2Dates(Xdays_fac)
                    
                Y=plotconfig['subfig'][cnt]['Customlines'][i]['Y']
                
                c=plotconfig['subfig'][cnt]['Customlines'][i]['c']
                w=plotconfig['subfig'][cnt]['Customlines'][i]['w']
                
                
                if plotdeploy['bokeh']==False:
                    ax[cnt].plot(Xdays_fac,Y,c, linewidth=w)


                elif plotdeploy['bokeh']==True:
                    bokehpp[cnt].line(X_fac, Y, line_color=c,alpha=0.5,linewidth=w)
                    


        if 'CandlePattern' in plotconfig['subfig'][cnt].keys():
            for i in range(len( plotconfig['subfig'][cnt]['CandlePattern'] )):
                X0=plotconfig['subfig'][cnt]['CandlePattern'][i]['X0']
                if plotconfig['subfig'][cnt]['CandlePattern'][i]['Xtype']=='dates':
                    X0=GC.Dates2days([X0])[0]*fac
                    # X0=matplotlib.dates.date2num(X0)
                
                Y0=plotconfig['subfig'][cnt]['CandlePattern'][i]['Y0']
                
                R=plotconfig['subfig'][cnt]['CandlePattern'][i]['R']
                c=plotconfig['subfig'][cnt]['CandlePattern'][i]['c']
                w=plotconfig['subfig'][cnt]['CandlePattern'][i]['w']
                
                ax[cnt].annotate(plotconfig['subfig'][cnt]['CandlePattern'][i]['annotate'], xy=(X0, Y0+1*R), xytext=(X0, Y0+3*R),fontsize=8,
                    arrowprops=dict(facecolor='black', shrink=0.05,frac=0.6,width=candle_width,headwidth=candle_width*4),
                    )

        if plotconfig['subfig'][cnt]['Chart'] == 'Volume':
            if plotconfig['subfig'][cnt]['type'] == 'Bar':
                
                if plotdeploy['bokeh']==False:
                    maxvol=Df['Volume'].max()
                    
                    ax[cnt]=volumeplot(ax[cnt],Df,daysnum,width=candle_width,alpha=0.8)

                    ax[cnt].set_ylim([0,maxvol*1.05])
                    ax[cnt].set_yticks([0,0.2*maxvol,0.4*maxvol,0.6*maxvol,0.8*maxvol,1*maxvol])
                    new_yticks=np.array([0,0.2,0.4,0.6,0.8,1])
                    ax[cnt].set_yticklabels(new_yticks)
                    
                    props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
                    ax[cnt].text(0.05*1, 0.95*1, 'Max Volume = '+str(maxvol), transform=ax[cnt].transAxes, fontsize=8,
                            verticalalignment='top', bbox=props)
    
                elif plotdeploy['bokeh']==True:
                    mm=max(Df.Volume)
                    mids = (Df.Volume)/2.0
                    bokehpp[cnt].rect(Df.index[inc], mids[inc]/mm, w, Df.Volume[inc]/mm, fill_color="white", line_color="green")
                    bokehpp[cnt].rect(Df.index[dec], mids[dec]/mm, w, Df.Volume[dec]/mm, fill_color="red", line_color="red")
                    bokehpp[cnt].title = bokehpp[cnt].title + '   Max Vol = '+str(mm)
                    bokehpp[cnt].y_range = bokeh.models.ranges.Range1d(start=0, end=1)

        if plotdeploy['bokeh']==True:
            bokehpp[cnt].yaxis.location="right"  
            bokehpp[cnt].xaxis.major_label_orientation = pi/4
            bokehpp[cnt].grid.grid_line_alpha=0.3

        cnt=cnt+1

    if plotdeploy['bokeh']==False:
        a=np.arange(0,len(daysnum),10)
        for i in range(0,len(ax)):
            if np.remainder(i,2)==0:
                ax[i].set_xticks(daysnum[a])
                ax[i].set_xticklabels(['']*len(daysnum[a]),rotation=45, horizontalalignment='right',size=8,visible=False) #, 
                # ax[i].get_xaxis().set_ticks([])
            else:
                ax[i].set_xticks(daysnum[a])
                ax[i].set_xticklabels(datestrs[a],rotation=45, horizontalalignment='right',size=15) #, visible=False

            ax[i].set_xlim([daysnum[0],daysnum[-1]])

        fig.tight_layout()

    elif plotdeploy['bokeh']==True:
        plot = vplot(bokehpp)

    if plotdeploy['save'] ==True:
        if plotdeploy['ImageCompress']==True:
            ram = StringIO()
            fig.savefig(ram,bbox_inches='tight')
            ram.seek(0)
            im = Image.open(ram)
            im2 = im.convert('RGB').convert('P', palette=Image.ADAPTIVE)
            im2.save( plotdeploy['savepath'], optimize=True,quality=70,format='PNG')    #
            ram.close()
            im.close()
            im2.close()

        elif plotdeploy['XtremeImageCompress']==True:
            ram = StringIO()
            fig.savefig(ram,bbox_inches='tight')
            ram.seek(0)
            im = Image.open(ram)
            im2 = im.convert('RGB').convert('P', palette=Image.ADAPTIVE, colors=10)
            im2.save( plotdeploy['savepath'] , optimize=True,quality=70,format='PNG')    #            
        elif plotdeploy['mpld3']==True:    
            ss=mpld3.fig_to_html(fig)
            if plotdeploy['savepath']!=None:
                with open(plotdeploy['savepath'],'w') as filename:
                    filename.write(ss)
            else:
                return ss
        elif plotdeploy['bokeh']==True:
            if plotdeploy['savepath']==None:
                script, div = components(plot)
                return script, div , CDN_script_bokeh
            else:
                output_file(plotdeploy['savepath'])

        else:    
            fig.savefig(plotdeploy['savepath'],bbox_inches='tight',transparent=True, format='png')
    	    plt.close(fig)
    	    import gc
    	    gc.collect()
            if Q!=None:
                Q.put(plotdeploy['savepath'])
            else:
                return plotdeploy['savepath']

                
        if plotdeploy['ClosePlot']==True:
            plt.close(fig)
            import gc
            gc.collect()

    else:
        if plotdeploy['show']==True:
            plt.show()
        
    return ''    
        
def candleplot(ax,Df,days,width,alpha):
    for ind in range(len(Df)):
        if Df['Open'].iloc[ind] <= Df['Close'].iloc[ind]:
            x=days[ind]-width/2
            y=Df['Open'].iloc[ind]
            height=Df['Close'].iloc[ind]-Df['Open'].iloc[ind]
            pp=Rectangle((x,y), width, height, angle=0.0, alpha=alpha,color='g',fill=True)
            ax.add_patch(pp)
            x=days[ind]
            ax.plot([x,x],[Df['Low'].iloc[ind],Df['High'].iloc[ind] ],'g')
        else:
            x=days[ind]-width/2
            y=Df['Close'].iloc[ind]
            height=Df['Open'].iloc[ind]-Df['Close'].iloc[ind]
            pp=Rectangle((x,y), width, height, angle=0.0, alpha=alpha,color='r',fill=True)
            ax.add_patch(pp)
            x=days[ind]
            ax.plot([x,x],[Df['Low'].iloc[ind],Df['High'].iloc[ind] ],'r')

    ax.tick_params(axis='y', which='major', labelsize=25)

    return ax

def volumeplot(ax,Df,days,width,alpha):
    for ind in range(len(Df)):
        if Df['Open'].iloc[ind] <= Df['Close'].iloc[ind]:
            x=days[ind]-width/2
            y=0
            height=Df['Volume'].iloc[ind]
            pp=Rectangle((x,y), width, height, angle=0.0, alpha=alpha,color='g',fill=True)
            ax.add_patch(pp)
        else:
            x=days[ind]-width/2
            y=0
            height=Df['Volume'].iloc[ind]
            pp=Rectangle((x,y), width, height, angle=0.0, alpha=alpha,color='r',fill=True)
            ax.add_patch(pp)

    return ax

  
        
def Bokehplots_GenerateHtmlPlots_SMAs(Df,plotconfig,plotdeploy):


    mids = (Df.Open + Df.Close)/2
    spans = abs(Df.Close-Df.Open)

    inc = Df.Close > Df.Open
    dec = Df.Open > Df.Close
    w = 12*60*60*1000 # half day in ms
 
    yrs=Df.index.year
    
    p=[]
    for ff in plotconfig:
        pp=figure(x_axis_type = "datetime",tools="pan,wheel_zoom,box_zoom,reset,previewsave,crosshair",
               name="candlestick", plot_height=ff['Dim'][0], plot_width=ff['Dim'][1])
        #plot_height=800, plot_width=1500   
        #hold()
        pp.title = ff['title'] 
        
        if 'Candle' in ff.keys():
            pp.segment(Df.date, Df.High, Df.date, Df.Low, color='black')

            pp.rect(Df.date[inc], mids[inc], w, spans[inc], fill_color="white", line_color="green")
            pp.rect(Df.date[dec], mids[dec], w, spans[dec], fill_color="red", line_color="red")
            pp.title =pp.title +' '+str(min(Df.index))[0:11]+' to ' +str(max(Df.index))[0:11]
            
        if 'SMA' in ff.keys():
            if 10 in ff['SMA']:
                pp.line(Df.date, Df.MA10, line_color="blue",line_width=1)
            if 20 in ff['SMA']:    
                pp.line(Df.date, Df.MA20, line_color="red",line_width=1)
            if 50 in ff['SMA']:
                pp.line(Df.date, Df.MA50, line_color="green",line_width=1)
            if 100 in ff['SMA']:
                pp.line(Df.date, Df.MA100, line_color="blue",line_width=2,line_dash=[2,4])
            if 200 in ff['SMA']:    
                pp.line(Df.date, Df.MA200, line_color="red",line_width=2,line_dash=[2,4])
            
            
        if 'EMA' in ff.keys():
            if 10 in ff['EMA']:
                pp.line(Df.date, Df.EMA10, line_color="blue",line_width=1)
            if 20 in ff['EMA']:    
                pp.line(Df.date, Df.EMA20, line_color="red",line_width=1)
            if 50 in ff['EMA']:
                pp.line(Df.date, Df.EMA50, line_color="green",line_width=1)
            if 100 in ff['EMA']:
                pp.line(Df.date, Df.EMA100, line_color="blue",line_width=2,line_dash=[2,4])
            if 200 in ff['EMA']:    
                pp.line(Df.date, Df.EMA200, line_color="red",line_width=2,line_dash=[2,4])
            
        
        if 'STD' in ff.keys():
            if 10 in ff['STD']:
                ssp=Df.MA10+2*Df.STD10
                ssm=Df.MA10-2*Df.STD10
                pp.line(Df.date, Df.MA10, line_color="blue",line_width=1)
                pp.line(Df.date, ssp, line_color="blue",line_width=1,line_dash=[4,4])
                pp.line(Df.date, ssm, line_color="blue",line_width=1,line_dash=[4,4])
            if 20 in ff['STD']:
                ssp=Df.MA20+2*Df.STD20
                ssm=Df.MA20-2*Df.STD20
                pp.line(Df.date, Df.MA20, line_color="red",line_width=1)
                pp.line(Df.date, ssp, line_color="red",line_width=1,line_dash=[4,4])
                pp.line(Df.date, ssm, line_color="red",line_width=1,line_dash=[4,4])
                
        if 'ESTD' in ff.keys():
            if 10 in ff['ESTD']:
                ssp=Df.EMA10+2*Df.ESTD10
                ssm=Df.EMA10-2*Df.ESTD10
                pp.line(Df.date, Df.EMA10, line_color="blue",line_width=1)
                pp.line(Df.date, ssp, line_color="blue",line_width=1,line_dash=[4,4])
                pp.line(Df.date, ssm, line_color="blue",line_width=1,line_dash=[4,4])
            if 20 in ff['ESTD']:
                ssp=Df.EMA20+2*Df.ESTD20
                ssm=Df.EMA20-2*Df.ESTD20
                pp.line(Df.date, Df.EMA20, line_color="red",line_width=1)
                pp.line(Df.date, ssp, line_color="red",line_width=1,line_dash=[4,4])
                pp.line(Df.date, ssm, line_color="red",line_width=1,line_dash=[4,4])        
        
        if 'MISCcols' in ff.keys():
            for lns in ff['MISCcols']:
                DS=Df[lns[0]].notnull()
                pp.line(DS.date, DS[lns[0]], line_color=lns[1],line_dash=lns[2],line_alpha=lns[3],line_width=lns[4])
        
        
        if 'MISCLines' in ff.keys():
            props=ff['MISCLines_props']
            #print ff['MISCLines']
            for lns in ff['MISCLines']:
                pp.line(lns[0], lns[1], line_color=props[0],line_dash=props[1],line_alpha=props[2],line_width=props[3])
        
        
        if 'Vol' in ff.keys():
            mm=max(Df.Volume)
            mids = (Df.Volume)/2.0
            pp.rect(Df.date[inc], mids[inc]/mm, w, Df.Volume[inc]/mm, fill_color="white", line_color="green")
            pp.rect(Df.date[dec], mids[dec]/mm, w, Df.Volume[dec]/mm, fill_color="red", line_color="red")

            
            
        if 'VolSMA' in ff.keys():
            mm=max(Df.Volume)
            if 10 in ff['VolSMA']:
                pp.line(Df.date, Df.VolMA10/mm, line_color="blue",line_width=1)
            if 20 in ff['VolSMA']:
                pp.line(Df.date, Df.VolMA20/mm, line_color="red",line_width=1)
            
            
        if 'VolEMA' in ff.keys():
            mm=max(Df.Volume)
            if 10 in ff['VolEMA']:
                pp.line(Df.date, Df.VolEMA10/mm, line_color="blue",line_width=1)
            if 20 in ff['VolEMA']:
                pp.line(Df.date, Df.VolEMA20/mm, line_color="red",line_width=1)
            
        f=yrs[0]        
        for g in range(1,len(yrs)):
            if yrs[g]>f:
                f=yrs[g]
                pp.line([Df.date.index[g],Df.date.index[g]], [min(Df.Close),max(Df.Close)], line_color="black",line_width=1,line_dash=[4,4])
                
        if 'Vol' in ff.keys() or 'VolSMA' in ff.keys() or 'VolEMA' in ff.keys():
            pp.title = pp.title + '   Max Vol = '+str(mm)
            pp.y_range = bokeh.models.ranges.Range1d(start=0, end=1)

        

        pp.yaxis.location="right"  
        pp.xaxis.major_label_orientation = pi/4
        pp.grid.grid_line_alpha=0.3
    
    
        p.append(pp)
        
        if showplot==True:
            output_file("lines.html", title="line plot example")
            print(p)
            # pf=gridplot([[p[0]],[p[1]]])
            show(p[0])
    
    return p     
    
    
    
#%%  ============================================================================= 
    
def GenerateHtmlDocPlotsDaily_SMAs_HTML(df,FileName):
    
    for i in range(0,len(df.keys()),30):
        reset_output()
        output_file(FileName+'_'+str(i), title='Daily_SMA')
        for s in df.keys()[i:(i+30)]:   
            plotconfig =[{'title':s,'Dim':[800,1500],'Candle':[],'SMA':[10,20,50,100,200]},
                        {'title':s,'Dim':[500,1500],'Vol':[],   'VolSMA':[10,20]}]
            p=Bokehplots_GenerateHtmlPlots_SMAs(df[s],plotconfig)  
            pf=gridplot([[p[0]],[p[1]]])
        
        show(pf)  # open a browser
        script, div = components(pf, CDN)
        return [script,div]

def GenerateHtmlDocPlotsDaily_EMAs_HTML(df,FileName):
    
    reset_output()
    output_file(FileName, title='Daily_EMA')
    for s in df.keys():        
        plotconfig =[{'title':s,'Dim':[800,1500],'Candle':[],'EMA':[10,20,50,100,200]},
                    {'title':s,'Dim':[500,1500],'Vol':[],   'VolEMA':[10,20]}]
        p=Bokehplots_GenerateHtmlPlots_SMAs(df[s],plotconfig)
        gridplot([[p[0]],[p[1]]])    
        
    show()  # open a browser
    
def GenerateHtmlDocPlotsDaily_STDs_HTML(df,FileName):
        
    reset_output()
    output_file(FileName, title='Daily_STD')
    for s in df.keys():        
        plotconfig =[{'title':s,'Dim':[800,1500],'Candle':[],'SMA':[10,20],'STD':[10,20]},
                    {'title':s,'Dim':[500,1500],'Vol':[],   'VolSMA':[10,20]}]
        p=Bokehplots_GenerateHtmlPlots_SMAs(df[s],plotconfig)  
        gridplot([[p[0]],[p[1]]])   
        
    show()  # open a browser
        
def GenerateHtmlDocPlotsDaily_ESTDs_HTML(df,FileName):
        
    reset_output()
    output_file(FileName, title='Daily_ESTD')
    for s in df.keys():        
        plotconfig =[{'title':s,'Dim':[800,1500],'Candle':[],'EMA':[10,20],'ESTD':[10,20]},
                    {'title':s,'Dim':[500,1500],'Vol':[],   'VolEMA':[10,20]}]
        p=Bokehplots_GenerateHtmlPlots_SMAs(df[s],plotconfig)
        gridplot([[p[0]],[p[1]]])            
    
    show()  # open a browser
    
def GenerateHtmlDocPlots_Daily_Weekly_HTML(dfd,dfw,FileName):
        
    reset_output()
    output_file(FileName, title='Daily_Weekly')
    for s in dfd.keys():
        plotconfig =[{'title':s,'Dim':[600,800],'Candle':[],'SMA':[10,20,50,100,200]},
                    {'title':s,'Dim':[300,800],'Vol':[],   'VolSMA':[10,20]}]
        pd=Bokehplots_GenerateHtmlPlots_SMAs(dfd[s],plotconfig)
         
        plotconfig =[{'title':s,'Dim':[600,800],'Candle':[],'SMA':[10,20,50,100,200]},
                    {'title':s,'Dim':[300,800],'Vol':[],   'VolSMA':[10,20]}]
        pw=Bokehplots_GenerateHtmlPlots_SMAs(dfw[s],plotconfig)
        
        gridplot([[pd[0],pw[0]],[pd[1],pw[1]]])      
            
    show()  # open a browser
        
def GenerateHtmlDocPlots_ALLSidebySide_HTML(df,FileName,plotconfig='None'):       
    reset_output()
    
    for i in range(0,len(df.keys()),30):
        reset_output()
        output_file(FileName+'_'+str(i), title='ALL_'+str(i))
        p=[];
        q=[];
        cnt=0;
        for s in df.keys()[i:(i+30)]:
            if plotconfig == 'None':
                plotconfig =[{'title':s,'Dim':[600,800],'Candle':[],'SMA':[10,20,50,100,200]},
                            {'title':s,'Dim':[300,800],'Vol':[],   'VolSMA':[10,20]}]
            else:
                for j in range(0,len(plotconfig)):
                    plotconfig[j]['title']=s
                    
                    
            pp=Bokehplots_GenerateHtmlPlots_SMAs(df[s],plotconfig)
            p.append([pp[0],pp[1]])
            cnt=cnt+1;
            if cnt==2:
                cnt=0
                q.append([p[0][0],p[1][0]])
                q.append([p[0][1],p[1][1]])
                gridplot(q)
                q=[]
                p=[]
                
        if len(p)==1:
            cnt=0 
            q.append([p[0][0]])
            q.append([p[0][1]])
            p=[]
            gridplot(q)  
        
          
        show()  # open a browser
        time.sleep(3) 
        
def GenerateHtmlDocPlots_IntervalShift_SidebySide_HTML(df,Symb,AggType,MaxInterval,ShiftBy,FileName,plotconfig='None'):
    # Only 1 stock plotted with interval shift
    # MaxInterval: Plot limits interval length r
    # ShiftBy: number of units to shift by
    reset_output()
    output_file(FileName, title=AggType+'_'+str(MaxInterval)+'Inter_'+str(ShiftBy)+'Shift')
    #p=[[[],[]],[[],[]],[[],[]]]
    p=[]        
    q=[]
    cnt=0
    l=len(df.index)
    ss=range(0,l,ShiftBy)
    for tt in ss:
        if tt+MaxInterval+ShiftBy>=l:
            DF=df.iloc[tt:].copy()
            if plotconfig == 'None':
                plotconfig =[{'title':Symb,'Dim':[400,600],'Candle':[],'SMA':[10,20,50,100,200]},
                            {'title':Symb,'Dim':[200,600],'Vol':[],   'VolSMA':[10,20]}]
            else:
                for j in range(0,len(plotconfig)):
                    plotconfig[j]['title']=Symb
            pp=Bokehplots_GenerateHtmlPlots_SMAs( DF,plotconfig)
            #p[cnt][0]=p1
            #p[cnt][1]=p2
            p.append(pp)
            cnt=cnt+1;
            if cnt==3:
                cnt=0
                q.append([p[0][0],p[1][0],p[2][0]])
                q.append([p[0][1],p[1][1],p[2][1]])               
                #p=[[[],[]],[[],[]],[[],[]]]
                #gridplot(q)  
                #q=[]
                p=[]
            break
            
        DF=df.iloc[tt:(tt+MaxInterval)].copy()
        if plotconfig == 'None':
            plotconfig =[{'title':Symb,'Dim':[400,600],'Candle':[],'SMA':[10,20,50,100,200]},
                        {'title':Symb,'Dim':[200,600],'Vol':[],   'VolSMA':[10,20]}]
        else:
                for j in range(0,len(plotconfig)):
                    plotconfig[j]['title']=Symb

        pp=Bokehplots_GenerateHtmlPlots_SMAs( DF,plotconfig)
        #p[cnt][0]=p1
        #p[cnt][1]=p2
        p.append(pp)
        cnt=cnt+1;
        if cnt==3:
            cnt=0
            q.append([p[0][0],p[1][0],p[2][0]])
            q.append([p[0][1],p[1][1],p[2][1]])               
            #p=[[[],[]],[[],[]],[[],[]]]
            #gridplot(q)  
            #q=[]
            p=[]
        
              
    if len(p)==1:
        q.append([p[0][0]])
        q.append([p[0][1]])
        p=[]
    if len(p)==2:
        q.append([p[0][0],p[1][0]])
        q.append([p[0][1],p[1][1]])
        p=[]
            
    gridplot(q)    
    show()  # open a browser


def JUST_BOKEH(Q,Filename,window,ShiftBy):
    reset_output()
    output_file(Filename, title='Fitting'+'_'+str(window)+'-'+str(ShiftBy))


    gridplot(Q)    
    show()  # open a browser
    
    

    
def compressImages(path,typ):
    files=os.listdir(path)
    files_png=[ff for ff in files if os.path.isfile(os.path.join(path,ff))]
    files_png=[ff for ff in files_png if imghdr.what(os.path.join(path,ff))=='png']
    ffdirs=[os.path.join(path,dd) for dd in files if os.path.isdir(os.path.join(path,dd))]
    # pdb.set_trace()
    for fp in ffdirs:
        compressImages(fp,typ)
    for pp in files_png:
        ff=os.path.join(path,pp)
        f2=os.path.join(path,'temp_'+pp)
        print ff
        if typ=='ImageCompress':
            ram=open(ff)
            im = Image.open(ram)
            im2 = im.convert('RGB').convert('P', palette=Image.ADAPTIVE)
            im2.save( f2, optimize=True,quality=70,format='PNG')    #
            ram.close()
            im.close()
            im2.close()
            g=open(f2)
            g.close()
            time.sleep(0.5)
            sbp.call(['mv',f2,ff])
        elif typ=='XtremeImageCompress':
            ram=open(ff)
            im = Image.open(ram)
            im2 = im.convert('RGB').convert('P', palette=Image.ADAPTIVE, colors=10)
            im2.save( f2 , optimize=True,quality=70,format='PNG')    #            
            ram.close()
            im.close()
            im2.close()
            g=open(f2)
            g.close()
            time.sleep(0.5)
            sbp.call(['mv',f2,ff])
    
    
      
