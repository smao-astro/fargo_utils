import argparse
import pathlib
import shutil

import numpy as np
import xarray as xr

import fargo_data_process.utils


def compute_v_los(data_v_r: xr.DataArray, data_v_theta: xr.DataArray) -> xr.DataArray:
    """
    Compute the line-of-sight velocity.

    Parameters:
    - data_v_r: Data for radial velocity. Coordinate transformation is done if needed
    - data_v_theta: Data for theta velocity. Coordinate transformation is done if needed

    Returns:
    - data_v_los: Computed line-of-sight velocity.
    """

    # interpolate to the centralized grid
    # v_r's r grid is not at the center, correct it
    data_v_r = data_v_r.interp(r=data_v_theta.r)
    # v_theta's theta grid is not at the center, correct it
    data_v_theta = data_v_theta.interp(theta=data_v_r.theta)

    # line-of-sight velocity
    data_v_los = data_v_r * np.cos(data_v_r.theta) - data_v_theta * np.sin(
        data_v_theta.theta
    )
    data_v_los.attrs = data_v_r.attrs
    data_v_los.attrs["phys_var_type"] = "v_los"

    return data_v_los


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data_root_dir", type=str)
    parser.add_argument("--dataset_id", type=str)
    parser.add_argument("--save_dir", type=str)
    args = parser.parse_args()

    data_dir = fargo_data_process.utils.match_run_dir(
        args.data_root_dir, args.dataset_id
    )
    save_dir = pathlib.Path(args.save_dir)
    save_dir.mkdir(exist_ok=True, parents=True)

    for file in [
        "batch_truth_sigma.nc",
        "batch_truth_v_r.nc",
        "batch_truth_v_theta.nc",
        "batch_truth_v_los.nc",
    ]:
        if (save_dir / file).exists():
            raise FileExistsError(f"{save_dir / file} exists.")
    # copy file to save_dir
    for file in [
        "batch_truth_sigma.nc",
        "batch_truth_v_r.nc",
        "batch_truth_v_theta.nc",
    ]:
        shutil.copy(data_dir / file, save_dir / file)

    # Line-of-sight velocity
    data_v_r = xr.open_dataarray(data_dir / "batch_truth_v_r.nc")
    data_v_theta = xr.open_dataarray(data_dir / "batch_truth_v_theta.nc")
    # convert to non-rotating frame
    data_v_theta = data_v_theta + data_v_theta.r
    data_v_los = compute_v_los(data_v_r, data_v_theta)
    data_v_los.to_netcdf(save_dir / "batch_truth_v_los.nc")


if __name__ == "__main__":
    main()
