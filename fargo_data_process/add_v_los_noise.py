import argparse
import functools
import multiprocessing
import pathlib
import shutil

import astropy.convolution
import numpy as np
import tqdm
import xarray as xr
from scipy.optimize import curve_fit

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
    return a * np.exp(-0.5 * ((x - b) / c) ** 2)


def jacobian(x, a, b, c):
    return np.stack(
        [
            gaussian(x, a, b, c) / a,
            gaussian(x, a, b, c) * (x - b) / c**2,
            gaussian(x, a, b, c) * (x - b) ** 2 / c**3,
        ],
        axis=-1,
    )


def fit_noisy_velocity_center(
    velocity: float, noise: np.array, vgrid: np.array, line_width: float
):
    """

    Args:
        velocity:
        noise:

    Returns:

    """
    if np.isnan(velocity):
        return np.nan
    line = np.exp(-0.5 * ((velocity - vgrid) / line_width) ** 2)
    line = line + noise
    try:
        out = curve_fit(
            gaussian,
            vgrid,
            line,
            # the parameters a, b, c are magnitude of the gaussian function, location of the peak, and standard deviation
            p0=np.array([1.0, float(velocity), line_width]),
            jac=jacobian,
        )
        popt, pcov = out[0], out[1]
    except RuntimeError:
        print("fitting failed")
        return np.nan
    # location of the peak of the new fitted Gaussian gives the noisy line-of-sight velocity
    return popt[1]


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
    parser.add_argument("--beam_size_physical", type=float, default=2.5, help="in AU")
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

    data_cart_array = data_cart.values
    vgrid = np.linspace(args.vmin, args.vmax, args.n_channels)
    line_width = args.line_width
    noisy_data_cart = np.empty(data_cart_array.shape) * np.nan
    # Create a partial function with vgrid and line_width fixed
    partial_fit_noisy_velocity_center = functools.partial(
        fit_noisy_velocity_center, vgrid=vgrid, line_width=line_width
    )

    # nested tqdm progress bar loop
    for run_index in tqdm.tqdm(range(data_cart_array.shape[0]), desc="run", ncols=80):
        # beam size below is in coordinate
        beam_size = (
            args.beam_size_physical / data_cart.isel(run=run_index)["r_p"].values
        )
        # beam size below is in pixel
        beam_size = beam_size / 5 * args.cartesian_resolution
        # cube noise map
        cube_noise_map = compute_cube_noise_map(
            beam_size,
            args.n_channels,
            args.cartesian_resolution,
            args.cube_noise_level,
            args.seed,
        )
        data_flattened = data_cart_array[run_index].flatten()
        cube_noise_map = cube_noise_map.reshape(cube_noise_map.shape[0], -1)

        # parallel
        with multiprocessing.Pool() as pool:
            # the output is flattened, shape: data.shape[1] * data.shape[2]
            noisy_data = pool.starmap(
                partial_fit_noisy_velocity_center,
                zip(data_flattened, cube_noise_map.T),
            )

        noisy_data = np.array(noisy_data).reshape(data_cart_array.shape[1:])
        noisy_data_cart[run_index] = noisy_data

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
