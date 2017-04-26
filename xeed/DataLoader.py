import os
import numpy as np
import pandas as pd
from binascii import hexlify
from string import digits
import datetime

def loadWerkFile( f , npoints=None ):
    if f.filename.lower().endswith('.csv'):
        return loadCsvFile(f,npoints)
    elif f.filename.lower().endswith('.bin'):
        return loadBinFile(f,npoints)
    else:
        raise ValueError('File format unknown for file=%s'%f.filename)

    
def loadPaths( paths , npoints=None ):
    # Ensure that input is a list of strings
    if type(paths) is not list:
        raise TypeError('input must be a list of paths')
    
    # Load DataFrame for each path in the list
    res = None
    for p in paths:
        if p.lower().endswith('.csv'):
            with open(p,'r') as f:
                df = loadCsvFile(f,npoints)
                df['SUBJECT'], df['LIMB'], df['LABEL'] = parse_filename(p)
        elif p.lower().endswith('.bin'):
            with open(p,'r') as f:
                df = loadBinFile(f,npoints)
                df['SUBJECT'], df['LIMB'], df['LABEL'] = parse_filename(p)
        else:
            raise TypeError('Not sure how to parse this file format')

        # Append this new file worth of data onto our merged dataframe
        if res is None:
            res = df
        else:
            res = res.append( df , ignore_index=True )

        # End the iteration if we've already populated enough rows
        if npoints is not None:
            if len(df) >= npoints:
                df = df.iloc[:npoints]
                break

    # Return combined DataFrame
    return res

#######################################################################
# HELPER FUNCTIONS
# Mostly for parsing binary formatted files
#######################################################################

    
def get_next_binsec( f ):
    s = hexlify( f.read(458) )

    # If length is different than expected then we have
    # reached end of file
    if not( len(s) == 916 ):
        return s,False

    # Assert that header is formatted correctly
    if not( s[:12] == '010001020300' ):
        raise ValueError('OneSecond header is %s != 010001020300, f=%s'%(s[:12],f))
    
    return s,True

def int_to_q( i ): return ( float(i) / 32767.5 ) - 1.0
def int_to_a( i ): return ( float(i) / 1092.25 ) - 30.0 # in m/s^2

def binsec_start_time( s ):
    return datetime.datetime.fromtimestamp( int(s[12:20],16) )

def binsec_to_bytepairs( s ):
    return [ s[i:i+4] for i in range(20,916,4) ]

def bytepairs_to_measurement( bytes2 , imeasure ):
    # There are 7 words per measurement, so our word iterator
    # should start at imeasure * 7
    itr = imeasure * 7
    qvec = [ int_to_q( int(bytes2[i],16) ) for i in range(itr,itr+4) ]
    avec = [ int_to_a( int(bytes2[i],16) ) for i in range(itr+4,itr+7) ]
    return qvec + avec

def loadBinFile( f , npoints=None ):

    df = pd.DataFrame()

    timestep = datetime.timedelta( milliseconds=31.25 )
    
    for i in xrange(32400): # Max time per file set to 9hrs
        
        # Try loading next second
        try:
            binsec , good = get_next_binsec( f )
        except ValueError:
            print 'Corrupt header found, ending loop over file'
            break
        
        # Break if the load failed because we reached EOF,
        # or some wierd data formatting
        if not(good): 
            break 

        time = binsec_start_time( binsec )
        
        # Convert second string to byte pairs
        bytepairs = binsec_to_bytepairs( binsec )
        
        # Convert bytepairs to measurements and append to table
        df = df.append( [ [time+(im*timestep)] + bytepairs_to_measurement(bytepairs,im) for im in range(32) ] , 
                        ignore_index=True )

        # End iteration if we've already populated enough rows
        if npoints is not None:
            if len(df) >= npoints:
                df = df.iloc[:npoints]
                break

    columns = ['DATETIME','Q0','Q1','Q2','Q3','AX','AY','AZ']
    if len(df)==0:
        return pd.DataFrame( columns=columns )

    df.columns = columns
    return df


def loadCsvFile( f , npoints=None ):
    df = pd.read_csv( f , index_col=None , nrows=npoints )
    df['DATETIME'] = [ datetime.datetime.fromtimestamp(t/1000) + datetime.timedelta(milliseconds=(t%1000))
                       for t in df['TIME'] ]
    df.drop( 'TIME' , axis=1 , inplace=True )
    return df

def parse_filename( fname ):
    f = os.path.basename(fname)
    fhits = f.split('_')

    if not( len(fhits)==3 ):
        raise ValueError('Filename %s (fullpath=%s) is not parsable without added logic'%(f,fname))
    
    subject = fhits[0]
    limb = fhits[1]
    label = fhits[2][:-4].translate( None , digits )
    return subject,limb,label
