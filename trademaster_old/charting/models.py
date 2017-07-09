from __future__ import unicode_literals
from __future__ import division

from django.db import models
import pandas as pd
from django import forms
from django.utils.safestring import mark_safe
from django.core.files import File
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
import json
import re
import tempfile
import numpy as np
import stockdata.models as stkmd

import os


import CTA.GenConfig as GC
import CTA.PatternRecognition.FeaturesExtraction as FE

years=list(np.arange(2002,pd.datetime.today().year+1,1))
years=[str(ss) for ss in years]

intervals=(('D','Daily'),('W','Weekly'),('M','Monthly'))

def LoadChartStyle_choice(user,username):
    choices=[]
    chartstyles_gen=StdChartProps.objects.filter(user=User.objects.get(username='@general@'))
    choices=choices+[(str(ss.pk),ss.chartstylename) for ss in chartstyles_gen]
    choices=choices+[('None','-----')]
    if username!='@general@':
        chartstyles_user=StdChartProps.objects.filter(user=user)
        choices=choices+[(str(ss.pk),ss.chartstylename) for ss in chartstyles_user]
    return choices

# import CTA.StockDataManager as SDM

# import CTA.PlotingManager as pltmag

# for each user save the type of chart properties



def DecodeChartUrls(url):
    from urlparse import urlparse, parse_qs
    o = urlparse(url)
    query = parse_qs(o.query)
    print url
    print query

    if 's' in query:
        symbol=query['s'][0]
    else:
        symbol=''

    if 'chartname' in query:
        chartname=query['chartname'][0]
    else:
        chartname=None

    if 'w' in query:
        window=query['w'][0]
    else:
        window=''

    if 'upch_pk' in query:
        upch_pk=query['upch_pk'][0]
    else:
        upch_pk=None

    
    if 'I' in query:
        Interval=query['I'][0]
    else:
        Interval=''


    if 'tf' in query:
        ToDate=query['tf'][0].split(',')
        ToDate=[int(ff) for ff in ToDate]
        tf=pd.datetime(ToDate[0],ToDate[1],ToDate[2])
    else:
        ToDate=None
        tf=None

    if 'ci' in query:
        candle_indicators=query['ci'][0].split(',')
    else:
        candle_indicators=''

    if 'vi' in query:
        volume_indicators=query['vi'][0].split(',')
    else:
        volume_indicators=''   

    if 'i' in query:
        indicators=query['i'][0].split(',')
    else:
        indicators=''

    if 'cp' in query:
        candle_patterns=query['cp'][0].split(',')
    else:
        candle_patterns=''

    if 'ch' in query:
        channels=query['ch'][0].split(',')
    else:
        channels=''

    if 'lt' in query:
        LinearTrends=query['lt'][0].split(',')
    else:
        LinearTrends=''

    if 'chartstyle__pk' in query:
        chartstyle__pk=int( query['chartstyle__pk'][0].split(',') )
    else:
        chartstyle__pk=-1
        
    if StdChartProps.objects.filter(pk=int(chartstyle__pk)).exists():
        chartpropquery=StdChartProps.objects.get(pk=int(chartstyle__pk)).GetChartProp()
    else:
        scp=StdChartProps.objects.get(chartstylename='@default@')
        chartpropquery=scp.GetChartProp()
        chartstyle__pk=scp.pk


    if window!='':
        window=int(window)
    else:
        window=None

    if Interval=='':
        Interval='D'
            
    print "---"*5
    print symbol
    print ToDate
    print Interval
    print window
    print candle_indicators
    print volume_indicators
    print indicators
    print candle_indicators
    print channels
    print LinearTrends
    print "+++"*5

    


    


    Output={'symbol':symbol,'ToDate':ToDate,
            'Interval':Interval,'window':window,'candle_indicators':candle_indicators,
            'volume_indicators':volume_indicators,'indicators':indicators,
            'channels':channels,'LinearTrends':LinearTrends,'chartstyle__pk':chartstyle__pk,'upch_pk':upch_pk,'chartname':chartname,
            'tf':tf,'chartpropquery':chartpropquery}

    return Output



# props_ci=['SMA10','SMA20','SMA50','SMA100','SMA200','EMA10','EMA20' , 'EMA50','EMA100' ,'EMA200' , 'STD10','STD20' ,'STD50', 'STD100', 'STD200',
#         'ESTD10', 'ESTD20', 'ESTD50', 'ESTD100', 'ESTD200']
# props_vi=['VolSMA10','VolSMA20' , 'VolEMA10','VolEMA20', 'VolSTD10', 'VolSTD20']
# props_i=['Return', 'ReturnSMA10', 'ReturnSMA20', 'SMAmaxDiff','AmpSMA10']
# props_cp=GC.CandlePatterns.keys()
# props_ch=FE.tubes.keys()
# props_lt=['top','mid','bottom']

# chartpropquery['ci']=[]
# chartpropquery['vi']=
# chartpropquery['i']=
# chartpropquery['cp']=
# chartpropquery['ch']=
# chartpropquery['lt']=


def GetYahooCharts_url(Symbol,window,width="300px",height="200px",mode='lazy'):
    if window==360:
        window='1y'
    if window==180:
        window='6m'
    if window==90:
        window='3m'
    if mode=='lazy':
        # return mark_safe('<img class="lazy" data-original="'+reverse('charting:savedchart')+'?charttype='+Plotname+'">') 
        return mark_safe('<img class="lazy" data-original="'+'http://chart.finance.yahoo.com/z?s='+Symbol+'&t='+window+'&q=c&l=on&z=l&p=m10,m20,m50,m100,m200'+'" style="width:'+width+';height:'+height+';">')             
    else:
        return mark_safe('<img src="'+'http://chart.finance.yahoo.com/z?s='+Symbol+'&t='+window+'&q=c&l=on&z=l&p=m10,m20,m50,m100,m200'+'" style="width:'+width+';height:'+height+';">') 



class StdChartProps(models.Model):
    chartstylename=models.CharField(max_length=20,null=True)
    user = models.ManyToManyField(User)
    chartprop=models.CharField(max_length=300,null=True)

    def UpdateChartProp(self,chartpropquery):
        self.chartprop=json.dumps(chartpropquery)

    def GetChartProp(self):
        return json.loads(self.chartprop)

    def __str__(self):
        return str(self.chartstylename)

def image_path(instance, filename):
    pth=os.path.join(str(instance.user),str(instance.window),str(instance.Interval),str(instance.chartsrc),instance.T.strftime("%Y-%m-%d")   )

    return os.path.join(pth,str(instance.Symbol)+'_'+str(instance.chartname)+'_'+str(instance.chartstyle_id) )

class UploadCharts(models.Model):
    
    chartname=models.CharField(max_length=500,null=True,blank=True)
    chartsrc=models.CharField(max_length=2,choices=[('Y','Yahoo'),('C','Custom'),('T','TradingView')], null=True,blank=True, default='C')
    chartstyle=models.ForeignKey(StdChartProps, on_delete=models.CASCADE, null=True)

    window=models.DecimalField(max_digits=4,decimal_places=0,null=True,blank=True)
    T= models.DateField(null=False)
    Symbol=models.ForeignKey(stkmd.Stock, on_delete=models.CASCADE,null=True)
    Interval = models.CharField(max_length=1, choices=intervals)
    user=models.ForeignKey(User, on_delete=models.CASCADE, null=True)


    created_at = models.DateTimeField(auto_now_add=True,null=True)
    updated_at = models.DateTimeField(auto_now=True,null=True)

    image = models.ImageField(upload_to=image_path)
    responsepng=models.TextField(null=True,blank=True)

    def uploadimage2file(self,file):
        temp = open(file, 'r')
        self.image = File(temp)
        self.save() 
        temp.close()

    def uploaddummy2file(self):
        from django.conf import settings
        
        file=os.path.join( settings.BASE_DIR,'charting' ,'static','charting','dummy.png' )
        temp = open(file, 'r')
        self.image = File(temp)
        self.save() 
        temp.close()

    def uploadfig2file(self,fig):
        # convert dict to json and save
        tf = tempfile.NamedTemporaryFile(suffix='.png',delete=False)
        fig.savefig(tf.name,bbox_inches='tight',transparent=True, format='png')
        temp = open(tf.name, 'r')
        self.image = File(temp)
        self.save() 
        temp.close()

    def get_remote_image(self,image_url):
        import urllib
        result = urllib.urlretrieve(image_url)
        self.image.save(
                os.path.basename(image_url),
                File(open(result[0]))
                )
        self.save()

    def GetcleanedURL(self):
        ss=self.image.url
        sk=ss.split('?')[0]
        if '.png' in ss and '.png' not in sk:
            sk=sk+'.png'
        return sk
    def GetorMakeChartUrls(self,mode='lazy',width="600px",height="500px",delayit=False):

        if bool(self.image) is False:
            import charting.tasks as tks
            if delayit==False:
                tks.MakeChart(str(self.Symbol),self.T.strftime("%Y,%m,%d"),int(self.window),self.Interval,self.pk,None)                
            else:
                # self.uploaddummy2file()
                tks.MakeChart.delay(str(self.Symbol),self.T.strftime("%Y,%m,%d"),int(self.window),self.Interval,self.pk,None)
                return "None"
                
            self.refresh_from_db()

        if mode=='lazy':
            # return mark_safe('<img class="lazy" data-original="'+reverse('charting:savedchart')+'?charttype='+Plotname+'">') 
            return mark_safe('<img class="lazy" data-original="'+self.GetcleanedURL()+'" style="width:'+width+';height:'+height+';">')             
        else:
            return mark_safe('<img src="'+self.GetcleanedURL()+'" style="width:'+width+';height:'+height+';">') 

    def Geturl_QuickCharturl(self,mode='lazy',width="600px",height="500px",delayit=False):

        if bool(self.image) is False:
            self.save()
            
            if mode=='lazy':
                return mark_safe('<img class="lazy" data-original="'+reverse('charting:quickchart')+'?upch_pk='+str(self.pk)+'" style="width:'+width+';height:'+height+';">') 
            else:
                return mark_safe('<img src="'+reverse('charting:quickchart')+'?upch_pk='+str(self.pk)+'" style="width:'+width+';height:'+height+';">') 
        else:
            if mode=='lazy':
                # return mark_safe('<img class="lazy" data-original="'+reverse('charting:savedchart')+'?charttype='+Plotname+'">') 
                return mark_safe('<img class="lazy" data-original="'+self.GetcleanedURL()+'" style="width:'+width+';height:'+height+';">')             
            else:
                return mark_safe('<img src="'+self.GetcleanedURL()+'" style="width:'+width+';height:'+height+';">') 

    @classmethod
    def GetCreateUrl_QuickCharturl(cls,symbol,T,window,Interval,chartname,chartsrc,chartstyle__pk,mode='lazy',width="600px",height="500px"):
        stk=stkmd.Stock.objects.get(Symbol=symbol)
        scp=StdChartProps.objects.get(pk=int(chartstyle__pk))
        if UploadCharts.objects.filter(user=None,Symbol=stk,T=T,window=window,Interval=Interval,chartname=chartname,chartsrc=chartsrc,chartstyle=scp).exists():
            chart=UploadCharts.objects.get(user=None,Symbol=stk,T=T,window=window,Interval=Interval,chartname=chartname,chartsrc=chartsrc,chartstyle=scp)   
        else:       
            chart=cls(user=None,Symbol=stk,T=T,window=window,Interval=Interval,chartname=chartname,chartsrc=chartsrc,chartstyle=scp)
            chart.save()

        return chart.Geturl_QuickCharturl(mode=mode,width=width,height=height)

    @classmethod
    def GetCreateMakeChart(cls,symbol,T,window,Interval,chartname,chartsrc,chartstyle__pk,mode='lazy',width="600px",height="500px"):
        stk=stkmd.Stock.objects.get(Symbol=symbol)
        scp=StdChartProps.objects.get(pk=int(chartstyle__pk))
        if UploadCharts.objects.filter(user=None,Symbol=stk,T=T,window=window,Interval=Interval,chartname=chartname,chartsrc=chartsrc,chartstyle=scp).exists():
            chart=UploadCharts.objects.get(user=None,Symbol=stk,T=T,window=window,Interval=Interval,chartname=chartname,chartsrc=chartsrc,chartstyle=scp)   
        else:       
            chart=cls(Symbol=stk,T=T,window=window,Interval=Interval,chartname=chartname,chartsrc=chartsrc,chartstyle=scp)
            chart.save()

        return chart.GetorMakeChartUrls(mode=mode,width=width,height=height,delayit=True)


    def load_responsepng(self,response):
        # with open(self.image.file, "rb") as f:
        response.content=self.image.file.read()
        return response


def GetCreateUrl_QuickCharturl_bulk(df,chartstyle__pk,chartname='StockChart',chartsrc='C',mode='lazy',width="600px",height="500px"):
    stks=stkmd.Stock.objects.filer(Symbol__in=df['Symbols'].tolist()).distinct('Symbol')
    scp=StdChartProps.objects.get(pk=int(chartstyle__pk))
    UCs=UploadCharts.objects.filter(user=None,Symbol__in=stks,T__in=list(df['T'].unique()),window__in=list(df['window'].unique()),Interval__in=list(df['Interval'].unique()),chartname=chartname,chartsrc=chartsrc,chartstyle=scp)
    dUC=pd.DataFrame(list( UCs.values('Symbol__Symbol','T','window','Interval','image','chartname','chartsrc','chartstyle__pk') ))
    dUC['index']=dUC['T'].apply(lambda x : x.strftime("%Y-%m-%d"))+'_'+dUC['Symbol__Symbol']+'_'+dUC['window'].astype(str)+'_'+dUC['Interval']
    df['index']=df['T'].apply(lambda x : x.strftime("%Y-%m-%d"))+'_'+df['Symbol__Symbol']+'_'+df['window'].astype(str)+'_'+df['Interval']
    todoindex=list( set(df['index'].tolist())-set(dUC['index'].tolist()) )
    L=[]
    for ind in df[ df['index'].isin(todoindex) ].index:
        stk=stkmd.Stock.objects.get(Symbol=df.loc[ind,'Symbols'])
        L.append(UploadCharts(user=None,Symbol=stk, T=df.loc[ind,'T'],window=df.loc[ind,'window'],Interval=df.loc[ind,'Interval'],chartname=chartname,chartsrc=chartsrc,chartstyle=scp))
    UploadCharts.objects.bulk_create(L)
    
    # if UploadCharts.objects.filter(user=None,Symbol=stk,T=T,window=window,Interval=Interval,chartname=chartname,chartsrc=chartsrc,chartstyle=scp).exists():
    #     chart=UploadCharts.objects.get(user=None,Symbol=stk,T=T,window=window,Interval=Interval,chartname=chartname,chartsrc=chartsrc,chartstyle=scp)   
    # else:       
    #     chart=UploadCharts(user=None,Symbol=stk,T=T,window=window,Interval=Interval,chartname=chartname,chartsrc=chartsrc,chartstyle=scp)
    #     chart.save()

    # return chart.Geturl_QuickCharturl(mode=mode,width=width,height=height)




## ------------------------   FORMS  ------------------------------------------------------
class Chartprops(forms.Form):
    
    props_ci=['SMA10','SMA20','SMA50','SMA100','SMA200','EMA10','EMA20' , 'EMA50','EMA100' ,'EMA200' , 'STD10','STD20' ,'STD50', 'STD100', 'STD200',
            'ESTD10', 'ESTD20', 'ESTD50', 'ESTD100', 'ESTD200']
    props_vi=['VolSMA10','VolSMA20' , 'VolEMA10','VolEMA20', 'VolSTD10', 'VolSTD20']
    props_i=['Return', 'ReturnSMA10', 'ReturnSMA20', 'SMAmaxDiff','AmpSMA10']


    props_cp=GC.CandlePatterns.keys()
    props_ch=FE.tubes.keys()
    props_lt=['top','mid','bottom']

    saved_chartstyles = forms.ChoiceField(label='Select a saved chart style', widget=forms.Select,choices=[],required=False)

    chartstylename=forms.CharField(label='Save Chart properties as ',widget=forms.Textarea( attrs={'rows': 1,'cols': 30}),required=False)

    SMA10=forms.BooleanField(label='10 day SMA: Close',required=False,initial=False)
    SMA20=forms.BooleanField(label='20 day SMA: Close',required=False,initial=False)
    SMA50=forms.BooleanField(label='50 day SMA: Close',required=False,initial=False)
    SMA100=forms.BooleanField(label='100 day SMA: Close',required=False,initial=False)
    SMA200=forms.BooleanField(label='200 day SMA: Close',required=False,initial=False)

    EMA10=forms.BooleanField(label='10 day EMA: Close',required=False,initial=False)
    EMA20=forms.BooleanField(label='20 day EMA: Close',required=False,initial=False)
    EMA50=forms.BooleanField(label='50 day EMA: Close',required=False,initial=False)
    EMA100=forms.BooleanField(label='100 day EMA: Close',required=False,initial=False)
    EMA200=forms.BooleanField(label='200 day EMA: Close',required=False,initial=False)

    STD10=forms.BooleanField(label='10 day SM-STD: Close',required=False,initial=False)
    STD20=forms.BooleanField(label='20 day SM-STD: Close',required=False,initial=False)
    STD50=forms.BooleanField(label='50 day SM-STD: Close',required=False,initial=False)
    STD100=forms.BooleanField(label='100 day SM-STD: Close',required=False,initial=False)
    STD200=forms.BooleanField(label='200 day SM-STD: Close',required=False,initial=False)

    ESTD10=forms.BooleanField(label='10 day EM-STD: Close',required=False,initial=False)
    ESTD20=forms.BooleanField(label='20 day EM-STD: Close',required=False,initial=False)
    ESTD50=forms.BooleanField(label='50 day EM-STD: Close',required=False,initial=False)
    ESTD100=forms.BooleanField(label='100 day EM-STD: Close',required=False,initial=False)
    ESTD200=forms.BooleanField(label='200 day EM-STD: Close',required=False,initial=False)


    VolSMA10=forms.BooleanField(label='10 day SMA: Volume',required=False,initial=False)
    VolSMA20=forms.BooleanField(label='20 day SMA: Volume',required=False,initial=False)
    VolEMA10=forms.BooleanField(label='10 day EMA: Volume',required=False,initial=False)
    VolEMA20=forms.BooleanField(label='20 day EMA: Volume',required=False,initial=False)


    VolSTD10=forms.BooleanField(label='10 day SM-STD: Volume',required=False,initial=False)
    VolSTD20=forms.BooleanField(label='20 day SM-STD: Volume',required=False,initial=False)
    
    Return=forms.BooleanField(label='Daily Return',required=False,initial=False)
    ReturnSMA10=forms.BooleanField(label='10 day SMA: Return',required=False,initial=False)   
    ReturnSMA20=forms.BooleanField(label='20 day SMA: Return',required=False,initial=False)

    SMAmaxDiff=forms.BooleanField(label='SMAmaxDiff Indicator',required=False,initial=False)
    AmpSMA10=forms.BooleanField(label='AmpSMA10 Indicator',required=False,initial=False)

    choices=[(str(key),str(value)) for key,value in GC.CandlePatterns.iteritems()]
    candle_patterns=forms.MultipleChoiceField(label='Select multiple Candle Patterns',choices=choices,required=False ,widget=forms.SelectMultiple(attrs={'size':'10','style':'width:400px;'}))

    pp=FE.tubes.keys()
    choices=[(str(key),str(key)) for key in sorted(pp)]
    channels=forms.MultipleChoiceField(label='Select the channel',choices=choices,required=False ,widget=forms.SelectMultiple(attrs={'size':'10',}))

    linear_trends=forms.MultipleChoiceField(label='Select linear trends',choices=[('top','top'),('mid','mid'),('bottom','bottom')],required=False ,widget=forms.SelectMultiple )

    def __init__(self, *args, **kwargs):

        if 'user' in kwargs.keys():
            self.user=kwargs.pop('user')
            self.username=str(self.user)
            if str(self.user)=='AnonymousUser':
                self.username='@general@'
                self.user=User.objects.get(username=self.username)
           
        else:
            self.username='@general@'
            self.user=User.objects.get(username='@general@')


        super(Chartprops, self).__init__(*args, **kwargs)

        LoadChartStyle_choice

        # self.fields['saved_chartstyles'].choices=[('','default')]+[(str(ss),str(ss)) for ss in StdChartProps.objects.filter(user=self.user)]
        self.fields['saved_chartstyles'].choices=LoadChartStyle_choice(self.user,self.user.username)
        

    def update_chartstyle(self):
        if self.cleaned_data['chartstylename']=='' or self.cleaned_data['chartstylename']==None:
            self.cleaned_data['chartstylename']=='default'

        if StdChartProps.objects.filter(user=self.user,chartstylename=self.cleaned_data['chartstylename']).exists()==False:
            chartpropstyle=StdChartProps(chartstylename=self.cleaned_data['chartstylename'])
            chartpropstyle.save()
            chartpropstyle.user.add(self.user)
            Q=self.getquery()
            chartpropstyle.UpdateChartProp(Q)
            chartpropstyle.save()
        else:
            chartpropstyle=StdChartProps.objects.get(user=self.user,chartstylename=self.cleaned_data['chartstylename'])
            Q=self.getquery()
            chartpropstyle.UpdateChartProp(Q)
            chartpropstyle.save()

    def GetSavedChartProp(self):
        print "99"*5
        print self.cleaned_data['saved_chartstyles']
        chartpropstyle=StdChartProps.objects.get(user=self.user,chartstylename=self.cleaned_data['saved_chartstyles'])
        Q=chartpropstyle.GetChartProp()
        return Q

    def getquery(self):
        print self.cleaned_data

        Q={'ci':[],'vi':[],'i':[],'cp':[],'ch':[],'lt':[]}
        for ss in self.props_ci:
            try: 
                if self.cleaned_data[ss]==True:
                    Q['ci'].append(ss)
            except:
                pass
        for ss in self.props_vi:
            try: 
                if self.cleaned_data[ss]==True:
                    Q['vi'].append(ss)
            except:
                pass

        for ss in self.props_i:
            try: 
                if self.cleaned_data[ss]==True:
                    Q['i'].append(ss)
            except:
                pass

        Q['cp']=self.cleaned_data['candle_patterns']
        Q['ch']=self.cleaned_data['channels']
        Q['lt']=self.cleaned_data['linear_trends']


        return Q


class Charts_view_form(forms.Form):
    watchlist = forms.ChoiceField(label='Select Stocks from Watchlist', widget=forms.Select,choices=[])
    symbol = forms.CharField(label='and/or Enter the symbols (comma/space separated for multiple)',widget=forms.Textarea( attrs={'rows': 1,
                                  'cols': 40,
                                  'style': 'height: 2em;'}),required=False)
    
    T = forms.DateField(label='To date',widget=forms.SelectDateWidget(years=years,
        empty_label=("Choose Year", "Choose Month", "Choose Day"),
    ),initial=pd.datetime.today().date())

    window=forms.ChoiceField(label='window length',choices=[('None','Select'),(90,'3 months'),(180,'6 months'),(360,'1 year'),(720,'2 years')],initial='None')
    Interval=forms.ChoiceField(label='Interval',choices=[('D','Daily')],initial='D')

    T0=forms.DateField(label='from date',widget=forms.SelectDateWidget(years=years,
        empty_label=("Choose Year", "Choose Month", "Choose Day"),
    ),required=False)

    def __init__(self, *args, **kwargs):

        if 'user' in kwargs.keys():
            self.user=kwargs.pop('user')
            self.username=str(self.user)
            if str(self.user)=='AnonymousUser':
                self.username='@general@'
                self.user=User.objects.get(username=self.username)
           
        else:
            self.username='@general@'
            self.user=User.objects.get(username='@general@')


        super(Charts_view_form, self).__init__(*args, **kwargs)

        print self.username

        self.fields['watchlist'].choices=[('None','Select Watchlist'),(str('None'),str('-------'))]

        if self.username!='@general@':
            try:
                Wuser=stkmd.Watchlist.objects.filter(user=self.user)
                Wuser=[str(w) for w in Wuser]
            except:
                Wuser=[]
            self.fields['watchlist'].choices=self.fields['watchlist'].choices+[(str(w),str(w)) for w in Wuser]

        try:
            Wgen=stkmd.Watchlist.objects.filter(user=User.objects.get(username='@general@') )
            Wgen=[str(w) for w in Wgen]
        except:
            Wgen=[]

        self.fields['watchlist'].choices=self.fields['watchlist'].choices+[(str('None'),str('-------'))]
        self.fields['watchlist'].choices=self.fields['watchlist'].choices+[(str(w),str(w)) for w in Wgen]

        self.symbs=[]

    def process_charts(self,user=None,chartpropquery=None):
        if user is None:
            user=User.objects.get(username='@general@')
            
        if str(user)=='AnonymousUser':
            user=User.objects.get(username='@general@')
        
        try:
            symbs=re.compile(r'[:,\s\n]').split(self.cleaned_data['symbol'])
            symbs=list(set(symbs))
            symbs=[ss.upper() for ss in symbs if ss!='']
            self.symbs=self.symbs+symbs
        except:
            pass
        
        print user
        print self.cleaned_data['watchlist']

        if self.cleaned_data['watchlist']!='None' and self.cleaned_data['watchlist']!=None:
            try:
                W=stkmd.Watchlist.objects.get(user=user,watchlistname=self.cleaned_data['watchlist'])
            except:
                return False,"Watchlist "+self.cleaned_data['watchlist']+" is not present for user "+str(user)

            symbs=W.stocks.all()
            self.symbs=self.symbs+[str(ss) for ss in symbs]
    

        print ", ".join(self.symbs)
        print "-+-"*10
        print chartpropquery
        print self.cleaned_data['window']
        print self.cleaned_data['T']
        print self.cleaned_data['T0']

        Interval=self.cleaned_data['Interval']
        
        T=pd.to_datetime(self.cleaned_data['T'],format="%Y-%m-%d").date()

        if (self.cleaned_data['T0']==None or self.cleaned_data['T0']=='None') and (self.cleaned_data['window']!=None or self.cleaned_data['window']!='None'):
            window=int( self.cleaned_data['window'] )
            T0=GC.GetWindowTfs(T,window)[0]
        elif (self.cleaned_data['T0']!=None or self.cleaned_data['T0']!='None') and (self.cleaned_data['window']==None or self.cleaned_data['window']=='None'):
            T0=pd.to_datetime(self.cleaned_data['T0'],format="%Y-%m-%d").date()
            window=(T-T0).days

        # t0str=T0.strftime("%Y,%m,%d")
        # tfstr=T.strftime("%Y,%m,%d")


        self.charturls=None

        if len(self.symbs)>0:
            # self.charturls=[]
            # for ss in self.symbs:
            #     self.charturls.append('?s='+ss+'&t0='+t0str+'&tf='+tfstr+'&w='+str(window)+'&ci='+chartpropquery['ci']+'&vi='+chartpropquery['vi']+'&i='+chartpropquery['i']+'&cp='+chartpropquery['cp'])
            self.charturls=GetChartUrls(self.symbs,T0,T,window,Interval,chartpropquery=chartpropquery,mode='lazy',width="600px",height="500px")





# class Chart_Study(forms.Form):
#     Symbol = forms.CharField(label='Append New Symbols (comma/space separated for multiple)',widget=forms.Textarea(attrs={'style':'width:300px;height:50px'})
#                                                     ,required=False)
    
#     def __init__(self, *args, **kwargs):
        
        
#         if 'watchlistname' in kwargs.keys():
#             self.watchlistname=kwargs.pop('watchlistname')
#         else:
#             self.watchlistname=None

#         if 'user' in kwargs.keys():
#             self.user=kwargs.pop('user')
#             if str(self.user)=='AnonymousUser':
#                 self.username='AnonymousUser'
#                 self.user=User.objects.get(username='@general@')
#             else:
#                 self.username=str(self.user)
#         else:
#             self.username='AnonymousUser'
#             self.user=User.objects.get(username='@general@')

#         super(Watchlist_view_form, self).__init__(*args, **kwargs)

#         if self.username!='AnonymousUser' and self.username!='@general@':
#             try:
#                 Wuser=Watchlist.objects.filter(user=self.user)
#                 Wuser=[str(w) for w in Wuser]
#             except:
#                 Wuser=[]
#             self.fields['watchlist'].choices=self.fields['watchlist'].choices+[(str(w),str(w)) for w in Wuser]

#         try:
#             Wgen=Watchlist.objects.filter(user=User.objects.get(username='@general@') )
#             Wgen=[str(w) for w in Wgen]
#         except:
#             Wgen=[]

        
#         self.fields['watchlist'].choices=self.fields['watchlist'].choices+[(str('-------'),str('-------'))]
#         self.fields['watchlist'].choices=self.fields['watchlist'].choices+[(str(w),str(w)) for w in Wgen]

#         self.symbs=[]

#         print "0---"*5
#         print '*'+str(self.watchlistname)+'*'
#         print '*'+str(self.user)+'*'

#         if self.watchlistname!=None:

#             try:
#                 W=Watchlist.objects.get(user=self.user,watchlistname=self.watchlistname)
#             except:
#                 try:
#                     W=Watchlist.objects.get(user=User.objects.get(username='@general@'),watchlistname=self.watchlistname)
#                 except:
#                     return False,"Watchlist "+self.watchlistname+" is not present for user "+str(self.user)

#             symbs=W.stocks.all()

#             self.symbs=[str(ss) for ss in symbs]
#             print ", ".join(self.symbs)








