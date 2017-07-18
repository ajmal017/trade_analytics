from __future__ import division

import numpy as np
import pandas as pd
import collections
import pdb
from scipy import interp
import scipy
import pickle
import os
import json
from scipy.sparse import coo_matrix, hstack ,vstack
import copy
import datascience.models as dtscmd

np.random.seed(1337)  # for reproducibility


###################################################################
####################   KERAS  #####################################
###################################################################
from keras.models import load_model
from keras.models import Sequential
from keras.layers.core import Dense, Dropout, Flatten
from keras.layers.convolutional import Convolution2D, MaxPooling2D, ZeroPadding2D,Convolution1D,ZeroPadding1D
from keras.optimizers import SGD
from keras.callbacks import EarlyStopping
from keras.utils import np_utils
from keras import __version__ as keras_version
from keras import regularizers
from keras.layers import Dense, Dropout, Activation
from keras.layers.advanced_activations import LeakyReLU,PReLU
from keras.layers.pooling import AveragePooling1D
from keras.datasets import mnist
from keras.models import Sequential
from keras.layers import Dense, Dropout, Activation, Flatten
from keras.layers import Convolution2D, MaxPooling2D
from keras.utils import np_utils
from keras import backend as K
from keras.preprocessing.image import ImageDataGenerator, array_to_img, img_to_array, load_img

from keras import applications
# deep models
from keras.layers import Input
from keras.preprocessing import image
from keras.applications.resnet50 import preprocess_input, decode_predictions
from keras.applications.resnet50 import ResNet50
from keras.applications.vgg16 import VGG16
from keras.applications.vgg19 import VGG19
from keras.applications.inception_v3 import InceptionV3




###################################################################
####################   SKLEARN  #####################################
###################################################################
from sklearn.cross_validation import KFold
from sklearn.metrics import log_loss
from sklearn.externals import joblib
from sklearn.metrics import average_precision_score,accuracy_score,recall_score,precision_score
from sklearn.metrics import log_loss,accuracy_score
from sklearn.tree import DecisionTreeClassifier
from sklearn import tree
from sklearn import preprocessing
from sklearn.preprocessing import OneHotEncoder,LabelEncoder
from sklearn import linear_model,decomposition
from sklearn.linear_model import LogisticRegression
from sklearn.feature_extraction import DictVectorizer
from sklearn import metrics
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score,r2_score
from sklearn.ensemble import RandomForestClassifier
from sklearn import svm
from sklearn.svm import SVC 
from sklearn.svm import LinearSVC
from sklearn.discriminant_analysis import QuadraticDiscriminantAnalysis
from sklearn.model_selection import StratifiedKFold
from itertools import cycle
from sklearn.metrics import roc_curve, auc

from sklearn.ensemble import ExtraTreesRegressor
from sklearn.neighbors import KNeighborsRegressor
from sklearn.linear_model import LinearRegression,SGDClassifier
from sklearn.linear_model import RidgeCV
from sklearn.cross_validation import train_test_split
from sklearn.tree import DecisionTreeRegressor
from sklearn.model_selection import cross_val_score, ShuffleSplit

from sklearn import datasets
from sklearn.model_selection import train_test_split
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import classification_report
from sklearn.svm import SVC


###################################################################
####################   XGBOOST  #####################################
###################################################################
import xgboost as xgb


###################################################################
####################   Exporting  #####################################
###################################################################




###################################################################
####################   BASE MODELS  #####################################
###################################################################


class BaseClassificationModel(object):
	name=None
	savetype='joblib'
	classification_type='binary'

	def __init__(self,model):
		self.model=model
		self.clf=self.loadmodel()
		if 'validation_metrics' not in self.model.Misc:
			self.model.Misc['validation_metrics']={}

	def loadmodel(self):
		path=self.model.modelpath()
		if self.saveformat=='joblib':
			with open(path,'r') as F:
				clf=joblib.load(F)

		return clf


	@classmethod
	def GenModels(cls,Project,data):
		pass

	def loaddata(self):
		if self.model.Data.Datatype!='Train':
			raise Exception("Need Training Data For model")
		self.validation_datasets=self.model.Data.ParentData.objects.filter(Datatype='Validation')
		self.train_data=self.model.Data 

	def pre_processing_train(self):
		"""
		Load the data and pre process it and then send it
		"""
		X,Y=self.train_data.full_data()
		return (X,Y)

	def pre_processing_validation(self,validation_data):
		"""
		Load the data and pre process it and then send it
		"""
		X,Y=validation_data.gen_shard()
		return (X,Y)

	def post_process_model(self):
		pass

	def train(self):
		X,Y=self.pre_processing_train()

		self.clf.fit(X,Y)

		self.post_process_model()

		self.model.Status='Trained'
		self.model.save()

	def predict(self,X):
		return self.clf.predict(X)

	def Run_validation(self,validation_data):
		Ypred=None
		Yvalid=None
		for X,Y in self.pre_processing_validation(validation_data):
			if Ypred is None:
				Ypred=self.predict(X)
				Yvalid=Y
			else:
				Ypred=np.vstack((Ypred, self.predict(X) ))
				Yvalid=np.vstack((Yvalid, Y ))

		model_metrics=self.getmetrics(Ypred,Yvalid)
		obj, created = dtscmd.ModelMetrics.objects.get_or_create(Data=validation_data,MLmodel=self.model)
		obj.Metrics=model_metrics
		obj.save()




	def Run_validation_all(self):
		for validation_data in self.validation_datasets:
			self.Run_validation(validation_data)

		self.model.Status='Validated'
		self.model.save()

	def Run_validation_id(self,validationid):
		validation_data = self.validation_datasets.get(id=validationid)
		self.Run_validation(validation_data)



	def getmetrics(self,Ypred,Yvalid):

		logloss=log_loss(Yvalid ,Ypred, eps=1e-15, normalize=True)
		avgprec= average_precision_score(Yvalid, Ypred)
		acc= accuracy_score(Yvalid, Ypred )
		recallscore= recall_score(Yvalid, Ypred,average='micro' )
		precisionscore= precision_score(Yvalid, Ypred ,average='micro' )

		model_metrics={'logloss':logloss, 'avgprec':avgprec, 'acc':acc, 'recallscore':recallscore , 'precisionscore':precisionscore }
		return model_metrics


	def savemodel(self):
		if self.model.saveformat=='joblib':
			joblib.dump(self.clf, self.model.modelpath())

		self.model.save()


		


