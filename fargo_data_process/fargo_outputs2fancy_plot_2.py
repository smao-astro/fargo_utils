import os

import matplotlib.figure
import matplotlib.pyplot as plt
import numpy as np

from .config import get_config
from .fargoData import TimeSeqData


def fancy_suplots(
    sigma: TimeSeqData,
    vx: TimeSeqData,
    vy: TimeSeqData,
    title: str,
    nxy=1000,
) -> matplotlib.figure.Figure:
    # values = data.flt_xyt_value[:, -1]
    # vmin = np.min(values)
    # vmax = np.max(values)

    fig = plt.figure(figsize=(10.0, 9), constrained_layout=True)
    # fig.suptitle(title)
    fig.supxlabel("$x/R_0$")
    fig.supylabel("$y/R_0$")
    axs = fig.subplots(
        3, 3, sharex=True, sharey=True, gridspec_kw={"wspace": 0.0, "hspace": 0.0}
    )
    for ax_row, data, cmap, label in zip(
        axs,
        (sigma, vy, vx),
        ("Reds", "bwr", "Reds"),
        ("$\Sigma$", "$v_r$", "$v_{\\theta}$"),
    ):
        # vmin, vmax
        values = data.flt_xyt_value[:, -1]
        vmin = np.min(values)
        vmax = np.max(values)

        for ax, frame in zip(
            ax_row, [data.frames[0], data.frames[10], data.frames[20]]
        ):
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

        cbar = fig.colorbar(im, ax=ax_row, shrink=0.8)
        cbar.set_label(label, fontsize="xx-large")

    return fig


def main(output_dir):

    sigma = TimeSeqData(output_dir, phys_var_type="dens")
    v_r = TimeSeqData(output_dir, phys_var_type="vy")
    v_theta = TimeSeqData(output_dir, phys_var_type="vx")
    fig = fancy_suplots(sigma, vx=v_theta, vy=v_r, title="")
    fig.savefig(os.path.join(output_dir, "all-simulated-cartesian.png"), format="png")


if __name__ == "__main__":
    main(get_config().output_dir)
