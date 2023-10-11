import argparse
import pathlib

import numpy as np
import xarray as xr

import fargo_data_process.mask_disks
import fargo_data_process.utils


def generate_spatial_noise(size, scale, seed=0):
    """
    Generate a 2D noise field with a dominant spatial scale.

    Parameters:
    - size: The size of the noise field (e.g., 256 for a 256x256 field).
    - scale: The dominant spatial scale in pixels, used to define the width of the Gaussian filter.
    - seed: The seed for the random number generator.

    Returns:
    - filtered_noise: The generated 2D noise field.
    """

    # Generate white noise
    rng = np.random.default_rng(seed)
    white_noise = rng.standard_normal((size, size))

    # Compute FFT
    f_white_noise = np.fft.fftshift(np.fft.fft2(white_noise))

    # Create a low-pass filter
    x = np.linspace(-size // 2, size // 2 - 1, size)
    y = np.linspace(-size // 2, size // 2 - 1, size)
    x, y = np.meshgrid(x, y)
    radius = np.sqrt(x**2 + y**2)
    filter = 1 - np.exp(-0.5 * (radius / scale) ** 2)

    # Apply the filter
    f_filtered_noise = f_white_noise * filter

    # Inverse FFT to get the spatial noise
    filtered_noise = np.real(np.fft.ifft2(np.fft.ifftshift(f_filtered_noise)))

    return filtered_noise


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
    scale = args.beam_size / 5 * size
    print(f"scale: {scale:.2f}")
    filtered_noise = generate_spatial_noise(size, scale, args.seed)
    filtered_noise = filtered_noise / np.std(filtered_noise) * args.noise

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


if __name__ == "__main__":
    main()
