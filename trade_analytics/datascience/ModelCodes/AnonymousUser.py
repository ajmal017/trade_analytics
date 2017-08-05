from __future__ import division
from datascience.ML import MLmodels
import numpy as np
filename=__name__.split('.')[-1]



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


