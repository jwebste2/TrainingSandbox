#!/usr/local/bin/python2

import ROOT
import csv
import pandas
import csv
import sys

import Tools.Report as report
import Tools.HistTools as htools

from Tools.RootCanvas import RootCanvas
from Tools.THMaps import TH1Map, TH2Map

c = RootCanvas()

from Tools.MVAPaperStyle import *
setStyle( htools )

##################################################################
###                     BEGIN SOURCE                           ###
##################################################################

"""
Create signal and background plots of ttbar reconstruction CSV data
using ROOT
"""

# Create dataframes from the csv files
df = pandas.DataFrame.from_csv( 'Data/ttReco/DelphesTtbar_ljet_none_4_4_1000_0.csv.bz2' , index_col=False )
report.info( "Loaded" , len(df) , "events" )

#
# Initialize all the histgorams we want to fill
#
report.info( "Initializing histograms" )

GeV = 1000.0

h1map = TH1Map()
h2map = TH2Map()

# 1D histograms
h1map.addHist( "nJets" , ";Number of Jets;Normalized Number of Events" , 10 , 0 , 10 )
h1map.addHist( "m1_lepW" , ";Constrained W Mass (solution #1) [GeV]" , 40 , 0 , 200 )
h1map.addHist( "m2_lepW" , ";Constrained W Mass (solution #2) [GeV]" , 40 , 0 , 200 )

# 2D histograms
# h2map.addHist( "Aplanarity_bjets" , "Aplanority_bjets" , ";Aplanarity_bjets;Aplanority_bjets;a.u." , 100 , 0 , 0.5 , 100 , 0 , 0.5 )

report.info( "Defined %i th1 objects and %i th2 objects" % (len(h1map.keys),len(h2map.keys)) )



#
# Fill histograms
#

report.info( "Iterating over all events and filling histograms" )
for iev in range(len(df)):
    for v in h1map.keys:
        if df["nuMomentumSolved"].values[iev]==1:
            h1map.fillSig( v , df[v].values[iev] , 1.0 ) # df["weight"].values[iev]
        else:
            h1map.fillBkg( v , df[v].values[iev] , 1.0 ) # df["weight"].values[iev]
    for v in h2map.keys:
        if df["nuMomentumSolved"].values[iev]==1:
            h2map.fillSig( v , df[v[0]].values[iev] , df[v[1]].values[iev] , 1.0 ) # df["weight"].values[iev]
        else:
            h2map.fillBkg( v , df[v[0]].values[iev] , df[v[1]].values[iev] , 1.0 ) # df["weight"].values[iev]            
            

# Format histograms
h1map.makePretty( norm=False )
h2map.makePretty( norm=False )
        
# Create legend
h1legend = h1map.getLegend( sigTitle="nuMomentumSolved==1" , bkgTitle="nuMomentumSolved==0" )


#
# Draw everything
#

for v in h1map.keys:
    h1map.th1_bkg_map[v].Draw( "hist e" )
    h1map.th1_sig_map[v].Draw( "hist e same" )
    h1legend.Draw()
    c.save( v )

for v in h2map.keys:
    h2map.th2_bkg_map[v].Draw( "colz" )
    c.saveWide()
    h2map.th2_sig_map[v].Draw( "colz" )
    c.saveWide()
    report.info( "%s background correlation factor = %g" % (v,h2map.th2_bkg_map[v].GetCorrelationFactor()) )
    report.info( "%s signal     correlation factor = %g" % (v,h2map.th2_sig_map[v].GetCorrelationFactor()) )
    
report.info( "done." )

# Open up the directory with output plots, just so we can see the results
c.openPlotDir()

