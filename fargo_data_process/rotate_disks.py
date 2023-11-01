import argparse
import pathlib
import typing

import numpy as np
import pandas as pd
import xarray as xr

import fargo_data_process.utils


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
    parser.add_argument("--planet_angle_file", type=str, default="planet_angles.csv")
    args = parser.parse_args()

    data_dir = fargo_data_process.utils.match_run_dir(
        args.data_root_dir, args.dataset_id
    )
    save_dir = pathlib.Path(args.save_dir)
    save_dir.mkdir(exist_ok=True, parents=True)
    # load planet angles
    df_planet_angles = pd.read_csv(args.planet_angle_file)
    run_ids = df_planet_angles["run_id"].values
    planet_angles = df_planet_angles["planet_angle"].values
    # to rad
    planet_angles = planet_angles * np.pi / 180.0

    for file in [
        "batch_truth_sigma.nc",
        "batch_truth_v_r.nc",
        "batch_truth_v_theta.nc",
    ]:
        if (save_dir / file).exists():
            raise FileExistsError(f"{save_dir / file} exists.")
        data = xr.open_dataarray(data_dir / file)
        rotated_data = rotate_iteratively(
            data, run_ids=run_ids, planet_angles=planet_angles
        )
        # save
        rotated_data.to_netcdf(save_dir / file)


if __name__ == "__main__":
    main()
