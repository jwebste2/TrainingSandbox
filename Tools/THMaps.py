#!/usr/local/bin/python2

import ROOT

import Report as report
import HistTools as htools

from MVAPaperStyle import *
setStyle( htools )

"""
Histogram maps to help producing plots for 
the ttH Machine Learning paper.
"""

class TH1Map:
    def __init__( self ):
        self.th1_bkg_map = {}
        self.th1_sig_map = {}
        self.xscale_map = {}
        self.xmax_map = {}
        self.keys = []
    def getKey( self , xname ):
        return (xname)
    def addHist( self , xname , title , xbins , xmin , xmax , xscale=1.0 ):
        key = self.getKey(xname)
        if key in self.keys:
            report.crash( "Trying to add the same hist twice" , key )
        self.th1_bkg_map[key] = ROOT.TH1F( "h1_%s_bkg"%key , title , xbins , xmin , xmax )
        self.th1_sig_map[key] = ROOT.TH1F( "h1_%s_sig"%key , title , xbins , xmin , xmax )
        self.xscale_map[key] = float(xscale)
        self.xmax_map[key] = float(xmax)
        self.keys += [key]
    def fillBkg( self , xname , val , weight ):
        v = min( val , self.xmax_map[self.getKey(xname)] - 0.0001 )
        self.th1_bkg_map[self.getKey(xname)].Fill( v/self.xscale_map[xname] , weight )
    def fillSig( self , xname , val , weight ):
        v = min( val , self.xmax_map[self.getKey(xname)] - 0.0001 )
        self.th1_sig_map[self.getKey(xname)].Fill( v/self.xscale_map[xname] , weight )
    def makePretty( self , norm=True ):
        for v in self.keys:
            if norm:
                htools.norm( self.th1_sig_map[v] )
                htools.norm( self.th1_bkg_map[v] )
            htools.makePretty( self.th1_sig_map[v] , color="sig" , linestyle="sig" )
            htools.makePretty( self.th1_bkg_map[v] , color="bkg" , linestyle="bkg" )
            htools.scaleMax( [self.th1_sig_map[v],self.th1_bkg_map[v]] , 1.2 )
    def getLegend( self , sigTitle="t#bar{t}H Signal" , bkgTitle="t#bar{t} Background" ):
        firstKey = self.keys[0]
        legend = ROOT.TLegend()
        legend.AddEntry( self.th1_sig_map[firstKey] , sigTitle , "lpe" )
        legend.AddEntry( self.th1_bkg_map[firstKey] , bkgTitle , "lpe" )
        htools.makePretty( legend , textsize=0.8 , textlocation=htools.LEFT )
        return legend

    
class TH2Map:
    def __init__( self ):
        self.th2_bkg_map = {}
        self.th2_sig_map = {}
        self.xscale_map = {}
        self.yscale_map = {}
        self.keys = []
    def getKey( self , xname , yname ):
        return (xname,yname)
    def addHist( self , xname , yname , title , xbins , xmin , xmax , ybins , ymin , ymax , xscale=1.0 , yscale=1.0 ):
        key = self.getKey(xname,yname)
        if key in self.keys:
            report.crash( "Trying to add the same hist twice" , key )
        self.th2_bkg_map[key] = ROOT.TH2F( "h2_%s_%s_bkg"%key , title , xbins , xmin , xmax , ybins , ymin , ymax )
        self.th2_sig_map[key] = ROOT.TH2F( "h2_%s_%s_sig"%key , title , xbins , xmin , xmax , ybins , ymin , ymax )
        self.xscale_map[key] = float(xscale)
        self.yscale_map[key] = float(yscale)
        self.keys += [key]
    def fillBkg( self , key , xval , yval , weight ):
        self.th2_bkg_map[key].Fill( xval/self.xscale_map[key] , yval/self.yscale_map[key] , weight )
    def fillSig( self , key , xval , yval , weight ):
        self.th2_sig_map[key].Fill( xval/self.xscale_map[key] , yval/self.yscale_map[key] , weight )
    def setBinLabels( self , key , xlabels=[] , ylabels=[] ):
        for ilabel,label in enumerate(xlabels):
            self.th2_sig_map[key].GetXaxis().SetBinLabel( ilabel+1 , label )
            self.th2_bkg_map[key].GetXaxis().SetBinLabel( ilabel+1 , label )
        for ilabel,label in enumerate(ylabels):
            self.th2_sig_map[key].GetYaxis().SetBinLabel( ilabel+1 , label )
            self.th2_bkg_map[key].GetYaxis().SetBinLabel( ilabel+1 , label )
    def makePretty( self , norm=True ):
        for v in self.keys:
            if norm:
                #htools.norm( self.th2_sig_map[v] , float(self.th2_sig_map[v].GetNbinsX()*self.th2_sig_map[v].GetNbinsY()) )
                #htools.norm( self.th2_bkg_map[v] , float(self.th2_sig_map[v].GetNbinsX()*self.th2_sig_map[v].GetNbinsY()) )
                htools.norm( self.th2_sig_map[v] )
                htools.norm( self.th2_bkg_map[v] )
            htools.makePretty( self.th2_sig_map[v] )
            htools.makePretty( self.th2_bkg_map[v] )
            self.th2_sig_map[v].SetMarkerColor( ROOT.kBlack )
            self.th2_bkg_map[v].SetMarkerColor( ROOT.kBlack )
