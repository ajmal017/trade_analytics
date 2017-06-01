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
import datascience.ML.MLmodels as MLmd

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
####################   BASE MODELS  #####################################
###################################################################

def GetModelClass(ModelClassName):
	if ModelClassName=='XGBOOST':
		return XGBOOSTmodels

	elif ModelClassName=='RandomForrest':
		return RandomForrestmodels

	elif ModelClassName=='LinearSVC':
		return LinearSVCmodels

	elif ModelClassName=='NN':
		return NNmodels

	elif ModelClassName=='CNN1D':
		return CNN1Dmodels

	else:
		print "Model not implemented"
		return None


class BaseClassificationModel(object):
	name=None
	savetype='joblib'

	def __init__(self):
		self.modelspara={}
		self.models={}
		self.modelsinfo={}

	def preprocessing_train(self,X_train,y_train):
		pass

	def preprocessing_test(self,X_test,y_test):
		pass

	def postprocess_model(self,modelname):
		pass

	def GenModels(self):
		pass

	def getmetrics(self,modelname):
		clf=self.models[modelname]
		Ypred = clf.predict(self.dtest)

		logloss=log_loss(self.y_test, Ypred, eps=1e-15, normalize=True)
		avgprec= average_precision_score(self.y_test, Ypred)
		acc= accuracy_score(self.y_test, Ypred )
		recallscore= recall_score(self.y_test, Ypred,average='micro' )
		precisionscore= precision_score(self.y_test, Ypred ,average='micro' )

		return {'logloss':logloss, 'avgprec':avgprec, 'acc':acc, 'recallscore':recallscore , 'precisionscore':precisionscore }

	@classmethod
	def loadmodel(cls,modelpath,modelname,modelinfo,modelpara):
		if cls.savetype=='joblib':
			clf=joblib.load(modelpath)
		C=cls()
		C.models[modelname]=clf
		C.modelsinfo[modelname]=modelinfo
		C.modelspara[modelname]=modelpara

	@classmethod
	def loadmodel_db(cls,model):
		if cls.savetype=='joblib':
			clf=joblib.load(model.modelpath())
		C=cls()
		C.models[modelname]=clf
		C.modelsinfo[modelname]=modelinfo
		C.modelspara[modelname]=modelpara

	def savemodel(self,modelname,path):
		clf=self.models[modelname]
		if clf.savetype=='joblib':
			joblib.dump(clf, os.path.join(path, modelname) )

	def trainmodel(self,modelname):

		n_estimators = self.modelslist[modelname]['n_estimators']
		max_features=self.modelslist[modelname]['max_features']
		max_depth=self.modelslist[modelname]['max_depth']

		

		clf.fit(self.X_train,self.y_train)
		self.models[modelname] =self.postprocess_model(clf)



		param = self.modelslist[modelname]['param']
		num_round = self.modelslist[modelname]['num_round']
		early_stopping_rounds=self.modelslist[modelname]['early_stopping_rounds']

		watchlist  = [(self.dtrain,'train')]

		clf = xgb.train(param, self.dtrain, num_round, watchlist,early_stopping_rounds=early_stopping_rounds,verbose_eval = False)
		self.models[modelname] =self.postprocess_model(clf)


###################################################################
####################   XGBOOST  #####################################
###################################################################
class XGBOOSTmodels(BaseClassificationModel):
	name='XGBOOST'
	savetype='joblib'

	def preprocessing_train(self,X_train,y_train):
		self.dtrain = xgb.DMatrix(X_train, label=y_train.reshape(-1,1))

	def preprocessing_test(self,X_test,y_test):
		self.dtest = xgb.DMatrix(X_test)
		self.y_test=y_test

	def postprocess_model(self,clf):
		return clf

	def GenModels(self):
		N=0
		param = {
					'max_depth':100, 'eta':0.02, 'silent':1, 'objective':'multi:softmax','num_class':8, 
					'nthread' :6, 'eval_metric':'mlogloss', 'subsample': 0.7, 'colsample_bytree': 0.7,
					'min_child_weight':0, 'booster':"gblinear",
				}
		num_round = 300
		early_stopping_rounds=10

		self.modelslist['XGBOOST_'+str(N)]= {'num_round':num_round,'early_stopping_rounds':early_stopping_rounds ,'param':param}



###################################################################
####################   RandomForrest  #####################################
###################################################################
class RandomForrestmodels(BaseClassificationModel):
	name='RandomForrest'
	saveformat='joblib'

	@classmethod
	def GenModels(cls,Project,data):
		N=0
		for n_estimators in [10,100,250,500]:
			for max_depth in [10,100,250,500]:
				for max_features in [30,40,50,60]:
					clf=RandomForestClassifier(n_estimators=n_estimators, n_jobs=5,max_depth=max_depth,max_features=max_features)
					modelparas={'n_estimators':n_estimators, 'n_jobs':5,'max_depth':max_depth,'max_features':max_features}
					model=MLmd.MLmodels(Project=Project,Data=data,Name=cls.name,Misc={'modelparas':modelparas} ,Status='UnTrained' ,saveformat=cls.saveformat)
					model.save()
					model.initialize()
					filename=model.modelpath()
					joblib.dump(clf, filename)
					N=N+1

	

###################################################################
####################   LinearSVC  #####################################
###################################################################
class LinearSVCmodels(BaseClassificationModel):
	name='LinearSVC'
	savetype='joblib'

	def preprocessing_train(self,X_train,y_train):
		self.X_train = X_train
		self.y_train = y_train

	def preprocessing_test(self,X_test,y_test):
		self.X_test = X_test
		self.y_test=y_test

	def postprocess_model(self,clf):
		return clf

	def GenModels(self):
		N=0
		for C in [1, 10, 100, 1000,10000]:
			C = self.modelslist[modelname]['C']
			clf=LinearSVC(C=C)
			clf.fit(self.X_train,self.y_train)
			self.models[modelname] =self.postprocess_model(clf)

			self.modelslist[self.name+'_'+str(N)]= {'C':C}
			N=N+1



###################################################################
####################   NN  #####################################
###################################################################
class NNmodels(BaseClassificationModel):
	name='NN'
	savetype='joblib'

	def preprocessing_train(self,X_train,y_train):
		self.X_train = X_train
		self.y_train = y_train

	def preprocessing_test(self,X_test,y_test):
		self.X_test = X_test
		self.y_test=y_test

	def postprocess_model(self,clf):
		return clf

	def GenModels(self):
		N=0
		batch_size = 500
		nb_epoch = 100
		random_state = 51
		
		model = Sequential()
		model.add(Dense(output_dim=100, input_dim=self.input_dim,kernel_regularizer=regularizers.l2(0.1),))
		model.add(Activation("linear"))
		model.add(Dropout(0.5))

		model.add(Dense(output_dim=8))
		model.add(Activation("softmax"))

		sgd = SGD(lr=1e-3, decay=1e-6, momentum=0.3, nesterov=True)
		model.compile(optimizer=sgd, loss='categorical_crossentropy', metrics=['accuracy'])
		self.modelslist[self.name+'_'+str(N)]=model
		
		C = self.modelslist[modelname]['C']
		clf=LinearSVC(C=C)
		clf.fit(self.X_train,self.y_train)
		self.models[modelname] =self.postprocess_model(clf)

		N=N+1


###################################################################
####################   CNN1D  #####################################
###################################################################
class CNN1Dmodels(BaseClassificationModel):
	name='CNN1D'
	savetype='joblib'

	def preprocessing_train(self,X_train,y_train):
		self.X_train = X_train
		self.y_train = y_train

	def preprocessing_test(self,X_test,y_test):
		self.X_test = X_test
		self.y_test=y_test

	def postprocess_model(self,clf):
		return clf

	def GenModels(self):
		N=0
		batch_size = 16
		nb_epoch = 20
		random_state = 51



		model = Sequential()
		model.add(ZeroPadding2D((1, 1), input_shape=(3, 224, 224)))
		model.add(Convolution2D(4, 3, 3, activation='relu'))
		model.add(ZeroPadding2D((1, 1)))
		model.add(Convolution2D(4, 3, 3, activation='relu'))
		model.add(MaxPooling2D(pool_size=(2, 2), strides=(2, 2)))

		model.add(ZeroPadding2D((1, 1)))
		model.add(Convolution2D(8, 3, 3, activation='relu'))
		model.add(ZeroPadding2D((1, 1)))
		model.add(Convolution2D(8, 3, 3, activation='relu'))
		model.add(MaxPooling2D(pool_size=(2, 2), strides=(2, 2)))

		model.add(Flatten())
		model.add(Dense(32, activation='relu'))
		model.add(Dropout(0.5))
		model.add(Dense(32, activation='relu'))
		model.add(Dropout(0.5))
		model.add(Dense(8, activation='softmax'))

		sgd = SGD(lr=1e-2, decay=1e-6, momentum=0.9, nesterov=True)
		model.compile(optimizer=sgd, loss='categorical_crossentropy')

		self.modelslist[self.name+'_'+str(N)]=model
		N=N+1

		
