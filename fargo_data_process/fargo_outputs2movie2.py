import argparse

import matplotlib.animation
import matplotlib.colors
import matplotlib.patches
import matplotlib.path
import matplotlib.pyplot as plt
import numpy as np
import xarray as xr

from .utils import resolve_save_dir


def plot_polar_mesh(log_sigma, vmin, vmax, run_dir):
    fig, ax_im = plt.subplots(figsize=(args.figure_width, args.figure_height))
    fig: plt.Figure
    ax_im: plt.Axes

    artists = []
    for i, t in enumerate(log_sigma.t.values):
        pcm = ax_im.pcolormesh(
            log_sigma.theta,
            log_sigma.r,
            log_sigma.isel(t=i).values,
            norm=matplotlib.colors.TwoSlopeNorm(vcenter=0.0, vmin=vmin, vmax=vmax),
            cmap="RdBu_r",
        )
        annotation = plt.annotate(
            f"t = {log_sigma.isel(t=i).t.values:.2f}",
            xy=(0.1, 0.1),
            xycoords="axes fraction",
            c="black",
        )
        artists.append([pcm, annotation])
    cbar = fig.colorbar(mappable=artists[0][0], ax=ax_im)
    cbar.ax.set_yticklabels([f"{10**v:.2f}" for v in cbar.ax.get_yticks()])

    if args.invert_yaxis:
        ax_im.invert_yaxis()
    ax_im.set_box_aspect(1)
    ax_im.set_xlabel("Azimuth")
    ax_im.set_ylabel(r"$R/R_{p}$")

    ani = matplotlib.animation.ArtistAnimation(
        fig, artists, interval=args.frame_interval, repeat=False
    )
    ani.save(run_dir / f"{args.filename}.mp4")


def plot_cartesian_mesh(log_sigma, vmin, vmax, run_dir):
    fig, ax_im = plt.subplots(figsize=(args.figure_width, args.figure_height))
    fig: plt.Figure
    ax_im: plt.Axes

    x = log_sigma.r * np.cos(log_sigma.theta)
    y = log_sigma.r * np.sin(log_sigma.theta)

    artists = []
    for i, t in enumerate(log_sigma.t.values):
        pcm = ax_im.pcolormesh(
            x,
            y,
            log_sigma.isel(t=i).values,
            norm=matplotlib.colors.TwoSlopeNorm(vcenter=0.0, vmin=vmin, vmax=vmax),
            cmap="RdBu_r",
        )
        annotation = plt.annotate(
            f"t = {log_sigma.isel(t=i).t.values:.2f}",
            xy=(0.1, 0.1),
            xycoords="axes fraction",
            c="black",
        )
        artists.append([pcm, annotation])
    cbar = fig.colorbar(mappable=artists[0][0], ax=ax_im)
    cbar.ax.set_yticklabels([f"{10**v:.2f}" for v in cbar.ax.get_yticks()])

    ax_im.set_xlabel("x")
    ax_im.set_ylabel("y")

    ani = matplotlib.animation.ArtistAnimation(
        fig, artists, interval=args.frame_interval, repeat=False
    )
    ani.save(run_dir / f"{args.filename}_cartesian.mp4")


def get_config(args=None):
    parser = argparse.ArgumentParser("main")
    parser.add_argument("--output_dir", type=str, default="fargo3d/outputs")
    parser.add_argument("--filename", type=str, default="dens")
    parser.add_argument("--vmin", type=float, default=None)
    parser.add_argument("--vmax", type=float, default=None)
    parser.add_argument("--figure_width", type=float, default=6.4)
    parser.add_argument("--figure_height", type=float, default=4.8)
    parser.add_argument("--invert_yaxis", type=int, choices=[0, 1], default=1)
    parser.add_argument(
        "--frame_interval",
        type=int,
        default=180,
        help="Delay between frames in milliseconds.",
    )

    return parser.parse_args(args)


def main(args):
    """convert fargo outputs to npz file with (N, 4) shape."""
    run_dir = resolve_save_dir(args.output_dir, ["variables.par"])

    sigma = xr.load_dataarray(run_dir / "test_dens.nc")
    # convert to orbits
    sigma["t"] = sigma["t"] / (2 * np.pi)
    log_sigma = np.log10(sigma)

    # movie
    vmin = np.min(log_sigma.values) if args.vmin is None else args.vmin
    vmax = np.max(log_sigma.values) if args.vmax is None else args.vmax

    plot_polar_mesh(log_sigma, vmin, vmax, run_dir)
    plot_cartesian_mesh(log_sigma, vmin, vmax, run_dir)


if __name__ == "__main__":
    args = get_config()
    main(args)
