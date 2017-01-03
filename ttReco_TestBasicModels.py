#!/usr/local/bin/python2

import sys
import os
import pandas
import csv
import math
import numpy as np

import Tools.Report as report

from Tools.DataFrameProcessor import DataFrameProcessor
from Tools.SeabornCanvas import SeabornCanvas
from Tools.Classifiers import *

canvas = SeabornCanvas()

##################################################################
###                     BEGIN SOURCE                           ###
##################################################################

"""
Example script for training a multi-variate classification model for
identifying particles in ttbar events coming from top decay
"""

# Start by loading some input data from a CSV file
df = pandas.DataFrame.from_csv( "Data/DelphesTtbar_ljet_none_4_4_1000_0.csv.bz2" , index_col=False )

# Shuffle the dataset to ensure the signal and background events are properly mixed.
# This is important because we will eventually the the sample into "training" and "test"
# subsets
#np.random.seed( 10 )
#df = df.iloc[np.random.permutation(len(df))]

# Some columns in the CSV file are just kept for book-keeping.
# Remove these here so they don't damage the training.
#df.drop( ["EventId","CombId"] , axis=1 , inplace=True )
ignore_features = [ "EventId" , "CombId" ]

# Before doing any training, lets generate a correlation matrix with all of our features
#report.info( "Plotting correlation matrix" )
#canvas.drawCorrelationMatrix( df , size=(30,30) )

# Make 2D distributions of features that are highly correlated
# to ensure this is understood
#report.info( "Plotting joint distributions" )
#canvas.drawScatter2D( df , "sumpT" , "pT1" )

# Make 1D histograms of each feature, separate for signal and noise
#report.info( "Plotting 1D histograms for each feature" )
#for col in df:
#    if col=="signal": continue
#    canvas.drawBinaryDist1D( col , 'signal' , df , nbins=40 , kde=False )

# Okay, on to the actual classification...
# Start by splitting sample into "training" and "test" subsets
trainSize = int(len(df)*0.8)
trainSize = trainSize - (trainSize % 12)
testSize  = len(df) - trainSize
report.info( "Total events = " , len(df) )
report.info( "Train size   = " , trainSize )
report.info( "Test size    = " , testSize )

df_train = df.head( trainSize )
df_test  = df.tail( testSize )

# Initialize the classifiers that we want to test out
my_classifiers = [
    DecisionTree( training_data=df_train , test_data=df_test , output_feature='signal' , ignore_features=ignore_features ) ,
    BDT( training_data=df_train , test_data=df_test , output_feature='signal' , n_estimators=10 ) ,
    ExtraRandomForest( training_data=df_train , test_data=df_test , output_feature='signal' , n_estimators=50 ) ,
    ExtraRandomForest( training_data=df_train , test_data=df_test , output_feature='signal' , n_estimators=100 , ignore_features=ignore_features ) ,
    XGBoost( training_data=df_train , test_data=df_test , output_feature='signal' , n_estimators=50 ) ,
]

#
# Train each model and dump some performance metrics
#
for cl in my_classifiers:
    print
    cl.train()
    cl.summary()
    print
    
# Make a new columns in the test dataset with the predictions from different classifiers
# Start by just created the series
predictions = {}
for cl in my_classifiers:
    predictions[cl.__str__()] = pandas.Series( cl.predict_proba_for_value(classvalue=1) , index=df_test.index )

# Now push each "prediction" series onto the test data
for k in predictions.keys():
    df_test[k+" Output"] = predictions[k]

# Now generate a "reciever operating characteristic" (ROC) curve, overlapping all classifiers
canvas.drawROC( df_test , class_label='signal' , signal_class=1 ,
                response_labels=[k+" Output" for k in predictions.keys()] ,
                response_titles=predictions.keys() )

# Plot binary distributions of output from models
for k in predictions.keys():
    canvas.drawBinaryDist1D( k+" Output" , 'signal' , df_test , nbins=100 , kde=False )


# Create another DataFrame that just contains the top likelihood combination from each event
for k in predictions.keys():

    tmp_df      = df_test[ignore_features+["signal",k+" Output"]]
    l_perEvent  = []
    bestCombo   = tmp_df.values[0]
    lastEventID = -1
    eventHasSig = False
    meanOutput  = 0.
    
    for irow,row in enumerate(tmp_df.values):
        if not( row[0] == lastEventID ):
            # Start of a fresh event
            if irow > 0:
                bestCombo += [1] if eventHasSig else [0]
                bestCombo += [ meanOutput / 12.0 ]
                l_perEvent += [ bestCombo ]
            bestCombo   = list(row)
            eventHasSig = False
            meanOutput  = 0.0
        if row[-1] > bestCombo[-1]: bestCombo = list(row)
        eventHasSig = eventHasSig or row[2]==1
        meanOutput += row[-1]
        lastEventID = row[0]

    bestCombo += [1] if eventHasSig else [0]
    bestCombo += [ meanOutput / 12.0 ]
    l_perEvent += [ bestCombo ]

    df_perEvent = pandas.DataFrame( data=l_perEvent , columns=ignore_features+["signal",k+" Output","signal2",k+" Mean Output"] )

    #
    # Draw the ROC curves!
    #
    
    #canvas.drawROC( df_perEvent , class_label='signal' , signal_class=1 ,
    #                response_labels=[k+" Output",k+" Mean Output"] ,
    #                response_titles=[k+" Output",k+" Mean Output"] )

    canvas.drawROC( df_perEvent , class_label='signal' , signal_class=1 ,
                    response_labels=[k+" Output"] ,
                    response_titles=[k+" Output"] )

    canvas.drawROC( df_perEvent , class_label='signal2' , signal_class=1 ,
                    response_labels=[k+" Output",k+" Mean Output"] ,
                    response_titles=[k+" Output",k+" Mean Output"] )

    # For each model, plot signal and background distributions of the model output
    canvas.drawBinaryDist1D( k+" Output" , "signal" , df_perEvent , nbins=100 , kde=False )


    
# Save & close the output Pdf
canvas.close()
canvas.preview()

report.info( "done." )



