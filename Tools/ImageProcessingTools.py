#!/usr/local/bin/python2

import sys
import os
import pandas
import csv
import math

import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import numpy as np
from matplotlib.backends.backend_pdf import PdfPages

from scipy.ndimage import rotate
from skimage import measure, morphology, restoration, transform
from skimage.feature import greycomatrix, greycoprops


class DR_ImageProcessingTools:

    """ 
    Contains functions for processing images and generating high-level features
    Input is assumed to be a gray scale image as a numpy array, entries [0,255]
    """

    ##################################################
    # Generic image conversion/altering tools
    ##################################################
        
    def _convert_binary( self , img , thresh=64 ):
        return img > thresh

    def _clean_binary( self , img_bw ):
        # Remove the edges of the image
        bw2 = img_bw.copy()
        bw2[:1, :] = False
        bw2[-1:, :] = False
        bw2.transpose()[:1, :] = False
        bw2.transpose()[-1:, :] = False
        # Remove small objects (noise)
        bw3 = morphology.remove_small_objects(bw2, 5)
        return bw3

    def _label_binary( self , img_bw , img ):
        # Find the regions in the binary image
        cc , self.num_regions = measure.label( img_bw , return_num=True )
        if self.num_regions < 2:
	    # Only background found
	    return cc
        elif self.num_regions > 2:
	    # Dilate the image to catch nearby objects if more than one region
	    bw2 = morphology.dilation( img_bw , morphology.disk(1) )
	    # Label the dilated image and intersect with the original
	    cc2 = img_bw * (measure.label(bw2) + 1)
        else:
	    cc2 = cc.copy()
        areas = np.asarray([v.filled_area for v in measure.regionprops(cc2, img)])
        obj_idx = np.argsort(areas)[-1]
        cc3 = 0 * np.ones_like(cc)
        cc3[cc2 == sorted(np.unique(cc2))[1:][obj_idx]] = 1
        return cc3

    def _calc_glcm( self , img , distances=[5] , angles=[0] , levels=256 , symmetric=False , normed=False ):
        return greycomatrix( img , distances , angles , levels , symmetric , normed )
    
    ##################################################
    # Initialize and process image
    # IMPORTANT: input img should be gray scale, built specifically for MNIST data
    ##################################################
    
    def __init__( self ):

        self.features = [
            self.num_regions ,
            self.area ,
            self.eccentricity ,
            self.equivalent_diameter ,
            self.major_axis_length ,
            self.mean_intensity ,
            self.minor_axis_length ,
            self.perimeter ,
            self.solidity ,
            self.euler_number ,
            self.inertia_tensor_xx ,
            self.inertia_tensor_xy ,
            self.inertia_tensor_yy ,
            self.moments_hu_1 ,
            self.moments_hu_2 ,
            self.moments_hu_3 ,
            self.moments_hu_4 ,
            self.moments_hu_5 ,
            self.moments_hu_6 ,
            self.moments_hu_7 ,
            self.weighted_moments_hu_1 ,
            self.weighted_moments_hu_2 ,
            self.weighted_moments_hu_3 ,
            self.weighted_moments_hu_4 ,
            self.weighted_moments_hu_5 ,
            self.weighted_moments_hu_6 ,
            self.weighted_moments_hu_7 ,
            self.contrast ,
            self.dissimilarity ,
            self.homogeneity ,
            self.energy ,
            self.correlation ,
            self.ASM ,
            self.trace ,
        ]

        self.featureNames = [ f.__name__ for f in self.features ]
        
    def process( self , img ):

        self.img = img

        # Calculate region properties for primary region in image
        self.img_binary  = self._convert_binary( self.img , thresh=64 )
        self.img_labeled = self._label_binary( self.img_binary , self.img )

        # Just the properties for region 0
        self.props       = measure.regionprops( self.img_labeled , self.img )[0] 

        # Calculate GLCM array
        self.glcm    = self._calc_glcm( self.img )
        

    ##################################################
    # General features
    ##################################################

    def num_regions( self ):
        return self.num_regions

    ##################################################
    # Regionprops features
    ##################################################

    def _inertia_tensor( self , idx ):
        arr = self.props['inertia_tensor']
        try:
	    val = arr[idx]
        except (IndexError, TypeError):
	    val = 0.
        return val
    
    def _moments_hu( self , idx ):
        arr = self.props['moments_hu']
        try:
	    val = arr[idx]
        except (IndexError, TypeError):
            val = 0.
        return val

    def _weighted_moments_hu( self , idx ):
        arr = self.props['weighted_moments_hu']
        try:
	    val = arr[idx]
        except (IndexError, TypeError):
	    val = 0.
        return val
    
    def area(self):
        return self.props['area']
    def eccentricity(self):
        return self.props['eccentricity']
    def equivalent_diameter(self):
        return self.props['equivalent_diameter']
    def major_axis_length(self):
        return self.props['major_axis_length']
    def mean_intensity(self):
        return self.props['mean_intensity']
    def minor_axis_length(self):
        return self.props['minor_axis_length']
    def perimeter(self):
        return self.props['perimeter']
    def solidity(self):
        return self.props['solidity']
    def euler_number(self):
        return self.props['euler_number']

    def inertia_tensor_xx(self):
        return self.props['inertia_tensor'][(0,0)]
    def inertia_tensor_xy(self):
        return self.props['inertia_tensor'][(0,1)]
    def inertia_tensor_yy(self):
        return self.props['inertia_tensor'][(1,1)]

    def moments_hu_1(self):
        return self.props['moments_hu'][0]
    def moments_hu_2(self):
        return self.props['moments_hu'][1]
    def moments_hu_3(self):
        return self.props['moments_hu'][2]
    def moments_hu_4(self):
        return self.props['moments_hu'][3]
    def moments_hu_5(self):
        return self.props['moments_hu'][4]
    def moments_hu_6(self):
        return self.props['moments_hu'][5]
    def moments_hu_7(self):
        return self.props['moments_hu'][6]

    def weighted_moments_hu_1(self):
        return self.props['weighted_moments_hu'][0]
    def weighted_moments_hu_2(self):
        return self.props['weighted_moments_hu'][1]
    def weighted_moments_hu_3(self):
        return self.props['weighted_moments_hu'][2]
    def weighted_moments_hu_4(self):
        return self.props['weighted_moments_hu'][3]
    def weighted_moments_hu_5(self):
        return self.props['weighted_moments_hu'][4]
    def weighted_moments_hu_6(self):
        return self.props['weighted_moments_hu'][5]
    def weighted_moments_hu_7(self):
        return self.props['weighted_moments_hu'][6]


    ##################################################
    # Glcm features
    ##################################################

    def contrast( self ):
        return greycoprops( self.glcm , 'contrast' )[0,0]
    def dissimilarity( self ):
        return greycoprops( self.glcm , 'dissimilarity' )[0,0]
    def homogeneity( self ):
        return greycoprops( self.glcm , 'homogeneity' )[0,0]
    def energy( self ):
        return greycoprops( self.glcm , 'energy' )[0,0]
    def correlation( self ):
        return greycoprops( self.glcm , 'correlation' )[0,0]
    def ASM( self ):
        return greycoprops( self.glcm , 'ASM' )[0,0]
    def trace( self ):
        return np.trace( np.squeeze(self.glcm) )
        
