import numpy as np
import pandas as pd
import progressbar as pb
import datetime

import Quaternions

#
# Helper functions for extracting features from dataset using sliding window
#

#freqbins = [ (0.0,0.5) , (0.5,1.0) , (1.0,2.0) , (2.0,4.0) , (4.0,8.0) , (8.0,16.001) ]
freqbins = [ (0.0,0.8) , (0.8,2.0) , (2.0,4.0) , (4.0,8.0) , (8.0,16.001) ]

def limbfeatures( df , suffix='' ):
    global freqbins

    df_features = df.copy()
    df_features.set_index( 'DATETIME' , inplace=True )

    # Fill in the missing times
    timeseries = pd.date_range( df_features.index.min() , df_features.index.max() , freq=datetime.timedelta(milliseconds=31.25) )
    df_timeseries = pd.DataFrame( index=timeseries )
    df_features = df_timeseries.join( df_features , how='left' , sort=True )

    # Compute a bunch of window features with 5s window
    N = 128
    #for fname in ['Q0','Q1','Q2','Q3','AMAG','ATRAN','AZ','PHI','THETA','PSI','AZQ','ATRANQ','XYANGLE']:
    for fname in [ 'AMAG' , 'AZ' , 'ATRAN' , 'AZQ' , 'ATRANQ' , 'XYANGLE' ]:
        print 'Computing features for', fname, N
        df_features = add_window_features( df_features , fname , N , freqbins )

    # Create a Sum(fft) summing over all quaternions
    #for w in range(len(freqbins)):
    #    c = [ 'FFTP_W%i_%s_%i'%(w,s,N) for s in ['Q0','Q1','Q2','Q3'] ]
    #    df_features['FFTP_W%i_QSUM_%i'%(w,N)] = df_features[c].sum(axis=1)
    #    df_features['FFTP_W%i_QMAX_%i'%(w,N)] = df_features[c].max(axis=1)

    #for w in range(len(freqbins)):
    #    c = [ 'FFTP_W%i_%s_%i'%(w,s,N) for s in ['PHI','THETA','PSI'] ]
    #    df_features['FFTP_W%i_EULERSUM_%i'%(w,N)] = df_features[c].sum(axis=1)
    #    df_features['FFTP_W%i_EULERMAX_%i'%(w,N)] = df_features[c].max(axis=1)
        
    # Psi has some long period oscillations when people walk,
    # so lets also grab a 15 second window
    #N = 480
    #for fname in ['PSI']:
    #    print 'Rolling features for', fname, N
    #    df_features = add_window_features( df_features , fname , N , freqbins )
        
    return df_features
    
    
def add_window_features( df , fname , N , freqbins ):
    # Determine indices of bin boundaries
    freqiters = get_freqiters( freqbins , N )
    # Create a rolling window object
    roll = df[fname].rolling( min_periods=N , window=N , center=True )
    # All the dirty work here
    df['MEAN_%s_%i'%(fname,N)] = roll.mean()
    df['STD_%s_%i'%(fname,N)] = roll.std()
    df['MAX_%s_%i'%(fname,N)] = roll.max()
    df['MIN_%s_%i'%(fname,N)] = roll.min()
    df['MED_%s_%i'%(fname,N)] = roll.median()
    df['RANGE_%s_%i'%(fname,N)] = roll.apply( lambda x: x.max()-x.min() )
    df['SKEW_%s_%i'%(fname,N)] = roll.skew()
    #df['SUM_%s_%i'%(fname,N)] = roll.sum() / float(N)
    for ifreq,freq in enumerate(freqiters):
        df['FFTP_W%i_%s_%i'%(ifreq,fname,N)] = roll.apply( lambda x: np.abs(np.fft.rfft(x))[freq[0]].sum() / freq[1] )
    return df

def zero_crosses( s ):
    n = 0
    for i in s.index:
        pass
        # FIXME
    return n

def get_freqiters( bins , N=160 ):
    freq = np.fft.rfftfreq(N,d=1.0/32.0)[1:]
    freqiters = []
    for ib,b in enumerate(bins):
        # determine all of the freq indices inside each bin
        inbin = []
        for ix,x in enumerate(freq):
            if x >= b[0] and x < b[1]:
                inbin += [ ix+1 ] # plus one because freq index starts with 1 !!
        # Create a slice with the max and the min
        lo, hi = min(inbin), max(inbin)
        freqiters += [ (slice(lo,hi),hi-lo) ]
    return freqiters


def doctor_raw_data( df ):

    # Ensure that all quaternions are unit-normalized
    Quaternions.normalize_df( df )

    # Compute acceleration magnitudes and Euler angles
    df['AMAG']  = np.sqrt( np.power(df['AX'],2) + np.power(df['AY'],2) + np.power(df['AZ'],2) )
    df['ATRAN'] = np.sqrt( np.power(df['AX'],2) + np.power(df['AY'],2) )
    df['PHI']   = Quaternions.get_phi( df['Q0'] , df['Q1'] , df['Q2'] , df['Q3'] )
    df['THETA'] = Quaternions.get_theta( df['Q0'] , df['Q1'] , df['Q2'] , df['Q3'] )
    df['PSI']   = Quaternions.get_psi( df['Q0'] , df['Q1'] , df['Q2'] , df['Q3'] )

    # Compute accelerations rotated into lab reference frame
    df['AXQ'], df['AYQ'], df['AZQ'] = Quaternions.qv_mult( (df['Q0'],df['Q1'],df['Q2'],df['Q3']) , (df['AX'],df['AY'],df['AZ']) )
    df['ATRANQ'] = np.sqrt( np.power(df['AXQ'],2) + np.power(df['AYQ'],2) )

    # Compute pendulum angle w.r.t. x-y plane (in lab frame)
    df['XYANGLE'] = Quaternions.get_xyangle( df['Q0'] , df['Q1'] , df['Q2'] , df['Q3'] )
