#!/usr/local/bin/python2

import os
import Report as report




class MVAResultProcessor:

    def __init__( self , dataDir="" , dataSubdir="" , outputFileName="" ):

        self.maxSoverSqrtB = [ -1 , -1 ]
        self.maxSoverB     = [ -1 , -1 ]
        self.maxPrecision  = [ -1 , -1 ]
        self.maxRecall     = [ -1 , -1 ]
        self.maxF1score    = [ -1 , -1 ]
        
        if len(dataDir)==0:
            # No input directory, so the information needs to be set by hand by user
            self.classifierName     = "UNKNOWN"
            self.configName         = ""
            self.nLayers            = -1
            self.nNodes             = -1
            self.nTrainingEventsStr = "-1"
            self.nTrainingEvents    = -1
            self.featuresTag        = "UNKNOWN"
            self.featuresTitle      = "UNKNOWN"
            self.auc                = -1
            self.aucStr             = "-1"
            self.trainingTime       = -1
            return

        self.classifierName = "NeuroBGD"
        
        self.dataDir        = dataDir
        self.dataSubdir     = dataSubdir
        self.outputFileName = outputFileName
        self.outputFilePath = os.path.join( self.dataDir , self.dataSubdir , "output" , self.outputFileName )

        # 
        # Step 0) Check configuration information included in filename
        #
        self.configWords = outputFileName[:-4].split("_")[1:]
        self.configName  = "_".join(self.configWords)
        self.nLayers     = int( self.configWords[1].split("x")[0] )
        self.nNodes      = int( self.configWords[1].split("x")[1] )

        if "20features" in outputFileName:
            # Special case because file name has slightly different format
            self.nTrainingEventsStr = "338K"
            self.nTrainingEvents    = 338000
            self.featuresTag        = "20features"
            self.featuresTitle      = "Top 20 Features"
            
        else:
            self.nTrainingEventsStr = self.configWords[0][2:].replace("k","K").replace("000","K")
            self.nTrainingEvents    = int( self.configWords[0][2:].replace("k","000") )
            self.featuresTag        = self.configWords[0][:2]
            self.featuresTitle      = "All Features" if self.featuresTag=="AF" else \
                                      "Extended Features" if self.featuresTag=="EF" else \
                                      "Basic Features" if self.featuresTag=="BF" else \
                                      "UNKNOWN"

        report.info( "Processing config" , self.featuresTag , self.featuresTitle , self.nTrainingEvents , self.nLayers , self.nNodes )

        #
        # Step 1) Grab the AUC from Roberto's "analysis" file that corresponds to this dataset
        #
        aucFileList = [ xf for xf in os.listdir(os.path.join(self.dataDir,self.dataSubdir,"analysis")) \
                        if ".txt" in xf and self.configName in xf ]

        if self.featuresTag=="20features":
            aucFileList = [ xf for xf in os.listdir(os.path.join(self.dataDir,self.dataSubdir,"analysis")) \
                            if ".txt" in xf and "%ix%i"%(self.nLayers,self.nNodes) in xf ]
            
        if not( len(aucFileList)==1 ):
            report.crash( "List of candidate AUC files =" , aucFileList )

        self.aucFilePath  = os.path.join( self.dataDir , self.dataSubdir , "analysis" , aucFileList[0] )
        inputAucFile = open( self.aucFilePath , 'r' )
        self.aucStr = ""
        for line in inputAucFile:
            words = line.split()
            if not( len(words)==3 ): continue
            if not( words[0]=="AUC" ): continue
            self.aucStr = words[2]
            break
        inputAucFile.close()
        if len(self.aucStr)==0:
            report.crash( "Could not find AUC in file" , self.aucFilePath )

        self.auc = float( self.aucStr )


        #
        # Step 2) Grab the training time from Roberto's "training logs" file corresponding to this data
        #
        trainFileList = [ xf for xf in os.listdir(os.path.join(self.dataDir,self.dataSubdir,"training logs")) \
                          if ".txt" in xf and self.configName in xf ]
        if not( len(trainFileList)==1 ):
            report.crash( "List of candidate training log files =" , trainFileList )

        self.trainFilePath  = os.path.join( self.dataDir , self.dataSubdir , "training logs" , trainFileList[0] )
        inputTrainFile = open( self.trainFilePath , 'r' )
        self.trainingTime = 0.0
        for line in inputTrainFile:
            words = line.split()
            if not( len(words)==2 ): continue
            if not( words[0]=="training_seconds_this_epoch:" ): continue
            self.trainingTime += float(words[1])
        inputTrainFile.close()
            
    def __repr__( self ):
        return "< %s AUC=%s trainingTime=%gs >" % (self.configName,self.aucStr,self.trainingTime)

        
def key_byAuc( r ):
    return r.auc

def key_byTrainingTime( r ):
    return r.trainingTime

def key_byTrainingEvents( r ):
    return r.nTrainingEvents

def key_byNodes( r ):
    return r.nNodes

def key_byLayers( r ):
    return r.nLayers

def key_byComplexity( r ):
    return r.nLayers * r.nNodes

def key_bySoverB( r ):
    return r.maxSoverB[0]

def key_bySoverSqrtB( r ):
    return r.maxSoverSqrtB[0]
