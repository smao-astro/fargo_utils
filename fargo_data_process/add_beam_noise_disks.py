import argparse
import pathlib
import astropy.convolution
import shutil
import numpy as np
import xarray as xr

import fargo_data_process.mask_disks
import fargo_data_process.utils


def generate_beam_noise(size, noise_level, beam_size, seed=0):
    # Generate white noise
    rng = np.random.default_rng(seed)
    noise = rng.standard_normal((size, size))
    # generate kernel
    kernel = astropy.convolution.Gaussian2DKernel(beam_size)
    # convolve the beam with the white noise
    noise = astropy.convolution.convolve(noise, kernel)
    noise = noise / np.std(noise) * noise_level
    return noise


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
    parser.add_argument("--beam_size", type=float)
    parser.add_argument("--seed", type=int, default=0)
    args = parser.parse_args()

    data_dir = fargo_data_process.utils.match_run_dir(
        args.data_root_dir, args.dataset_id
    )
    save_dir = pathlib.Path(args.save_dir)
    save_dir.mkdir(exist_ok=True, parents=True)

    file = "batch_truth_sigma.nc"
    if (save_dir / file).exists():
        raise FileExistsError(f"{save_dir / file} exists.")
    data = xr.open_dataarray(data_dir / file)
    # generate noise
    size = 512
    scale = args.beam_size / 2.5 * size
    print(f"scale: {scale:.2f}")
    filtered_noise = generate_beam_noise(size, args.noise, scale, args.seed)

    # convert to cartesian
    x = y = np.linspace(-2.5, 2.5, size)
    data_in_cartesian = fargo_data_process.utils.xarray_polar_to_cartesian(data, x, y)
    # add noise
    data_in_cartesian = data_in_cartesian * 10**filtered_noise
    # convert back to polar
    data = fargo_data_process.utils.xarray_cartesian_to_polar(
        data_in_cartesian, data.r.values, data.theta.values
    )

    data.to_netcdf(save_dir / file)

    # copy file to save_dir
    for file in [
        "batch_truth_v_r.nc",
        "batch_truth_v_theta.nc",
    ]:
        shutil.copy(data_dir / file, save_dir / file)


if __name__ == "__main__":
    main()
