import argparse
import pathlib

import xarray as xr
import yaml


def get_config():
    parser = argparse.ArgumentParser()
    parser.add_argument("--runs_dir", type=str, default=".")
    parser.add_argument("--yaml_file", type=str, default="fargo_runs.yml")
    parser.add_argument("--save_dir", type=str, default=".")
    config = parser.parse_args()
    return config


def yaml_file_check(fargo_runs):
    cri = [key in fargo_runs for key in ["runs", "parameters"]]
    return all(cri)


def main(runs_dir, yaml_file, save_dir):
    """Collect all fargo runs, concat data to one file.

    Args:
        config:

    Returns:

    """
    runs_dir = pathlib.Path(runs_dir)
    save_dir = pathlib.Path(save_dir)

    # read from yaml_file
    with open(yaml_file, "r") as f:
        fargo_runs = yaml.safe_load(f)

    # valid file content
    if not yaml_file_check(fargo_runs):
        raise ValueError("Yaml file does not pass the check.")

    outputs_dir = []
    for run in fargo_runs["runs"]:
        run_outputs_dir = list(runs_dir.glob(f"{run}*/fargo3d/outputs"))
        if len(run_outputs_dir) == 1:
            run_outputs_dir = run_outputs_dir[0]
            # check if files exist
            for phys_var_type in ["dens", "vy", "vx"]:
                data_file = run_outputs_dir / f"test_{phys_var_type}.nc"
                if not data_file.exists():
                    raise FileNotFoundError(f"{data_file} not found.")
            outputs_dir.append(run_outputs_dir)
        else:
            raise ValueError(f"run id={run}, failed to match run dir.")
    # outputs_dir = [
    #     list(runs_dir.glob(f"{run}*/fargo3d/outputs"))[0] for run in fargo_runs["runs"]
    # ]

    # only support single parameter
    if len(fargo_runs["parameters"]) > 1:
        raise NotImplementedError
    parameter = fargo_runs["parameters"][0]

    for phys_var_type in ["dens", "vy", "vx"]:
        # load xarrays
        xarrays = [
            xr.load_dataarray(odir / f"test_{phys_var_type}.nc") for odir in outputs_dir
        ]
        new_dim = xr.DataArray(
            [float(array.attrs[parameter]) for array in xarrays], dims=parameter
        )
        # concat xarrays
        xarrays = xr.concat(xarrays, dim=new_dim)
        # update attributes
        xarrays.attrs.pop(parameter)

        # save to file
        xarrays.to_netcdf(save_dir / f"batch_test_{phys_var_type}.nc")


if __name__ == "__main__":
    config = get_config()
    main(config.runs_dir, config.yaml_file, config.save_dir)
