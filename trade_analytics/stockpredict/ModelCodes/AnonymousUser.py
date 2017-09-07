from __future__ import division
from datascience.ML import MLmodels
import numpy as np
import pandas as pd
import keras

filename=__name__.split('.')[0]


############################ Customize models here ###############################

class RandomForrrest_1(MLmodels.RandomForrestmodels):
	"""
	Random forrest :
	@input: 30 days close, 30 days volume : flat
	@output: 0-1 class : profit/(profit+loss) 
	"""
	filename=filename

	def pre_processing_train(self,X,Y):
		return (X,np.round(Y))

	def pre_processing_validation(self,X,Y):
		return (X,np.round(Y))


class RandomForrrest_2(MLmodels.RandomForrestmodels):
	"""
	Random forrest :
	@input: 23 days close+SMA_all, 23 days volume+SMA10 : flat
	@output: 0-1 class : 1 is return >5% 
	"""
	filename=filename
	RequiredInputCols=['High','Low','SMA10','SMA20','SMA50','SMA100','SMA200','Volume','VolSMA10']
	def pre_processing_train(self,X,Y):
		Y[Y<5]=0
		Y[Y>=5]=1
		return (X,Y)

	def pre_processing_validation(self,X,Y):
		Y[Y<5]=0
		Y[Y>=5]=1
		return (X,Y)
	

class SVC_1(MLmodels.LinearSVCmodels):
	"""
	SVC
	@input: 23 days close+SMA_all, 23 days volume+SMA10 : flat
	@output: 0-1 class : 1 is return >5%  
	"""
	filename=filename
	RequiredInputCols=['High','Low','SMA10','SMA20','SMA50','SMA100','SMA200','Volume','VolSMA10']
	def pre_processing_train(self,X,Y):
		Y[Y<5]=0
		Y[Y>=5]=1
		return (X,Y)

	def pre_processing_validation(self,X,Y):
		Y[Y<5]=0
		Y[Y>=5]=1
		return (X,Y)


class QDA_1(MLmodels.QDAmodels):
	"""
	SVC
	@input: 23 days close+SMA_all, 23 days volume+SMA10 : flat
	@output: 0-1 class : 1 is return >5%  
	"""
	filename=filename
	RequiredInputCols=['High','Low','SMA10','SMA20','SMA50','SMA100','SMA200','Volume','VolSMA10']
	def pre_processing_train(self,X,Y):
		Y[Y<5]=0
		Y[Y>=5]=1
		return (X,Y)

	def pre_processing_validation(self,X,Y):
		Y[Y<5]=0
		Y[Y>=5]=1
		return (X,Y)


	
class NN_1(MLmodels.NNmodels_1layer):
	"""
	Neural networks 1D :
	@input: 23 days close+SMA_all, 23 days volume+SMA10 : flat
	@output: 0-1 class : 1 is return >5% 
	"""
	filename=filename
	RequiredInputCols=['High','Low','SMA10','SMA20','SMA50','SMA100','SMA200','Volume','VolSMA10']
	def pre_processing_train(self,X,Y):
		Y[Y<5]=0
		Y[Y>=5]=1
		Y=keras.utils.np_utils.to_categorical(Y)
		return (X,Y)

	def pre_processing_validation(self,X,Y):
		Y[Y<5]=0
		Y[Y>=5]=1
		Y=keras.utils.np_utils.to_categorical(Y)
		return (X,Y)
	

