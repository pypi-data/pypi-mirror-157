""" Python wrapper for liblip for multivariate scattered data interpolation. 

Simplifies the usage of liblip by handling all Numpy and CFFI calls
The Lipschitz interpolant possesses a number of desirable features, such
 as continuous dependence on the data, preservation of Lipschitz properties 
 and of the range of the data, uniform approximation and best error bounds. 
 On the practical side, construction and evaluation of the interpolant is 
 com- putationally stable. There is no accumulation of errors with the size 
 of the data set and dimension.
In addition to the Lipschitz constant, the user can provide information about 
other properties of f, such as monotonicity with respect to any subset of variables, 
upper and lower bounds (not necessarily constant bounds). If the data are given with errors, 
then it can be smoothened to satisfy the required properties. The Lipschitz constant, 
if unknown, can be estimated from the data using sample splitting and cross-validation techniques. 
The library also provides methods for approximation of locally Lipschitz functions.<br>

This file can also be imported as a module and contains the following
functions:
    * init - initializes package data
    * free - frees package data  
    * STCSetLipschitz
    * STCBuildLipInterpolant
    * STCValue
"""
import numpy as np
import random
import math
from  _liblip import ffi, lib as fm

###
# Helper functions
###

# global variable to support trace-info while testing
isTest = True

# decorator to execute a function once
def run_once(f):
    def wrapper(*args, **kwargs):
        if not wrapper.has_run:
            wrapper.has_run = True
            return f(*args, **kwargs)
    wrapper.has_run = False
    return wrapper

# Trace function
def trace( str):
    if isTest == True: print( "-- ", str, " --")

@run_once
def trace_once( str):
    trace( str)
    
# use numpy to create an intc array with n zeros and cast to CFFI 
def create_intc_zeros_as_CFFI_int( n):
    x = np.zeros( n, np.intc)
    px = ffi.cast( "int *", x.ctypes.data)
    return x, px

# use numpy to create an float array with n zeros and cast to CFFI 
def create_float_zeros_as_CFFI_double( n):
    x = np.zeros( n, float)
    px = ffi.cast( "double *", x.ctypes.data)
    return x, px

def convert_py_float_to_cffi( x):
    if isinstance( x, np.ndarray) == True:
        px = x
    else:
        px = np.array( x)
        if px.dtype != "float64": px = px.astype( float)
    pxcffi = ffi.cast( "double *", px.ctypes.data)
    return px, pxcffi


def convert_py_int_to_cffi( x):
    if x != None:
        x = np.intc( x)
        px = np.array( x)
        pxcffi = ffi.cast( "int *", px.ctypes.data)
    else: 
        px = np.array( 0)
        pxcffi = ffi.cast( "int *", 0)
    return px, pxcffi
   

###
# The python minimum wrapper 
###

def init( dim, npts):
    """Initializes the package data

    Args:
        dim (int): The number of dimensions
        npts (int): The number of points per dimension
        y (target function: Function to initialize YData. (default is NaN)

    Returns:
        x, XData, YData (float arrays): Data initialised with 0
    """
    trace( "init")        
    x = x = np.zeros( dim + 1, float)
    XData = np.zeros( dim * npts, float) 
    YData = np.zeros( npts, float)
    
    return x, XData, YData

def free():
    """Frees the package data

    Args:
        no arguments
    Returns:
        0: no error 
    """
    trace( "free")        
    return 0   

# Python wrapper for:
#    void STCSetLipschitz(double* x)
def STCSetLipschitz( lip_const):
    """Supplies the Lipschitz constant

    Args:
        lip_cost (float): Lipschitz constant

    Returns:
        no return value
    """
    trace( "void STCSetLipschitz(double* x)")
    plip_constnp, plip_const = convert_py_float_to_cffi( lip_const)
    fm.STCSetLipschitz( plip_const)    


# Python wrapper for:
#    int STCBuildLipInterpolant(int *Dim, int *Ndata, double* x, double* y)
def STCBuildLipInterpolant( Dim, Ndata, x, y):
    """Builds Lipschitz interpolant using the simplicial distance for 
    subsequent fast evaluation. 

    Args:
    Dim (int): dimension of the data set 
    Ndata (int): the size of the data set
    x (float array): abscissae of the data, stored rowwise
    y (float array): values to be interpolated
    Returns:
        Lipschitz interpolant
    """
    trace( "int STCBuildLipInterpolant(int *Dim, int *Ndata, double* x, double* y)")
    pDimnp, pDim = convert_py_int_to_cffi( Dim)
    pNdatanp, pNdata = convert_py_int_to_cffi( Ndata)
    pxnp, px = convert_py_float_to_cffi( x)
    pynp, py = convert_py_float_to_cffi( y)

    return fm.STCBuildLipInterpolant( pDim, pNdata, px, py)


# Python wrapper for:
#    double STCValue( double* x );
def STCValue( x):
    """Computes the value of the interpolant at any given point x, using fast method.
    Must be called after STCBuildLipInterpolant() procedure.

    Args:
        x (float array): point

    Returns:
        (foat): interpolant
    """
    trace_once( "double STCValue( double* x );")
    pxnp, px = convert_py_float_to_cffi( x)
    
    return fm.STCValue( px)

###
# Remaining wrapper functions 
###

# Python wrapper for:
#    double	LipIntValue(int* Dim, int* Ndata, double* x, double* Xd,double* y,  double* Lipconst, int* Index)
def LipIntValue(Dim, Ndata, x, Xd, y, Lipconst, Index):
    """LipIntValue

    Args:
        Dim (int):
        Ndata (int):
        x (float):
        Xd (float):
        y (float):
        Lipconst (float):
        Index (int):

    Returns:
        (double):
    """
    trace( "double	LipIntValue(int* Dim, int* Ndata, double* x, double* Xd,double* y,  double* Lipconst, int* Index)")
    pDimnp, pDim = convert_py_int_to_cffi( Dim)
    pNdatanp, pNdata = convert_py_int_to_cffi( Ndata)
    pxnp, px = convert_py_float_to_cffi( x)
    pXdnp, pXd = convert_py_float_to_cffi( Xd)
    pynp, py = convert_py_float_to_cffi( y)
    pLipconstnp, pLipconst = convert_py_float_to_cffi( Lipconst)
    pIndexnp, pIndex = convert_py_int_to_cffi( Index)

    yy = fm.LipIntValue( pDim, pNdata, px, pXd, py, pLipconst, pIndex)
    return yy


# Python wrapper for:
#    double	LipIntValueAuto(int* Dim, int* Ndata, double* x,double* Xd, double* y, int* Index)
def LipIntValueAuto(Dim, Ndata, x, Xd, y, Index):
    """LipIntValueAuto

    Args:
        Dim (int):
        Ndata (int):
        x (float):
        Xd (float):
        y (float):
        Index (int):

    Returns:
        (double):
    """
    trace( "double	LipIntValueAuto(int* Dim, int* Ndata, double* x,double* Xd, double* y, int* Index)")
    pDimnp, pDim = convert_py_int_to_cffi( Dim)
    pNdatanp, pNdata = convert_py_int_to_cffi( Ndata)
    pxnp, px = convert_py_float_to_cffi( x)
    pXdnp, pXd = convert_py_float_to_cffi( Xd)
    pynp, py = convert_py_float_to_cffi( y)
    pIndexnp, pIndex = convert_py_int_to_cffi( Index)
    yy = fm.LipIntValueAuto( pDim, pNdata, px, pXd, py, pIndex)
    return yy


# Python wrapper for:
#    double	LipIntValueCons(int* Dim, int* Ndata, int* Cons, double* x, double* Xd,double* y,  double* Lipconst, int* Index)
def LipIntValueCons(Dim, Ndata, Cons, x, Xd, y, Lipconst, Index):
    """LipIntValueCons

    Args:
        Dim (int):
        Ndata (int):
        Cons (int):
        x (float):
        Xd (float):
        y (float):
        Lipconst (float):
        Index (int):

    Returns:
        (double):
    """
    trace( "double	LipIntValueCons(int* Dim, int* Ndata, int* Cons, double* x, double* Xd,double* y,  double* Lipconst, int* Index)")
    pDimnp, pDim = convert_py_int_to_cffi( Dim)
    pNdatanp, pNdata = convert_py_int_to_cffi( Ndata)
    pConsnp, pCons = convert_py_int_to_cffi( Cons)
    pxnp, px = convert_py_float_to_cffi( x)
    pXdnp, pXd = convert_py_float_to_cffi( Xd)
    pynp, py = convert_py_float_to_cffi( y)
    pLipconstnp, pLipconst = convert_py_float_to_cffi( Lipconst)
    pIndexnp, pIndex = convert_py_int_to_cffi( Index)
    yy = fm.LipIntValueCons( pDim, pNdata, pCons, px, pXd, py, pLipconst, pIndex)
    return yy


# Python wrapper for:
#    double	LipIntValueConsLeftRegion(int* Dim, int* Ndata, int* Cons, double* x, double* Xd,double* y,  double* Lipconst, double* Region, int* Index)
def LipIntValueConsLeftRegion(Dim, Ndata, Cons, x, Xd, y, Lipconst, Region, Index):
    """LipIntValueConsLeftRegion

    Args:
        Dim (int):
        Ndata (int):
        Cons (int):
        x (float):
        Xd (float):
        y (float):
        Lipconst (float):
        Region (float):
        Index (int):

    Returns:
        (double):
    """
    trace( "double	LipIntValueConsLeftRegion(int* Dim, int* Ndata, int* Cons, double* x, double* Xd,double* y,  double* Lipconst, double* Region, int* Index)")
    pDimnp, pDim = convert_py_int_to_cffi( Dim)
    pNdatanp, pNdata = convert_py_int_to_cffi( Ndata)
    pConsnp, pCons = convert_py_int_to_cffi( Cons)
    pxnp, px = convert_py_float_to_cffi( x)
    pXdnp, pXd = convert_py_float_to_cffi( Xd)
    pynp, py = convert_py_float_to_cffi( y)
    pLipconstnp, pLipconst = convert_py_float_to_cffi( Lipconst)
    pRegionnp, pRegion = convert_py_float_to_cffi( Region)
    pIndexnp, pIndex = convert_py_int_to_cffi( Index)
    yy = fm.LipIntValueConsLeftRegion( pDim, pNdata, pCons, px, pXd, py, pLipconst, pRegion, pIndex)
    return yy


# Python wrapper for:
#    double	LipIntValueConsRightRegion(int* Dim, int* Ndata, int* Cons, double* x, double* Xd,double* y,  double* Lipconst, double* Region, int* Index)
def LipIntValueConsRightRegion(Dim, Ndata, Cons, x, Xd, y, Lipconst, Region, Index):
    """LipIntValueConsRightRegion

    Args:
        Dim (int):
        Ndata (int):
        Cons (int):
        x (float):
        Xd (float):
        y (float):
        Lipconst (float):
        Region (float):
        Index (int):

    Returns:
        (double):
    """
    trace( "double	LipIntValueConsRightRegion(int* Dim, int* Ndata, int* Cons, double* x, double* Xd,double* y,  double* Lipconst, double* Region, int* Index)")
    pDimnp, pDim = convert_py_int_to_cffi( Dim)
    pNdatanp, pNdata = convert_py_int_to_cffi( Ndata)
    pConsnp, pCons = convert_py_int_to_cffi( Cons)
    pxnp, px = convert_py_float_to_cffi( x)
    pXdnp, pXd = convert_py_float_to_cffi( Xd)
    pynp, py = convert_py_float_to_cffi( y)
    pLipconstnp, pLipconst = convert_py_float_to_cffi( Lipconst)
    pRegionnp, pRegion = convert_py_float_to_cffi( Region)
    pIndexnp, pIndex = convert_py_int_to_cffi( Index)
    yy = fm.LipIntValueConsRightRegion( pDim, pNdata, pCons, px, pXd, py, pLipconst, pRegion, pIndex)
    return yy


# Python wrapper for:
#    double	LipIntValueLocal(int *Dim, int *Ndata, double* x, double* Xd,double* y)
def LipIntValueLocal(Dim, Ndata, x, Xd, y):
    """LipIntValueLocal

    Args:
        Dim (int):
        Ndata (int):
        x (float):
        Xd (float):
        y (float):

    Returns:
        (double):
    """
    trace( "double	LipIntValueLocal(int *Dim, int *Ndata, double* x, double* Xd,double* y)")
    pDimnp, pDim = convert_py_int_to_cffi( Dim)
    pNdatanp, pNdata = convert_py_int_to_cffi( Ndata)
    pxnp, px = convert_py_float_to_cffi( x)
    pXdnp, pXd = convert_py_float_to_cffi( Xd)
    pynp, py = convert_py_float_to_cffi( y)
    yy = fm.LipIntValueLocal( pDim, pNdata, px, pXd, py)
    return yy


# Python wrapper for:
#    double	LipIntValueLocalCons(int *Dim, int *Ndata,int* Cons, double* x, double* Xd,double* y)
def LipIntValueLocalCons(Dim, Ndata, Cons, x, Xd, y):
    """LipIntValueLocalCons

    Args:
        Dim (int):
        Ndata (int):
        Cons (int):
        x (float):
        Xd (float):
        y (float):

    Returns:
        (double):
    """
    trace( "double	LipIntValueLocalCons(int *Dim, int *Ndata,int* Cons, double* x, double* Xd,double* y)")
    pDimnp, pDim = convert_py_int_to_cffi( Dim)
    pNdatanp, pNdata = convert_py_int_to_cffi( Ndata)
    pConsnp, pCons = convert_py_int_to_cffi( Cons)
    pxnp, px = convert_py_float_to_cffi( x)
    pXdnp, pXd = convert_py_float_to_cffi( Xd)
    pynp, py = convert_py_float_to_cffi( y)
    yy = fm.LipIntValueLocalCons( pDim, pNdata, pCons, px, pXd, py)
    return yy


# Python wrapper for:
#    double	LipIntValueLocalConsLeftRegion(int *Dim, int *Ndata,int* Cons, double* x, double* Xd,double* y, double* Region)
def LipIntValueLocalConsLeftRegion(Dim, Ndata, Cons, x, Xd, y, Region):
    """LipIntValueLocalConsLeftRegion

    Args:
        Dim (int):
        Ndata (int):
        Cons (int):
        x (float):
        Xd (float):
        y (float):
        Region (float):

    Returns:
        (double):
    """
    trace( "double	LipIntValueLocalConsLeftRegion(int *Dim, int *Ndata,int* Cons, double* x, double* Xd,double* y, double* Region)")
    pDimnp, pDim = convert_py_int_to_cffi( Dim)
    pNdatanp, pNdata = convert_py_int_to_cffi( Ndata)
    pConsnp, pCons = convert_py_int_to_cffi( Cons)
    pxnp, px = convert_py_float_to_cffi( x)
    pXdnp, pXd = convert_py_float_to_cffi( Xd)
    pynp, py = convert_py_float_to_cffi( y)
    pRegionnp, pRegion = convert_py_float_to_cffi( Region)
    yy = fm.LipIntValueLocalConsLeftRegion( pDim, pNdata, pCons, px, pXd, py, pRegion)
    return yy


# Python wrapper for:
#    double	LipIntValueLocalConsRightRegion(int *Dim, int *Ndata,int* Cons, double* x, double* Xd,double* y, double* Region)
def LipIntValueLocalConsRightRegion(Dim, Ndata, Cons, x, Xd, y, Region):
    """LipIntValueLocalConsRightRegion

    Args:
        Dim (int):
        Ndata (int):
        Cons (int):
        x (float):
        Xd (float):
        y (float):
        Region (float):

    Returns:
        (double):
    """
    trace( "double	LipIntValueLocalConsRightRegion(int *Dim, int *Ndata,int* Cons, double* x, double* Xd,double* y, double* Region)")
    pDimnp, pDim = convert_py_int_to_cffi( Dim)
    pNdatanp, pNdata = convert_py_int_to_cffi( Ndata)
    pConsnp, pCons = convert_py_int_to_cffi( Cons)
    pxnp, px = convert_py_float_to_cffi( x)
    pXdnp, pXd = convert_py_float_to_cffi( Xd)
    pynp, py = convert_py_float_to_cffi( y)
    pRegionnp, pRegion = convert_py_float_to_cffi( Region)
    yy = fm.LipIntValueLocalConsRightRegion( pDim, pNdata, pCons, px, pXd, py, pRegion)
    return yy


# Python wrapper for:
#    void	LipIntComputeLipschitz(int *Dim, int *Ndata, double* x, double* y)
def LipIntComputeLipschitz(Dim, Ndata, x, y):
    """LipIntComputeLipschitz

    Args:
        Dim (int):
        Ndata (int):
        x (float):
        y (float):

    Returns:
        <none>
    """
    trace( "void	LipIntComputeLipschitz(int *Dim, int *Ndata, double* x, double* y)")
    pDimnp, pDim = convert_py_int_to_cffi( Dim)
    pNdatanp, pNdata = convert_py_int_to_cffi( Ndata)
    pxnp, px = convert_py_float_to_cffi( x)
    pynp, py = convert_py_float_to_cffi( y)
    fm.LipIntComputeLipschitz( pDim, pNdata, px, py)
    return 


# Python wrapper for:
#    void 	LipIntComputeLocalLipschitz(int *Dim, int *Ndata, double* x, double* y)
def LipIntComputeLocalLipschitz(Dim, Ndata, x, y):
    """LipIntComputeLocalLipschitz

    Args:
        Dim (int):
        Ndata (int):
        x (float):
        y (float):

    Returns:
        <none>
    """
    trace( "void 	LipIntComputeLocalLipschitz(int *Dim, int *Ndata, double* x, double* y)")
    pDimnp, pDim = convert_py_int_to_cffi( Dim)
    pNdatanp, pNdata = convert_py_int_to_cffi( Ndata)
    pxnp, px = convert_py_float_to_cffi( x)
    pynp, py = convert_py_float_to_cffi( y)
    fm.LipIntComputeLocalLipschitz( pDim, pNdata, px, py)
    return 


# Python wrapper for:
#    void	LipIntComputeLipschitzCV(int *Dim, int *Ndata, double* Xd, double* y, double* T, int* type, int* Cons, double* Region, double *W)
def LipIntComputeLipschitzCV(Dim, Ndata, Xd, y, T, type, Cons, Region, W):
    """LipIntComputeLipschitzCV

    Args:
        Dim (int):
        Ndata (int):
        Xd (float):
        y (float):
        T (float):
        type (int):
        Cons (int):
        Region (float):
        W (float):

    Returns:
        <none>
    """
    trace( "void	LipIntComputeLipschitzCV(int *Dim, int *Ndata, double* Xd, double* y, double* T, int* type, int* Cons, double* Region, double *W)")
    pDimnp, pDim = convert_py_int_to_cffi( Dim)
    pNdatanp, pNdata = convert_py_int_to_cffi( Ndata)
    pXdnp, pXd = convert_py_float_to_cffi( Xd)
    pynp, py = convert_py_float_to_cffi( y)
    pTnp, pT = convert_py_float_to_cffi( T)
    ptypenp, ptype = convert_py_int_to_cffi( type)
    pConsnp, pCons = convert_py_int_to_cffi( Cons)
    pRegionnp, pRegion = convert_py_float_to_cffi( Region)
    pWnp, pW = convert_py_float_to_cffi( W)
    fm.LipIntComputeLipschitzCV( pDim, pNdata, pXd, py, pT, ptype, pCons, pRegion, pW)
    return 


# Python wrapper for:
#    void	LipIntComputeLipschitzSplit(int *Dim, int *Ndata, double* Xd, double* y, double* T, double* ratio,int* type, int* Cons, double* Region, double *W)
def LipIntComputeLipschitzSplit(Dim, Ndata, Xd, y, T, ratio, type, Cons, Region, W):
    """LipIntComputeLipschitzSplit

    Args:
        Dim (int):
        Ndata (int):
        Xd (float):
        y (float):
        T (float):
        ratio (float):
        type (int):
        Cons (int):
        Region (float):
        W (float):

    Returns:
        <none>
    """
    trace( "void	LipIntComputeLipschitzSplit(int *Dim, int *Ndata, double* Xd, double* y, double* T, double* ratio,int* type, int* Cons, double* Region, double *W)")
    pDimnp, pDim = convert_py_int_to_cffi( Dim)
    pNdatanp, pNdata = convert_py_int_to_cffi( Ndata)
    pXdnp, pXd = convert_py_float_to_cffi( Xd)
    pynp, py = convert_py_float_to_cffi( y)
    pTnp, pT = convert_py_float_to_cffi( T)
    prationp, pratio = convert_py_float_to_cffi( ratio)
    ptypenp, ptype = convert_py_int_to_cffi( type)
    pConsnp, pCons = convert_py_int_to_cffi( Cons)
    pRegionnp, pRegion = convert_py_float_to_cffi( Region)
    pWnp, pW = convert_py_float_to_cffi( W)
    fm.LipIntComputeLipschitzSplit( pDim, pNdata, pXd, py, pT, pratio, ptype, pCons, pRegion, pW)
    return 


# Python wrapper for:
#    void	LipIntSmoothLipschitz(int *Dim, int *Ndata,  double* Xd, double* y, double* T,  double* LC, int* fW, int* fC, int* fR, double* W, int* Cons, double* Region)
def LipIntSmoothLipschitz(Dim, Ndata, Xd, y, T, LC, fW, fC, fR, W, Cons, Region):
    """LipIntSmoothLipschitz

    Args:
        Dim (int):
        Ndata (int):
        Xd (float):
        y (float):
        T (float):
        LC (float):
        fW (int):
        fC (int):
        fR (int):
        W (float):
        Cons (int):
        Region (float):

    Returns:
        <none>
    """
    trace( "void	LipIntSmoothLipschitz(int *Dim, int *Ndata,  double* Xd, double* y, double* T,  double* LC, int* fW, int* fC, int* fR, double* W, int* Cons, double* Region)")
    pDimnp, pDim = convert_py_int_to_cffi( Dim)
    pNdatanp, pNdata = convert_py_int_to_cffi( Ndata)
    pXdnp, pXd = convert_py_float_to_cffi( Xd)
    pynp, py = convert_py_float_to_cffi( y)
    pTnp, pT = convert_py_float_to_cffi( T)
    pLCnp, pLC = convert_py_float_to_cffi( LC)
    pfWnp, pfW = convert_py_int_to_cffi( fW)
    pfCnp, pfC = convert_py_int_to_cffi( fC)
    pfRnp, pfR = convert_py_int_to_cffi( fR)
    pWnp, pW = convert_py_float_to_cffi( W)
    pConsnp, pCons = convert_py_int_to_cffi( Cons)
    pRegionnp, pRegion = convert_py_float_to_cffi( Region)
    fm.LipIntSmoothLipschitz( pDim, pNdata, pXd, py, pT, pLC, pfW, pfC, pfR, pW, pCons, pRegion)
    return 


# Python wrapper for:
#    double	LipIntGetLipConst() 
def LipIntGetLipConst():
    """LipIntGetLipConst

    Args:

    Returns:
        (double):
    """
    trace( "double	LipIntGetLipConst() ")
    yy = fm.LipIntGetLipConst( )
    return yy


# Python wrapper for:
#    void		LipIntGetScaling(double *S) 
def LipIntGetScaling(S):
    """LipIntGetScaling

    Args:
        S (float):

    Returns:
        <none>
    """
    trace( "void		LipIntGetScaling(double *S) ")
    pSnp, pS = convert_py_float_to_cffi( S)
    fm.LipIntGetScaling( pS)
    return 


# Python wrapper for:
#    int		LipIntComputeScaling(int *Dim, int *Ndata, double* XData, double* YData)
def LipIntComputeScaling(Dim, Ndata, XData, YData):
    """LipIntComputeScaling

    Args:
        Dim (int):
        Ndata (int):
        XData (float):
        YData (float):

    Returns:
        (int):
    """
    trace( "int		LipIntComputeScaling(int *Dim, int *Ndata, double* XData, double* YData)")
    pDimnp, pDim = convert_py_int_to_cffi( Dim)
    pNdatanp, pNdata = convert_py_int_to_cffi( Ndata)
    pXDatanp, pXData = convert_py_float_to_cffi( XData)
    pYDatanp, pYData = convert_py_float_to_cffi( YData)
    yy = fm.LipIntComputeScaling( pDim, pNdata, pXData, pYData)
    return yy


# Python wrapper for:
#    void	ConvertXData(int *Dim, int* npts,  double* XData)
def ConvertXData(Dim, npts, XData):
    """ConvertXData

    Args:
        Dim (int):
        npts (int):
        XData (float):

    Returns:
        <none>
    """
    trace( "void	ConvertXData(int *Dim, int* npts,  double* XData)")
    pDimnp, pDim = convert_py_int_to_cffi( Dim)
    pnptsnp, pnpts = convert_py_int_to_cffi( npts)
    pXDatanp, pXData = convert_py_float_to_cffi( XData)
    fm.ConvertXData( pDim, pnpts, pXData)
    return 


# Python wrapper for:
#    void	ConvertXDataAUX(int *Dim, int* npts,  double* XData, double *auxdata)
def ConvertXDataAUX(Dim, npts, XData, auxdata):
    """ConvertXDataAUX

    Args:
        Dim (int):
        npts (int):
        XData (float):
        auxdata (float):

    Returns:
        <none>
    """
    trace( "void	ConvertXDataAUX(int *Dim, int* npts,  double* XData, double *auxdata)")
    pDimnp, pDim = convert_py_int_to_cffi( Dim)
    pnptsnp, pnpts = convert_py_int_to_cffi( npts)
    pXDatanp, pXData = convert_py_float_to_cffi( XData)
    pauxdatanp, pauxdata = convert_py_float_to_cffi( auxdata)
    fm.ConvertXDataAUX( pDim, pnpts, pXData, pauxdata)
    return 


# Python wrapper for:
#    int		LipIntVerifyMonotonicity(int *Dim, int* npts, int* Cons,  double* XData, double* YData, double* LC, double* eps)
def LipIntVerifyMonotonicity(Dim, npts, Cons, XData, YData, LC, eps):
    """LipIntVerifyMonotonicity

    Args:
        Dim (int):
        npts (int):
        Cons (int):
        XData (float):
        YData (float):
        LC (float):
        eps (float):

    Returns:
        (int):
    """
    trace( "int		LipIntVerifyMonotonicity(int *Dim, int* npts, int* Cons,  double* XData, double* YData, double* LC, double* eps)")
    pDimnp, pDim = convert_py_int_to_cffi( Dim)
    pnptsnp, pnpts = convert_py_int_to_cffi( npts)
    pConsnp, pCons = convert_py_int_to_cffi( Cons)
    pXDatanp, pXData = convert_py_float_to_cffi( XData)
    pYDatanp, pYData = convert_py_float_to_cffi( YData)
    pLCnp, pLC = convert_py_float_to_cffi( LC)
    pepsnp, peps = convert_py_float_to_cffi( eps)
    yy = fm.LipIntVerifyMonotonicity( pDim, pnpts, pCons, pXData, pYData, pLC, peps)
    return yy


# Python wrapper for:
#    int		LipIntVerifyMonotonicityLeftRegion(int *Dim, int* npts, int* Cons,  double* XData, double* YData, double* Region, double* LC, double* eps)
def LipIntVerifyMonotonicityLeftRegion(Dim, npts, Cons, XData, YData, Region, LC, eps):
    """LipIntVerifyMonotonicityLeftRegion

    Args:
        Dim (int):
        npts (int):
        Cons (int):
        XData (float):
        YData (float):
        Region (float):
        LC (float):
        eps (float):

    Returns:
        (int):
    """
    trace( "int		LipIntVerifyMonotonicityLeftRegion(int *Dim, int* npts, int* Cons,  double* XData, double* YData, double* Region, double* LC, double* eps)")
    pDimnp, pDim = convert_py_int_to_cffi( Dim)
    pnptsnp, pnpts = convert_py_int_to_cffi( npts)
    pConsnp, pCons = convert_py_int_to_cffi( Cons)
    pXDatanp, pXData = convert_py_float_to_cffi( XData)
    pYDatanp, pYData = convert_py_float_to_cffi( YData)
    pRegionnp, pRegion = convert_py_float_to_cffi( Region)
    pLCnp, pLC = convert_py_float_to_cffi( LC)
    pepsnp, peps = convert_py_float_to_cffi( eps)
    yy = fm.LipIntVerifyMonotonicityLeftRegion( pDim, pnpts, pCons, pXData, pYData, pRegion, pLC, peps)
    return yy


# Python wrapper for:
#    int		LipIntVerifyMonotonicityRightRegion(int *Dim, int* npts, int* Cons,  double* XData, double* YData, double* Region, double* LC, double* eps)
def LipIntVerifyMonotonicityRightRegion(Dim, npts, Cons, XData, YData, Region, LC, eps):
    """LipIntVerifyMonotonicityRightRegion

    Args:
        Dim (int):
        npts (int):
        Cons (int):
        XData (float):
        YData (float):
        Region (float):
        LC (float):
        eps (float):

    Returns:
        (int):
    """
    trace( "int		LipIntVerifyMonotonicityRightRegion(int *Dim, int* npts, int* Cons,  double* XData, double* YData, double* Region, double* LC, double* eps)")
    pDimnp, pDim = convert_py_int_to_cffi( Dim)
    pnptsnp, pnpts = convert_py_int_to_cffi( npts)
    pConsnp, pCons = convert_py_int_to_cffi( Cons)
    pXDatanp, pXData = convert_py_float_to_cffi( XData)
    pYDatanp, pYData = convert_py_float_to_cffi( YData)
    pRegionnp, pRegion = convert_py_float_to_cffi( Region)
    pLCnp, pLC = convert_py_float_to_cffi( LC)
    pepsnp, peps = convert_py_float_to_cffi( eps)
    yy = fm.LipIntVerifyMonotonicityRightRegion( pDim, pnpts, pCons, pXData, pYData, pRegion, pLC, peps)
    return yy


# Python wrapper for:
#    double	LipIntInfValue(int *Dim, int *Ndata, double* x, double* Xd,double* y,  double* Lipconst, int* Index)
def LipIntInfValue(Dim, Ndata, x, Xd, y, Lipconst, Index):
    """LipIntInfValue

    Args:
        Dim (int):
        Ndata (int):
        x (float):
        Xd (float):
        y (float):
        Lipconst (float):
        Index (int):

    Returns:
        (double):
    """
    trace( "double	LipIntInfValue(int *Dim, int *Ndata, double* x, double* Xd,double* y,  double* Lipconst, int* Index)")
    pDimnp, pDim = convert_py_int_to_cffi( Dim)
    pNdatanp, pNdata = convert_py_int_to_cffi( Ndata)
    pxnp, px = convert_py_float_to_cffi( x)
    pXdnp, pXd = convert_py_float_to_cffi( Xd)
    pynp, py = convert_py_float_to_cffi( y)
    pLipconstnp, pLipconst = convert_py_float_to_cffi( Lipconst)
    pIndexnp, pIndex = convert_py_int_to_cffi( Index)
    yy = fm.LipIntInfValue( pDim, pNdata, px, pXd, py, pLipconst, pIndex)
    return yy


# Python wrapper for:
#    double	LipIntInfValueAuto(int *Dim, int *Ndata, double* x,double* Xd, double* y, int* Index)
def LipIntInfValueAuto(Dim, Ndata, x, Xd, y, Index):
    """LipIntInfValueAuto

    Args:
        Dim (int):
        Ndata (int):
        x (float):
        Xd (float):
        y (float):
        Index (int):

    Returns:
        (double):
    """
    trace( "double	LipIntInfValueAuto(int *Dim, int *Ndata, double* x,double* Xd, double* y, int* Index)")
    pDimnp, pDim = convert_py_int_to_cffi( Dim)
    pNdatanp, pNdata = convert_py_int_to_cffi( Ndata)
    pxnp, px = convert_py_float_to_cffi( x)
    pXdnp, pXd = convert_py_float_to_cffi( Xd)
    pynp, py = convert_py_float_to_cffi( y)
    pIndexnp, pIndex = convert_py_int_to_cffi( Index)
    yy = fm.LipIntInfValueAuto( pDim, pNdata, px, pXd, py, pIndex)
    return yy


# Python wrapper for:
#    double	LipIntInfValueCons(int *Dim, int *Ndata, int* Cons, double* x, double* Xd,double* y,  double Lipconst, int* Index)
def LipIntInfValueCons(Dim, Ndata, Cons, x, Xd, y, Lipconst, Index):
    """LipIntInfValueCons

    Args:
        Dim (int):
        Ndata (int):
        Cons (int):
        x (float):
        Xd (float):
        y (float):
        Lipconst (float):
        Index (int):

    Returns:
        (double):
    """
    trace( "double	LipIntInfValueCons(int *Dim, int *Ndata, int* Cons, double* x, double* Xd,double* y,  double Lipconst, int* Index)")
    pDimnp, pDim = convert_py_int_to_cffi( Dim)
    pNdatanp, pNdata = convert_py_int_to_cffi( Ndata)
    pConsnp, pCons = convert_py_int_to_cffi( Cons)
    pxnp, px = convert_py_float_to_cffi( x)
    pXdnp, pXd = convert_py_float_to_cffi( Xd)
    pynp, py = convert_py_float_to_cffi( y)
    pIndexnp, pIndex = convert_py_int_to_cffi( Index)
    yy = fm.LipIntInfValueCons( pDim, pNdata, pCons, px, pXd, py, Lipconst, pIndex)
    return yy


# Python wrapper for:
#    double	LipIntInfValueConsLeftRegion(int *Dim, int *Ndata, int* Cons, double* x, double* Xd,double* y,  double* Lipconst, double* Region, int* Index)
def LipIntInfValueConsLeftRegion(Dim, Ndata, Cons, x, Xd, y, Lipconst, Region, Index):
    """LipIntInfValueConsLeftRegion

    Args:
        Dim (int):
        Ndata (int):
        Cons (int):
        x (float):
        Xd (float):
        y (float):
        Lipconst (float):
        Region (float):
        Index (int):

    Returns:
        (double):
    """
    trace( "double	LipIntInfValueConsLeftRegion(int *Dim, int *Ndata, int* Cons, double* x, double* Xd,double* y,  double* Lipconst, double* Region, int* Index)")
    pDimnp, pDim = convert_py_int_to_cffi( Dim)
    pNdatanp, pNdata = convert_py_int_to_cffi( Ndata)
    pConsnp, pCons = convert_py_int_to_cffi( Cons)
    pxnp, px = convert_py_float_to_cffi( x)
    pXdnp, pXd = convert_py_float_to_cffi( Xd)
    pynp, py = convert_py_float_to_cffi( y)
    pLipconstnp, pLipconst = convert_py_float_to_cffi( Lipconst)
    pRegionnp, pRegion = convert_py_float_to_cffi( Region)
    pIndexnp, pIndex = convert_py_int_to_cffi( Index)
    yy = fm.LipIntInfValueConsLeftRegion( pDim, pNdata, pCons, px, pXd, py, pLipconst, pRegion, pIndex)
    return yy


# Python wrapper for:
#    double	LipIntInfValueConsRightRegion(int *Dim, int *Ndata, int* Cons, double* x, double* Xd,double* y,  double* Lipconst, double* Region, int* Index)
def LipIntInfValueConsRightRegion(Dim, Ndata, Cons, x, Xd, y, Lipconst, Region, Index):
    """LipIntInfValueConsRightRegion

    Args:
        Dim (int):
        Ndata (int):
        Cons (int):
        x (float):
        Xd (float):
        y (float):
        Lipconst (float):
        Region (float):
        Index (int):

    Returns:
        (double):
    """
    trace( "double	LipIntInfValueConsRightRegion(int *Dim, int *Ndata, int* Cons, double* x, double* Xd,double* y,  double* Lipconst, double* Region, int* Index)")
    pDimnp, pDim = convert_py_int_to_cffi( Dim)
    pNdatanp, pNdata = convert_py_int_to_cffi( Ndata)
    pConsnp, pCons = convert_py_int_to_cffi( Cons)
    pxnp, px = convert_py_float_to_cffi( x)
    pXdnp, pXd = convert_py_float_to_cffi( Xd)
    pynp, py = convert_py_float_to_cffi( y)
    pLipconstnp, pLipconst = convert_py_float_to_cffi( Lipconst)
    pRegionnp, pRegion = convert_py_float_to_cffi( Region)
    pIndexnp, pIndex = convert_py_int_to_cffi( Index)
    yy = fm.LipIntInfValueConsRightRegion( pDim, pNdata, pCons, px, pXd, py, pLipconst, pRegion, pIndex)
    return yy


# Python wrapper for:
#    double	LipIntInfValueLocal(int *Dim, int *Ndata, double* x, double* Xd,double* y)
def LipIntInfValueLocal(Dim, Ndata, x, Xd, y):
    """LipIntInfValueLocal

    Args:
        Dim (int):
        Ndata (int):
        x (float):
        Xd (float):
        y (float):

    Returns:
        (double):
    """
    trace( "double	LipIntInfValueLocal(int *Dim, int *Ndata, double* x, double* Xd,double* y)")
    pDimnp, pDim = convert_py_int_to_cffi( Dim)
    pNdatanp, pNdata = convert_py_int_to_cffi( Ndata)
    pxnp, px = convert_py_float_to_cffi( x)
    pXdnp, pXd = convert_py_float_to_cffi( Xd)
    pynp, py = convert_py_float_to_cffi( y)
    yy = fm.LipIntInfValueLocal( pDim, pNdata, px, pXd, py)
    return yy


# Python wrapper for:
#    double	LipIntInfValueLocalCons(int *Dim, int *Ndata,int* Cons, double* x, double* Xd,double* y)
def LipIntInfValueLocalCons(Dim, Ndata, Cons, x, Xd, y):
    """LipIntInfValueLocalCons

    Args:
        Dim (int):
        Ndata (int):
        Cons (int):
        x (float):
        Xd (float):
        y (float):

    Returns:
        (double):
    """
    trace( "double	LipIntInfValueLocalCons(int *Dim, int *Ndata,int* Cons, double* x, double* Xd,double* y)")
    pDimnp, pDim = convert_py_int_to_cffi( Dim)
    pNdatanp, pNdata = convert_py_int_to_cffi( Ndata)
    pConsnp, pCons = convert_py_int_to_cffi( Cons)
    pxnp, px = convert_py_float_to_cffi( x)
    pXdnp, pXd = convert_py_float_to_cffi( Xd)
    pynp, py = convert_py_float_to_cffi( y)
    yy = fm.LipIntInfValueLocalCons( pDim, pNdata, pCons, px, pXd, py)
    return yy


# Python wrapper for:
#    double	LipIntInfValueLocalConsLeftRegion(int *Dim, int *Ndata,int* Cons, double* x, double* Xd,double* y, double* Region)
def LipIntInfValueLocalConsLeftRegion(Dim, Ndata, Cons, x, Xd, y, Region):
    """LipIntInfValueLocalConsLeftRegion

    Args:
        Dim (int):
        Ndata (int):
        Cons (int):
        x (float):
        Xd (float):
        y (float):
        Region (float):

    Returns:
        (double):
    """
    trace( "double	LipIntInfValueLocalConsLeftRegion(int *Dim, int *Ndata,int* Cons, double* x, double* Xd,double* y, double* Region)")
    pDimnp, pDim = convert_py_int_to_cffi( Dim)
    pNdatanp, pNdata = convert_py_int_to_cffi( Ndata)
    pConsnp, pCons = convert_py_int_to_cffi( Cons)
    pxnp, px = convert_py_float_to_cffi( x)
    pXdnp, pXd = convert_py_float_to_cffi( Xd)
    pynp, py = convert_py_float_to_cffi( y)
    pRegionnp, pRegion = convert_py_float_to_cffi( Region)
    yy = fm.LipIntInfValueLocalConsLeftRegion( pDim, pNdata, pCons, px, pXd, py, pRegion)
    return yy


# Python wrapper for:
#    double	LipIntInfValueLocalConsRightRegion(int *Dim, int *Ndata,int* Cons, double* x, double* Xd,double* y, double* Region)
def LipIntInfValueLocalConsRightRegion(Dim, Ndata, Cons, x, Xd, y, Region):
    """LipIntInfValueLocalConsRightRegion

    Args:
        Dim (int):
        Ndata (int):
        Cons (int):
        x (float):
        Xd (float):
        y (float):
        Region (float):

    Returns:
        (double):
    """
    trace( "double	LipIntInfValueLocalConsRightRegion(int *Dim, int *Ndata,int* Cons, double* x, double* Xd,double* y, double* Region)")
    pDimnp, pDim = convert_py_int_to_cffi( Dim)
    pNdatanp, pNdata = convert_py_int_to_cffi( Ndata)
    pConsnp, pCons = convert_py_int_to_cffi( Cons)
    pxnp, px = convert_py_float_to_cffi( x)
    pXdnp, pXd = convert_py_float_to_cffi( Xd)
    pynp, py = convert_py_float_to_cffi( y)
    pRegionnp, pRegion = convert_py_float_to_cffi( Region)
    yy = fm.LipIntInfValueLocalConsRightRegion( pDim, pNdata, pCons, px, pXd, py, pRegion)
    return yy


# Python wrapper for:
#    void	LipIntInfComputeLipschitz(int *Dim, int *Ndata, double* x, double* y)
def LipIntInfComputeLipschitz(Dim, Ndata, x, y):
    """LipIntInfComputeLipschitz

    Args:
        Dim (int):
        Ndata (int):
        x (float):
        y (float):

    Returns:
        <none>
    """
    trace( "void	LipIntInfComputeLipschitz(int *Dim, int *Ndata, double* x, double* y)")
    pDimnp, pDim = convert_py_int_to_cffi( Dim)
    pNdatanp, pNdata = convert_py_int_to_cffi( Ndata)
    pxnp, px = convert_py_float_to_cffi( x)
    pynp, py = convert_py_float_to_cffi( y)
    fm.LipIntInfComputeLipschitz( pDim, pNdata, px, py)
    return 


# Python wrapper for:
#    void	LipIntInfComputeLocalLipschitz(int *Dim, int *Ndata, double* x, double* y)
def LipIntInfComputeLocalLipschitz(Dim, Ndata, x, y):
    """LipIntInfComputeLocalLipschitz

    Args:
        Dim (int):
        Ndata (int):
        x (float):
        y (float):

    Returns:
        <none>
    """
    trace( "void	LipIntInfComputeLocalLipschitz(int *Dim, int *Ndata, double* x, double* y)")
    pDimnp, pDim = convert_py_int_to_cffi( Dim)
    pNdatanp, pNdata = convert_py_int_to_cffi( Ndata)
    pxnp, px = convert_py_float_to_cffi( x)
    pynp, py = convert_py_float_to_cffi( y)
    fm.LipIntInfComputeLocalLipschitz( pDim, pNdata, px, py)
    return 


# Python wrapper for:
#    void	LipIntInfComputeLipschitzCV(int *Dim, int *Ndata, double* Xd, double* y, double* T, int* type, int* Cons, double* Region, double *W)
def LipIntInfComputeLipschitzCV(Dim, Ndata, Xd, y, T, type, Cons, Region, W):
    """LipIntInfComputeLipschitzCV

    Args:
        Dim (int):
        Ndata (int):
        Xd (float):
        y (float):
        T (float):
        type (int):
        Cons (int):
        Region (float):
        W (float):

    Returns:
        <none>
    """
    trace( "void	LipIntInfComputeLipschitzCV(int *Dim, int *Ndata, double* Xd, double* y, double* T, int* type, int* Cons, double* Region, double *W)")
    pDimnp, pDim = convert_py_int_to_cffi( Dim)
    pNdatanp, pNdata = convert_py_int_to_cffi( Ndata)
    pXdnp, pXd = convert_py_float_to_cffi( Xd)
    pynp, py = convert_py_float_to_cffi( y)
    pTnp, pT = convert_py_float_to_cffi( T)
    ptypenp, ptype = convert_py_int_to_cffi( type)
    pConsnp, pCons = convert_py_int_to_cffi( Cons)
    pRegionnp, pRegion = convert_py_float_to_cffi( Region)
    pWnp, pW = convert_py_float_to_cffi( W)
    fm.LipIntInfComputeLipschitzCV( pDim, pNdata, pXd, py, pT, ptype, pCons, pRegion, pW)
    return 


# Python wrapper for:
#    void	LipIntInfComputeLipschitzSplit(int *Dim, int *Ndata, double* Xd, double* y, double* T, double* ratio, int* type, int* Cons, double* Region, double *W)
def LipIntInfComputeLipschitzSplit(Dim, Ndata, Xd, y, T, ratio, type, Cons, Region, W):
    """LipIntInfComputeLipschitzSplit

    Args:
        Dim (int):
        Ndata (int):
        Xd (float):
        y (float):
        T (float):
        ratio (float):
        type (int):
        Cons (int):
        Region (float):
        W (float):

    Returns:
        <none>
    """
    trace( "void	LipIntInfComputeLipschitzSplit(int *Dim, int *Ndata, double* Xd, double* y, double* T, double* ratio, int* type, int* Cons, double* Region, double *W)")
    pDimnp, pDim = convert_py_int_to_cffi( Dim)
    pNdatanp, pNdata = convert_py_int_to_cffi( Ndata)
    pXdnp, pXd = convert_py_float_to_cffi( Xd)
    pynp, py = convert_py_float_to_cffi( y)
    pTnp, pT = convert_py_float_to_cffi( T)
    prationp, pratio = convert_py_float_to_cffi( ratio)
    ptypenp, ptype = convert_py_int_to_cffi( type)
    pConsnp, pCons = convert_py_int_to_cffi( Cons)
    pRegionnp, pRegion = convert_py_float_to_cffi( Region)
    pWnp, pW = convert_py_float_to_cffi( W)
    fm.LipIntInfComputeLipschitzSplit( pDim, pNdata, pXd, py, pT, pratio, ptype, pCons, pRegion, pW)
    return 


# Python wrapper for:
#    void	LipIntInfSmoothLipschitz(int *Dim, int *Ndata,  double* Xd, double* y, double* T,  double* LC,  int* fW, int* fC, int* fR, double* W, int* Cons, double* Region)
def LipIntInfSmoothLipschitz(Dim, Ndata, Xd, y, T, LC, fW, fC, fR, W, Cons, Region):
    """LipIntInfSmoothLipschitz

    Args:
        Dim (int):
        Ndata (int):
        Xd (float):
        y (float):
        T (float):
        LC (float):
        fW (int):
        fC (int):
        fR (int):
        W (float):
        Cons (int):
        Region (float):

    Returns:
        <none>
    """
    trace( "void	LipIntInfSmoothLipschitz(int *Dim, int *Ndata,  double* Xd, double* y, double* T,  double* LC,  int* fW, int* fC, int* fR, double* W, int* Cons, double* Region)")
    pDimnp, pDim = convert_py_int_to_cffi( Dim)
    pNdatanp, pNdata = convert_py_int_to_cffi( Ndata)
    pXdnp, pXd = convert_py_float_to_cffi( Xd)
    pynp, py = convert_py_float_to_cffi( y)
    pTnp, pT = convert_py_float_to_cffi( T)
    pLCnp, pLC = convert_py_float_to_cffi( LC)
    pfWnp, pfW = convert_py_int_to_cffi( fW)
    pfCnp, pfC = convert_py_int_to_cffi( fC)
    pfRnp, pfR = convert_py_int_to_cffi( fR)
    pWnp, pW = convert_py_float_to_cffi( W)
    pConsnp, pCons = convert_py_int_to_cffi( Cons)
    pRegionnp, pRegion = convert_py_float_to_cffi( Region)
    fm.LipIntInfSmoothLipschitz( pDim, pNdata, pXd, py, pT, pLC, pfW, pfC, pfR, pW, pCons, pRegion)
    return 


# Python wrapper for:
#    double	LipIntInfGetLipConst() 
def LipIntInfGetLipConst():
    """LipIntInfGetLipConst

    Args:

    Returns:
        (double):
    """
    trace( "double	LipIntInfGetLipConst() ")
    yy = fm.LipIntInfGetLipConst( )
    return yy


# Python wrapper for:
#    void	LipIntInfGetScaling(double *S) 
def LipIntInfGetScaling(S):
    """LipIntInfGetScaling

    Args:
        S (float):

    Returns:
        <none>
    """
    trace( "void	LipIntInfGetScaling(double *S) ")
    pSnp, pS = convert_py_float_to_cffi( S)
    fm.LipIntInfGetScaling( pS)
    return 


# Python wrapper for:
#    int		LipIntInfComputeScaling(int *Dim, int *Ndata, double* XData, double* YData)
def LipIntInfComputeScaling(Dim, Ndata, XData, YData):
    """LipIntInfComputeScaling

    Args:
        Dim (int):
        Ndata (int):
        XData (float):
        YData (float):

    Returns:
        (int):
    """
    trace( "int		LipIntInfComputeScaling(int *Dim, int *Ndata, double* XData, double* YData)")
    pDimnp, pDim = convert_py_int_to_cffi( Dim)
    pNdatanp, pNdata = convert_py_int_to_cffi( Ndata)
    pXDatanp, pXData = convert_py_float_to_cffi( XData)
    pYDatanp, pYData = convert_py_float_to_cffi( YData)
    yy = fm.LipIntInfComputeScaling( pDim, pNdata, pXData, pYData)
    return yy


# Python wrapper for:
#    int		LipIntInfVerifyMonotonicity(int *Dim, int* npts, int* Cons,  double* XData, double* YData, double LC, double ep)
def LipIntInfVerifyMonotonicity(Dim, npts, Cons, XData, YData, LC, ep):
    """LipIntInfVerifyMonotonicity

    Args:
        Dim (int):
        npts (int):
        Cons (int):
        XData (float):
        YData (float):
        LC (float):
        ep (float):

    Returns:
        (int):
    """
    trace( "int		LipIntInfVerifyMonotonicity(int *Dim, int* npts, int* Cons,  double* XData, double* YData, double LC, double ep)")
    pDimnp, pDim = convert_py_int_to_cffi( Dim)
    pnptsnp, pnpts = convert_py_int_to_cffi( npts)
    pConsnp, pCons = convert_py_int_to_cffi( Cons)
    pXDatanp, pXData = convert_py_float_to_cffi( XData)
    pYDatanp, pYData = convert_py_float_to_cffi( YData)
    yy = fm.LipIntInfVerifyMonotonicity( pDim, pnpts, pCons, pXData, pYData, LC, ep)
    return yy


# Python wrapper for:
#    int		LipIntInfVerifyMonotonicityLeftRegion(int *Dim, int npts, int* Cons,  double* XData, double* YData, double* Region, double* LC, double* eps)
def LipIntInfVerifyMonotonicityLeftRegion(Dim, npts, Cons, XData, YData, Region, LC, eps):
    """LipIntInfVerifyMonotonicityLeftRegion

    Args:
        Dim (int):
        npts (int):
        Cons (int):
        XData (float):
        YData (float):
        Region (float):
        LC (float):
        eps (float):

    Returns:
        (int):
    """
    trace( "int		LipIntInfVerifyMonotonicityLeftRegion(int *Dim, int npts, int* Cons,  double* XData, double* YData, double* Region, double* LC, double* eps)")
    pDimnp, pDim = convert_py_int_to_cffi( Dim)
    pConsnp, pCons = convert_py_int_to_cffi( Cons)
    pXDatanp, pXData = convert_py_float_to_cffi( XData)
    pYDatanp, pYData = convert_py_float_to_cffi( YData)
    pRegionnp, pRegion = convert_py_float_to_cffi( Region)
    pLCnp, pLC = convert_py_float_to_cffi( LC)
    pepsnp, peps = convert_py_float_to_cffi( eps)
    yy = fm.LipIntInfVerifyMonotonicityLeftRegion( pDim, npts, pCons, pXData, pYData, pRegion, pLC, peps)
    return yy


# Python wrapper for:
#    int		LipIntInfVerifyMonotonicityRightRegion(int *Dim, int npts, int* Cons,  double* XData, double* YData, double* Region, double* LC, double* eps)
def LipIntInfVerifyMonotonicityRightRegion(Dim, npts, Cons, XData, YData, Region, LC, eps):
    """LipIntInfVerifyMonotonicityRightRegion

    Args:
        Dim (int):
        npts (int):
        Cons (int):
        XData (float):
        YData (float):
        Region (float):
        LC (float):
        eps (float):

    Returns:
        (int):
    """
    trace( "int		LipIntInfVerifyMonotonicityRightRegion(int *Dim, int npts, int* Cons,  double* XData, double* YData, double* Region, double* LC, double* eps)")
    pDimnp, pDim = convert_py_int_to_cffi( Dim)
    pConsnp, pCons = convert_py_int_to_cffi( Cons)
    pXDatanp, pXData = convert_py_float_to_cffi( XData)
    pYDatanp, pYData = convert_py_float_to_cffi( YData)
    pRegionnp, pRegion = convert_py_float_to_cffi( Region)
    pLCnp, pLC = convert_py_float_to_cffi( LC)
    pepsnp, peps = convert_py_float_to_cffi( eps)
    yy = fm.LipIntInfVerifyMonotonicityRightRegion( pDim, npts, pCons, pXData, pYData, pRegion, pLC, peps)
    return yy


# Python wrapper for:
#    void	LipIntInfSmoothLipschitzSimp(int *Dim, int* npts,  double* XData, double* YData, double* TData,  double* LC)
def LipIntInfSmoothLipschitzSimp(Dim, npts, XData, YData, TData, LC):
    """LipIntInfSmoothLipschitzSimp

    Args:
        Dim (int):
        npts (int):
        XData (float):
        YData (float):
        TData (float):
        LC (float):

    Returns:
        <none>
    """
    trace( "void	LipIntInfSmoothLipschitzSimp(int *Dim, int* npts,  double* XData, double* YData, double* TData,  double* LC)")
    pDimnp, pDim = convert_py_int_to_cffi( Dim)
    pnptsnp, pnpts = convert_py_int_to_cffi( npts)
    pXDatanp, pXData = convert_py_float_to_cffi( XData)
    pYDatanp, pYData = convert_py_float_to_cffi( YData)
    pTDatanp, pTData = convert_py_float_to_cffi( TData)
    pLCnp, pLC = convert_py_float_to_cffi( LC)
    fm.LipIntInfSmoothLipschitzSimp( pDim, pnpts, pXData, pYData, pTData, pLC)
    return 


# Python wrapper for:
#    void	LipIntInfSmoothLipschitzSimpW(int *Dim, int* npts,  double* XData, double* YData, double* TData,  double* LC, double* W)
def LipIntInfSmoothLipschitzSimpW(Dim, npts, XData, YData, TData, LC, W):
    """LipIntInfSmoothLipschitzSimpW

    Args:
        Dim (int):
        npts (int):
        XData (float):
        YData (float):
        TData (float):
        LC (float):
        W (float):

    Returns:
        <none>
    """
    trace( "void	LipIntInfSmoothLipschitzSimpW(int *Dim, int* npts,  double* XData, double* YData, double* TData,  double* LC, double* W)")
    pDimnp, pDim = convert_py_int_to_cffi( Dim)
    pnptsnp, pnpts = convert_py_int_to_cffi( npts)
    pXDatanp, pXData = convert_py_float_to_cffi( XData)
    pYDatanp, pYData = convert_py_float_to_cffi( YData)
    pTDatanp, pTData = convert_py_float_to_cffi( TData)
    pLCnp, pLC = convert_py_float_to_cffi( LC)
    pWnp, pW = convert_py_float_to_cffi( W)
    fm.LipIntInfSmoothLipschitzSimpW( pDim, pnpts, pXData, pYData, pTData, pLC, pW)
    return 


# Python wrapper for:
#    int	STCBuildLipInterpolantExplicit(int *Dim, int *Ndata, double* x, double* y)
def STCBuildLipInterpolantExplicit(Dim, Ndata, x, y):
    """STCBuildLipInterpolantExplicit

    Args:
        Dim (int):
        Ndata (int):
        x (float):
        y (float):

    Returns:
        (int):
    """
    trace( "int	STCBuildLipInterpolantExplicit(int *Dim, int *Ndata, double* x, double* y)")
    pDimnp, pDim = convert_py_int_to_cffi( Dim)
    pNdatanp, pNdata = convert_py_int_to_cffi( Ndata)
    pxnp, px = convert_py_float_to_cffi( x)
    pynp, py = convert_py_float_to_cffi( y)
    yy = fm.STCBuildLipInterpolantExplicit( pDim, pNdata, px, py)
    return yy


# Python wrapper for:
#    int	STCBuildLipInterpolantColumn(int *Dim, int *Ndata, double* x, double* y)
def STCBuildLipInterpolantColumn(Dim, Ndata, x, y):
    """STCBuildLipInterpolantColumn

    Args:
        Dim (int):
        Ndata (int):
        x (float):
        y (float):

    Returns:
        (int):
    """
    trace( "int	STCBuildLipInterpolantColumn(int *Dim, int *Ndata, double* x, double* y)")
    pDimnp, pDim = convert_py_int_to_cffi( Dim)
    pNdatanp, pNdata = convert_py_int_to_cffi( Ndata)
    pxnp, px = convert_py_float_to_cffi( x)
    pynp, py = convert_py_float_to_cffi( y)
    yy = fm.STCBuildLipInterpolantColumn( pDim, pNdata, px, py)
    return yy


# Python wrapper for:
#    int	STCBuildLipInterpolantExplicitColumn(int *Dim, int *Ndata, double* x, double* y)
def STCBuildLipInterpolantExplicitColumn(Dim, Ndata, x, y):
    """STCBuildLipInterpolantExplicitColumn

    Args:
        Dim (int):
        Ndata (int):
        x (float):
        y (float):

    Returns:
        (int):
    """
    trace( "int	STCBuildLipInterpolantExplicitColumn(int *Dim, int *Ndata, double* x, double* y)")
    pDimnp, pDim = convert_py_int_to_cffi( Dim)
    pNdatanp, pNdata = convert_py_int_to_cffi( Ndata)
    pxnp, px = convert_py_float_to_cffi( x)
    pynp, py = convert_py_float_to_cffi( y)
    yy = fm.STCBuildLipInterpolantExplicitColumn( pDim, pNdata, px, py)
    return yy


# Python wrapper for:
#    double	STCValueExplicit( double* x )
def STCValueExplicit(x):
    """STCValueExplicit

    Args:
        x (float):

    Returns:
        (double):
    """
    trace( "double	STCValueExplicit( double* x )")
    pxnp, px = convert_py_float_to_cffi( x)
    yy = fm.STCValueExplicit( px)
    return yy


# Python wrapper for:
#    void	STCFreeMemory()
def STCFreeMemory():
    """STCFreeMemory

    Args:

    Returns:
        <none>
    """
    trace( "void	STCFreeMemory()")
    fm.STCFreeMemory( )
    return 


