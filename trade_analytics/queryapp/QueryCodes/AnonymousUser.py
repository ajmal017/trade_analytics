from __future__ import division
from queryapp.libs import registerquery, querymodel
import pandas as pd
import numpy as np
filename=__name__.split('.')[-1]


# --------------  features has to be the name of the class ------------------
# Define your features in this class

class queries(querymodel):
	
	
	@registerquery(filename=filename,category='Momentum')
	def CCICHERRIES(self,T):
		"""
		HasCherries
		"""
		if not hasattr(self,'Qdf'):
			self.Qdf=self.GetStockData(self.Symbolid)

		if 'CCI5' not in self.Qdf.columns:
			self.Qdf['CCI5']=self.GetFeature('CCI5')

		if 'CCI50' not in self.Qdf.columns:
			self.Qdf['CCI50']=self.GetFeature('CCI50')

		if 'CCICHERRIES' not in self.Qdf.columns:
			self.Qdf['CCICHERRIES']=(self.Qdf['CCI50']-self.Qdf['CCI5'])>180
			self.Qdf['CCICHERRIES']=self.Qdf['CCICHERRIES'].apply(lambda x: int(x))
			

		ind=self.Qdf.index[self.Qdf.index<=T]
		if len(ind)>0:
			ind=ind[-1]
			return self.Qdf.loc[ind,'CCICHERRIES'] 
		else:
			return None
		



	


# --------- This is required to sync the features to the database -------------
queries.finalize(filename)