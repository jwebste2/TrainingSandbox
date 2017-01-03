#!/usr/local/bin/python2

import sys
import os
import ROOT

class RootCanvas:

    """ 
    Elaborated TCanvas-like class for drawing and saving ROOT plots to
    Pdf files.
    """

    def __init__( self ):

        self.execName  = os.path.basename( sys.argv[0] )
        self.outputTag = "_".join( [self.execName[:-3]] + sys.argv[1:] )

        self.outputPdfDir = "Output/"+self.outputTag+"_pdf"
        self.outputEpsDir = "Output/"+self.outputTag+"_eps"

        for d in [ self.outputPdfDir , self.outputEpsDir ]:
            os.system( "rm -rf "+d )
            os.system( "mkdir -p "+d )
    
        self.plotId = 1

        # Keep track of poisson stats
        ROOT.TH1.SetDefaultSumw2()
        ROOT.TH2.SetDefaultSumw2()

        # Turn off PostScript messages that print every time I save to .ps
        ROOT.gErrorIgnoreLevel = ROOT.kWarning

        # Setup ROOT style
        ROOT.gStyle.SetPadTickX( 1 )
        ROOT.gStyle.SetPadTickY( 1 )
        ROOT.gStyle.SetOptStat( 0 )
        ROOT.gStyle.SetOptTitle( 0 )
        
        self.canvas = ROOT.TCanvas( "canvas" , "canvas" , 800 , 800 )
        self.canvas.SetTopMargin( 0.1 )
        self.canvas.SetRightMargin( 0.1 )
        self.canvas.SetBottomMargin( 0.18 )
        self.canvas.SetLeftMargin( 0.15 )
        self.canvas.SetTicks( 0 , 1 )


    #
    # Save whatever is currently drawn on the canvas to a Pdf file
    #
    def save( self , name="" , logx=False , logy=False ):
        if logx: self.canvas.SetLogx( 1 )
        if logy: self.canvas.SetLogy( 1 )

        if len(name)==0:
            self.canvas.SaveAs( "%s/%03i.pdf" % (self.outputPdfDir,self.plotId) )
            self.canvas.SaveAs( "%s/%03i.eps" % (self.outputEpsDir,self.plotId) )
            self.plotId += 1
        else:
            self.canvas.SaveAs( "%s/%s.pdf" % (self.outputPdfDir,name) )
            self.canvas.SaveAs( "%s/%s.eps" % (self.outputEpsDir,name) )

        self.canvas.SetLogx( 0 )
        self.canvas.SetLogy( 0 )


    #
    # Save whatever is currently drawn on the canvas to a wide Pdf image
    # (for very wide histograms, etc)
    #
    def saveWide( self , name="" , logx=False , logy=False ):
        self.canvas.SetRightMargin( 0.18 )
        self.save( name , logx , logy )
        self.canvas.SetRightMargin( 0.1 )

    #
    # Save the canvas to Pdf after making the vertical scale logarithmic
    #
    def saveLogy( self , name="" ):
        self.save( name , logy=True )

    #
    # Save whatever is currently drawn to the canvas to a tall Pdf image
    # (for very tall histograms, etc)
    #
    def saveTall( self , name="" , logx=False , logy=False ):
        self.canvas.SetCanvasSize( 800 , 1600 )
        self.canvas.SetTopMargin( 0.05 )
        self.canvas.SetBottomMargin( 0.09 )
        self.save( name , logx , logy )
        self.canvas.SetCanvasSize( 800 , 800 )
        self.canvas.SetTopMargin( 0.1 )
        self.canvas.SetBottomMargin( 0.18 )

    # Open up the output directory to view the images
    def openPlotDir( self ):
        os.system( "open "+self.outputPdfDir )

    
