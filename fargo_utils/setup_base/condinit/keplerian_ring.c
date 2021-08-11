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
               (1.0 + pow(M_E, -0.5 * pow((r - RINGCENTER) / RINGWIDTH, 2.0)) /
                          (RINGWIDTH * sqrt(2 * M_PI)));
      soundspeed = ASPECTRATIO * pow(r / R0, FLARINGINDEX) * omega * r;

#ifdef ISOTHERMAL
      cs[l] = soundspeed;
#endif
#ifdef ADIABATIC
      e[l] = pow(soundspeed, 2) * rho[l] / (GAMMA - 1.0);
#endif

      vphi[l] = omega * r;
      vphi[l] -= OMEGAFRAME * r;

      real part =
          (RINGWIDTH * RINGWIDTH) *
          (sqrt(2.0) +
           2.0 * pow(M_E, 0.5 * pow((r - RINGCENTER) / RINGWIDTH, 2.0)) *
               sqrt(M_PI) * RINGWIDTH);
      vr[l] =
          3.0 * NU *
          (2.0 * sqrt(2.0) * r * r - 2.0 * sqrt(2.0) * r * RINGCENTER - part) /
          (2.0 * r * part);
    }
  }
}

void CondInit() {
  Fluids[0] = CreateFluid("gas", GAS);
  SelectFluid(0);
  Init();
}
