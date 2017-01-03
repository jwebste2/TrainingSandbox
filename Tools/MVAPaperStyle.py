#!/usr/local/bin/python2

import ROOT

def setStyle( htools ):
    htools.LINEWIDTH             = 3
    htools.COLORMAP["bkg"]       = ROOT.kBlack
    htools.COLORMAP["sig"]       = ROOT.kBlue
    htools.COLORMAP["bkgstack"]  = ROOT.kYellow
    htools.COLORMAP["sigstack"]  = ROOT.kBlue
    htools.COLORMAP["roc"]       = ROOT.kBlue
    htools.MARKERSTYLEMAP["roc"] = 20
    htools.MARKERSTYLEMAP["sig"] = 1
    htools.MARKERSTYLEMAP["bkg"] = 1
    htools.LINESTYLEMAP["sig"]   = ROOT.kDashed
    htools.LINESTYLEMAP["bkg"]   = ROOT.kSolid
    return

