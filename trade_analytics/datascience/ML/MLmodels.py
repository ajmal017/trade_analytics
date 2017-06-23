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
####################   BASE MODELS  #####################################
###################################################################

def ModelFactory(ModelClassName):
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


		


###################################################################
####################   XGBOOST  #####################################
###################################################################
class XGBOOSTmodels(BaseClassificationModel):
	name='XGBOOST'
	saveformat='xgboost'

	def savemodel(self):
		filename=self.model.modelpath()
		self.clf.save_model(filename)
		
		self.model.save()

	def loadmodel(self):
		path=self.model.modelpath()
		clf = xgb.Booster() #init model
		clf.load_model(path) # load data

		return clf

	def predict(self,X):
		dtest = xgb.DMatrix(X)
		return self.clf.predict(dtest)

	def train(self):
		X,Y=self.pre_processing_train()

		dtrain = xgb.DMatrix( X, label=Y)
		
		evallist  = [(dtrain,'train')]
		plst=self.model.Misc['modelparas']['plst']
		num_round=self.model.Misc['modelparas']['num_round']
		self.clf.train( plst, dtrain, num_round, evallist )

		self.post_process_model()

	@classmethod
	def GenModels(cls,Project,Data):

		D=Data.gen_one_shard()
		X=D['X']
		Y=D['Y']
		
		N=0
		num_round = 300
		early_stopping_rounds=10
		param = {
					 'silent':1, 'objective':'multi:softmax','num_class':8, 
					'nthread' :6, 'eval_metric':'mlogloss', 'subsample': 0.7, 'colsample_bytree': 0.7,
					'min_child_weight':0, 'booster':"gbtree",
				}

		
		for max_depth in [50,100,250,500]:
			for eta in np.arange(0.1,0.9,0.2):
				for lmda in [0,10,50,100]:

					if Data.ouput_type=='binary:':
						for obj in ['reg:linear','reg:logistic','binary:logistic']:
							param['max_depth']=max_depth
							param['eta']=eta
							param['lambda']=lmda
							param['objective']=obj
							param['max_delta_step']=1
							param['scale_pos_weight'] = Data.Misc['#0']/Data.Misc['#1'] #sum_wneg/sum_wpos

							plst = list(param.items())+[('eval_metric', 'ams@0.15'),('eval_metric', 'auc'),('eval_metric','rmse'),('eval_metric','mae'),('eval_metric','logloss'),('eval_metric','logloss')]
							plst=plst+[('eval_metric','error@%s'%t) for t in np.arange(0,1,0.1) ]
							
							num_round=eta*1000

							dtrain = xgb.DMatrix( X, label=Y)
							evallist  = [(dtrain,'train')]
							plst = param.items()
							bst = xgb.train( plst, dtrain, num_round, evallist )

							modelparas={'param':param,'plst':plst,'num_round':num_round,'early_stopping_rounds':early_stopping_rounds}

							model=dtscmd.MLmodels(Project=Project,Data=Data,Name=cls.name,Misc={'modelparas':modelparas} ,Status='UnTrained' ,saveformat=cls.saveformat)
							model.save()
							model.initialize()
							filename=model.modelpath()
							bst.save_model(filename)
							
							
							N=N+1

					elif Data.ouput_type=='multiclass':
						for obj in ['reg:linear','reg:logistic','multi:softprob']:
							param['max_depth']=max_depth
							param['eta']=eta
							param['lambda']=lmda
							param['objective']=obj
							param['max_delta_step']=1		

							plst = list(param.items())+[('eval_metric', 'ams@0.15'),('eval_metric', 'auc'),('eval_metric','rmse'),('eval_metric','mae'),('eval_metric','logloss'),('eval_metric','logloss')]
							plst=plst+[('eval_metric','error@%s'%t) for t in np.arange(0,1,0.1) ]
							
							num_round=eta*1000

							dtrain = xgb.DMatrix( X, label=Y)
							evallist  = [(dtrain,'train')]
							plst = param.items()
							bst = xgb.train( plst, dtrain, num_round, evallist )

							modelparas={'param':param,'plst':plst,'num_round':num_round,'early_stopping_rounds':early_stopping_rounds}

							model=dtscmd.MLmodels(Project=Project,Data=Data,Name=cls.name,Misc={'modelparas':modelparas} ,Status='UnTrained' ,saveformat=cls.saveformat)
							model.save()
							model.initialize()
							filename=model.modelpath()
							bst.save_model(filename)
							
							N=N+1
		



###################################################################
####################   RandomForrest  #####################################
###################################################################
class RandomForrestmodels(BaseClassificationModel):
	name='RandomForrest'
	saveformat='joblib'

	@classmethod
	def GenModels(cls,Project,Data):
		if Data.Datatype!='Train':
			raise Exception("Need Training Data For model")

		N=0
		for n_estimators in [10,100,250,500]:
			for max_depth in [10,100,250,500]:
				for max_features in ['log2','auto',30,40,50,60]+list(np.arange(0,1,0.3)):
					for  class_weight in ['balanced_subsample',None]:
						clf=RandomForestClassifier(n_estimators=n_estimators, n_jobs=5,max_depth=max_depth,max_features=max_features,class_weight=class_weight)
						modelparas={'n_estimators':n_estimators, 'n_jobs':5,'max_depth':max_depth,'max_features':max_features}
						model=dtscmd.MLmodels(Project=Project,Data=Data,Name=cls.name,Misc={'modelparas':modelparas} ,Status='UnTrained' ,saveformat=cls.saveformat)
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
	saveformat='joblib'

	@classmethod
	def GenModels(cls,Project,Data):
		if Data.Datatype!='Train':
			raise Exception("Need Training Data For model")

		N=0
		for C in [1, 10, 100, 1000,10000]:
			clf=LinearSVC(C=C)
			modelparas={'C':C}
			model=dtscmd.MLmodels(Project=Project,Data=Data,Name=cls.name,Misc={'modelparas':modelparas} ,Status='UnTrained' ,saveformat=cls.saveformat)
			model.save()
			model.initialize()
			filename=model.modelpath()
			joblib.dump(clf, filename)
			N=N+1

###################################################################
####################   QuadraticDiscriminantAnalysis  ###############
###################################################################
class QDAmodels(BaseClassificationModel):
	name='QDA'
	saveformat='joblib'

	@classmethod
	def GenModels(cls,Project,Data):
		if Data.Datatype!='Train':
			raise Exception("Need Training Data For model")

		N=0
		for reg_param in [1, 10, 100, 1000,10000]:
			clf=QuadraticDiscriminantAnalysis(reg_param=reg_param)
			modelparas={'reg_param':reg_param}
			model=dtscmd.MLmodels(Project=Project,Data=Data,Name=cls.name,Misc={'modelparas':modelparas} ,Status='UnTrained' ,saveformat=cls.saveformat)
			model.save()
			model.initialize()
			filename=model.modelpath()
			joblib.dump(clf, filename)
			N=N+1

###################################################################
####################   NN  #####################################
###################################################################
class NNmodels(BaseClassificationModel):
	name='NN'
	saveformat='keras'

	def savemodel(self):
		filename=self.model.modelpath()
		self.clf.save(filename)
		self.model.save()

	def loadmodel(self):
		path=self.model.modelpath()
		clf = load_model(path)
		return clf

	def train(self):
		X,Y=self.pre_processing_train()

		self.clf.fit(X,Y, batch_size=32, epochs=10, verbose=1, callbacks=None, validation_split=0.0, validation_data=None, shuffle=True, class_weight=None, sample_weight=None, initial_epoch=0)

		self.post_process_model()

	@classmethod
	def GenModels(cls,Project,Data):
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
		
		modelparas={}
		dbmodel=dtscmd.MLmodels(Project=Project,Data=Data,Name=cls.name,Misc={'modelparas':modelparas} ,Status='UnTrained' ,saveformat=cls.saveformat)
		dbmodel.save()
		dbmodel.initialize()
		filename=dbmodel.modelpath()
		
		model.save(filename)

		N=N+1


###################################################################
####################   CNN1D  #####################################
###################################################################
class CNN1Dmodels(BaseClassificationModel):
	name='CNN1D'
	saveformat='keras'

	@classmethod
	def GenModels(cls,Project,Data):
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

		modelparas={}
		dbmodel=dtscmd.MLmodels(Project=Project,Data=Data,Name=cls.name,Misc={'modelparas':modelparas} ,Status='UnTrained' ,saveformat=cls.saveformat)
		dbmodel.save()
		dbmodel.initialize()
		filename=dbmodel.modelpath()
		
		model.save(filename)


		N=N+1

		
