import argparse
import pathlib
import shutil

import astropy.convolution
import numpy as np
import scipy.optimize
import xarray as xr

import fargo_data_process.utils


def synthetic_cube(
    data_cart: np.array,
    velocity_min: float,
    velocity_max: float,
    n_channels: int,
    gaussian_std: float,
):
    """

    Args:
        data_cart:
        velocity_min:
        velocity_max:
        n_channels:
        gaussian_std:

    Returns:
        cube_noiseless: cube without noise, shape (n_channels, data_cart.shape[0], data_cart.shape[1])
        vgrid: velocity grid, shape (n_channels,)
    """
    vgrid = np.linspace(velocity_min, velocity_max, n_channels)
    cube_noiseless = np.exp(
        -0.5 * ((data_cart - vgrid[:, None, None]) / gaussian_std) ** 2
    )
    return cube_noiseless, vgrid


def compute_cube_noise_map(
    beam_size_pixel: float,
    n_channels: int,
    size: int,
    cube_noise_level: float,
    seed: int = 0,
) -> np.array:
    """

    Args:
        beam_size_pixel:
        n_channels:
        size:
        cube_noise_level:
        seed:

    Returns:
        noise_convolved: shape (n_channels, size, size)
    """
    rng = np.random.default_rng(seed)

    # generate kernel
    kernel = astropy.convolution.Gaussian2DKernel(beam_size_pixel)

    # for each channel, spatially convolve the beam with the white noise
    noise_convolved = np.empty((n_channels, size, size))
    for i in range(n_channels):
        noise_map = rng.standard_normal((size, size))
        convolved_noise_map = astropy.convolution.convolve(noise_map, kernel)
        convolved_noise_map = (
            convolved_noise_map / np.std(convolved_noise_map) * cube_noise_level
        )
        noise_convolved[i] = convolved_noise_map

    return noise_convolved


def gaussian(x, a, b, c):
    return a * np.exp(-0.5 * ((x - b) / c) ** 2)


def compute_noisy_v_los(
    cube_noisy: np.array, vlos_clean: np.array, vgrid: np.array, gaussian_std: float
) -> np.array:
    """

    Args:
        cube_noisy:
        vlos_clean:
        vgrid:
        gaussian_std:

    Returns:
        noisy_data_cart: shape (data_cart.shape[0], data_cart.shape[1])
    """
    shape = cube_noisy.shape[1:]
    noisy_data_cart = np.zeros(shape) * np.nan
    for i in range(len(shape[0])):
        for j in range(len(shape[1])):
            if np.isnan(vlos_clean[i, j]):
                continue
            try:
                popt, pcov = scipy.optimize.curve_fit(
                    gaussian,
                    vgrid,
                    cube_noisy[:, i, j],
                    # the parameters a, b, c are magnitude of the gaussian function, location of the peak, and standard deviation
                    p0=[1, vlos_clean[i, j], gaussian_std],
                )
            except RuntimeError:
                print("fitting failed")
                continue
            # peak of the new fitted-gaussian gives the noisy line-of-sight velocity
            noisy_data_cart[i, j] = popt[1]
    return noisy_data_cart


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data_root_dir", type=str)
    parser.add_argument("--dataset_id", type=str)
    parser.add_argument("--save_dir", type=str)
    parser.add_argument("--cartesian_resolution", type=int, default=512, help="pixels")
    parser.add_argument("--vmin", type=float, default=-2, help="in Keplerian velocity")
    parser.add_argument("--vmax", type=float, default=2, help="in Keplerian velocity")
    parser.add_argument(
        "--line_width", type=float, default=0.1, help="in Keplerian velocity"
    )
    parser.add_argument("--beam_size_physical", type=float, default=0.05, help="in r_p")
    parser.add_argument("--n_channels", type=int, default=200)
    parser.add_argument("--cube_noise_level", type=float, default=0.1)
    parser.add_argument("--seed", type=int, default=0)
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
    data = xr.open_dataarray(data_dir / "batch_truth_v_los.nc")
    # to cartesian
    x = y = np.linspace(-2.5, 2.5, args.cartesian_resolution)
    data_cart = fargo_data_process.utils.xarray_polar_to_cartesian(data, x, y)
    cube, vgrid = synthetic_cube(
        data_cart.values,
        velocity_min=args.vmin,
        velocity_max=args.vmax,
        n_channels=args.n_channels,
        gaussian_std=args.line_width,
    )
    # add noise to v_los
    beam_size_pixel = args.beam_size_physical / 5 * args.cartesian_resolution
    cube_noise_map = compute_cube_noise_map(
        beam_size_pixel,
        args.n_channels,
        args.cartesian_resolution,
        args.cube_noise_level,
        args.seed,
    )
    noisy_data_cart = compute_noisy_v_los(
        cube + cube_noise_map,
        data_cart.values,
        vgrid,
        args.line_width,
    )
    noisy_data_cart = xr.DataArray(
        noisy_data_cart, coords=data_cart.coords, attrs=data_cart.attrs
    )
    # convert back to polar
    noisy_data = fargo_data_process.utils.xarray_cartesian_to_polar(
        noisy_data_cart, data.r.values, data.theta.values
    )
    noisy_data.to_netcdf(save_dir / "batch_truth_v_los.nc")


if __name__ == "__main__":
    main()
