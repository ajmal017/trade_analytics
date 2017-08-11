import numpy as np
import pandas as pd
import stockdata.models as stkmd
import models as md
from stockdata.models import GetSectors,GetIndustries,GetStockData,GetStockMeta


# Id:
# User: @general@
# Name: Close
# Group: Price
# Description: Close Price at T
# Operators: gt,lt,gte,lte,equalto
# Units: None
# Created at:
# Updated at:
def Close(data):
	#numpy available as np
	#pandas available as pd
	# No other module can be used
	T=data["T"]
	df=data["df"]
	TrendsMid=data["TrendsMid"]
	TrendsTop=data["TrendsTop"]
	TrendsBottom=data["TrendsBottom"]
	return df['Close'].iloc[-1]




# Id:
# User: @general@
# Name: RV05
# Group: Volume
# Description: Number of candles with Relative volumne less than 0.5
# Created at:
# Updated at:
def RV05(data):
	#numpy available as np
	#pandas available as pd
	# No other module can be used
	T=data["T"]
	df=data["df"]
	TrendsMid=data["TrendsMid"]
	TrendsTop=data["TrendsTop"]
	TrendsBottom=data["TrendsBottom"]
	return len(df[df['VolRel10']<=0.5])


# Id:
# User: @general@
# Name: RV025
# Group: Volume
# Description: Number of candles with Relative volumne less than 0.25
# Created at:
# Updated at:
def RV025(data):
	#numpy available as np
	#pandas available as pd
	# No other module can be used
	T=data["T"]
	df=data["df"]
	TrendsMid=data["TrendsMid"]
	TrendsTop=data["TrendsTop"]
	TrendsBottom=data["TrendsBottom"]
	return len(df[df['VolRel10']<=0.25])