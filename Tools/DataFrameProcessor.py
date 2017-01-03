#!/usr/local/bin/python2

import sys
import os
import pandas
import csv
import math
import numpy as np

class DataFrameProcessor:

    """ 
    Class designed for basic data processing.
    Designed to work specifically with panda.DataFrame data structures. Basically
    a boiler plate for all functions that could be helpful in manipulating/cleaning
    a dataset.
    """

    def __init__( self , data ):

        # Make sure input has the correct type
        if not type(data) == pandas.core.frame.DataFrame:
            raise Exception( 'Data should be type panda.DataFrame' )
        
        self.data = data

    # List the parameters in dataset
    # Meant to be used as a sanity check
    def summary( self ):

        print 'Number of entries:',len(self.data)

        print 'Unique entries in each column:'
        for col in self.data:
            print col, '\n', self.data[col].unique()

            
    # List the columns
    # Meant to be used as a sanity check
    def listColumns( self ):
        print "List of columns:"
        for col in self.data:
            print col


    # List feature pairs with Pearsons |correlation| >= X
    # To be used in case you want to filter out highly correlated features
    def listCorrelationsGEQ( self , x ):
        corrmatrix = self.data.corr( method = 'pearson' )
        nentries = 0
        for icol,col in enumerate(corrmatrix):
            for irow,row in enumerate(corrmatrix):
                if irow <= icol: continue
                if abs(corrmatrix[col][row]) < x: continue
                if math.isnan(corrmatrix[col][row]): continue
                print col,row,corrmatrix[col][row]
                nentries += 1
        print 'Feature pairs found: %i' % (nentries)


    # Find the features correlated with "col" above threshold X
    def getFeatureCorrelationsGEQ( self , col , x ):
        corrlist = self.data.corr( method = 'pearson' )[col].drop( col )
        corrlist = corrlist.drop( [ row for row in self.data if not row==col and (abs(corrlist[row])<x or math.isnan(corrlist[row])) ] )
        return corrlist

    
    # Find the features most strongly correlated with "col"
    def getFeatureMaxCorrelations( self , col ):
        corrlist = self.data.corr( method = 'pearson' )[col].drop( col )
        corrlist = corrlist.drop( [ row for row in self.data if not row==col and not abs(corrlist[row]) == max(abs(corrlist)) ] )
        return corrlist

    
    # Discard features correlated with other features above threshold X
    def discardFeatureCorrelationsGEQ( self , col , x ):
        corrlist = self.getFeatureCorrelationsGEQ( col , x )
        for key in corrlist.keys():
            print 'Discarding feature %s, correlation with %s = %g (abs >= %g)' % (key,col,corrlist[key],x)
            self.discardColumns( [key] )

            
    # Discard at least on feature for every correlation above threshold X        
    def discardCorrelationsGEQ( self , x ):
        corrmatrix = self.data.corr( method = 'pearson' )
        for icol,col in enumerate(corrmatrix):
            for irow,row in enumerate(corrmatrix):
                if irow <= icol: continue
                if abs(corrmatrix[col][row]) < x: continue
                if math.isnan(corrmatrix[col][row]): continue
                print 'Discarding feature %s, correlation with %s = %g (abs >= %g)' % (col,row,corrmatrix[row][col],x)
                self.discardColumns( [col] )
                break


    # Drop a particular column
    def discardColumns( self , cols ):
        new_data = self.data.drop( cols , axis=1 )
        self.data = new_data

        
    # Drop all columns except for those in this list
    def discardAllColumnsBut( self , cols ):
        new_data = pandas.DataFrame()
        for col in cols:
            print col
            new_data[col] = self.data[col]
        self.data = new_data

        
    # drop columns that have single value for all events
    def discardSingleValueColumns( self ):
        to_discard = [ x for x in self.data if len(self.data[x].unique())==1 ]
        if( len(to_discard) > 0 ):
            print 'Discarding columns with no information:'
            for c in to_discard: print '  %s' % c
            self.discardColumns( to_discard )

            
    # Explode a particular parameter into dummy/indicator variables
    def generateDummyParameters( self , cols ):
        for col in cols:
            # generate the new dummy variables
            for elem in self.data[col].unique():
                self.data[col+'_'+str(elem)] = 1*(self.data[col] == elem)
            # now drop the original column so there is no redundency
            self.data.drop( [col] , axis=1 , inplace=True )

            
    # Divide parameter into a one bit response based on whether value is above or below a specified
    # threshold
    def convertToBinary( self , col , thresh ):
        self.data[col+'_yes'] = 1*(self.data[col] > thresh)
        self.data.drop( col , axis=1 , inplace=True )

        
    # Remove events by requiring a column takes on a particular value
    def requireValue( self , col , value ):
        new_data = self.data.loc[ self.data[col] == value ]
        new_data = new_data.drop( [col] , axis=1 )
        print "Retained %i/%i entries after requiring %s==%s " % (len(new_data),len(self.data),col,value)
        self.data = new_data


    # Remove events with column equal to a specified value
    def discardValue( self , col , value ):
        new_data = self.data.loc[ self.data[col] != value ]
        print "Retained %i/%i entries after requiring %s!=%s " % (len(new_data),len(self.data),col,value)
        self.data = new_data

        
    # Drop all events that contain any NaN's
    def discardNaNs( self , cols ):
        new_data = self.data.dropna( axis=0 , how='any' , subset=cols , inplace=False )
        print "Retained %i/%i entries after dropping NaNs in " % (len(new_data),len(self.data)), cols
        self.data = new_data


    # Replace all NaN's for a particular column with a specified value
    def fillNaNs( self , col , value ):
        if not col in self.data.columns:
            raise Exception( 'Column not found' )
        self.data[col].fillna( value , inplace=True )


    # Replace all values "init" with value "new" in specified column
    def replaceValueWith( self , col , init_value , new_value ):
        if not col in self.data.columns:
            raise Exception( 'Column not found' )
        self.data.loc[:,col].replace( init_value , new_value , inplace=True )

        
    # Sort columns alphabetically
    def sort( self , response ):
        arranged_cols = sorted( self.data.columns.tolist() )
        if response in arranged_cols:
            # Make the response the last column
            arranged_cols = [ x for x in arranged_cols if x != response ]
            arranged_cols += [ response ]
        self.data = self.data[arranged_cols]


    # Add another column (e.g. SignalOrBackground) with a particular value (e.g. SIG)
    # WARNING: This is not the recommended way to add a column, but it seems to work
    def addColumn( self , colname , val ):
        self.data[colname] = pandas.Series( np.full(len(self.data),val) , index=self.data.index )

        
    # Append another separated DataFrame
    def append( self , df ):
        self.data = self.data.append( df )


    # Save the DataFrame to CSV file
    def saveCsv( self , path ):
        self.data.to_csv( path )
        

    
