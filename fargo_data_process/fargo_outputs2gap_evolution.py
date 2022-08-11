import pathlib
import pandas as pd
import argparse
import numpy as np
import xarray as xr


def get_config(args=None):
    parser = argparse.ArgumentParser("main")
    parser.add_argument("--output_dir", type=str, default="fargo3d/outputs")
    parser.add_argument("--r_min", type=float, required=True)
    parser.add_argument("--r_max", type=float, required=True)

    return parser.parse_args(args)


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


def main(args):
    """convert fargo outputs to npz file with (N, 4) shape."""
    run_dir = resolve_save_dir(args.output_dir, ["variables.par"])

    sigma = xr.load_dataarray(run_dir / "test_dens.nc")
    r_index_selected = np.logical_and(sigma.r > args.r_min, sigma.r < args.r_max)
    sigma = sigma.where(r_index_selected, drop=True)
    mean_gas_evolution: pd.Series
    mean_gas_evolution = sigma.mean(dim=("r", "theta")).to_pandas()
    mean_gas_evolution.to_csv(run_dir / "gap_density_evo.csv")


if __name__ == "__main__":
    args = get_config()
    main(args)
