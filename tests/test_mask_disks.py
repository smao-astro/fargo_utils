import matplotlib.pyplot as plt
import numpy as np
import pytest
import xarray as xr

import fargo_data_process.mask_disks
import fargo_data_process.utils


@pytest.fixture
def data():
    return xr.open_dataarray(
        "/Users/kyika/project/pinn/onet-disk2D-single/cedar/pm_al_ar_fung_gap2steady4test/runs/cdd269f6907d4672b6d94a6a88aa01b4/batch_truth_sigma.nc"
    )


@pytest.mark.parametrize(
    "lo_select, hi_select",
    [
        (-np.pi / 2, np.pi / 2),
        (np.pi / 2, 3 * np.pi / 2),
        (np.pi / 2, -np.pi / 2),
    ],
)
def test_mask_disks_0(data, lo_select, hi_select):
    data_select = fargo_data_process.mask_disks.mask_disks(data, lo_select, hi_select)
    x = y = np.linspace(-2, 2, 200)

    run_id = data["run"].values[0]
    data_cart = fargo_data_process.utils.xarray_polar_to_cartesian(
        data.sel(run=run_id), x, y
    )
    data_cart_half = fargo_data_process.utils.xarray_polar_to_cartesian(
        data_select.sel(run=run_id), x, y
    )

    # plot
    fig, axes = plt.subplots(1, 2, figsize=(10, 5))
    axes[0].pcolormesh(x, y, data_cart, shading="auto")
    axes[1].pcolormesh(x, y, data_cart_half, shading="auto")
    fig.show()
    assert True


def test_mask_disks_1(data):
    lo_select = np.random.default_rng().uniform(-np.pi, np.pi, len(data["run"]))
    hi_select = lo_select + np.pi
    data_select = fargo_data_process.mask_disks.mask_disks(data, lo_select, hi_select)
    x = y = np.linspace(-2, 2, 200)

    for run_id in data["run"].values[:3]:
        data_cart = fargo_data_process.utils.xarray_polar_to_cartesian(
            data.sel(run=run_id), x, y
        )
        data_cart_half = fargo_data_process.utils.xarray_polar_to_cartesian(
            data_select.sel(run=run_id), x, y
        )

        # plot
        fig, axes = plt.subplots(1, 2, figsize=(10, 5))
        axes[0].pcolormesh(x, y, data_cart, shading="auto")
        axes[1].pcolormesh(x, y, data_cart_half, shading="auto")
        fig.show()
    assert True
