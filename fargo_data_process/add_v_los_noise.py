import argparse
import pathlib
import shutil

import astropy.convolution
from jax.config import config

config.update("jax_enable_x64", True)
import jax.numpy as jnp
import numpy as np
import tqdm
import xarray as xr
from jaxfit import CurveFit

import fargo_data_process.utils


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
    return a * jnp.exp(-0.5 * ((x - b) / c) ** 2)


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
    jcf = CurveFit(flength=len(vgrid))
    noisy_data_cart = np.zeros(shape) * np.nan
    for i in range(shape[0]):
        for j in range(shape[1]):
            if np.isnan(vlos_clean[i, j]):
                continue
            try:
                popt, pcov = jcf.curve_fit(
                    gaussian,
                    vgrid,
                    cube_noisy[:, i, j],
                    # the parameters a, b, c are magnitude of the gaussian function, location of the peak, and standard deviation
                    p0=np.array([1.0, vlos_clean[i, j], gaussian_std]),
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

    # Line-of-sight velocity
    data = xr.open_dataarray(data_dir / "batch_truth_v_los.nc")
    # to cartesian
    x = y = np.linspace(-2.5, 2.5, args.cartesian_resolution)
    data_cart = fargo_data_process.utils.xarray_polar_to_cartesian(data, x, y)
    # cube noise map
    beam_size_pixel = args.beam_size_physical / 5 * args.cartesian_resolution
    cube_noise_map = compute_cube_noise_map(
        beam_size_pixel,
        args.n_channels,
        args.cartesian_resolution,
        args.cube_noise_level,
        args.seed,
    )
    data_cart_array = data_cart.values
    vgrid = np.linspace(args.vmin, args.vmax, args.n_channels)
    jcf = CurveFit(flength=args.n_channels)
    noisy_data_cart = np.zeros(data_cart_array.shape) * np.nan
    # nested tqdm progress bar loop
    for run_index in tqdm.tqdm(range(data_cart_array.shape[0]), desc="run", ncols=80):
        for i in range(data_cart_array.shape[1]):
            for j in range(data_cart_array.shape[2]):
                if np.isnan(data_cart_array[run_index, i, j]):
                    continue
                line = np.exp(
                    -0.5
                    * ((data_cart_array[run_index, i, j] - vgrid) / args.line_width)
                    ** 2
                )
                line = line + cube_noise_map[:, i, j]
                try:
                    popt, pcov = jcf.curve_fit(
                        gaussian,
                        vgrid,
                        line,
                        # the parameters a, b, c are magnitude of the gaussian function, location of the peak, and standard deviation
                        p0=np.array(
                            [1.0, data_cart_array[run_index, i, j], args.line_width]
                        ),
                    )
                except RuntimeError:
                    print("fitting failed")
                    continue
                # location of the peak of the new fitted Gaussian gives the noisy line-of-sight velocity
                noisy_data_cart[run_index, i, j] = popt[1]

    noisy_data_cart = xr.DataArray(
        noisy_data_cart,
        coords=data_cart.coords,
        attrs=data_cart.attrs,
    )
    # convert back to polar
    noisy_data = fargo_data_process.utils.xarray_cartesian_to_polar(
        noisy_data_cart, data.r.values, data.theta.values
    )
    noisy_data.to_netcdf(save_dir / "batch_truth_v_los.nc")

    # copy file to save_dir
    for file in [
        "batch_truth_sigma.nc",
        "batch_truth_v_r.nc",
        "batch_truth_v_theta.nc",
    ]:
        shutil.copy(data_dir / file, save_dir / file)


if __name__ == "__main__":
    main()
