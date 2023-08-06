/**************************************************************************

 ***************************************************************************/

//#include "liblip.h"
//#include "dliblip.h"

#include "liblipc.h"

// global variables

// an instance of the interpolant class
STCInterpolant		gl;

// simple Lipschitz interpolant
SLipInt					sli;
// simple Lipschitz interpolant
SLipIntInf				slii;

// Lipschitz constant (not yet set)
double	GlobalLip=0;

#define LIBEXP extern "C"

LIBEXP void	STCSetLipschitz(real* x) {GlobalLip=*x;}

LIBEXP int	STCBuildLipInterpolant(int* Dim, int* Ndata, double* x, double* y)
{
	gl.SetData(*Dim,*Ndata,x,y);

	// Lipschitz constants live here
	if(GlobalLip<=0) {
		gl.DetermineLipschitz();
		gl.SetConstants();			// automatic
	} else
		gl.SetConstants(GlobalLip,*Dim+1);  // if it was specified

	gl.Construct();

	return gl.LastError();
//	if(gl.LastError()==ERR_LIP_LOW) cout << "Lipschitz const low or data coincide" << endl;
}

LIBEXP int	STCBuildLipInterpolantExplicit(int* Dim, int* Ndata,  double* x, double* y)
{
	gl.SetData(*Dim,*Ndata,x,y);

	// Lipschitz constants live here
	if(GlobalLip<=0) {
		gl.DetermineLipschitz();
		gl.SetConstants();			// automatic, but slow
	} else
		gl.SetConstants(GlobalLip,*Dim+1);

	gl.ConstructExplicit();

	return gl.LastError();

//	if(gl.LastError()==ERR_LIP_LOW) cout << "Lipschitz const low or data coincide" << endl;
}

// the methods below are identical to the above, but use columnwise storage of matrices
LIBEXP int	STCBuildLipInterpolantColumn(int* Dim, int* Ndata, double* x, double* y)
{
	gl.SetDataColumn(*Dim,*Ndata,x,y);

	// Lipschitz constants live here
	if(GlobalLip<=0) {
		gl.DetermineLipschitz();
		gl.SetConstants();			// automatic
	} else
		gl.SetConstants(GlobalLip,*Dim+1);  // if it was specified

	gl.Construct();

	return gl.LastError();
//	if(gl.LastError()==ERR_LIP_LOW) cout << "Lipschitz const low or data coincide" << endl;
}

LIBEXP int	STCBuildLipInterpolantExplicitColumn(int* Dim, int* Ndata,  double* x, double* y)
{
	gl.SetDataColumn(*Dim,*Ndata,x,y);

	// Lipschitz constants live here
	if(GlobalLip<=0) {
		gl.DetermineLipschitz();
		gl.SetConstants();			// automatic, but slow
	} else
		gl.SetConstants(GlobalLip,*Dim+1);

	gl.ConstructExplicit();

	return gl.LastError();

//	if(gl.LastError()==ERR_LIP_LOW) cout << "Lipschitz const low or data coincide" << endl;
}


LIBEXP  double	STCValue( double* x )
{
	return gl.Value(gl.Dim-1,x); // need to compute the slack variable
}

LIBEXP  double	STCValueExplicit( double* x )
{
	return gl.ValueExplicit(gl.Dim-1,x);
}


LIBEXP  void	STCFreeMemory() {gl.FreeMemory();}




/*--------------------------------------------------------*/
/* interface to the members of SLipInt class */
LIBEXP double	LipIntValue(int *Dim, int *Ndata, double* x, double* Xd,double* y,  double* Lipconst, int* Index)
{ return sli.Value(*Dim, *Ndata, x, Xd, y, *Lipconst, Index); }

LIBEXP double	LipIntValueAuto(int *Dim, int *Ndata, double* x,double* Xd, double* y, int* Index)
{ return sli.Value(*Dim, *Ndata, x, Xd,y, Index); }

LIBEXP double	LipIntValueCons(int* Dim, int* Ndata, int* Cons, double* x, double* Xd,double* y,  double* Lipconst, int* Index)
{ return sli.ValueCons(*Dim, *Ndata, Cons, x, Xd, y, *Lipconst, Index); }

LIBEXP double	LipIntValueConsLeftRegion(int* Dim, int* Ndata, int* Cons, double* x, double* Xd,double* y,  double* Lipconst, double* Region, int* Index)
{ return sli.ValueConsLeftRegion(*Dim, *Ndata, Cons, x, Xd, y, *Lipconst, Region, Index); }

LIBEXP double	LipIntValueConsRightRegion(int* Dim, int* Ndata, int* Cons, double* x, double* Xd,double* y,  double* Lipconst, double* Region, int* Index)
{ return sli.ValueConsRightRegion(*Dim, *Ndata, Cons, x, Xd, y, *Lipconst, Region, Index); }


LIBEXP double	LipIntValueLocal(int* Dim, int* Ndata, double* x, double* Xd,double* y)
{ return sli.ValueLocal(*Dim, *Ndata, x, Xd,y); }

LIBEXP double	LipIntValueLocalCons(int* Dim, int* Ndata,int* Cons, double* x, double* Xd,double* y)
{ return sli.ValueLocalCons(*Dim, *Ndata, Cons, x, Xd,y); }

LIBEXP double	LipIntValueLocalConsLeftRegion(int* Dim, int* Ndata,int* Cons, double* x, double* Xd,double* y, double* Region)
{ return sli.ValueLocalConsLeftRegion(*Dim, *Ndata, Cons, x, Xd,y,Region); }

LIBEXP double	LipIntValueLocalConsRightRegion(int* Dim, int* Ndata,int* Cons, double* x, double* Xd,double* y, double* Region)
{ return sli.ValueLocalConsRightRegion(*Dim, *Ndata, Cons, x, Xd,y,Region); }


LIBEXP void	LipIntComputeLipschitz(int* Dim, int* Ndata, double* x, double* y)
{  sli.ComputeLipschitz(*Dim, *Ndata, x, y); }

LIBEXP void	LipIntComputeLocalLipschitz(int* Dim, int* Ndata, double* x, double* y)
{ sli.ComputeLocalLipschitz(*Dim, *Ndata, x, y);}

LIBEXP void	LipIntComputeLipschitzCV(int* Dim, int* Ndata, double* Xd, double* y, double* T,
			int* type, int* Cons, double* Region, double *W)
{	sli.ComputeLipschitzCV(*Dim,  *Ndata, Xd,  y,  T, *type,  Cons,  Region,  W); }

LIBEXP void	LipIntComputeLipschitzSplit(int* Dim, int* Ndata, double* Xd, double* y, double* T, double* ratio,
			int* type, int* Cons, double* Region, double *W)
{	sli.ComputeLipschitzSplit(*Dim,  *Ndata, Xd,  y,  T, *ratio, *type,  Cons,  Region,  W); }


LIBEXP void	LipIntSmoothLipschitz(int* Dim, int* Ndata,  double* Xd, double* y, double* T,  double* LC, 
							  int* fW, int* fC, int* fR, double* W, int* Cons, double* Region)
{ // fR is 0, 1-left, 2-right
	sli.SmoothLipschitz2internal(*Dim,*Ndata,Xd,  y,  T, 0,*fW, *fC, LC,  W, Cons, *fR, Region);
}


LIBEXP double	LipIntGetLipConst() 
{ return sli.MaxLipConst; }

LIBEXP void	LipIntGetScaling(double *S) 
{	int i;
	for(i=0;i<sli.NPTS;i++) 
	S[i]=sli.Scaling[i]; 
}


LIBEXP int		LipIntComputeScaling(int* Dim, int* Ndata, double* XData, double* YData)
{	return sli.ComputeScaling(*Dim, *Ndata, XData,YData); }



LIBEXP void	ConvertXData(int* dim, int* npts,  double* XData)
{    sli.ConvertXData(*dim, *npts, XData); }

LIBEXP void	ConvertXDataAUX(int* dim, int* npts,  double* XData, double *auxdata)
{    sli.ConvertXData(*dim, *npts, XData,auxdata); }

LIBEXP int		LipIntVerifyMonotonicity(int* dim, int* npts, int* Cons,  double* XData, double* YData, double* LC, double* eps)
{	return sli.VerifyMonotonicity(*dim,*npts,Cons,XData,YData,*LC,*eps); }

LIBEXP int		LipIntVerifyMonotonicityLeftRegion(int* dim, int* npts, int* Cons,  double* XData, double* YData, double* Region, double* LC, double* eps)
{	return sli.VerifyMonotonicityLeftRegion(*dim,*npts,Cons,XData,YData,Region,*LC,*eps); }

LIBEXP int		LipIntVerifyMonotonicityRightRegion(int* dim, int* npts, int* Cons,  double* XData, double* YData, double* Region, double* LC, double* eps)
{	return sli.VerifyMonotonicityRightRegion(*dim,*npts,Cons,XData,YData,Region,*LC,*eps); }




/* interface to the members of SLipIntInf class ====================================== */
LIBEXP double	LipIntInfValue(int* Dim, int* Ndata, double* x, double* Xd,double* y,  double* Lipconst, int* Index)
{ return slii.Value(*Dim, *Ndata, x, Xd, y, *Lipconst, Index); }

LIBEXP double	LipIntInfValueAuto(int* Dim, int* Ndata, double* x,double* Xd, double* y, int* Index)
{ return slii.Value(*Dim, *Ndata, x, Xd,y, Index); }

LIBEXP double	LipIntInfValueCons(int* Dim, int* Ndata, int* Cons, double* x, double* Xd,double* y,  double* Lipconst, int* Index)
{ return slii.ValueCons(*Dim, *Ndata, Cons, x, Xd, y, *Lipconst, Index); }

LIBEXP double	LipIntInfValueConsLeftRegion(int* Dim, int* Ndata, int* Cons, double* x, double* Xd,double* y,  double* Lipconst, double* Region, int* Index)
{ return sli.ValueConsLeftRegion(*Dim, *Ndata, Cons, x, Xd, y, *Lipconst, Region, Index); }

LIBEXP double	LipIntInfValueConsRightRegion(int* Dim, int* Ndata, int* Cons, double* x, double* Xd,double* y,  double* Lipconst, double* Region, int* Index)
{ return slii.ValueConsRightRegion(*Dim, *Ndata, Cons, x, Xd, y, *Lipconst, Region, Index); }


LIBEXP double	LipIntInfValueLocal(int* Dim, int* Ndata, double* x, double* Xd,double* y)
{ return slii.ValueLocal(*Dim, *Ndata, x, Xd,y); }

LIBEXP double	LipIntInfValueLocalCons(int *Dim, int* Ndata,int* Cons, double* x, double* Xd,double* y)
{ return slii.ValueLocalCons(*Dim, *Ndata, Cons, x, Xd,y); }

LIBEXP double	LipIntInfValueLocalConsLeftRegion(int* Dim, int* Ndata,int* Cons, double* x, double* Xd,double* y, double* Region)
{ return slii.ValueLocalConsLeftRegion(*Dim, *Ndata, Cons, x, Xd,y,Region); }

LIBEXP double	LipIntInfValueLocalConsRightRegion(int* Dim, int* Ndata,int* Cons, double* x, double* Xd,double* y, double* Region)
{ return slii.ValueLocalConsRightRegion(*Dim, *Ndata, Cons, x, Xd,y,Region); }


LIBEXP void	LipIntInfComputeLipschitz(int* Dim, int* Ndata, double* x, double* y)
{  slii.ComputeLipschitz(*Dim, *Ndata, x, y); }

LIBEXP void	LipIntInfComputeLocalLipschitz(int* Dim, int* Ndata, double* x, double* y)
{ slii.ComputeLocalLipschitz(*Dim, *Ndata, x, y);}

LIBEXP void	LipIntInfComputeLipschitzCV(int* Dim, int* Ndata, double* Xd, double* y, double* T,
			int* type, int* Cons, double* Region, double *W)
{	slii.ComputeLipschitzCV(*Dim,  *Ndata, Xd,  y,  T, *type,  Cons,  Region,  W); }

LIBEXP void	LipIntInfComputeLipschitzSplit(int* Dim, int* Ndata, double* Xd, double* y, double* T, double* ratio,
			int* type, int* Cons, double* Region, double *W)
{	slii.ComputeLipschitzSplit(*Dim,  *Ndata, Xd,  y,  T, *ratio, *type,  Cons,  Region,  W); }


LIBEXP void	LipIntInfSmoothLipschitz(int* Dim, int* Ndata,  double* Xd, double* y, double* T,  double* LC, 
							  int* fW, int* fC, int* fR, double* W, int* Cons, double* Region)
{ // fR is 0, 1-left, 2-right
	slii.SmoothLipschitz2internal(*Dim,*Ndata,Xd,  y,  T, 0,*fW, *fC, LC,  W, Cons, *fR, Region);
}


LIBEXP double	LipIntInfGetLipConst() 
{ return slii.MaxLipConst; }

LIBEXP void	LipIntInfGetScaling(double *S) 
{	int i;
	for(i=0;i<sli.NPTS;i++) 
	S[i]=slii.Scaling[i]; 
}


LIBEXP int		LipIntInfComputeScaling(int* Dim, int* Ndata, double* XData, double* YData)
{	return slii.ComputeScaling(*Dim, *Ndata, XData,YData); }


LIBEXP int		LipIntInfVerifyMonotonicity(int* dim, int* npts, int* Cons,  double* XData, double* YData, double* LC, double* eps)
{	return slii.VerifyMonotonicity(*dim,*npts,Cons,XData,YData,*LC,*eps); }

LIBEXP int		LipIntInfVerifyMonotonicityLeftRegion(int* dim, int* npts, int* Cons,  double* XData, double* YData, double* Region, double* LC, double* eps)
{	return slii.VerifyMonotonicityLeftRegion(*dim,*npts,Cons,XData,YData,Region,*LC,*eps); }

LIBEXP int		LipIntInfVerifyMonotonicityRightRegion(int* dim, int* npts, int* Cons,  double* XData, double* YData, double* Region, double* LC, double* eps)
{	return slii.VerifyMonotonicityRightRegion(*dim,*npts,Cons,XData,YData,Region,*LC,*eps); }


LIBEXP void	LipIntInfSmoothLipschitzSimp(int* dim, int* npts,  double* XData, double* YData, double* TData,  double* LC)
{	slii.SmoothLipschitzSimp(*dim,*npts,XData,YData,TData,*LC);}

LIBEXP void	LipIntInfSmoothLipschitzSimpW(int* dim, int* npts,  double* XData, double* YData, double* TData,  double *LC, double* W)
{	slii.SmoothLipschitzSimpW(*dim,*npts,XData,YData,TData,*LC,W);}
