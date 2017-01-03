#!/usr/local/bin/python2

import ROOT
import Report as report


#
#  Hist drawing / setup tools
#

# Enum text locations
LEFT   = 1
RIGHT  = 2
CENTER = 3

# Style adjustables
LINEWIDTH = 2

# Color adjustables
COLORMAP = {
    -1 : ROOT.kBlack ,
    0 : ROOT.kBlue-6 ,
    1 : ROOT.kRed-6 ,
    2 : ROOT.kGreen-6 ,
    3 : ROOT.kMagenta-6 ,
    4 : ROOT.kCyan-6 ,
    5 : ROOT.kYellow-6 ,
    6 : ROOT.kBlue+3 ,
    7 : ROOT.kRed+3 ,
    8 : ROOT.kGreen+3 ,
    9 : ROOT.kMagenta+3 ,
    10 : ROOT.kCyan+3 ,
    11 : ROOT.kYellow+3 ,
    68 : ROOT.kGreen ,
    95 : ROOT.kYellow ,
}
LINESTYLEMAP = {}
MARKERSTYLEMAP = {}
GRAYMAP = {
    0 : 17 ,
    1 : 16 ,
    2 : 15 ,
    3 : 14 ,
    4 : 13 ,
    5 : 12 ,
}

def getColor( i ):
    if i in COLORMAP.keys(): return COLORMAP[i]
    if type(i) is int:
        if i >= 100: return i-100
    return ROOT.kBlack

def getLineStyle( i ):
    if i in LINESTYLEMAP.keys(): return LINESTYLEMAP[i]
    if type(i) is int:
        return i
    return ROOT.kSolid

def getMarkerStyle( i ):
    if i in MARKERSTYLEMAP.keys(): return MARKERSTYLEMAP[i]
    if type(i) is int:
        return (20+i) % 100
    return 20

def getGray( i ):
    if i in GRAYMAP.keys(): return GRAYMAP[i]
    return ROOT.kBlack

def norm( h , n=1.0 ):
    h.Scale( n / h.Integral() )

def scaleMax( h , scale ):
    if type(h) is list:
        m = max( [ ih.GetMaximum() for ih in h ] )
        for ih in h:
            ih.SetMaximum( scale * m )
            ih.SetMinimum( 0.0 )
    else:
        h.SetMaximum( scale * h.GetMaximum() )
        h.SetMinimum( 0.0 )

def getBinNormalization( h ):
    xrange = h.GetXaxis().GetBinLowEdge( h.GetXaxis().GetFirst() ) - h.GetXaxis().GetBinUpEdge( h.GetXaxis().GetLast() )
    return xrange / float(h.GetNbinsX())
    

#
# Boiler plate function for configuring any root object so it
# looks at least a little bit nice...
#    
def makePretty( o , color=0 , textsize=1.0 , textlocation=LEFT , linewidth=-1 , linestyle=ROOT.kSolid , fill=False ):

    if linewidth < 0: linewidth = LINEWIDTH
    
    if isinstance(o,ROOT.TH2):
        # It is important that TH2 comes before TH1 in this list of cases
        # since TH2 inherits TH1
        o.GetXaxis().SetTitleFont( 42 )
        o.GetXaxis().SetLabelFont( 42 )
        o.GetXaxis().SetTitleSize( 0.035 )
        o.GetXaxis().SetLabelSize( 0.035 )
        o.GetXaxis().SetTitleOffset( 1.45 )
        o.GetYaxis().SetTitleFont( 42 )
        o.GetYaxis().SetLabelFont( 42 )
        o.GetYaxis().SetTitleSize( 0.035 )
        o.GetYaxis().SetLabelSize( 0.035 )
        o.GetYaxis().SetTitleOffset( 2.00 )
        o.GetZaxis().SetTitleFont( 42 )
        o.GetZaxis().SetLabelFont( 42 )
        o.GetZaxis().SetTitleSize( 0.035 )
        o.GetZaxis().SetLabelSize( 0.035 )
        o.GetZaxis().SetTitleOffset( 1.65 )
        o.SetLineColor( getColor(color) )
        o.SetFillColor( getColor(color) )
        o.SetFillStyle( 0 )
        o.SetMarkerColor( getColor(color) )
        o.SetMinimum( 0.0 )
        o.SetContour( 160 )
        
    elif isinstance(o,ROOT.TH1):
        if fill:
            o.SetFillColor( getColor(color) )
            o.SetFillStyle( 1001 )
            o.SetLineColor( ROOT.kBlack )
            o.SetLineWidth( linewidth )
        else:
            o.SetFillColor( getColor(color) )
            o.SetFillStyle( 0 )
            o.SetLineColor( getColor(color) )
            o.SetLineWidth( linewidth )
        o.SetLineStyle( getLineStyle(linestyle) )
        o.SetMarkerColor( getColor(color) )
        o.SetMarkerStyle( getMarkerStyle(color) )
        o.GetXaxis().SetTitleFont( 42 )
        o.GetXaxis().SetLabelFont( 42 )
        o.GetXaxis().SetTitleSize( 0.035 )
        o.GetXaxis().SetLabelSize( 0.035 )
        o.GetXaxis().SetTitleOffset( 1.45 );
        o.GetYaxis().SetTitleFont( 42 )
        o.GetYaxis().SetLabelFont( 42 )
        o.GetYaxis().SetTitleSize( 0.035 )
        o.GetYaxis().SetLabelSize( 0.035 )
        o.GetYaxis().SetTitleOffset( 2.00 )
        o.SetMinimum( 0.0 )

    elif isinstance(o,ROOT.TF1):
        o.SetLineColor( getColor(color) )
        o.SetLineWidth( linewidth )
        o.SetLineStyle( getLineStyle(linestyle) )
        o.SetMarkerColor( getColor(color) )
        o.SetMarkerStyle( getMarkerStyle(color) )
        o.GetXaxis().SetTitleFont( 42 )
        o.GetXaxis().SetLabelFont( 42 )
        o.GetXaxis().SetTitleSize( 0.035 )
        o.GetXaxis().SetLabelSize( 0.035 )
        o.GetXaxis().SetTitleOffset( 1.45 );
        o.GetYaxis().SetTitleFont( 42 )
        o.GetYaxis().SetLabelFont( 42 )
        o.GetYaxis().SetTitleSize( 0.035 )
        o.GetYaxis().SetLabelSize( 0.035 )
        o.GetYaxis().SetTitleOffset( 2.00 )

    elif isinstance(o,ROOT.TGraph2D):
        o.GetHistogram().GetXaxis().SetTitleFont( 42 )
        o.GetHistogram().GetXaxis().SetLabelFont( 42 )
        o.GetHistogram().GetXaxis().SetTitleSize( 0.035 )
        o.GetHistogram().GetXaxis().SetLabelSize( 0.035 )
        o.GetHistogram().GetXaxis().SetTitleOffset( 1.45 )
        o.GetHistogram().GetYaxis().SetTitleFont( 42 )
        o.GetHistogram().GetYaxis().SetLabelFont( 42 )
        o.GetHistogram().GetYaxis().SetTitleSize( 0.035 )
        o.GetHistogram().GetYaxis().SetLabelSize( 0.035 )
        o.GetHistogram().GetYaxis().SetTitleOffset( 2.00 )
        o.GetHistogram().GetZaxis().SetTitleFont( 42 )
        o.GetHistogram().GetZaxis().SetLabelFont( 42 )
        o.GetHistogram().GetZaxis().SetTitleSize( 0.035 )
        o.GetHistogram().GetZaxis().SetLabelSize( 0.035 )
        o.GetHistogram().GetZaxis().SetTitleOffset( 1.65 )
        o.GetHistogram().SetLineColor( getColor(color) )
        o.GetHistogram().SetFillColor( getColor(color) )
        o.GetHistogram().SetFillStyle( 0 )
        o.GetHistogram().SetMarkerColor( getColor(color) )
        o.GetHistogram().SetContour( 160 )
        
    elif isinstance(o,ROOT.TGraph):
        o.SetLineColor( getColor(color) )
        o.SetFillColor( getColor(color) )
        o.SetMarkerColor( getColor(color) )
        o.SetLineWidth( linewidth )
        o.SetMarkerStyle( getMarkerStyle(color) )
        o.GetXaxis().SetTitleFont( 42 )
        o.GetXaxis().SetLabelFont( 42 )
        o.GetXaxis().SetTitleSize( 0.035 )
        o.GetXaxis().SetLabelSize( 0.035 )
        o.GetXaxis().SetTitleOffset( 1.45 );
        o.GetYaxis().SetTitleFont( 42 )
        o.GetYaxis().SetLabelFont( 42 )
        o.GetYaxis().SetTitleSize( 0.035 )
        o.GetYaxis().SetLabelSize( 0.035 )
        o.GetYaxis().SetTitleOffset( 2.00 )

    elif isinstance(o,ROOT.TLine):
        o.SetLineColor( getColor(color) )
        o.SetLineWidth( linewidth )
        o.SetLineStyle( getLineStyle(linestyle) )
        if isinstance(o,ROOT.TArrow):
            o.SetFillColor( getColor(color) )

    elif isinstance(o,ROOT.TLegend) or isinstance(o,ROOT.TPaveText):
        o.SetBorderSize( 0 )
        o.SetTextFont( 42 )
        o.SetFillStyle( 0 )
        o.SetTextColor( ROOT.kBlack )
        nlines       = o.GetSize() if isinstance(o,ROOT.TPaveText) else o.GetNRows()
        padheight    = 1.0
        padtopmargin = 0.1
        textheight   = ( textsize * 0.04 / padheight ) * float(nlines)
        y2           = 1.0 - (0.01/padheight) - padtopmargin
        y1           = y2 - textheight
        o.SetTextSize( textsize * 0.04 / padheight )
        o.SetY2NDC( y2 )
        o.SetY1NDC( y1 )
        if textlocation==LEFT:
            o.SetX1NDC( 0.17 )
            o.SetX2NDC( 0.40 )
            o.SetTextAlign( 12 )
        elif textlocation==RIGHT:
            o.SetX1NDC( 0.85 )
            o.SetX2NDC( 0.86 )
            #o.SetX1NDC( 0.78 )
            #o.SetX2NDC( 0.79 )
            o.SetTextAlign( 32 )
        elif textlocation==CENTER:
            o.SetX1NDC( 0.40 )
            o.SetX2NDC( 0.43 )
            o.SetTextAlign( 12 )
        else:
            report.crash( "unknown texthorizontal argument" , texthorizontal )

    else:
        report.crash( "makePretty function doesnt know how to configure this type" , type(o) )
