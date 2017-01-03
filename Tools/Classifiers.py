#!/usr/local/bin/python2

import time

import numpy as np
import sklearn.naive_bayes
import sklearn.tree
import sklearn.ensemble
import sklearn.semi_supervised
import sklearn.decomposition
import sklearn.svm
import nolearn.dbn
import matplotlib.pyplot as plt
import pandas
import random
import sys
import math
import xgboost
import os

from sklearn.metrics import accuracy_score, f1_score, roc_auc_score, log_loss, precision_score, recall_score
from sklearn.model_selection import cross_val_score

import Report as report


class GenericClassificationModel( object ):

    """
    Generic MV training structure, gets inherited by specific classifiers (e.g. DecisionTree or RandomForest).
    Contains generic functions for training and scoring classifier.
    """
    
    #
    # Primary purpose of __init__ is to
    # format training and test data into separate sets for dependent
    # and independent (output_feature) parameters
    #
    def __init__( self , training_data , test_data , output_feature , ignore_features , learner ):

        # Create a directory where we can save classifier snapshots
        self.execName   = os.path.basename( sys.argv[0] )
        self.outputTag  = "_".join( [self.execName[:-3]] + sys.argv[1:] )
        self.outputPath = "Output/"+self.outputTag+"_classifierOutput"
        os.system( "mkdir -p "+self.outputPath )

        # Name of the variable that we would like to predict
        self.output_feature = output_feature
        self.feature_names  = [col for col in training_data if col != self.output_feature and col not in ignore_features]

        # Store the training and test datasets
        self.training_data = training_data[self.feature_names+[self.output_feature]]
        self.test_data     = test_data[self.feature_names+[self.output_feature]]

        # Isolate the training features and classes
        self.training_features = training_data[self.feature_names]
        self.training_classes  = training_data[self.output_feature]
        self.nclasses          = len( np.unique( self.training_classes.values ) )

        # Isolate the test features and classes, but only if the test data
        # was actually included by user
        self.test_classes = None
        self.test_features = None
        if test_data is not None:
            self.test_features  = test_data[self.feature_names]
            if self.output_feature in test_data:
                self.test_classes = test_data[self.output_feature]
            else:
                self.test_classes = None

        # The learner here is overridden by inheriting classifier
        self.learner = learner

        
    # Overridden by inheriting classifier
    def __str__( self ):
        return "GenericClassificationModel"

    #
    # Train function uses from the inherited learner
    # Also keeps track of training time
    #
    def train( self ):
        report.info( "Training %s"%self.__str__() )
        start = time.time()
        self.learner.fit( self.training_features.values , self.training_classes.values )
        stop = time.time()
        self.traintime = stop - start

    #
    # Print and return a full ranking of all the features
    # If quiet=True, then we don't bother printing
    #
    def ranking( self , quiet=False):
        try:
            f = self.learner.feature_importances_
        except AttributeError:
            report.warn( self.__str__()+" has no feature ranking" )
            f = None
        if f is None:
            return None
        nf     = self.feature_names
        f , nf = (list(t) for t in zip(*sorted(zip(f, nf))))
        f      = list(reversed(f))
        nf     = list(reversed(nf))
        if not quiet:
            report.info( "Ranking:" )
            for i in range(len(self.feature_names)):
                report.blank( "%50s : %g" % (nf[i], f[i]) )
        return nf

    #
    #  Functions for producing predicted output for predicted
    # "probability" metrics on test/training data
    #
    def predict( self , elem ): return self.learner.predict(elem)
    def predict_test( self ): return self.learner.predict( self.test_features )
    def predict_training( self ): return self.learner.predict( self.training_features )
    def predict_proba_test( self ): return self.learner.predict_proba( self.test_features )
    def predict_proba_training( self ): return self.learner.predict_proba( self.training_features )
    def predict_proba_for_value( self , classvalue=1 ):
        full_probas = self.predict_proba_test()
        classindex  = np.where( self.learner.classes_==classvalue )[0][0]
        return [ x[classindex] for x in full_probas ]
    
    #
    # Return a generic cross validation test score using "cross_val_score"
    #
    def cross_val_test_score( self , scoring ):
        if self.test_classes is None:
            raise Exception( 'Cant score because test data has undefined output feature' )
        return cross_val_score( self.learner , self.test_features.values , self.test_classes.values , scoring=scoring )

    #
    # Return generic cross validation training score using "cross_val_score"
    #
    def cross_val_training_score( self , scoring ):
        return cross_val_score( self.learner , self.training_features.values , self.training_classes.values , scoring=scoring )

    #
    # Some specific metric score functions
    #
    def accuracy( self ): return accuracy_score( self.test_classes.values , self.predict_test() )
    def precision( self ): return precision_score( self.test_classes.values , self.predict_test() )
    def recall( self ): return recall_score( self.test_classes.values , self.predict_test() )
    def f1score( self ): return f1_score( self.test_classes.values , self.predict_test() )
    def log_loss( self ): return log_loss( self.test_classes.values , self.predict_proba_test() )
    def auc( self , classvalue=1): return roc_auc_score( self.test_classes.values , self.predict_proba_for_value(classvalue) )
    
    # 
    # Print and return a summary of the training results.
    # If quiet=True then don't bother printing
    #
    def summary( self , quiet=False ):
        s = []
        s += [ "Classifier Info for %s:"%self.__str__() ]
        s += [ "nFeatures        = %i" % len(self.feature_names) ]
        r = self.ranking(quiet=True)
        if r is not None:
            s += [ "Top 5            = ["+",".join(r[:5])+"]" ]
        s += [ "Training time    = %0.2fs" % self.traintime ]
        if self.test_classes is not None:
            s += [ "Accuracy         = %g" % self.accuracy() ]
            s += [ "Precision        = %g" % self.precision() ]
            s += [ "Recall           = %g" % self.recall() ]
            s += [ "F1-score         = %g" % self.f1score() ]
            s += [ "Log-loss         = %g" % self.log_loss() ]
            s += [ "AUC              = %g" % self.auc() ]
        if not quiet:
            for l in s:
                report.blank( l )
        return s

    #
    # Save summary and predictinos to a file so they can be used as input
    # to another model
    #
    def savePredictions( self , data=None , name="predictions" ):

        # Create a dictionary of probability predictions for input data
        probas = {}
        if self.output_feature in data:
            probas[self.output_feature] = data[self.output_feature].values
        tmp = self.learner.predict_proba( data[self.feature_names].values )

        # Define each feature in the map with a unique name
        for ic,c in enumerate(self.learner.classes_):
            cname = "%s_%s__%s"%(self.outputTag,self.__str__(),str(c))
            probas[cname] = [ row[ic] for row in tmp ]

        # Save to CSV file
        pandas.DataFrame(probas).to_csv( "%s/%s_%s.csv"%(self.outputDir,self.__str__(),name) , index=False )
        del probas
        del tmp

        # Save a summary file with training info
        summaryFile = open( "%s/%s_%s_summary.txt" % (self.outputDir,self.__str__(),name) , 'w' )
        s = summary( quiet=True )
        for l in s:
            summaryFile.write( l+"\n" )
        summaryFile.close()

        report.info( "Predictions saved to %s" % self.outputDir )

        


        
                
# Decision Tree classifier.
# For more info: http://scikit-learn.org/stable/modules/tree.html#classification
class DecisionTree( GenericClassificationModel ):
    def __init__( self , training_data , test_data=None , output_feature='signal' , ignore_features=[] ):

        self.learner = sklearn.tree.DecisionTreeClassifier( max_depth=None, #def = None
                                                            min_samples_split=2, #def = 2
                                                            min_samples_leaf=50, #def = 1
                                                            max_features=None, # def = None --> n_features
                                                            max_leaf_nodes=None, # def = None
                                                            random_state=1 )

        super(DecisionTree,self).__init__( training_data , test_data , output_feature , ignore_features , self.learner )

    def __str__( self ):
        return "DecisionTree"
        


# Boosted decision tree classifier.
# For more info: http://scikit-learn.org/stable/modules/ensemble.html#adaboost
class BDT( GenericClassificationModel ):
    def __init__( self , training_data , test_data=None , output_feature='signal' , ignore_features=[] , \
                  n_estimators=50 , learning_rate=1.0 ):

        self.rawtree = sklearn.tree.DecisionTreeClassifier( max_depth=None, #def = None
                                                            min_samples_split=2, #def = 2
                                                            min_samples_leaf=50, #def = 1
                                                            max_features=None, # def = None --> n_features
                                                            max_leaf_nodes=None, # def = None
                                                            random_state=1 )

        self.learner = sklearn.ensemble.AdaBoostClassifier( base_estimator=self.rawtree ,
                                                            n_estimators=n_estimators, # def = 50
                                                            learning_rate=learning_rate, # def = 1.0
                                                            algorithm='SAMME.R', # def = SAMME.R
                                                            random_state=1 )

        self.tag = "_".join( [str(n_estimators),str(learning_rate)] )

        super(BDT,self).__init__( training_data , test_data , output_feature , ignore_features , self.learner )

    def __str__( self ):
        return "BDT_"+self.tag



# Extremely randomized forest classifier
# For more info: http://scikit-learn.org/stable/modules/ensemble.html#random-forests
class ExtraRandomForest( GenericClassificationModel ):
    def __init__( self , training_data , test_data=None , output_feature='signal' , ignore_features=[] , \
                  n_estimators=10 , max_features='auto' , max_depth=None , \
                  min_samples_split=2 , bootstrap=False , verbose=0 ):

        self.learner = sklearn.ensemble.ExtraTreesClassifier( random_state = 1, # def = None
                                                              n_estimators = n_estimators, # def = 10
                                                              max_features = max_features, # 'auto', # def = 'auto' (sqrt n_features)
                                                              max_depth = max_depth, # def = None
                                                              min_samples_split = min_samples_split, # def = 2
                                                              bootstrap = bootstrap, # def = False
                                                              verbose = verbose )

        self.tag = "_".join( [str(n_estimators),str(max_features),str(max_depth),str(min_samples_split),str(bootstrap)] )

        super(ExtraRandomForest, self).__init__( training_data , test_data , output_feature , ignore_features , self.learner )
        
    def __str__( self ):
        return "ExtraRandomForest_"+self.tag
        


    
# XGBoost... the best of the best!
# (implementation in progress)
class XGBoost( GenericClassificationModel ):
    def __init__( self , training_data , test_data=None , output_feature='signal' , ignore_features=[] , \
                  max_depth=3 , learning_rate=0.1 , n_estimators=500 , gamma=0 , nthread=-1 , silent=True ):

        self.learner = xgboost.XGBClassifier( max_depth = max_depth,
                                              learning_rate = learning_rate,
                                              n_estimators = n_estimators,
                                              silent = silent,
                                              objective = 'binary:logistic',
                                              nthread = nthread,
                                              gamma = gamma,
                                              min_child_weight=1,
                                              max_delta_step=0,
                                              subsample=1,
                                              colsample_bytree=1,
                                              colsample_bylevel=1,
                                              reg_alpha=0,
                                              reg_lambda=1,
                                              scale_pos_weight=1,
                                              base_score=0.5,
                                              seed=1,
                                              missing=None )
        
        self.tag = "_".join( [str(max_depth),str(learning_rate),str(n_estimators),str(gamma)] )
        
        super(XGBoost, self).__init__( training_data , test_data , output_feature , ignore_features , self.learner )

    def __str__( self ):
        return "XGBoost_"+self.tag
        

