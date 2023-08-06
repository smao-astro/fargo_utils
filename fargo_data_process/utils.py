import pathlib
from typing import Union

import numpy as np
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

    data_array = xr.DataArray(
        data_array.reshape((len(y), len(x))),
        coords=coords,
        dims=["y", "x"],
    )

    return data_array
