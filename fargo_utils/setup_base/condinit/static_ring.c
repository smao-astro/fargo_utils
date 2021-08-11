#include "fargo3d.h"

void Init() {

  OUTPUT(Density);
  OUTPUT(Energy);
  OUTPUT(Vx);
  OUTPUT(Vy);

  int i, j, k;
  real r, omega;
  real soundspeed;

  real *vphi = Vx->field_cpu;
  real *vr = Vy->field_cpu;
  real *rho = Density->field_cpu;

#ifdef ADIABATIC
  real *e = Energy->field_cpu;
#endif
#ifdef ISOTHERMAL
  real *cs = Energy->field_cpu;
#endif

  i = j = k = 0;

  for (j = 0; j < Ny + 2 * NGHY; j++) {
    for (i = 0; i < Nx + 2 * NGHX; i++) {

      r = Ymed(j);
      omega = sqrt(G * MSTAR / r / r / r);

      rho[l] = SIGMA0 *
               (1.0 + pow(M_E, -(r - RINGCENTER) * (r - RINGCENTER) /
                                   (2 * RINGWIDTH * RINGWIDTH)) /
                          (RINGWIDTH * sqrt(2 * M_PI))) *
               (1.0 + NOISE * (drand48() - .5));
      soundspeed = ASPECTRATIO * pow(r / R0, FLARINGINDEX) * omega * r;

#ifdef ISOTHERMAL
      cs[l] = soundspeed;
#endif
#ifdef ADIABATIC
      e[l] = pow(soundspeed, 2) * rho[l] / (GAMMA - 1.0);
#endif

      vphi[l] = sqrt(
          (1.0 +
           ASPECTRATIO * ASPECTRATIO * pow(r, 2.0 * FLARINGINDEX) *
               (-1.0 + 2.0 * FLARINGINDEX -
                r * (r - RINGCENTER) / (RINGWIDTH * RINGWIDTH) /
                    (1.0 + sqrt(2 * M_PI) * RINGWIDTH *
                               pow(M_E, 0.5 * pow((r - RINGCENTER) / RINGWIDTH,
                                                  2.0))))) /
          r);
      vphi[l] -= OMEGAFRAME * r;
      vphi[l] *= (1. + ASPECTRATIO * NOISE * (drand48() - .5));

      vr[l] = soundspeed * NOISE * (drand48() - .5);
    }
  }
}

void CondInit() {
  Fluids[0] = CreateFluid("gas", GAS);
  SelectFluid(0);
  Init();
}
