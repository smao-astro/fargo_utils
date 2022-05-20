import numpy as np
import pytest

from fargo_data_process.fargoData import TimeSeqData, Coor


@pytest.fixture
def output_dir():
    return "/Users/kyika/project/pinn/fargo_utils/tmp/fargo3d/outputs"


def test_coor_get_x_edge(output_dir):
    coor = Coor(output_dir)
    assert coor.x_edge.shape == (int(coor._setup["NX"]) + 1,)


def test_flt_x_ymin_t_value(output_dir):
    tsdata = TimeSeqData(output_dir, "dens")
    assert (
        tsdata.flt_x_ymin_t_value.ndim == 2 and tsdata.flt_x_ymin_t_value.shape[1] == 4
    )


def test_flt_rmin_theta_t_value(output_dir):
    tsdata = TimeSeqData(output_dir, "dens")
    assert len(np.unique(tsdata.flt_rmin_theta_t_value[:, 0])) == 1


def test_to_cartesian(output_dir):
    tsdata = TimeSeqData(output_dir, "dens")
    value = tsdata.frames[0].to_cartesian(1000)
    assert 1
