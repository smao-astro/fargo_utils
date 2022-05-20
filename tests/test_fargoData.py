import numpy as np

from .fargoData import TimeSeqData


def test_flt_x_ymin_t_value():
    tsdata = TimeSeqData("/Users/kyika/project/pinn/fargo_utils/tmp/fargo3d/outputs", "dens")
    assert (
        tsdata.flt_x_ymin_t_value.ndim == 2 and tsdata.flt_x_ymin_t_value.shape[1] == 4
    )


def test_flt_rmin_theta_t_value():
    tsdata = TimeSeqData("/Users/kyika/project/pinn/fargo_utils/tmp/fargo3d/outputs", "dens")
    assert len(np.unique(tsdata.flt_rmin_theta_t_value[:, 0])) == 1


def test_to_cartesian():
    tsdata = TimeSeqData("/Users/kyika/project/pinn/fargo_utils/tmp/fargo3d/outputs", "dens")
    value = tsdata.frames[0].to_cartesian(1000)
    assert 1
