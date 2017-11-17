import pandas as pd
import numpy as np
"""
Module for Datasets
- Dataset holds X,Y,Meta
- Can be a single file, single in memory X,Y
- Can be shards
- Has to support :
	- run a function that runs on a full column
	- run a function that runs on all columns simultaneously
	- run a function on set of samples

- apply a pipeline of functions that modify the sample
"""

class Dataset(object):

	def apply_pipeline(self,pipeline,axis=0):
		pass
