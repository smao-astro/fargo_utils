import os

import matplotlib.figure
import matplotlib.pyplot as plt
import numpy as np

from .config import get_config
from .fargoData import TimeSeqData


def fancy_suplots(
    data: TimeSeqData, title: str, cmap: str = "Reds", nxy=1000
) -> matplotlib.figure.Figure:
    values = data.flt_xyt_value[:, -1]
    vmin = np.min(values)
    vmax = np.max(values)

    fig = plt.figure(figsize=(9, 3))
    fig.suptitle(title)
    fig.supxlabel("$x/R_0$")
    fig.supylabel("$y/R_0$")
    axs = fig.subplots(1, 3, sharex=True, sharey=True, gridspec_kw={"wspace": 0.0})
    for ax, frame in zip(axs, [data.frames[0], data.frames[10], data.frames[20]]):
        extent = [-frame.ymax, frame.ymax, -frame.ymax, frame.ymax]
        im = ax.imshow(
            frame.to_cartesian(nxy),
            cmap=cmap,
            origin="lower",
            extent=extent,
            aspect="equal",
            vmin=vmin,
            vmax=vmax,
        )
        ax.annotate(
            f"t = {frame.time/(2*np.pi):.2f} orbit",
            xy=(0.1, 0.1),
            xycoords="axes fraction",
            c="black",
        )

    fig.colorbar(im, ax=axs, shrink=0.8)

    return fig


def main(output_dir):

    sigma = TimeSeqData(output_dir, phys_var_type="dens")
    sigma_fig = fancy_suplots(sigma, "$\Sigma$")
    sigma_fig.savefig(
        os.path.join(output_dir, "dens-simulated-cartesian-row.png"), format="png"
    )
    v_r = TimeSeqData(output_dir, phys_var_type="vy")
    v_r_fig = fancy_suplots(v_r, "$v_r$")
    v_r_fig.savefig(
        os.path.join(output_dir, "vy-simulated-cartesian-row.png"), format="png"
    )
    v_theta = TimeSeqData(output_dir, phys_var_type="vx")
    v_theta_fig = fancy_suplots(v_theta, "$v_{\\theta}$")
    v_theta_fig.savefig(
        os.path.join(output_dir, "vx-simulated-cartesian-row.png"), format="png"
    )


if __name__ == "__main__":
    main(get_config().output_dir)
