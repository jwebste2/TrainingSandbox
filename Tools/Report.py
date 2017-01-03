#!/usr/local/bin/python2

from sys import exit

def generic_print( tag , args ):
    if len(args) > 0:
        if hasattr( args[0] , 'write' ):
            args[0].write( tag + " ".join( [str(a) for a in args[1:]] ) + "\n" )
            args = args[1:]
    print tag + " ".join( [str(a) for a in args] )

def info( *args ): generic_print( "INFO   : " , args )
def warn( *args ): generic_print( "\033[01;33mWARN   : \033[00m" , args )
def debug( *args ): generic_print( "\033[01;36mDEBUG  : \033[00m" , args )
def error( *args ): generic_print( "\033[01;31mERROR  : \033[00m" , args )
def blank( *args ): generic_print( "  " , args )

def crash( *args ):
    generic_print( "\033[01;31mCRASH  : \033[00m" , args )
    exit()

def printassert( cond , *args ):
    if not(cond):
        generic_print( "\033[01;31mASSERT : \033[00m" , args )
        exit()
            
