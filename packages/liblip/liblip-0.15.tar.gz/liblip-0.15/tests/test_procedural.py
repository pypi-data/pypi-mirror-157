import liblip as ll
import sys
import math
import random

# Trace function
def trace( str):
    print( '######')
    print( "## ", str)
    print( '######')
    
# test function, here just a product of sin(2x)sin(2y),...
def fun2( dat, dim):
    s = 1.0
    for j in range( dim): s *= math.sin( 2 * dat[j])
    return s

# generate data randomly
def generate_random_data( dim, npts):
    x, XData, YData = ll.init( dim, npts)
    for i in range( npts):
        for j in range( dim):
            x[j] = random.random() * 3.0
            XData[i * dim + j] = x[j]
        YData[i] = fun2( x, dim)
    return x, XData, YData

###
# Initial test    
# ###  
def initial_test():
    trace( 'initial test: start')
    dim = 3
    npts = 1500
    lip_const = 10.0
    K2 = 100
           
    x, XData, YData = generate_random_data( dim, npts)

    ll.STCSetLipschitz( lip_const)
    ll.STCBuildLipInterpolant( dim, npts, XData, YData)

    err2 = 0
    err = 0
    for k in range( K2):
        for j in range( dim): x[j] = random.random() * 3.0 # randomly choose a test point
        w = ll.STCValue( x)
        w1 = fun2( x, dim) # the true function
        w = abs( w - w1) # compute the error
        if( err < w): err = w
        err2 += w * w    
    err2 = math.sqrt( err2 / K2) # average error RMSE
    print( "Interpolation max error: ",err)
    print( "Average error: ", err2)
    trace( 'initial test: end')

###
# example of usage of SLipInt class
###
def test_slip_int():
    trace( 'example of usage of SLipInt class: start')

    dim=4        # the dimension and size of the data set
    npts=1000
    LipConst=4
    x, XData, YData = generate_random_data( dim, npts)

    for j in range( dim): x[j]=random.random() * 3.0 # some random x
    # calculate the value
    index = [0] * npts
    w = ll.LipIntValue( dim,npts,x,XData, YData,LipConst,index)

    # estimate Lipschitz constant
    ll.LipIntComputeLipschitz(dim,npts,XData, YData)
    # uses the computed Lipschitz constant
    w = ll.LipIntValue(dim,npts,x,XData, YData,LipConst,index)
    print( "w: ", w)
    # the same using local Lipschitz constants  
    ll.LipIntComputeLocalLipschitz(dim,npts,XData, YData)
    # calculate the value
    w = ll.LipIntValueLocal(dim,npts,x,XData, YData)
    print( "w: ", w)
    trace( 'example of usage of SLipInt class: end')

###
# example of usage of SLipInt class for monotone interpolation
###
def test_slip_int_for_monotone_interpolation():
    trace( 'example of usage of SLipInt class for monotone interpolation: start')
    dim=4       # the dimension and size of the data set
    npts=1000
    LipConst=4
    x, XData, YData = generate_random_data( dim, npts)    
    Region = [1.5] * dim
    # function monotone incr. wrt first variable
    # function monotone decr. wrt first variable
    # unrestricted wrt other variables
    Cons = [0, -1, 0 ,0]

    # calculate the value
    w = ll.LipIntValueCons(dim,npts,Cons,x,XData, YData,LipConst, None)
    print( "w: ", w)
    # assume monotonicity for x<<Region only
    w = ll.LipIntValueConsLeftRegion(dim,npts,Cons,x,XData, YData, LipConst, Region, None)
    print( "w: ", w)
    ll.LipIntComputeLocalLipschitz(dim,npts,XData, YData)
    w = ll.LipIntValueLocalCons(dim,npts,Cons,x,XData, YData)
    print( "w: ", w)
    w = ll.LipIntValueLocalConsLeftRegion(dim,npts,Cons,x,XData, YData,Region)
    print( "w: ", w)
    trace( 'example of usage of SLipInt class for monotone interpolation: end')

###
# example of usage of SLipInt class with extra bounds
###
def test_slip_int_with_extra_bounds():
    trace( 'example of usage of SLipInt class with extra bounds: start')
    dim=4        # the dimension and size of the data set
    npts=1000
    LipConst=4

    # arrays to store the data
    x, XData, YData = generate_random_data( dim, npts)   
    # calculate the value
    w = ll.LipIntValue(dim,npts,x,XData, YData, LipConst, None)
    print( "w: ", w)
    # estimate Lipschitz constant
    ll.LipIntComputeLipschitz(dim,npts,XData, YData)
    # uses the computed Lipschitz constant
    w = ll.LipIntValue(dim,npts,x,XData, YData, LipConst, None)
    print( "w: ", w)
    trace( 'example of usage of SLipInt class with extra bounds: end')

###
# example of usage of STCInterpolant class
###
def test_STCInterpolant():
    trace( 'example of usage of STCInterpolant class: start')
    dim=4             # the dimension and size of the data set
    npts=1000

    # arrays to store the data
    x, XData, YData = generate_random_data( dim, npts)  
    # supply the data and eliminate repeated values
    ll.LipIntSetData(dim,npts, XData,YData,1)
    LipConst = ll.LipIntDetermineLipschitz()
    ll.LipIntSetConstants()  # supply Lipschitz constant
    ll.LipIntConstruct()     # construct the interpolant
    x1 = [0] * 10  # reserve space for at least dim+1 components
    w=ll.LipIntValue(dim,x1) # calculate the value
    print( "w: ", w)
    # alternatively, pre-compute the slack variable
    s = 0
    for j in range( 0, dim): s += x1[j]
    x1[dim] = 1.0-s
    w=ll.LipIntValue(dim+1,x1, None)         # calculate the value
    print( "w: ", w)
    w=ll.LipIntValueExplicit(dim+1,x1, None) # same using explicit method
    print( "w: ", w)
    ll.LipIntFreeMemory()  # destroys the interpolant
    trace( 'example of usage of STCInterpolant class: end')


###
# example using procedural interface
###
def test_procedural_interface():
    trace( 'using using procedural interface: start')
    dim=4             # the dimension and the data set
    npts=1000

    # arrays to store the data
    LipConst = 10.0
    # arrays to store the data
    x, XData, YData = generate_random_data( dim, npts)

    # compute the Lipschitz constant in max-norm
    ll.LipIntInfComputeLipschitz( dim, npts, XData, YData)
    # calculate the value
    w=ll.LipIntInfValue( dim, npts,x,XData, YData, LipConst, None)
    print( "w: ", w)
    # the same in Euclidean norm, but using local Lipschitz values
    ll.LipIntComputeLocalLipschitz( dim, npts, XData, YData)
    # calculate the value
    w=ll.LipIntValueLocal( dim, npts,x,XData, YData)
    print( "w: ", w)
    # now using fast method and simplicial distance
    ll.STCSetLipschitz( LipConst)  # supply Lipschitz constant
    # suppy the data
    ll.STCBuildllLipInterpolant( dim, npts, XData, YData)
    w=ll.STCValue(x) # calculate the value
    print( "w: ", w)
    trace( 'using using procedural interface: end')


###
# example for smoothing
###
def test_smoothing():
    trace( 'example for smoothing: start')
    dim=4        # the dimension and size of the data set
    npts=200
    LipConst=4.0
   
    # arrays to store the data
    x, XData, YData = generate_random_data( dim, npts)
    TData = [0.0] * npts
    for i in range( 0, npts): 
        YData[i] = fun2( x, dim)+ 0.1 * ( random.random() - 1)  # noisy function values
    ll.LipIntSmoothLipschitz(dim, npts,XData,YData,TData,LipConst, None, None, None, None, None, None)
    # other possibilities:
    #  ll.LipInt.SmoothLipschitzCons(dim, npts,Cons, XData,YData,TData,LipConst)
    #  ll.LipInt.SmoothLipschitzW(dim, npts,XData,YData,TData,LipConst,W)
    #  ll.LipInt.ComputeLipschitzCV(dim, npts,XData,YData,TData)
    #  etc...
   
    # calculate the approximation at x
    w = ll.LipIntValue(dim,npts,x,XData, TData, LipConst, None)
    print( "w: ", w)
    # prepare data for the fast method using simplicial distance
    ll.LipIntInfSmoothLipschitzSimp(dim, npts,XData,YData,TData,LipConst)
    ll.STCLipIntSetData(dim,npts, XData,TData)
    ll.STCLipIntSetConstants(LipConst)  # supply Lipschitz constant
    ll.STCLipIntConstruct()     # construct the interpolant
    x1 = [0.0] * 10  # reserve space for at least dim+1 components
    for j in range( 0, dim): x1[j] = random.random() * 3.0 # some random x
    w = ll.STCLipIntValue(dim,x1) # calculate the value
    print( "w: ", w)
    trace( 'example for smoothing: end')

###
# example of usage of STCInterpolant class and smoothened data
###
def test_STCInterpolant_smoothened_data():
    trace( 'example of usage of STCInterpolant class and smoothened data: start')
    dim=3             # the dimension and size of the data set
    npts=1000
    LipConst=2.5
   
    # arrays to store the data
    x, XData, YData = generate_random_data( dim, npts)
    TData = [0.0] * npts

    # smoothen the data
    ll.LipIntInfSmoothLipschitzSimp(dim,npts,XData,YData,TData,LipConst)
    # supply the smoothened data (TData, not YData)
    # ll.LipIntSetData(dim,npts, XData,TData,0)
    ll.LipIntSetConstants(LipConst)  # supply Lipschitz constant
    ll.LipIntConstruct()          # construct the interpolant
    x1 = [0.0] * 10  # reserve space for at least dim+1 components
    for j in range( 0, dim): random.random() * 3.0 # some random x
    w = ll.LipIntValue(dim,x1) # calculate the value
    print( "w: ", w)
    # alternatively, pre-compute the slack variable
    s = 0
    for j in range( 0, dim): s += x1[j] 
    x1[dim] = 1.0 - s
    w = ll.LipIntValue(dim+1,x1)         # calculate the value
    print( "w: ", w)
    ll.LipIntFreeMemory()  # destroys the interpolant
    trace( 'example of usage of STCInterpolant class and smoothened data: end')

###
# Main test program
###
initial_test()
test_slip_int()
test_slip_int_for_monotone_interpolation()
test_slip_int_with_extra_bounds()
# test_STCInterpolant()
# test_procedural_interface()
# test_smoothing()
# test_STCInterpolant_smoothened_data()



# Test wrapper for:
#    double	LipIntValue(int* Dim, int* Ndata, double* x, double* Xd,double* y,  double* Lipconst, int* Index)
# ll.LipIntValue(Dim, Ndata, x, Xd, y, Lipconst, Index)


# Test wrapper for:
#    double	LipIntValueAuto(int* Dim, int* Ndata, double* x,double* Xd, double* y, int* Index)
# ll.LipIntValueAuto(Dim, Ndata, x, Xd, y, Index)


# Test wrapper for:
#    double	LipIntValueCons(int* Dim, int* Ndata, int* Cons, double* x, double* Xd,double* y,  double* Lipconst, int* Index)
# ll.LipIntValueCons(Dim, Ndata, Cons, x, Xd, y, Lipconst, Index)


# Test wrapper for:
#    double	LipIntValueConsLeftRegion(int* Dim, int* Ndata, int* Cons, double* x, double* Xd,double* y,  double* Lipconst, double* Region, int* Index)
# ll.LipIntValueConsLeftRegion(Dim, Ndata, Cons, x, Xd, y, Lipconst, Region, Index)


# Test wrapper for:
#    double	LipIntValueConsRightRegion(int* Dim, int* Ndata, int* Cons, double* x, double* Xd,double* y,  double* Lipconst, double* Region, int* Index)
# ll.LipIntValueConsRightRegion(Dim, Ndata, Cons, x, Xd, y, Lipconst, Region, Index)


# Test wrapper for:
#    double	LipIntValueLocal(int *Dim, int *Ndata, double* x, double* Xd,double* y)
# ll.LipIntValueLocal(Dim, Ndata, x, Xd, y)


# Test wrapper for:
#    double	LipIntValueLocalCons(int *Dim, int *Ndata,int* Cons, double* x, double* Xd,double* y)
# ll.LipIntValueLocalCons(Dim, Ndata, Cons, x, Xd, y)


# Test wrapper for:
#    double	LipIntValueLocalConsLeftRegion(int *Dim, int *Ndata,int* Cons, double* x, double* Xd,double* y, double* Region)
# ll.LipIntValueLocalConsLeftRegion(Dim, Ndata, Cons, x, Xd, y, Region)


# Test wrapper for:
#    double	LipIntValueLocalConsRightRegion(int *Dim, int *Ndata,int* Cons, double* x, double* Xd,double* y, double* Region)
# ll.LipIntValueLocalConsRightRegion(Dim, Ndata, Cons, x, Xd, y, Region)


# Test wrapper for:
#    void	LipIntComputeLipschitz(int *Dim, int *Ndata, double* x, double* y)
# ll.LipIntComputeLipschitz(Dim, Ndata, x, y)


# Test wrapper for:
#    void 	LipIntComputeLocalLipschitz(int *Dim, int *Ndata, double* x, double* y)
# ll.LipIntComputeLocalLipschitz(Dim, Ndata, x, y)


# Test wrapper for:
#    void	LipIntComputeLipschitzCV(int *Dim, int *Ndata, double* Xd, double* y, double* T, int* type, int* Cons, double* Region, double *W)
# ll.LipIntComputeLipschitzCV(Dim, Ndata, Xd, y, T, type, Cons, Region, W)


# Test wrapper for:
#    void	LipIntComputeLipschitzSplit(int *Dim, int *Ndata, double* Xd, double* y, double* T, double* ratio,int* type, int* Cons, double* Region, double *W)
# ll.LipIntComputeLipschitzSplit(Dim, Ndata, Xd, y, T, ratio, type, Cons, Region, W)


# Test wrapper for:
#    void	LipIntSmoothLipschitz(int *Dim, int *Ndata,  double* Xd, double* y, double* T,  double* LC, int* fW, int* fC, int* fR, double* W, int* Cons, double* Region)
# ll.LipIntSmoothLipschitz(Dim, Ndata, Xd, y, T, LC, fW, fC, fR, W, Cons, Region)


# Test wrapper for:
#    double	LipIntGetLipConst() 
# ll.LipIntGetLipConst()


# Test wrapper for:
#    void		LipIntGetScaling(double *S) 
# ll.LipIntGetScaling(S)


# Test wrapper for:
#    int		LipIntComputeScaling(int *Dim, int *Ndata, double* XData, double* YData)
# ll.LipIntComputeScaling(Dim, Ndata, XData, YData)


# Test wrapper for:
#    void	ConvertXData(int *Dim, int* npts,  double* XData)
# ll.ConvertXData(Dim, npts, XData)


# Test wrapper for:
#    void	ConvertXDataAUX(int *Dim, int* npts,  double* XData, double *auxdata)
# ll.ConvertXDataAUX(Dim, npts, XData, auxdata)


# Test wrapper for:
#    int		LipIntVerifyMonotonicity(int *Dim, int* npts, int* Cons,  double* XData, double* YData, double* LC, double* eps)
# ll.LipIntVerifyMonotonicity(Dim, npts, Cons, XData, YData, LC, eps)


# Test wrapper for:
#    int		LipIntVerifyMonotonicityLeftRegion(int *Dim, int* npts, int* Cons,  double* XData, double* YData, double* Region, double* LC, double* eps)
# ll.LipIntVerifyMonotonicityLeftRegion(Dim, npts, Cons, XData, YData, Region, LC, eps)


# Test wrapper for:
#    int		LipIntVerifyMonotonicityRightRegion(int *Dim, int* npts, int* Cons,  double* XData, double* YData, double* Region, double* LC, double* eps)
# ll.LipIntVerifyMonotonicityRightRegion(Dim, npts, Cons, XData, YData, Region, LC, eps)


# Test wrapper for:
#    double	LipIntInfValue(int *Dim, int *Ndata, double* x, double* Xd,double* y,  double* Lipconst, int* Index)
# ll.LipIntInfValue(Dim, Ndata, x, Xd, y, Lipconst, Index)


# Test wrapper for:
#    double	LipIntInfValueAuto(int *Dim, int *Ndata, double* x,double* Xd, double* y, int* Index)
# ll.LipIntInfValueAuto(Dim, Ndata, x, Xd, y, Index)


# Test wrapper for:
#    double	LipIntInfValueCons(int *Dim, int *Ndata, int* Cons, double* x, double* Xd,double* y,  double Lipconst, int* Index)
# ll.LipIntInfValueCons(Dim, Ndata, Cons, x, Xd, y, Lipconst, Index)


# Test wrapper for:
#    double	LipIntInfValueConsLeftRegion(int *Dim, int *Ndata, int* Cons, double* x, double* Xd,double* y,  double* Lipconst, double* Region, int* Index)
# ll.LipIntInfValueConsLeftRegion(Dim, Ndata, Cons, x, Xd, y, Lipconst, Region, Index)


# Test wrapper for:
#    double	LipIntInfValueConsRightRegion(int *Dim, int *Ndata, int* Cons, double* x, double* Xd,double* y,  double* Lipconst, double* Region, int* Index)
# ll.LipIntInfValueConsRightRegion(Dim, Ndata, Cons, x, Xd, y, Lipconst, Region, Index)


# Test wrapper for:
#    double	LipIntInfValueLocal(int *Dim, int *Ndata, double* x, double* Xd,double* y)
# ll.LipIntInfValueLocal(Dim, Ndata, x, Xd, y)


# Test wrapper for:
#    double	LipIntInfValueLocalCons(int *Dim, int *Ndata,int* Cons, double* x, double* Xd,double* y)
# ll.LipIntInfValueLocalCons(Dim, Ndata, Cons, x, Xd, y)


# Test wrapper for:
#    double	LipIntInfValueLocalConsLeftRegion(int *Dim, int *Ndata,int* Cons, double* x, double* Xd,double* y, double* Region)
# ll.LipIntInfValueLocalConsLeftRegion(Dim, Ndata, Cons, x, Xd, y, Region)


# Test wrapper for:
#    double	LipIntInfValueLocalConsRightRegion(int *Dim, int *Ndata,int* Cons, double* x, double* Xd,double* y, double* Region)
# ll.LipIntInfValueLocalConsRightRegion(Dim, Ndata, Cons, x, Xd, y, Region)


# Test wrapper for:
#    void	LipIntInfComputeLipschitz(int *Dim, int *Ndata, double* x, double* y)
# ll.LipIntInfComputeLipschitz(Dim, Ndata, x, y)


# Test wrapper for:
#    void	LipIntInfComputeLocalLipschitz(int *Dim, int *Ndata, double* x, double* y)
# ll.LipIntInfComputeLocalLipschitz(Dim, Ndata, x, y)


# Test wrapper for:
#    void	LipIntInfComputeLipschitzCV(int *Dim, int *Ndata, double* Xd, double* y, double* T, int* type, int* Cons, double* Region, double *W)
# ll.LipIntInfComputeLipschitzCV(Dim, Ndata, Xd, y, T, type, Cons, Region, W)


# Test wrapper for:
#    void	LipIntInfComputeLipschitzSplit(int *Dim, int *Ndata, double* Xd, double* y, double* T, double* ratio, int* type, int* Cons, double* Region, double *W)
# ll.LipIntInfComputeLipschitzSplit(Dim, Ndata, Xd, y, T, ratio, type, Cons, Region, W)


# Test wrapper for:
#    void	LipIntInfSmoothLipschitz(int *Dim, int *Ndata,  double* Xd, double* y, double* T,  double* LC,  int* fW, int* fC, int* fR, double* W, int* Cons, double* Region)
# ll.LipIntInfSmoothLipschitz(Dim, Ndata, Xd, y, T, LC, fW, fC, fR, W, Cons, Region)


# Test wrapper for:
#    double	LipIntInfGetLipConst() 
# ll.LipIntInfGetLipConst()


# Test wrapper for:
#    void	LipIntInfGetScaling(double *S) 
# ll.LipIntInfGetScaling(S)


# Test wrapper for:
#    int		LipIntInfComputeScaling(int *Dim, int *Ndata, double* XData, double* YData)
# ll.LipIntInfComputeScaling(Dim, Ndata, XData, YData)


# Test wrapper for:
#    int		LipIntInfVerifyMonotonicity(int *Dim, int* npts, int* Cons,  double* XData, double* YData, double LC, double ep)
# ll.LipIntInfVerifyMonotonicity(Dim, npts, Cons, XData, YData, LC, ep)


# Test wrapper for:
#    int		LipIntInfVerifyMonotonicityLeftRegion(int *Dim, int npts, int* Cons,  double* XData, double* YData, double* Region, double* LC, double* eps)
# ll.LipIntInfVerifyMonotonicityLeftRegion(Dim, npts, Cons, XData, YData, Region, LC, eps)


# Test wrapper for:
#    int		LipIntInfVerifyMonotonicityRightRegion(int *Dim, int npts, int* Cons,  double* XData, double* YData, double* Region, double* LC, double* eps)
# ll.LipIntInfVerifyMonotonicityRightRegion(Dim, npts, Cons, XData, YData, Region, LC, eps)


# Test wrapper for:
#    void	LipIntInfSmoothLipschitzSimp(int *Dim, int* npts,  double* XData, double* YData, double* TData,  double* LC)
# ll.LipIntInfSmoothLipschitzSimp(Dim, npts, XData, YData, TData, LC)


# Test wrapper for:
#    void	LipIntInfSmoothLipschitzSimpW(int *Dim, int* npts,  double* XData, double* YData, double* TData,  double* LC, double* W)
# ll.LipIntInfSmoothLipschitzSimpW(Dim, npts, XData, YData, TData, LC, W)


# Test wrapper for:
#    int	STCBuildLipInterpolantExplicit(int *Dim, int *Ndata, double* x, double* y)
# ll.STCBuildLipInterpolantExplicit(Dim, Ndata, x, y)


# Test wrapper for:
#    int	STCBuildLipInterpolantColumn(int *Dim, int *Ndata, double* x, double* y)
# ll.STCBuildLipInterpolantColumn(Dim, Ndata, x, y)


# Test wrapper for:
#    int	STCBuildLipInterpolantExplicitColumn(int *Dim, int *Ndata, double* x, double* y)
# ll.STCBuildLipInterpolantExplicitColumn(Dim, Ndata, x, y)


# Test wrapper for:
#    double	STCValueExplicit( double* x )
# ll.STCValueExplicit(x)


# Test wrapper for:
#    void	STCFreeMemory()
# ll.STCFreeMemory()


print( "-- test procedural end --")