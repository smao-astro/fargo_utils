import pathlib
from typing import Union

import numpy as np
import scipy.interpolate as si
import xarray as xr


def match_run_dir(runs_dir: Union[str, pathlib.Path], run_id: str) -> pathlib.PosixPath:
    runs_dir = pathlib.Path(runs_dir)
    run_dir = list(runs_dir.glob(run_id + "*"))
    if len(run_dir) == 1:
        return run_dir[0]
    else:
        raise ValueError


def resolve_save_dir(output_dir, file_list, verbose=True):
    save_dir = pathlib.Path(output_dir)
    # resolve soft links
    for file in file_list:
        if (save_dir / file).exists():
            save_dir = (save_dir / file).resolve().parent
            break
    else:
        raise FileNotFoundError(f"Can not find {file_list} in {save_dir}")

    if verbose:
        print(f"save_dir={save_dir}")
    return save_dir


def xarray_polar_to_cartesian(data_array: xr.DataArray, x, y):
    x = np.array(x)
    y = np.array(y)
    if x.ndim != 1 or y.ndim != 1:
        raise ValueError("x and y must be 1D array.")

    # y is outer axis, x is inner axis
    xgrid, ygrid = np.meshgrid(x, y, indexing="xy")
    # pseudo dimension
    r = xr.DataArray(np.sqrt(xgrid.flatten() ** 2 + ygrid.flatten() ** 2), dims="i")
    theta = xr.DataArray(np.arctan2(ygrid.flatten(), xgrid.flatten()), dims="i")

    coords = {k: data_array[k] for k in set(data_array.coords) - {"r", "theta"}}
    coords.update({"y": ("y", y), "x": ("x", x)})

    data_array = data_array.interp({"r": r, "theta": theta}).values

    if data_array.ndim == 2:
        data_array = xr.DataArray(
            data_array.reshape((-1, len(y), len(x))),
            coords=coords,
            dims=["run", "y", "x"],
        )
    else:
        data_array = xr.DataArray(
            data_array.reshape((len(y), len(x))),
            coords=coords,
            dims=["y", "x"],
        )

    return data_array


def xarray_cartesian_to_polar(data_array: xr.DataArray, r, theta):
    r = np.array(r)
    theta = np.array(theta)
    if r.ndim != 1 or theta.ndim != 1:
        raise ValueError("r and theta must be 1D array.")

    # theta is outer axis, r is inner axis
    rgrid, thetagrid = np.meshgrid(r, theta, indexing="ij")
    # pseudo dimension
    x = xr.DataArray(rgrid.flatten() * np.cos(thetagrid.flatten()), dims="i")
    y = xr.DataArray(rgrid.flatten() * np.sin(thetagrid.flatten()), dims="i")

    coords = {k: data_array[k] for k in set(data_array.coords) - {"x", "y"}}
    coords.update({"r": ("r", r), "theta": ("theta", theta)})

    data_array = data_array.interp({"x": x, "y": y}).values

    if data_array.ndim == 2:
        data_array = xr.DataArray(
            data_array.reshape((-1, len(r), len(theta))),
            coords=coords,
            dims=["run", "r", "theta"],
        )
    else:
        data_array = xr.DataArray(
            data_array.reshape((len(r), len(theta))),
            coords=coords,
            dims=["r", "theta"],
        )

    return data_array


def rotate_dataarray(data_array, delta):
    """
    Rotates a given xarray DataArray along the theta dimension by a given angle delta.

    Args:
        data_array (xr.DataArray): Input xarray DataArray with the last dimension being the theta dimension.
        delta (float): Rotation angle in radians (-pi to pi).

    Notes:
        Theoretically the rotation angle can be different among fargo cases (along run dimension), but that would cause the outputs have different theta grid, thus we can not stack them together to one DataArray. Additional care must be taken.

    Returns:
        xr.DataArray: Rotated xarray DataArray.
    """
    # Check if the data_array has a theta dimension
    if "theta" not in data_array.dims:
        raise ValueError("Input data_array must have a 'theta' dimension.")

    # Ensure delta is within the valid range
    if not -np.pi <= delta <= np.pi:
        raise ValueError("Rotation angle 'delta' must be in the range [-pi, pi].")
    # convert delta to range [-pi, pi). I am not sure if this is necessary, but might be safer.
    delta = np.mod(delta + np.pi, 2 * np.pi) - np.pi

    # sort the theta dimension
    data_array = data_array.sortby("theta")

    values = data_array.values
    theta = data_array.theta.values
    # the last dimension is the theta dimension

    # shifted theta values, limit to [-pi, pi)
    theta_shifted = np.mod(theta + delta + np.pi, 2 * np.pi) - np.pi
    # sort values and theta_shifted by theta_shifted
    idx = np.argsort(theta_shifted)
    theta_shifted = theta_shifted[idx]
    values = values[..., idx]

    # pad the values array with first and last value to avoid interpolation errors at the edges
    theta_shifted = np.concatenate(
        [
            # in range [-3pi, -pi)
            np.mod(theta_shifted[-1:] + np.pi, 2 * np.pi) - 3 * np.pi,
            theta_shifted,
            # in range [pi, 3pi)
            np.mod(theta_shifted[:1] + np.pi, 2 * np.pi) + np.pi,
        ]
    )
    values = np.concatenate((values[..., -1:], values, values[..., :1]), axis=-1)

    # Interpolate the data_array along the theta dimension to theta
    # the last dimension is the theta dimension
    values = si.interp1d(theta_shifted, values, axis=-1)(theta)

    # assemble the new data_array
    values = xr.DataArray(
        values, dims=data_array.dims, coords=data_array.coords, attrs=data_array.attrs
    )
    return values
