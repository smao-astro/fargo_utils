import argparse
import pathlib

import matplotlib.animation
import matplotlib.colors
import matplotlib.patches
import matplotlib.path
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import xarray as xr


def get_config(args=None):
    parser = argparse.ArgumentParser("main")
    parser.add_argument("--output_dir", type=str, default="fargo3d/outputs")
    parser.add_argument("--vmin", type=float, default=None)
    parser.add_argument("--vmax", type=float, default=None)
    parser.add_argument("--delta", type=float, default=None)

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


def cal_delta(aspectratio, planetmass):
    rh = (planetmass / 3) ** (1 / 3)
    h = aspectratio
    delta = 2.0 * np.maximum(rh, h)
    return delta


def create_patch(delta):
    vertices_left = [
        (-np.pi, 1 - delta),
        (-delta, 1 - delta),
        (-delta, 1 + delta),
        (-np.pi, 1 + delta),
    ]
    vertices_right = [
        (np.pi, 1 - delta),
        (delta, 1 - delta),
        (delta, 1 + delta),
        (np.pi, 1 + delta),
    ]

    code_left = code_right = [matplotlib.path.Path.MOVETO] + [
        matplotlib.path.Path.LINETO
    ] * 3
    path = matplotlib.path.Path(
        vertices=vertices_left + vertices_right, codes=code_left + code_right
    )
    pathpatch = matplotlib.patches.PathPatch(path, facecolor="none", edgecolor="green")

    return pathpatch


def cal_gap_depth(sigma, delta):
    selected_index_theta = np.logical_or(sigma.theta < -delta, sigma.theta > delta)
    selected_index_r = np.logical_and(sigma.r > 1 - delta, sigma.r < 1 + delta)
    selected_index = np.logical_and(selected_index_theta, selected_index_r)

    sigma_gap = sigma.where(selected_index)
    gap_depth = sigma_gap.mean(["r", "theta"])
    return gap_depth


def main(args):
    """convert fargo outputs to npz file with (N, 4) shape."""
    run_dir = resolve_save_dir(args.output_dir, ["variables.par"])

    sigma = xr.load_dataarray(run_dir / "test_dens.nc")
    # convert to orbits
    sigma["t"] = sigma["t"] / (2 * np.pi)
    log_sigma = np.log10(sigma)

    aspectratio = float(sigma.attrs["ASPECTRATIO"])
    planetmass = float(sigma.attrs["PLANETMASS"])

    delta = cal_delta(aspectratio, planetmass) if args.delta is None else args.delta
    print(f"Delta={delta:.2g}")

    gap_depth = cal_gap_depth(sigma, delta)

    # movie
    vmin = np.min(log_sigma.values) if args.vmin is None else args.vmin
    vmax = np.max(log_sigma.values) if args.vmax is None else args.vmax

    fig, (ax_curve, ax_im) = plt.subplots(
        nrows=2, ncols=1, gridspec_kw={"height_ratios": [0.4, 0.6]}, figsize=(9, 12)
    )
    fig: plt.Figure
    ax_curve: plt.Axes
    ax_im: plt.Axes

    ax_curve.plot(gap_depth.t.values, gap_depth.values)

    artists = []
    for i, t in enumerate(log_sigma.t.values):
        point = ax_curve.plot(gap_depth.t[i], gap_depth.values[i], "bs")
        pcm = ax_im.pcolormesh(
            log_sigma.theta,
            log_sigma.r,
            log_sigma.isel(t=i).values,
            norm=matplotlib.colors.TwoSlopeNorm(vcenter=0.0, vmin=vmin, vmax=vmax),
            cmap="RdBu_r",
        )
        artists.append([point[0], pcm])
    fig.colorbar(mappable=artists[0][1], ax=ax_im)

    ax_curve.set_yscale("log")
    ax_curve.set_xlabel("orbits")
    ax_curve.set_ylabel(r"$\Sigma_{gap}$")

    ax_im.add_patch(create_patch(delta))
    ax_im.invert_yaxis()
    ax_im.set_box_aspect(1)
    ax_im.set_xlabel(r"$\theta$")
    ax_im.set_ylabel("r")

    ani = matplotlib.animation.ArtistAnimation(fig, artists, interval=180, repeat=False)
    ani.save(run_dir / "gap_evolution.mp4")

    # save
    gap_depth: pd.Series
    gap_depth = gap_depth.to_pandas()
    gap_depth.to_csv(run_dir / "gap_density_evo.csv")


if __name__ == "__main__":
    args = get_config()
    main(args)
