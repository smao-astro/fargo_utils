import argparse
import os

import matplotlib.pyplot as plt

from .fargoData import TimeSeqData


def main(
    output_dir,
    period_of_t_step,
    fig_width,
    fig_height,
    font_size,
    legend_prec,
    sigma_ymin,
    sigma_ymax,
    v_r_ymin,
    v_r_ymax,
    v_theta_ymin,
    v_theta_ymax,
):

    plt.rcParams.update({"font.size": font_size})
    sigma = TimeSeqData(output_dir, phys_var_type="dens")
    sigma_fig = sigma.plot_mean_over_x(
        period_of_t_step,
        figsize=(fig_width, fig_height),
        legend_prec=legend_prec,
        ymin=sigma_ymin,
        ymax=sigma_ymax,
    )
    sigma_fig.savefig(
        os.path.join(output_dir, sigma.phys_var_type + "-simulated-radial.png"),
        format="png",
    )

    v_r = TimeSeqData(output_dir, phys_var_type="vy")
    v_r_fig = v_r.plot_mean_over_x(
        period_of_t_step,
        figsize=(fig_width, fig_height),
        legend_prec=legend_prec,
        ymin=v_r_ymin,
        ymax=v_r_ymax,
    )
    # v_r_fig.get_axes()[0].get_legend().remove()
    # v_r_fig.legend(loc='lower right')
    v_r_fig.savefig(
        os.path.join(output_dir, v_r.phys_var_type + "-simulated-radial.png"),
        format="png",
    )

    v_theta = TimeSeqData(output_dir, phys_var_type="vx")
    v_theta_fig = v_theta.plot_mean_over_x(
        period_of_t_step,
        figsize=(fig_width, fig_height),
        legend_prec=legend_prec,
        ymin=v_theta_ymin,
        ymax=v_theta_ymax,
    )
    v_theta_fig.savefig(
        os.path.join(output_dir, v_theta.phys_var_type + "-simulated-radial.png"),
        format="png",
    )
    plt.rcParams.update(plt.rcParamsDefault)


if __name__ == "__main__":
    parser = argparse.ArgumentParser("main")
    parser.add_argument("--output_dir", type=str, default="fargo3d/outputs")
    parser.add_argument("--period_of_t_step", type=int, default=5)
    parser.add_argument(
        "--fig_width", type=float, default=plt.rcParamsDefault["figure.figsize"][0]
    )
    parser.add_argument(
        "--fig_height", type=float, default=plt.rcParamsDefault["figure.figsize"][1]
    )
    parser.add_argument(
        "--font_size", type=float, default=plt.rcParamsDefault["font.size"]
    )
    parser.add_argument("--legend_prec", type=int, default=2)
    parser.add_argument("--sigma_ymin", type=float)
    parser.add_argument("--sigma_ymax", type=float)
    parser.add_argument("--v_r_ymin", type=float)
    parser.add_argument("--v_r_ymax", type=float)
    parser.add_argument("--v_theta_ymin", type=float)
    parser.add_argument("--v_theta_ymax", type=float)
    config = parser.parse_args()
    main(
        output_dir=config.output_dir,
        period_of_t_step=config.period_of_t_step,
        fig_width=config.fig_width,
        fig_height=config.fig_height,
        font_size=config.font_size,
        legend_prec=config.legend_prec,
        sigma_ymin=config.sigma_ymin,
        sigma_ymax=config.sigma_ymax,
        v_r_ymin=config.v_r_ymin,
        v_r_ymax=config.v_r_ymax,
        v_theta_ymin=config.v_theta_ymin,
        v_theta_ymax=config.v_theta_ymax,
    )
