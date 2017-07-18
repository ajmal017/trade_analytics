from __future__ import division
from datascience.ML.MLmodels  import *
import datascience.libs as dtsclibs
import joblib


filename=__name__.split('.')[-1]

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
							info={'createdbyclass':cls.__name__,'doc':cls.__doc__}

							model=dtscmd.MLmodels(Project=Project,Data=Data,Name=cls.name,Info=info,Misc={'modelparas':modelparas} ,Status='UnTrained' ,saveformat=cls.saveformat)
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
class RandomForrestmodels(MLmodels.BaseClassificationModel):
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
class LinearSVCmodels(MLmodels.BaseClassificationModel):
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
class QDAmodels(MLmodels.BaseClassificationModel):
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
class NNmodels(MLmodels.BaseClassificationModel):
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
class CNN1Dmodels(MLmodels.BaseClassificationModel):
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

		
