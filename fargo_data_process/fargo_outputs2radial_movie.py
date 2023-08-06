import argparse
import os

import matplotlib.animation as ani
import matplotlib.pyplot as plt
import numpy as np

from .fargoData import TimeSeqData


class RadialDistributionEvolution:
    def __init__(
        self,
        r,
        values,
        t,
        title_func,
        label_func,
        y_axis_name="values",
        y_min=None,
        y_max=None,
    ):
        """

        Args:
            r: (r_num,) array. Radial distance at each sample position.
            values: A list of (t_num, r_num) array. An array of evolution of the radial distribution of the values.
                E.g. from SelfSimilarSolution.postprocess.data.GridTimeSeriesXY.mean_values_over_theta.
            t: (t_num,) array.
            label_func: A function of values' (list) index.
            title_func: A function of t.

        Attributes:
            values: (t_num, N, r_num) array. N == len(values).
        """
        self.r = r
        if not isinstance(values, (list, tuple)):
            values = [values]
        self.values = np.stack(values, axis=1)
        self.t = t
        self.title_func = title_func
        self.label_func = label_func
        self.y_axis_name = y_axis_name

        self.fig, self.ax = plt.subplots()
        self.fig.subplots_adjust(bottom=0.15)
        self.fig.subplots_adjust(left=0.20)
        self.lines = []
        for i in range(self.values.shape[1]):
            # frame t==0
            self.lines.append(
                self.ax.plot(
                    self.r,
                    self.values[0, i],
                    "-",
                    label=self.label_func(i),
                )[0]
            )

        self.y_min = np.min(self.values) if y_min is None else y_min
        self.y_max = np.max(self.values) if y_max is None else y_max

    def _init(self):
        self.ax.set_xlabel(r"$r/R_0$")
        self.ax.set_ylabel(self.y_axis_name)
        self.ax.set_ylim(self.y_min, self.y_max)
        self.ax.legend(fontsize="small")
        return self.lines

    def _animate(self, values_and_t):
        values, t = values_and_t
        for line, value in zip(self.lines, values):
            line.set_ydata(value)
        self.ax.set_title(self.title_func(t), pad=10)
        return self.lines

    @property
    def animation(self):
        frames = list(zip(self.values, self.t))
        return ani.FuncAnimation(
            self.fig, self._animate, frames, self._init, repeat=False, interval=180
        )


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
        ani = RadialDistributionEvolution(
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
