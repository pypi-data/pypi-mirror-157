from cffi import FFI
import os

ffibuilder = FFI()
PATH = os.path.dirname(__file__)

ffibuilder.cdef(r"""
    double	LipIntValue(int* Dim, int* Ndata, double* x, double* Xd,double* y,  double* Lipconst, int* Index);
    double	LipIntValueAuto(int* Dim, int* Ndata, double* x,double* Xd, double* y, int* Index);
    double	LipIntValueCons(int* Dim, int* Ndata, int* Cons, double* x, double* Xd,double* y,  double* Lipconst, int* Index);double	LipIntValueConsLeftRegion(int* Dim, int* Ndata, int* Cons, double* x, double* Xd,double* y,  double* Lipconst, double* Region, int* Index);
    double	LipIntValueConsRightRegion(int* Dim, int* Ndata, int* Cons, double* x, double* Xd,double* y,  double* Lipconst, double* Region, int* Index);
    double	LipIntValueLocal(int *Dim, int *Ndata, double* x, double* Xd,double* y);
    double	LipIntValueLocalCons(int *Dim, int *Ndata,int* Cons, double* x, double* Xd,double* y);
    double	LipIntValueLocalConsLeftRegion(int *Dim, int *Ndata,int* Cons, double* x, double* Xd,double* y, double* Region);
    double	LipIntValueLocalConsRightRegion(int *Dim, int *Ndata,int* Cons, double* x, double* Xd,double* y, double* Region);
    void	LipIntComputeLipschitz(int *Dim, int *Ndata, double* x, double* y);
    void	LipIntComputeLocalLipschitz(int *Dim, int *Ndata, double* x, double* y);
    void	LipIntComputeLipschitzCV(int *Dim, int *Ndata, double* Xd, double* y, double* T, int* type, int* Cons, double* Region, double *W);
    void	LipIntComputeLipschitzSplit(int *Dim, int *Ndata, double* Xd, double* y, double* T, double* ratio, int* type, int* Cons, double* Region, double *W);
    void	LipIntSmoothLipschitz(int *Dim, int *Ndata,  double* Xd, double* y, double* T,  double* LC, int* fW, int* fC, int* fR, double* W, int* Cons, double* Region);
    double	LipIntGetLipConst() ;
    void	LipIntGetScaling(double *S) ;
    int		LipIntComputeScaling(int *Dim, int *Ndata, double* XData, double* YData);
    void	ConvertXData(int *Dim, int* npts,  double* XData);
    void	ConvertXDataAUX(int *Dim, int* npts,  double* XData, double *auxdata);
    int		LipIntVerifyMonotonicity(int *Dim, int* npts, int* Cons,  double* XData, double* YData, double* LC, double* eps);
    int		LipIntVerifyMonotonicityLeftRegion(int *Dim, int* npts, int* Cons,  double* XData, double* YData, double* Region, double* LC, double* eps);
    int		LipIntVerifyMonotonicityRightRegion(int *Dim, int* npts, int* Cons,  double* XData, double* YData, double* Region, double* LC, double* eps);
    double	LipIntInfValue(int *Dim, int *Ndata, double* x, double* Xd,double* y,  double* Lipconst, int* Index);
    double	LipIntInfValueAuto(int *Dim, int *Ndata, double* x,double* Xd, double* y, int* Index);
    double	LipIntInfValueCons(int *Dim, int *Ndata, int* Cons, double* x, double* Xd,double* y,  double Lipconst, int* Index);
    double	LipIntInfValueConsLeftRegion(int *Dim, int *Ndata, int* Cons, double* x, double* Xd,double* y,  double* Lipconst, double* Region, int* Index);
    double	LipIntInfValueConsRightRegion(int *Dim, int *Ndata, int* Cons, double* x, double* Xd,double* y,  double* Lipconst, double* Region, int* Index);
    double	LipIntInfValueLocal(int *Dim, int *Ndata, double* x, double* Xd,double* y);
    double	LipIntInfValueLocalCons(int *Dim, int *Ndata,int* Cons, double* x, double* Xd,double* y);
    double	LipIntInfValueLocalConsLeftRegion(int *Dim, int *Ndata,int* Cons, double* x, double* Xd,double* y, double* Region);
    double	LipIntInfValueLocalConsRightRegion(int *Dim, int *Ndata,int* Cons, double* x, double* Xd,double* y, double* Region);
    void	LipIntInfComputeLipschitz(int *Dim, int *Ndata, double* x, double* y);
    void	LipIntInfComputeLocalLipschitz(int *Dim, int *Ndata, double* x, double* y);
    void	LipIntInfComputeLipschitzCV(int *Dim, int *Ndata, double* Xd, double* y, double* T,int* type, int* Cons, double* Region, double *W);
    void	LipIntInfComputeLipschitzSplit(int *Dim, int *Ndata, double* Xd, double* y, double* T, double* ratio,int* type, int* Cons, double* Region, double *W);
    void	LipIntInfSmoothLipschitz(int *Dim, int *Ndata,  double* Xd, double* y, double* T,  double* LC, int* fW, int* fC, int* fR, double* W, int* Cons, double* Region);
    double	LipIntInfGetLipConst() ;
    void	LipIntInfGetScaling(double *S) ;
    int		LipIntInfComputeScaling(int *Dim, int *Ndata, double* XData, double* YData);
    int		LipIntInfVerifyMonotonicity(int *Dim, int* npts, int* Cons,  double* XData, double* YData, double LC, double ep);
    int		LipIntInfVerifyMonotonicityLeftRegion(int *Dim, int npts, int* Cons,  double* XData, double* YData, double* Region, double* LC, double* eps);
    int		LipIntInfVerifyMonotonicityRightRegion(int *Dim, int npts, int* Cons,  double* XData, double* YData, double* Region, double* LC, double* eps);
    void	LipIntInfSmoothLipschitzSimp(int *Dim, int* npts,  double* XData, double* YData, double* TData,  double* LC);
    void	LipIntInfSmoothLipschitzSimpW(int *Dim, int* npts,  double* XData, double* YData, double* TData,  double* LC, double* W);
    int	STCBuildLipInterpolant(int *Dim, int *Ndata, double* x, double* y);
    int	STCBuildLipInterpolantExplicit(int *Dim, int *Ndata, double* x, double* y);
    int	STCBuildLipInterpolantColumn(int *Dim, int *Ndata, double* x, double* y);
    int	STCBuildLipInterpolantExplicitColumn(int *Dim, int *Ndata, double* x, double* y);
    void	STCSetLipschitz(double* x);
    double	STCValue( double* x );
    double	STCValueExplicit( double* x );
    void	STCFreeMemory();
    """, override=True)

liblip_src=['src/glpavl.c','src/glpbfi.c','src/glpdmp.c','src/glphbm.c','src/glpiet.c','src/glpinv.c','src/glpios1.c','src/glpios2.c','src/glpios3.c',
'src/glpipm.c','src/glpipp1.c','src/glpipp2.c','src/glplib1a.c','src/glplib1b.c','src/glplib2.c','src/glplib3.c','src/glplib4.c',
'src/glplpp1.c','src/glplpp2.c','src/glplpx1.c','src/glplpx2.c','src/glplpx3.c','src/glplpx4.c','src/glplpx5.c','src/glplpx6a.c',
'src/glplpx6b.c','src/glplpx6c.c','src/glplpx6d.c','src/glplpx7.c','src/glplpx7a.c','src/glplpx7b.c','src/glplpx8a.c','src/glplpx8b.c',
'src/glplpx8c.c','src/glplpx8d.c','src/glplpx8e.c','src/glpluf.c','src/glpmat.c','src/glpmip1.c','src/glpmip2.c','src/glpmpl1.c',
'src/glpmpl2.c','src/glpmpl3.c','src/glpmpl4.c','src/glpqmd.c','src/glprng.c','src/glpspx1.c','src/glpspx2.c','src/glpstr.c',
'src/glptsp.c','src/forest.cpp','src/interpol.cpp','src/liblip.cpp','src/slipint.cpp']

ffibuilder.set_source("_liblip",r""" #include "liblip.h" """,  
    sources=liblip_src,
    include_dirs=[PATH],
    )

if __name__ == "__main__":
    ffibuilder.compile(verbose=True)
