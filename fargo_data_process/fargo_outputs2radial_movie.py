import argparse
import os

import numpy as np

import jaxdisk2D.physics_informed_training.postprocess.animation as ANIMATION
from .fargoData import TimeSeqData


def main(
    output_dir,
    period_of_t_step,
    legend_prec,
    sigma_ymin,
    sigma_ymax,
    v_r_ymin,
    v_r_ymax,
    v_theta_ymin,
    v_theta_ymax,
    r_min,
    r_max,
):
    _r_min = -np.inf if r_min is None else r_min
    _r_max = np.inf if r_max is None else r_max
    for phys_var_type, y_min, y_max in zip(
        ["dens", "vx", "vy"],
        [sigma_ymin, v_theta_ymin, v_r_ymin],
        [sigma_ymax, v_theta_ymax, v_r_ymax],
    ):
        tsdata = TimeSeqData(output_dir, phys_var_type=phys_var_type)
        # get r
        r = tsdata.y
        # get values
        value_list = [frame.mean_value_over_x for frame in tsdata.frames]
        value_list = np.array(value_list[::period_of_t_step])
        # filter by r_min and r_max
        selected_index = np.logical_and(r > _r_min, r < _r_max)
        r = r[selected_index]
        value_list = value_list[..., selected_index]
        # ANIMATION.RadialDistributionEvolution require that value_list is a list of (t_num, r_num) array.
        value_list = [value_list]
        # get t
        t = tsdata.t[::period_of_t_step]
        # get ani
        ani = ANIMATION.RadialDistributionEvolution(
            r,
            value_list,
            t,
            title_func=lambda t_: f"{tsdata.phys_var_type}: time={t_ / (2 * np.pi):.{legend_prec}f} orbit",
            label_func=lambda _: "FARGO",
            y_min=y_min,
            y_max=y_max,
        )
        # save
        if r_min is not None or r_max is not None:
            ani.animation.save(
                os.path.join(
                    output_dir,
                    "radial-"
                    + tsdata.phys_var_type
                    + "-fargo"
                    + f"-{r_min}-{r_max}"
                    + ".mp4",
                )
            )
        else:
            ani.animation.save(
                os.path.join(
                    output_dir, "radial-" + tsdata.phys_var_type + "-fargo" + ".mp4"
                )
            )


if __name__ == "__main__":
    # config
    parser = argparse.ArgumentParser("main")
    parser.add_argument("--output_dir", type=str, default="fargo3d/outputs")
    parser.add_argument("--period_of_t_step", type=int, default=1)
    parser.add_argument("--legend_prec", type=int, default=3)
    parser.add_argument("--sigma_ymin", type=float)
    parser.add_argument("--sigma_ymax", type=float)
    parser.add_argument("--v_r_ymin", type=float)
    parser.add_argument("--v_r_ymax", type=float)
    parser.add_argument("--v_theta_ymin", type=float)
    parser.add_argument("--v_theta_ymax", type=float)
    parser.add_argument("--r_min", type=float)
    parser.add_argument("--r_max", type=float)
    config = parser.parse_args()

    # run
    main(
        output_dir=config.output_dir,
        period_of_t_step=config.period_of_t_step,
        legend_prec=config.legend_prec,
        sigma_ymin=config.sigma_ymin,
        sigma_ymax=config.sigma_ymax,
        v_r_ymin=config.v_r_ymin,
        v_r_ymax=config.v_r_ymax,
        v_theta_ymin=config.v_theta_ymin,
        v_theta_ymax=config.v_theta_ymax,
        r_min=config.r_min,
        r_max=config.r_max,
    )
