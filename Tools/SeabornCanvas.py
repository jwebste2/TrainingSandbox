#!/usr/local/bin/python2

import os
import sys
import pandas
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import sklearn.metrics

import Report as report

from matplotlib.backends.backend_pdf import PdfPages
from matplotlib import cm


class SeabornCanvas:

    """
    Class to generate plots/histograms/etc for preliminary studies of datasets.
    Makes use of the Searborn module rather than ROOT... in case you don't
    want to waste your life troubleshooting ROOT problems :-)
    """

    def __init__( self ):

        self.execName  = os.path.basename( sys.argv[0] )
        self.outputTag = "_".join( [self.execName[:-3]] + sys.argv[1:] )
        self.outputPath = "Output/"+self.outputTag+".pdf"
        
        # Initialize a Pdf file to store output plots
        self.pdf = PdfPages( self.outputPath )
        
        # Set the plotting style
        #sns.set_style( 'darkgrid' )
        sns.set_style( 'white' )

    # 
    # Close the Pdf
    #  This must be called before ending script or the Pdf gets corrupted
    #
    def close( self ):
        self.pdf.close()
        report.info( "Output pdf saved to" , self.outputPath )

    #
    #  Add current figure to Pdf file and then close plot
    #  Also save to path if provided
    #
    def save( self , path=None ):
        self.pdf.savefig()
        if not( path==None ):
            plt.savefig( path+'.png' )
            plt.savefig( path+'.svg' )
        plt.close()
        
    #    
    # Add 1D distribution (similar to above but with seaborn) to Pdf file
    #
    def drawDist1D( self , xlabel , data , size=(9,9) , color='g' , kde=True , nbins=50 ):
        f, ax = plt.subplots(figsize=size)
        sns.distplot( data[xlabel] , color=color , ax=ax , kde=kde )
        ax.set_xlabel( xlabel )
        f.tight_layout()
        self.save()


    #
    # Draw overlapping 1D histograms using "category" as classifier.
    # It is assumed that category is set to either 0 or 1 for each event.
    #
    def drawBinaryDist1D( self , xlabel , category , data , size=(9,9) , kde=True , nbins=50 ):
        f , ax = plt.subplots(figsize=size)
        r , lo , hi = max(data[xlabel])-min(data[xlabel]) , min(data[xlabel]) , max(data[xlabel])
        bins = np.arange( lo - 0.1*r , hi + 0.1*r , 1.2*r / nbins )
        sns.distplot( data.loc[data[category]==0][xlabel] , ax=ax , norm_hist=True , kde=kde , bins=bins , color='b' )
        sns.distplot( data.loc[data[category]==1][xlabel] , ax=ax , norm_hist=True , kde=kde , bins=bins , color='r' )
        ax.set_xlabel( xlabel )
        f.tight_layout()
        self.save()

        
    #
    # Draw ROC curve "class_label" as the classifier
    #
    def drawROC( self , df , class_label , response_labels , response_titles , signal_class=1 ):
        plt.figure()
        plt.plot([0, 1], [0, 1], 'k--')
        for ir,r in enumerate(response_labels):
            fpr, tpr, _ = sklearn.metrics.roc_curve( df[class_label] , df[r] , pos_label=signal_class )
            roc_auc = sklearn.metrics.auc( fpr , tpr )
            plt.plot(fpr, tpr, label='%s (AUC = %0.2f)' % (response_titles[ir],roc_auc) )
        plt.xlim([0.0, 1.0])
        plt.ylim([0.0, 1.05])
        plt.xlabel('Background Efficiency')
        plt.ylabel('Signal Efficiency')
        plt.legend(loc="lower right")
        self.save()


    #
    # Draw a box plot
    #
    def drawBoxPlot( self , df , Xlabel , Ylabel , hue=None ):
        sns.boxplot( x=Xlabel , y=Ylabel , hue=hue , data=df )
        self.save()


    #
    # Draw a generic curve
    #
    def drawCurve( self , X , Y , Xlabel='' , Ylabel='' ):
        plt.figure()
        plt.plot( X , Y )
        plt.xlabel( Xlabel )
        plt.ylabel( Ylabel )
        self.save()

    #
    # Draw a list of curves
    #
    def drawCurves( self , X , Y , Ytitles , Xlabel='' , Ylabel='' ):
        plt.figure()
        for iy,y in enumerate(Y):
            plt.plot( X , y , label=Ytitles[iy] )
        plt.xlabel( Xlabel )
        plt.ylabel( Ylabel )
        plt.legend(loc="upper left")
        self.save()
        

    #
    # Add correlation matrix to Pdf file
    #
    def drawCorrelationMatrix( self , d , title=None , size=(9,9) ):
        corr = d.corr()
        mask = np.zeros_like( corr , dtype=np.bool )
        mask[np.triu_indices_from(mask)] = True

        f, ax     = plt.subplots(figsize=size)
        cmap      = sns.diverging_palette(220, 10, as_cmap=True)
        cmap.name = 'Correlation'

        sns.heatmap( corr , mask=mask , cmap=cmap , vmax=1.0 , square=True ,
                     linewidths=0.5 , cbar_kws={"shrink":0.5} , ax=ax )
        
        #sns.corrplot( d , annot=False , sig_stars=False , diag_names=False, cmap=cmap , ax=ax )
        if title:
            ax.set_title( title )
        f.tight_layout()
        self.save()
        

    #
    # Add a 2D scatter to Pdf file
    #
    def drawJointPlot( self , d , xname , yname , kind='reg' , showr=True ):

        # Check that columns exist
        if not( xname in d.columns and yname in d.columns ):
            raise Exception( 'Missing column' )

        # Ensure that types are floats
        float_d = d[[xname,yname]].astype(float)

        # Now draw the plot
        if showr:
            sns.jointplot( xname , yname , data=float_d , kind=kind )
        else:
            sns.jointplot( xname , yname , data=float_d , kind=kind , stat_func=None )
        self.save()
        

    #
    # Different method for drawing a 2D scatter plot (without using Seaborn)
    #
    def drawScatter2D( self , d , xname , yname ):
        if not( xname in d.columns and yname in d.columns ):
            raise Exception( 'Missing column' )
        f , ax = plt.subplots()
        ax.scatter( d[xname] , d[yname] , color='slategray' )
        ax.set_xlabel( xname )
        ax.set_ylabel( yname )
        f.tight_layout()
        self.save()

    #
    # Kernel density estimation plot
    #
    def drawKDEPlot( self , d , xname , yname=None , bw='scott' , shade=True ):
        sns.kdeplot( d[xname] , data2=(d[yname] if yname!=None else None) , bw=bw , shade=shade )
        self.save()
        
        
    #
    # Open up the output file using "Preview"
    #
    def preview( self ):
        os.system( "open -a Preview "+self.outputPath )        
