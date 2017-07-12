import pandas as pd
import numpy as np
from stockdata.models import GetSectors,GetIndustries,GetStockData,GetStockMeta
from research.featuremanager import Rallylength


# Id: 1
# User: @general@
# Name: FutMXRtQt
# Group: Performance
# Description:  The maximum quaterly performance i.e profit(positive)/loss(negative) possible T+3m assuming buy on T date
# Created at: 2016-07-12 23:00:15.338585+00:00
# Updated at: 2016-07-12 23:00:15.338604+00:00
None

#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---

# Id: 2
# User: @general@
# Name: FutMNRtQt
# Group: Performance
# Description:  The minimum quaterly performance i.e profit(positive)/loss(negative) possible T+3m assuming buy on T date
# Created at: 2016-07-12 23:00:15.382205+00:00
# Updated at: 2016-07-12 23:00:15.382229+00:00
None

#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---

# Id: 3
# User: @general@
# Name: FutMXRtHf
# Group: Performance
# Description:  The maximum half yearly performance i.e profit(positive)/loss(negative) possible T+6m assuming buy on T date
# Created at: 2016-07-12 23:00:15.415759+00:00
# Updated at: 2016-07-12 23:00:15.415781+00:00
None

#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---

# Id: 4
# User: @general@
# Name: FutMNRtHf
# Group: Performance
# Description:  The minimum half yearly performance i.e profit(positive)/loss(negative) possible T+6m assuming buy on T date
# Created at: 2016-07-12 23:00:15.448701+00:00
# Updated at: 2016-07-12 23:00:15.448724+00:00
None

#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---

# Id: 5
# User: @general@
# Name: FutMXRtAn
# Group: Performance
# Description:  The maximum annual performance i.e profit(positive)/loss(negative) possible T+1y assuming buy on T date
# Created at: 2016-07-12 23:00:15.481932+00:00
# Updated at: 2016-07-12 23:00:15.481955+00:00
None

#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---

# Id: 6
# User: @general@
# Name: FutMNRtAn
# Group: Performance
# Description:  The minimum annual performance i.e profit(positive)/loss(negative) possible T+1y assuming buy on T date
# Created at: 2016-07-12 23:00:15.515572+00:00
# Updated at: 2016-07-12 23:00:15.515594+00:00
None

#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---

# Id: 7
# User: @general@
# Name: PastMXRtQt
# Group: Performance
# Description:  The maximum quaterly performance i.e profit(positive)/loss(negative) in T-3m assuming sell on T date
# Created at: 2016-07-12 23:00:15.548354+00:00
# Updated at: 2016-07-12 23:00:15.548378+00:00
None

#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---

# Id: 8
# User: @general@
# Name: PastMNRtQt
# Group: Performance
# Description:  The minimum quaterly performance i.e profit(positive)/loss(negative) in T-3m assuming sell on T date
# Created at: 2016-07-12 23:00:15.581657+00:00
# Updated at: 2016-07-12 23:00:15.581680+00:00
None

#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---

# Id: 9
# User: @general@
# Name: PastMXRtHf
# Group: Performance
# Description:  The maximum half yearly performance i.e profit(positive)/loss(negative) in T-6m assuming sell on T date
# Created at: 2016-07-12 23:00:15.615371+00:00
# Updated at: 2016-07-12 23:00:15.615391+00:00
None

#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---

# Id: 10
# User: @general@
# Name: PastMNRtHf
# Group: Performance
# Description:  The minimum half yearly performance i.e profit(positive)/loss(negative) in T-6m assuming sell on T date
# Created at: 2016-07-12 23:00:15.647985+00:00
# Updated at: 2016-07-12 23:00:15.648008+00:00
None

#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---

# Id: 11
# User: @general@
# Name: PastMXRtAn
# Group: Performance
# Description:  The maximum half yearly performance i.e profit(positive)/loss(negative) in T-1y assuming sell on T date
# Created at: 2016-07-12 23:00:15.681267+00:00
# Updated at: 2016-07-12 23:00:15.681290+00:00
None

#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---

# Id: 12
# User: @general@
# Name: PastMNRtAn
# Group: Performance
# Description:  The minimum half yearly performance i.e profit(positive)/loss(negative) in T-1y assuming sell on T date
# Created at: 2016-07-12 23:00:15.714910+00:00
# Updated at: 2016-07-12 23:00:15.714942+00:00
None

#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---

# Id: 15
# User: nagavenkat
# Name: RV15
# Group: Volume
# Description: Number of candles with Relative volumne greater than 1.5
# Created at: 2016-07-14 22:38:10.907180+00:00
# Updated at: 2016-07-14 22:38:10.907215+00:00
def RV15(data):
	#numpy available as np
	#pandas available as pd
	# No other module can be used
	T=data["T"]
	df=data["df"]
	TrendsMid=data["TrendsMid"]
	TrendsTop=data["TrendsTop"]
	TrendsBottom=data["TrendsBottom"]
	return len(df[df['VolRel10']>=1.5])

#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---

# Id: 16
# User: nagavenkat
# Name: RV2
# Group: Volume
# Description: Number of candles in the window for which relative volume(with volume SMA10) is greater than 2
# Created at: 2016-07-14 22:39:51.024007+00:00
# Updated at: 2016-07-14 22:39:51.024040+00:00
def RV2(data):
	#numpy available as np
	#pandas available as pd
	# No other module can be used
	T=data["T"]
	df=data["df"]
	TrendsMid=data["TrendsMid"]
	TrendsTop=data["TrendsTop"]
	TrendsBottom=data["TrendsBottom"]
	return len(df[df['VolRel10']>=2])

#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---

# Id: 17
# User: nagavenkat
# Name: RV3
# Group: Volume
# Description: Number of candles with relative volume greater than
# Created at: 2016-07-14 22:49:46.757978+00:00
# Updated at: 2016-07-14 22:49:46.758012+00:00
def RV3(data):
	#numpy available as np
	#pandas available as pd
	# No other module can be used
	T=data["T"]
	df=data["df"]
	TrendsMid=data["TrendsMid"]
	TrendsTop=data["TrendsTop"]
	TrendsBottom=data["TrendsBottom"]
	return len(df[df['VolRel10']>=3])

#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---

# Id: 18
# User: nagavenkat
# Name: RV4
# Group: Volume
# Description: Number of candles with RV greater than 4
# Created at: 2016-07-14 22:50:55.218349+00:00
# Updated at: 2016-07-14 22:50:55.218384+00:00
def RV4(data):
	#numpy available as np
	#pandas available as pd
	# No other module can be used
	T=data["T"]
	df=data["df"]
	TrendsMid=data["TrendsMid"]
	TrendsTop=data["TrendsTop"]
	TrendsBottom=data["TrendsBottom"]
	return len(df[df['VolRel10']>=4])

#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---

# Id: 19
# User: nagavenkat
# Name: GAPUP
# Group: Price
# Description: Number of gap ups in the window
# Created at: 2016-07-14 22:54:35.960343+00:00
# Updated at: 2016-07-14 22:54:35.960394+00:00
def GAPUP(data):
	#numpy available as np
	#pandas available as pd
	# No other module can be used
	T=data["T"]
	df=data["df"]
	dfmax=df[['Open','Close']].max(axis=1)
	dfmin=df[['Open','Close']].min(axis=1)
	gapups=dfmin.iloc[1:]-dfmax.iloc[0:-1]  # current min - prev max
	return len(gapups[gapups>=0])

#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---

# Id: 20
# User: nagavenkat
# Name: GAPDWN
# Group: Price
# Description: Number of candles with gap down in window
# Created at: 2016-07-14 22:56:26.458071+00:00
# Updated at: 2016-07-14 22:56:26.458109+00:00
def GAPDWN(data):
	#numpy available as np
	#pandas available as pd
	# No other module can be used
	T=data["T"]
	df=data["df"]
	dfmax=df[['Open','Close']].max(axis=1)
	dfmin=df[['Open','Close']].min(axis=1)
	gapdowns=dfmin.iloc[0:-1]-dfmax.iloc[1:]
	return len(gapdowns[gapdowns>0])

#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---

# Id: 21
# User: nagavenkat
# Name: SMA10
# Group: Price
# Description: Number of candles above SMA10
# Created at: 2016-07-14 23:01:36.314607+00:00
# Updated at: 2016-07-14 23:01:36.314645+00:00
def SMA10(data):
	#numpy available as np
	#pandas available as pd
	# No other module can be used
	T=data["T"]
	df=data["df"]
	dfmax=df[['Open','Close']].max(axis=1)
	dfabove10=dfmax-df['SMA10']
	return len(dfabove10[dfabove10>=0])

#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---

# Id: 22
# User: nagavenkat
# Name: SMA20
# Group: Price
# Description: Number of candles above SMA20
# Created at: 2016-07-14 23:04:32.537840+00:00
# Updated at: 2016-07-14 23:04:32.537876+00:00
def SMA20(data):
	#numpy available as np
	#pandas available as pd
	# No other module can be used
	T=data["T"]
	df=data["df"]
	dfmax=df[['Open','Close']].max(axis=1)
	dfabove20=dfmax-df['SMA20']
	return len(dfabove20[dfabove20>=0])

#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---

# Id: 23
# User: nagavenkat
# Name: SMA102050100200
# Group: Price
# Description: Number of candles for which SMA10 > SMA20 > SMA50 > SMA100 > SMA200
# Created at: 2016-07-14 23:06:14.912779+00:00
# Updated at: 2016-07-14 23:06:14.912814+00:00
def SMA102050100200(data):
	#numpy available as np
	#pandas available as pd
	# No other module can be used
	T=data["T"]
	Df=data["df"]
	Dfabove102050100200=Df[(Df['SMA10'] >= Df['SMA20']) & (Df['SMA20'] >= Df['SMA50']) & (Df['SMA50'] >= Df['SMA100']) & (Df['SMA100'] >= Df['SMA200'])].copy()
	return len(Dfabove102050100200)

#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---

# Id: 24
# User: nagavenkat
# Name: SMA50100200
# Group: Price
# Description: Number of candles for which SMA50 > SMA100 > SMA200
# Created at: 2016-07-14 23:08:07.347150+00:00
# Updated at: 2016-07-14 23:08:07.347188+00:00
def SMA50100200(data):
	#numpy available as np
	#pandas available as pd
	# No other module can be used
	T=data["T"]
	Df=data["df"]
	Dfabove50100200=Df[(Df['SMA50'] >= Df['SMA100']) & (Df['SMA100'] >= Df['SMA200'])].copy()    
	return len(Dfabove50100200)

#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---

# Id: 25
# User: nagavenkat
# Name: SMA102050
# Group: Price
# Description: No of candles for which SMA10 > SMA20 > SMA50
# Created at: 2016-07-14 23:12:01.029261+00:00
# Updated at: 2016-07-14 23:12:01.029298+00:00
def SMA102050(data):
	#numpy available as np
	#pandas available as pd
	# No other module can be used
	T=data["T"]
	Df=data["df"]
	Dfabove2050=Df[(Df['SMA10'] >= Df['SMA20']) & (Df['SMA20'] >= Df['SMA50'])].copy() 
	return len(Dfabove2050)

#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---

# Id: 14
# User: nagavenkat
# Name: CNDLS
# Group: description
# Description: Number of Candles in the window
# Created at: 2016-07-14 22:36:06.790949+00:00
# Updated at: 2016-07-27 21:02:19.010728+00:00
def CNDLS(data):
	#numpy available as np
	#pandas available as pd
	# No other module can be used
	T=data["T"]
	df=data["df"]
	TrendsMid=data["TrendsMid"]
	TrendsTop=data["TrendsTop"]
	TrendsBottom=data["TrendsBottom"]
	
# 	data['DebugOutput']='OK'
	return len(df)

#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---

# Id: 26
# User: nagavenkat
# Name: SMA102050100200_rally
# Group: Price
# Description: Number of consecutive candles for which SMA10 > SMA20 > SMA50 > SMA100 > SMA200
# Created at: 2016-07-14 23:34:49.164356+00:00
# Updated at: 2016-07-21 02:59:29.408951+00:00
def SMA102050100200_rally(data):
	#numpy available as np
	#pandas available as pd
	# No other module can be used
	T=data["T"]
	Df=data["df"]
	Df['No']=range(len(Df))
	Dfabove102050100200=Df[(Df['SMA10'] >= Df['SMA20']) & (Df['SMA20'] >= Df['SMA50']) & (Df['SMA50'] >= Df['SMA100']) & (Df['SMA100'] >= Df['SMA200'])].copy()
	L=Rallylength(Dfabove102050100200['No'].values,tol=3)
	m=-1
	p=-1
	for i in range(len(L)):
	    if len(L[i])>m:
	        m=len(L[i])
	        p=L[i]
	data['DebugOutput']=[aa.strftime('%Y-%m-%d') for aa in Df.index[p]]
	return m

#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---

# Id: 27
# User: nagavenkat
# Name: SMA2050100200_Trally
# Group: Price
# Description: Longest rally from the end for wchich SMA 20 > 50 >100 > 200
# Created at: 2016-07-23 01:25:44.070572+00:00
# Updated at: 2016-07-28 16:46:33.264404+00:00
def SMA2050100200_Trally(data):
	#numpy available as np
	#pandas available as pd
	# No other module can be used
	T=data["T"]
	Df=data["df"]
	Df['No']=range(len(Df))
	Dfabove2050100200=Df[(Df['SMA20'] >= Df['SMA50']) & (Df['SMA50'] >= Df['SMA100']) & (Df['SMA100'] >= Df['SMA200'])].copy()
	L=Rallylength(Dfabove2050100200['No'].values,tol=3)
	cnt=0
	for ind in Df['No'].iloc[-10:-1]:
	    if ind in L[-1]:
	        cnt=cnt+1
	if cnt >0:
	    data['DebugOutput']={"dates":[aa.strftime('%Y-%m-%d') for aa in Df.index[L[-1]] ], "L[-1]":list( L[-1] ) ,"EndNo":Df['No'].iloc[-10:-1].tolist() }
	    return len(L[-1])
	else:
	    data['DebugOutput']={"dates":[aa.strftime('%Y-%m-%d') for aa in Df.index[L[-1]] ], "L[-1]":list( L[-1] ) ,"EndNo":Df['No'].iloc[-10:-1].tolist() }
	    return 0

#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---

# Id: 28
# User: nagavenkat
# Name: Close
# Group: Price
# Description: Close price
# Created at: 2016-09-03 22:00:37.761039+00:00
# Updated at: 2016-09-03 22:00:37.761073+00:00
def Close(data):
	#numpy available as np
	#pandas available as pd
	# No other module can be used
	T=data["T"]
	df=data["df"]
	TrendsMid=data["TrendsMid"]
	TrendsTop=data["TrendsTop"]
	TrendsBottom=data["TrendsBottom"]
	# Use data["DebugOutput"] to show output for debugging
	return float(df['Close'].iloc[-1])

#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---

# Id: 29
# User: nagavenkat
# Name: RV05
# Group: Volume
# Description: Number of candles with Relative volumne less than 0.5
# Created at: 2016-09-03 22:04:18.301031+00:00
# Updated at: 2016-09-03 22:04:18.301063+00:00
def RV05(data):
	#numpy available as np
	#pandas available as pd
	# No other module can be used
	T=data["T"]
	df=data["df"]
	TrendsMid=data["TrendsMid"]
	TrendsTop=data["TrendsTop"]
	TrendsBottom=data["TrendsBottom"]
	# Use data["DebugOutput"] to show output for debugging
	return len(df[df['VolRel10']<=0.5])

#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---

# Id: 30
# User: nagavenkat
# Name: RV025
# Group: Volume
# Description: Number of candles with Relative volumne less than 0.25
# Created at: 2016-09-03 22:05:35.893310+00:00
# Updated at: 2016-09-03 22:05:35.893343+00:00
def RV025(data):
	#numpy available as np
	#pandas available as pd
	# No other module can be used
	T=data["T"]
	df=data["df"]
	TrendsMid=data["TrendsMid"]
	TrendsTop=data["TrendsTop"]
	TrendsBottom=data["TrendsBottom"]
	# Use data["DebugOutput"] to show output for debugging
	return len(df[df['VolRel10']<=0.25])

#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---

