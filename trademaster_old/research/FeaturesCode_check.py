import pandas as pd
import numpy as np 

from research.feature_exec import Rallylength

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

