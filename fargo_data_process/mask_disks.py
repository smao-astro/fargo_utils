from typing import Iterable, Union

import numpy as np
import xarray as xr


def mask_disks_azimuthally(
    data: xr.DataArray,
    lo_select: Union[float, Iterable],
    hi_select: Union[float, Iterable],
) -> xr.DataArray:
    "Select a region in polar coordinates and mask the rest."
    hi_select = np.mod(hi_select + np.pi, 2 * np.pi) - np.pi
    lo_select = xr.DataArray(lo_select, dims=["run"], coords={"run": data["run"]})
    hi_select = xr.DataArray(hi_select, dims=["run"], coords={"run": data["run"]})
    select_below = data.theta > lo_select
    select_above = data.theta < hi_select
    selected_region = xr.where(
        lo_select < hi_select, select_above & select_below, select_above | select_below
    )
    data = data.where(selected_region, other=np.nan)
    return data


def mask_disks_radially(
    data: xr.DataArray,
    lo_select: Union[float, Iterable],
    hi_select: Union[float, Iterable],
) -> xr.DataArray:
    lo_select = xr.DataArray(lo_select, dims=["run"], coords={"run": data["run"]})
    hi_select = xr.DataArray(hi_select, dims=["run"], coords={"run": data["run"]})
    selected_region = (data.r > lo_select) & (data.r < hi_select)
    data = data.where(selected_region, other=np.nan)
    return data
