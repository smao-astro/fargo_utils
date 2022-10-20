#include "fargo3d.h"

void Init() {
  
  OUTPUT(Density);
  OUTPUT(Energy);
  OUTPUT(Vx);
  OUTPUT(Vy);

  int i,j,k;
  real r, omega;
  real soundspeed;
  real h2;
  
  real *vphi = Vx->field_cpu;
  real *vr   = Vy->field_cpu;
  real *rho  = Density->field_cpu;
  
#ifdef ADIABATIC
  real *e   = Energy->field_cpu;
#endif
#ifdef ISOTHERMAL
  real *cs   = Energy->field_cpu;
#endif

  i = j = k = 0;
  
  for (j=0; j<Ny+2*NGHY; j++) {
    for (i=0; i<Nx+2*NGHX; i++) {
      
      r = Ymed(j);
      omega = sqrt(G*MSTAR/r/r/r);
      
      rho[l] = SIGMA0*pow(r/R0,-SIGMASLOPE)*(1.0+NOISE*(drand48()-.5));
      soundspeed  = ASPECTRATIO*pow(r/R0,FLARINGINDEX)*omega*r;

#ifdef ISOTHERMAL
      cs[l] = soundspeed;
#endif
#ifdef ADIABATIC
      e[l] = pow(soundspeed,2)*rho[l]/(GAMMA-1.0);
#endif
      h2 = pow(ASPECTRATIO,2)*pow(r/R0,2*FLARINGINDEX);
      vphi[l] = pow(1-0.5*h2,0.5)*pow(r/R0,-0.5);
      vphi[l] -= OMEGAFRAME*r;
      vphi[l] *= (1.+ASPECTRATIO*NOISE*(drand48()-.5));

      vr[l] = -3.0/2.0*ALPHA*h2*pow(r/R0,-0.5);
      vr[l]   += soundspeed*NOISE*(drand48()-.5);
    }
  } 
}

void CondInit() {
   Fluids[0] = CreateFluid("gas",GAS);
   SelectFluid(0);
   Init();
}