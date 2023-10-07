import argparse
import pathlib

import numpy as np
import xarray as xr

import fargo_data_process.mask_disks
import fargo_data_process.utils


def main():
    """
        --data_root_dir
    /Users/kyika/project/pinn/onet-disk2D-single/cedar/pm_al_ar_fung_gap2steady4test/runs/
    --dataset_id
    cdd269f6
        Returns:

    """
    parser = argparse.ArgumentParser()
    parser.add_argument("--data_root_dir", type=str)
    parser.add_argument("--dataset_id", type=str)
    parser.add_argument("--save_dir", type=str)
    parser.add_argument("--noise", type=float, help="in dex")
    parser.add_argument("--seed", type=int, default=0)
    args = parser.parse_args()

    data_dir = fargo_data_process.utils.match_run_dir(
        args.data_root_dir, args.dataset_id
    )
    save_dir = pathlib.Path(args.save_dir)
    save_dir.mkdir(exist_ok=True, parents=True)
    for file in [
        "batch_truth_sigma.nc",
    ]:
        if (save_dir / file).exists():
            raise FileExistsError(f"{save_dir / file} exists.")
        data = xr.open_dataarray(data_dir / file)
        rng = np.random.default_rng(seed=args.seed)
        data = data * 10 ** rng.normal(0, args.noise, data.shape)
        data.to_netcdf(save_dir / file)


if __name__ == "__main__":
    main()
