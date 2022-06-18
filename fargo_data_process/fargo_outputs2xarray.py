import pathlib

from .config import get_config
from .fargoData import TimeSeqData


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


def main(output_dir):
    """convert fargo outputs to npz file with (N, 4) shape."""
    save_dir = resolve_save_dir(output_dir, ["variables.par"])

    dens = TimeSeqData(output_dir, phys_var_type="dens").xarray
    print(f"dens shape {dens.shape}")
    vx = TimeSeqData(output_dir, phys_var_type="vx").xarray
    print(f"vx shape {vx.shape}")
    vy = TimeSeqData(output_dir, phys_var_type="vy").xarray
    print(f"vy shape {vy.shape}")
    dens.to_netcdf(save_dir / "test_dens.nc")
    vx.to_netcdf(save_dir / "test_vx.nc")
    vy.to_netcdf(save_dir / "test_vy.nc")


if __name__ == "__main__":
    main(get_config().output_dir)
