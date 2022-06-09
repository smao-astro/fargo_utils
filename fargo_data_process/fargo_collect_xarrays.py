import argparse
import pathlib
import shutil

import xarray as xr
import yaml


def get_config():
    parser = argparse.ArgumentParser()
    parser.add_argument("--runs_dir", type=str, default=".")
    parser.add_argument("--yaml_file", type=str, default="fargo_runs.yml")
    parser.add_argument("--save_dir", type=str, default=".")
    parser.add_argument(
        "--collecting_mode", type=str, choices=["all", "last_t_frame"], default="all"
    )
    config = parser.parse_args()
    return config


def select_last_time_frame(data: xr.DataArray):
    data = data.isel(t=-1)
    data = data.drop("t")
    return data


def yaml_file_check(fargo_runs):
    cri = [key in fargo_runs for key in ["runs", "parameters"]]
    return all(cri)


def main(runs_dir, yaml_file, save_dir, collecting_mode):
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

    # only support single parameter
    if len(fargo_runs["parameters"]) > 1:
        raise NotImplementedError
    parameter = fargo_runs["parameters"][0]

    fargo_setups = None
    for new_phys_var_type, phys_var_type in zip(
        ["sigma", "v_r", "v_theta"], ["dens", "vy", "vx"]
    ):
        # load xarrays
        if collecting_mode == "all":
            xarrays = [
                xr.load_dataarray(odir / f"test_{phys_var_type}.nc")
                for odir in outputs_dir
            ]
        elif collecting_mode == "last_t_frame":
            xarrays = [
                select_last_time_frame(
                    xr.load_dataarray(odir / f"test_{phys_var_type}.nc")
                )
                for odir in outputs_dir
            ]
        else:
            raise NotImplementedError
        new_dim = xr.DataArray(
            [float(array.attrs[parameter]) for array in xarrays], dims=parameter
        )
        # concat xarrays
        xarrays = xr.concat(xarrays, dim=new_dim)
        # update attributes
        xarrays.attrs.pop(parameter)
        if fargo_setups is None:
            fargo_setups = xarrays.attrs
            fargo_setups.pop("phys_var_type")

        # save to file
        xarrays.to_netcdf(save_dir / f"batch_truth_{new_phys_var_type}.nc")

    # save fargo_setups
    with (save_dir / "fargo_setups.yml").open("w") as f:
        yaml.safe_dump(fargo_setups, f)
    # save a arg_groups.yml
    run0 = fargo_runs["runs"][0]
    arg_groups_file = f"{run0}*/fargo3d/setups/*/arg_groups.yml"
    arg_groups_file = list(runs_dir.glob(arg_groups_file))[0]
    shutil.copy(arg_groups_file, save_dir)


if __name__ == "__main__":
    config = get_config()
    main(config.runs_dir, config.yaml_file, config.save_dir, config.collecting_mode)
