import pickle as pkl
import zlib
import zmq
import pandas as pd

colors=['b','g','r','c','m','y','k','w']
markers=['o','s','^','<','>','*','+']

indicatorlist_std=[ 
	{'name':'SMA','timeperiod':20,'colname':'SMA20'},
	{'name':'SMA','timeperiod':50,'colname':'SMA50'},
	{'name':'SMA','timeperiod':100,'colname':'SMA100'},
	{'name':'SMA','timeperiod':200,'colname':'SMA200'},
	{'name':'EMA','timeperiod':8,'colname':'EMA8'},
] 




pricecols_std=[
			{'colname':'SMA20','plotargs':('r',),'plotkwargs':{'label':'SMA20',}},
			{'colname':'SMA50','plotargs':('b',),'plotkwargs':{'label':'SMA50',}},
			{'colname':'SMA100','plotargs':('g',),'plotkwargs':{'label':'SMA100',}},
			{'colname':'SMA200','plotargs':('m',),'plotkwargs':{'label':'SMA200',}},
			{'colname':'EMA8','plotargs':('r--',),'plotkwargs':{'label':'EMA8',}},

]


def request_db_charts(entries,ip,indicatorlist=indicatorlist_std,pricecols=pricecols_std,querycols=(),featcols=(),window=360):
	if type(entries)==pd.DataFrame:
		if 'T' in entries.columns:
			df=entries[['Symbol','T']].copy()
			df['TF']=df['T']
			df['T0']=df['TF'].apply(lambda x: (x-pd.DateOffset(window)).date() )
		else:		
			df=entries['Symbol'].copy()
			df['TF']=df.index.copy()
			df['T0']=df['TF'].apply(lambda x: (x-pd.DateOffset(window)).date() )

		entries=df[['Symbol','TF','T0']].to_dict('records')

	context = zmq.Context()

	print("Connecting to charting server")
	socket = context.socket(zmq.REQ)
	socket.connect("tcp://localhost:%s" % ip)

	msg={'indicatorlist':indicatorlist,'pricecols':pricecols,'querycols':querycols,'featcols':featcols,'entries':entries }
	p=pkl.dumps(msg)
	z=zlib.compress(p)

	socket.send(z)

	#  Get the reply.
	message = socket.recv()
	print message
	socket.close()
