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

canvas = SeabornCanvas()

##################################################################
###                     BEGIN SOURCE                           ###
##################################################################

"""
Example script for training a multi-variate classification model for
identifying particles in ttbar events coming from top decay
"""

# Start by loading some input data from a CSV file
df = pandas.DataFrame.from_csv( 'Data/ttReco/DelphesTtbar_ljet_none_4_4_1000_0.csv.bz2' , index_col=False )

# Dump the number of columns in the dataset
# (there must be a prettier way to code this...)
ncol = 0
for col in df:
    ncol += 1
report.info( "nColumns =" , ncol )

# List the variables that have |r| > 0.99 for debugging purposes
# It should be easy to spot cases where I've accidentally included the
# same feature twice.
report.info( "Calculating correlations > 99%" )
dfp = DataFrameProcessor( df )
dfp.listCorrelationsGEQ( 0.99 )

# Make a massive Pearson's correlation matrix
report.info( "Plotting correlation matrix" )
canvas.drawCorrelationMatrix( df , size=(30,30) )

# Make 2D distributions of features that are highly correlated
# to ensure this is understood
#report.info( "Plotting joint distributions" )
#canvas.drawScatter2D( df , "wp_hadWJet2" , "wpsum_hadW" )

# Make 1D histograms of each feature, separate for signal and noise
report.info( "Plotting 1D histograms for each feature" )
for col in df:
    if col=="signal": continue
    if col=="CombId": continue
    if col=="EventId": continue
    print col
    try:
        canvas.drawBinaryDist1D( col , 'signal' , df , nbins=40 , kde=False )
    except IndexError:
        report.warn( "Unable to produce bins, possibly all events have the same value?" )
        
# Save & close the output Pdf
canvas.close()
canvas.preview()

report.info( "done." )
