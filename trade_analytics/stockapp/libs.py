from __future__ import division
from utility  import codemanager as cdmng
import stockapp.models as stkmd
import utility.models as utmd

import os
import imp
import shutil
import pandas as pd
import time



class DataMetaManager(object):
	def __init__(self,collist):
		self.collist=collist

	def getdf(self):
		pass
		
	