import os

import numpy as np
import pytest

from fargo_data_process.fargoData import TimeSeqData, Coor, GridData, FrameData


@pytest.fixture
def output_dir():
    return "/Users/kyika/project/pinn/fargo_utils/tmp/fargo3d/outputs"


def test_coor_get_x_edge(output_dir):
    coor = Coor(output_dir)
    assert coor.x_edge.shape == (int(coor._setup["NX"]) + 1,)


def test_GridData(output_dir):
    coor = Coor(output_dir)
    nx = int(coor._setup["NX"])
    ny = int(coor._setup["NY"])
    griddata = GridData(os.path.join(output_dir, "gasdens0.dat"), ny, nx)

    assert griddata.value.shape == (ny, nx, 1)


def test_FrameData(output_dir):
    coor = Coor(output_dir)
    framedata = FrameData(
        os.path.join(output_dir, "gasdens0.dat"),
        coor._setup,
        coor.y_center,
        coor.x_center,
    )
    cri = [
        np.isclose(framedata.time, 0.0),
        framedata.xy_value.shape == (framedata.ny, framedata.nx, 3),
        framedata.flt_xyt_value.shape == (framedata.ny * framedata.nx, 4),
    ]
    assert all(cri)


def test_FrameData_xy_value(output_dir):
    coor = Coor(output_dir)
    framedata = FrameData(
        os.path.join(output_dir, "gasdens0.dat"),
        coor._setup,
        coor.y_center,
        coor.x_center,
    )
    r = framedata.xy_value[:, 0, 1]
    cri = [
        framedata.xy_value.shape == (framedata.ny, framedata.nx, 3),
        np.amin(r) > 0.4,
        np.amax(r) < 2.5,
    ]
    assert all(cri)


def test_TimeSeqData_values(output_dir):
    tsdata = TimeSeqData(output_dir, "dens")
    ny = int(tsdata.setup["NY"])
    nx = int(tsdata.setup["NX"])
    nt = len(tsdata.frames)
    assert tsdata.values.shape == (nt, ny, nx, 1)


def test_TimeSeqData_flt_xyt_value(output_dir):
    tsdata = TimeSeqData(output_dir, "dens")
    value = tsdata.flt_xyt_value

    cri = [value.shape[1] == 4, np.amin(value[:, 1]) > 0.4]
    assert all(cri)


def test_TimeSeqData_flt_r_theta_t_value(output_dir):
    tsdata = TimeSeqData(output_dir, "dens")
    value = tsdata.flt_r_theta_t_value

    cri = [value.shape[1] == 4, np.amin(value[:, 0]) > 0.4]
    assert all(cri)


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
