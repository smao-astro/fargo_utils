import argparse
import pathlib
import typing

import numpy as np
import xarray as xr

import fargo_data_process.utils

R_UNIT = 100  # AU


def rotate_iteratively(
    dataarray: xr.DataArray, run_ids: typing.Iterable, planet_angles: typing.Iterable
) -> xr.DataArray:
    rotated_data_list = []
    for run_id, planet_angle in zip(run_ids, planet_angles):
        rotated_data = fargo_data_process.utils.rotate_dataarray(
            dataarray.sel(run=run_id), planet_angle
        )
        rotated_data_list.append(rotated_data)
    rotated_data = xr.concat(rotated_data_list, dim="run")
    return rotated_data


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data_root_dir", type=str)
    parser.add_argument("--dataset_id", type=str)
    parser.add_argument("--save_dir", type=str)
    parser.add_argument("--r_p_min", type=float, default=50, help="in AU")
    parser.add_argument("--r_p_max", type=float, default=150, help="in AU")
    parser.add_argument("--num_images", type=int, default=256)
    args = parser.parse_args()

    data_dir = fargo_data_process.utils.match_run_dir(
        args.data_root_dir, args.dataset_id
    )
    save_dir = pathlib.Path(args.save_dir)
    save_dir.mkdir(exist_ok=True, parents=True)

    r_p = np.random.default_rng(111).uniform(
        args.r_p_min, args.r_p_max, size=args.num_images
    )
    theta_p = np.random.default_rng(222).uniform(
        -np.pi / 2, np.pi / 2, size=args.num_images
    )

    for file in [
        "batch_truth_sigma.nc",
        "batch_truth_v_r.nc",
        "batch_truth_v_theta.nc",
    ]:
        if (save_dir / file).exists():
            raise FileExistsError(f"{save_dir / file} exists.")
        data = xr.open_dataarray(data_dir / file)
        # assign r_p and theta_p
        data = data.assign_coords(r_p=("run", r_p), theta_p=("run", theta_p))
        # rotate by theta_p
        data = rotate_iteratively(
            data, run_ids=data["run"].values, planet_angles=data["theta_p"].values
        )
        # correct azimuthal velocity from rotating frame to inertial frame
        if file == "batch_truth_v_theta.nc":
            data = data + data["r"]
        # scaling surface density and velocities
        data = data * (data["r_p"] / R_UNIT) ** -0.5
        # save
        data.to_netcdf(save_dir / file)


if __name__ == "__main__":
    main()
