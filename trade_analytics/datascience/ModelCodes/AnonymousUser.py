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


class RandomForrrest_2(MLmodels.RandomForrestmodels):
	"""
	Random forrest :
	@input: 23 days close+SMA_all, 23 days volume+SMA10 : flat
	@output: 0-1 class : 1 is return >5% 
	"""
	filename=filename
	


	def pre_processing_train(self,X,Y):
		Y[Y<5]=0
		Y[Y>=5]=1
		return (X,Y)

	def pre_processing_validation(self,X,Y):
		Y[Y<5]=0
		Y[Y>=5]=1
		return (X,Y)





class NN_1(MLmodels.NNmodels):
	"""
	Neural networks 1D :
	@input: 23 days close+SMA_all, 23 days volume+SMA10 : flat
	@output: 0-1 class : 1 is return >5% 
	"""
	filename=filename
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
	

N=0
batch_size = 5000
nb_epoch = 25
random_state = 51

input_dim=X.shape[1]

model = Sequential()
model.add(Dense(output_dim=90, input_dim=input_dim,kernel_regularizer=regularizers.l2(0.4),))
model.add(Activation("sigmoid"))
model.add(Dropout(0.1))

# model.add(Dense(output_dim=25, input_dim=input_dim,kernel_regularizer=regularizers.l2(0.1),))
# model.add(Activation("sigmoid"))
# model.add(Dropout(0.1))


model.add(Dense(output_dim=2))
model.add(Activation("softmax"))

optm = SGD(lr=1e-4, decay=1e-6, momentum=0.5, nesterov=True)
# optm=keras.optimizers.RMSprop(lr=0.001, rho=0.9, epsilon=1e-08, decay=0.0)
model.compile(optimizer=optm, loss='categorical_crossentropy', metrics=['accuracy'])

model.fit(X,Y1, batch_size=batch_size, epochs=nb_epoch, verbose=1, callbacks=None, validation_split=0.3, validation_data=None, shuffle=True, class_weight=class_weights, sample_weight=None, initial_epoch=0)