from __future__ import division
import sys
import numpy as np
import pandas as pd
import collections
import pdb
from scipy import interp
import scipy
import pickle
import os
import json
from scipy.sparse import coo_matrix, hstack, vstack
import copy
import datascience.models as dtscmd
import time
np.random.seed(1337)  # for reproducibility


###################################################################
####################   KERAS  #####################################
###################################################################
from keras.models import load_model
from keras.models import Sequential
from keras.layers.core import Dense, Dropout, Flatten
from keras.layers.convolutional import Convolution2D, MaxPooling2D, ZeroPadding2D, Convolution1D, ZeroPadding1D
from keras.optimizers import SGD
from keras.callbacks import EarlyStopping
from keras.utils import np_utils
from keras import __version__ as keras_version
from keras import regularizers
from keras.layers import Dense, Dropout, Activation
from keras.layers.advanced_activations import LeakyReLU, PReLU
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
from sklearn.metrics import average_precision_score, accuracy_score, recall_score, precision_score
from sklearn.metrics import log_loss, accuracy_score
from sklearn.tree import DecisionTreeClassifier
from sklearn import tree
from sklearn import preprocessing
from sklearn.preprocessing import OneHotEncoder, LabelEncoder
from sklearn import linear_model, decomposition
from sklearn.linear_model import LogisticRegression
from sklearn.feature_extraction import DictVectorizer
from sklearn import metrics
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score, r2_score
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
from sklearn.linear_model import LinearRegression, SGDClassifier
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
import multiprocessing
n_jobs = multiprocessing.cpu_count() - 2
n_jobs = max([n_jobs, 2])

import pdb

###################################################################
####################   dataapp stock data  ###############################
###################################################################

import dataapp.libs as dtalibs
import datascience.libs as dtsclibs

###################################################################
####################   BASE MODELS  #####################################
###################################################################
