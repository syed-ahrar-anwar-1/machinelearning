# -*- coding: utf-8 -*-
"""Pulsar Class.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1ryUN_jgE1OH33kYshA6ECfA4oS9lKrHx
"""

import os
import sys
import time
import scipy
import keras
import logging
import threading
import numpy as np
import pandas as pd
from keras import optimizers
from pandas import DataFrame
from keras.optimizers import SGD
from sklearn import preprocessing
from sklearn.pipeline import Pipeline
from keras.constraints import maxnorm
from datetime import datetime, timedelta
from sklearn.metrics import accuracy_score
from sklearn.model_selection import GridSearchCV
from sklearn.linear_model import LogisticRegression
from keras.models import model_from_json, Sequential
from sklearn.feature_selection import SelectFromModel
from keras.wrappers.scikit_learn import KerasClassifier
from keras.layers.normalization import BatchNormalization
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint
from keras.layers import Flatten, Dense, Activation, Dropout
from tensorflow.python.keras.layers import Dense
from tensorflow.python.keras import Sequential
from sklearn.ensemble import RandomForestClassifier, ExtraTreesClassifier
from sklearn.preprocessing import OneHotEncoder, LabelEncoder, StandardScaler, MinMaxScaler
from sklearn.model_selection import train_test_split, cross_val_score, KFold, StratifiedKFold
import warnings
warnings.filterwarnings("ignore")

from google.colab import files

uploaded = files.upload()

for fn in uploaded.keys():
  print('User uploaded file "{name}" with length {length} bytes'.format(
      name=fn, length=len(uploaded[fn])))

data = pd.read_csv('pulsar_stars.csv')
data

data.groupby('target_class').count()

data.plot(x=' Excess kurtosis of the DM-SNR curve', y=' Mean of the DM-SNR curve', kind = 'scatter')
data.plot(x=' Excess kurtosis of the integrated profile', y=' Mean of the integrated profile', kind = 'scatter')

print(data.columns.values)

#data = data.groupby('target_class').head(1600)
data

x = data
min_max_scaler = preprocessing.MinMaxScaler()
x_scaled = min_max_scaler.fit_transform(x)
data = pd.DataFrame(x_scaled)
train, test = train_test_split(data, test_size=0.20, random_state=42)
print(train.shape)
print(test.shape)
ncols = len(train.columns)
nrows = len(train.index)
ncolstest = len(test.columns)
nrowstest = len(test.index)
xtrain = train.iloc[:, 0:(ncols -1)].values.reshape(nrows, ncols-1)
ytrain = train.iloc[:, (ncols-1)].values.reshape(nrows, 1)
xtest = test.iloc[:, 0:(ncolstest -1)].values.reshape(nrowstest, ncolstest-1)
ytest = test.iloc[:, (ncolstest-1)].values.reshape(nrowstest, 1)
xtrain.reshape(xtrain.shape[0],xtrain.shape[1],1)
print(xtrain.shape)
print(ytrain.shape)

model = LogisticRegression()
scores = []
kfold = KFold(n_splits=3, shuffle=True, random_state=42)
for i, (train, test) in enumerate(kfold.split(xtrain,ytrain)):
    model.fit(xtrain,ytrain)
    score = model.score(xtest,ytest)
    scores.append(score)

print(score)

model = Sequential()
model.add(Dense(320, input_shape=(xtrain.shape[0],xtrain.shape[1],), activation='sigmoid'))
model.add(Dense(64, activation='sigmoid'))
model.add(Dense(16, activation='sigmoid'))
model.add(Dense(1, activation='sigmoid'))
model.compile(optimizer='rmsprop',
              loss='binary_crossentropy',
              metrics=['mse', 'accuracy'])
earlystop = [EarlyStopping(monitor='val_loss', patience=2)]
model.fit(xtrain, ytrain, epochs=100, verbose=1, validation_split = 0.20, callbacks = earlystop)

predicted = pd.DataFrame(model.predict_classes(xtest),columns=['predicted class'])
xtest = pd.DataFrame(xtest, columns=xtest.columns.values)
ytest = pd.DataFrame(ytest, columns=ytest.columns.values)
final = pd.concat([xtest, ytest, predicted], axis = 1)

model.evaluate(xtest, ytest, verbose=2)