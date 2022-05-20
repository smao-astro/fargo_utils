import os
import re
from glob import glob

import matplotlib.animation as animation
import matplotlib.figure
import matplotlib.pyplot as plt
import numpy as np
import skimage.transform


def get_frame_index(file_path: str) -> int:
    """Extract the index of frame from file name

    :param file_path: the file path of FARGO3D outputs data |
        e.g. job/2020-05-30_13-17-14/outputs/gasdens5.dat
    :return: the number included in the file name |
        e.g. 5
    """
    file_name = os.path.basename(file_path)
    return int(re.findall("\d+", file_name)[0])


def neighbor_average(array: np.ndarray) -> np.ndarray:
    """compute the coordinate value at cell center using the coordinate at cell edges

    :param array: 1D array, coordinate values along one axis
    :return: the coordinate value at cell center
    """
    return (array[1:] + array[:-1]) / 2.0


def get_setup(output_dir: str) -> dict:
    """read the setup of FARGO3D simulation from ``variables.par``

    Make sure that ``variables.par`` exists.
    the value stored as string, manually convert to float/int is needed when using.

    :param output_dir: the directory path of the FARGO3D outputs
    :return: key-value pairs for the setup parameters
    """
    setup = {}
    with open(os.path.join(output_dir, "variables.par")) as f:
        lines = f.readlines()
        for line in lines:
            key, value = line.split()
            setup[key] = value

    return setup


class Coor(object):
    """class that store the coordinate values of grid used by FARGO3D"""

    def __init__(self, output_dir: str):
        """

        :param output_dir: the directory path of the FARGO3D outputs
        """
        self._output_dir = output_dir
        self._setup = get_setup(output_dir)
        self._NGHY = 3
        self._x_edge = self.get_x_edge()
        self._y_edge = self.get_y_edge()
        self._x_center = neighbor_average(self.x_edge)
        self._y_center = neighbor_average(self.y_edge)

    def get_x_edge(self):
        # check whether x axis is used in fargo simulation
        assert int(self._setup["NX"]) != 1, "Warning: int(self._setup['NX']) == 1"
        # check whether the shape match the parameter in variables.par
        x_edge = np.loadtxt(os.path.join(self._output_dir, "domain_x.dat"))
        assert x_edge.shape[0] - 1 == int(
            self._setup["NX"]
        ), "x coor shape do not match NX"
        # check whether the begining and ending of the coor match the min and max in variables.par
        assert np.isclose(x_edge[0], float(self._setup["XMIN"])) and np.isclose(
            x_edge[-1], float(self._setup["XMAX"])
        )
        return x_edge

    def get_y_edge(self):
        # check whether y axis is used in fargo simulation
        assert int(self._setup["NY"]) != 1, "Warning: int(self._setup['NY']) == 1"

        y_edge = np.loadtxt(os.path.join(self._output_dir, "domain_y.dat"))
        # check whether the shape match the parameter in variables.par
        assert (
            y_edge.shape[0] - 1 == int(self._setup["NY"]) + 2 * self._NGHY
        ), "y coor shape do not match NY"
        # crop y coor
        y_edge = y_edge[3:-3]
        # check whether the begining and ending of the coor match the min and max in variables.par
        assert np.isclose(y_edge[0], float(self._setup["YMIN"])) and np.isclose(
            y_edge[-1], float(self._setup["YMAX"])
        )
        return y_edge

    @property
    def x_edge(self) -> np.ndarray:
        """

        :return: array with shape (NX+1,)
        """
        return np.copy(self._x_edge)

    @property
    def y_edge(self) -> np.ndarray:
        """

        :return: Array with shape (NY+1,)
        """
        return np.copy(self._y_edge)

    @property
    def x_center(self) -> np.ndarray:
        """

        :return: Array with shape (NX,)
        """
        # check whether the shape match the parameter in variables.par
        assert self._x_center.shape[0] == int(
            self._setup["NX"]
        ), "x coor shape do not match NX"
        return np.copy(self._x_center)

    @property
    def y_center(self) -> np.ndarray:
        """

        :return: Array with shape (NY,)
        """
        # check whether the shape match the parameter in variables.par
        assert self._y_center.shape[0] == int(
            self._setup["NY"]
        ), "y coor shape do not match NY"
        return np.copy(self._y_center)

    @property
    def x_min(self):
        """

        :return: Array with shape (NX,)
        """
        return np.copy(self.x_edge[:-1])

    @property
    def y_min(self):
        """

        :return: Array with shape (NY,)
        """
        return np.copy(self.y_edge[:-1])

    @property
    def grid_center(self) -> np.ndarray:
        """coordinate values of grid for centering variables

        default for dens

        :return: (NY, NX, 2)
        """
        x_grid, y_grid = np.meshgrid(self.x_center, self.y_center, indexing="xy")
        return np.stack([x_grid, y_grid], axis=-1)

    @property
    def grid_x_staggered(self) -> np.ndarray:
        """coordinate values of grid for x-staggering variables

        default for vx

        :return: (NY, NX, 2)
        """
        x_grid, y_grid = np.meshgrid(self.x_min, self.y_center, indexing="xy")
        return np.stack([x_grid, y_grid], axis=-1)

    @property
    def grid_y_staggered(self) -> np.ndarray:
        """coordinate values of grid for y-staggering variables

        default for vy

        :return: (NY, NX, 2)
        """
        x_grid, y_grid = np.meshgrid(self.x_center, self.y_min, indexing="xy")
        return np.stack([x_grid, y_grid], axis=-1)


class CartesianToPolar:
    def __init__(self, nxy, nr, ntheta, rmin, rmax, theta_min, theta_max):
        self.nxy = nxy
        self.nr = nr
        self.ntheta = ntheta
        self.rmin = rmin
        self.rmax = rmax
        self.theta_min = theta_min
        self.theta_max = theta_max

    def __call__(self, output_coor):
        # pixel to coordinate
        output_coor = 2 * self.rmax * (output_coor / self.nxy - 0.5)
        """(column, row)"""

        x, y = np.split(output_coor, 2, axis=1)
        r = np.sqrt(x ** 2 + y ** 2)
        theta = np.arctan2(y, x)
        """from -pi to pi"""

        # coordinate to pixel
        r = (r - self.rmin) / (self.rmax - self.rmin) * self.nr
        theta = (
            (theta - self.theta_min) / (self.theta_max - self.theta_min) * self.ntheta
        )

        return np.hstack([theta, r])


class GridData(object):
    """FARGO3D output data from one file, such as ``gasdens5.dat``, at one time step, include only one physical
    variable.

    """

    def __init__(self, file_path: str, ny: int, nx: int):
        self.file_path = file_path
        self._ny = ny
        self._nx = nx
        self._grid_value = None

    @property
    def phys_var_type(self) -> str:
        """physics variable type (name), could be **dens** / **vx** / **vy**

            it is auto determined from the file name

        :return: physics variable type (name)
        """
        file_name = os.path.basename(self.file_path)
        for choice in ["dens", "vx", "vy"]:
            if choice in file_name:
                return choice
        else:
            raise TypeError(
                "can not determine data file type, expect ['dens', 'vx', 'vy']"
            )

    @property
    def frame_index(self) -> int:
        """index that indicate the number of NINTERM (time) since start

            t = frame_index * NINTERM * DT

        :return: frame_index
        """
        return get_frame_index(self.file_path)

    def __read_data(self) -> np.ndarray:
        """

        :return: (NY, NX, 1)
        """
        return np.fromfile(self.file_path, dtype=np.float).reshape(
            self._ny, self._nx, 1
        )

    @property
    def value(self) -> np.ndarray:
        """the value at every cell in the grid

        it can represent 3 physical quantity: **dens**, **vx**, **vy**
        the position of each quantity is specified by the simulation,
        by default **dens** is centered, **vx** is on the interface of x axis between two cell (x staggering), **vy** staggering on y

        :return: (NY, NX, 1)
        """
        # TODO I am not sure whether or not this is safe
        if self._grid_value is None:
            self._grid_value = self.__read_data()
        return np.copy(self._grid_value)

    @property
    def mean_value_over_x(self) -> np.ndarray:
        """Mean value over azimuthal direction.

        :return: (NY,)
        """
        return np.mean(self.value, axis=1).flatten()


class FrameData(GridData):
    """FARGO3D output data from one file, such as ``gasdens5.dat``, at one time step, include only one physical
    variable.

    """

    def __init__(self, file_path: str, setup: dict, grid):
        """

        :param file_path: the file path of FARGO3D outputs data
        :param setup: FARGO3D setup parameter which defined the simulation problem. |
            setup = get_setup(output_dir)
        :param grid: Array that contain the coordinate value of grid, shape (NY, NX, 2).
        """
        self._setup = setup
        super(FrameData, self).__init__(
            file_path=file_path, ny=int(setup["NY"]), nx=int(setup["NX"])
        )
        self.grid = grid

    @property
    def time(self) -> float:
        return self.frame_index * int(self._setup["NINTERM"]) * float(self._setup["DT"])

    @property
    def orbit(self) -> float:
        return self.time / (2 * np.pi)

    @property
    def setup(self) -> dict:
        return self._setup

    @property
    def xy_value(self):
        """

        :return: Array with the first two column contain the coordinates and the third column the data value,
        shape (NY, NX, 3).
        """
        grid_value = self.value
        return np.concatenate([self.grid, grid_value], axis=-1)

    @property
    def flt_xy_value(self):
        """

        :return: Array with shape (NY * NX, 3).
        """
        return np.vstack(self.xy_value)

    @property
    def xyt_value(self):
        """insert t to last axis, third column

        :return: Array with shape (NY, NX, 4).
        """
        return np.insert(self.xy_value, obj=-1, values=self.time, axis=-1)

    @property
    def flt_xyt_value(self):
        return np.vstack(self.xyt_value)

    @property
    def x_ymin_t_value(self):
        return self.xyt_value[0]

    @property
    def x_ymax_t_value(self):
        return self.xyt_value[-1]

    @property
    def xmin(self):
        return np.amin(self.grid[..., 0])

    @property
    def xmax(self):
        return np.amax(self.grid[..., 0])

    @property
    def ymin(self):
        return np.amin(self.grid[..., 1])

    @property
    def ymax(self):
        return np.amax(self.grid[..., 1])

    def to_cartesian(self, nxy):
        cartesian_to_polar = CartesianToPolar(
            nxy,
            nr=self._ny,
            ntheta=self._nx,
            rmin=self.ymin,
            rmax=self.ymax,
            theta_min=self.xmin,
            theta_max=self.xmax,
        )
        value = self.value.reshape(self.value.shape[:2])
        return skimage.transform.warp(
            value, cartesian_to_polar, output_shape=(nxy, nxy)
        )


class TimeSeqData(object):
    def __init__(self, output_dir: str, phys_var_type: str):
        """

        :param str output_dir: the directory path of the FARGO3D outputs
            e.g. /Users/kyika/project/pinn/disk2D/job/2021-01-20_23-40-18/outputs
        :param str phys_var_type: expect ['dens', 'vx', 'vy']
        """
        self.output_dir = output_dir
        self.phys_var_type = phys_var_type
        self._setup = get_setup(self.output_dir)
        self._coor = Coor(self.output_dir)

    @property
    def coor(self) -> Coor:
        return self._coor

    @property
    def x(self) -> np.array:
        if self.phys_var_type == "dens":
            return self.coor.x_center
        elif self.phys_var_type == "vx":
            return self.coor.x_min
        elif self.phys_var_type == "vy":
            return self.coor.x_center
        else:
            raise KeyError(f"{self.phys_var_type}")

    @property
    def y(self) -> np.array:
        if self.phys_var_type == "dens":
            return self.coor.y_center
        elif self.phys_var_type == "vx":
            return self.coor.y_center
        elif self.phys_var_type == "vy":
            return self.coor.y_min
        else:
            raise KeyError(f"{self.phys_var_type}")

    @property
    def grid(self):
        if self.phys_var_type == "dens":
            return self.coor.grid_center
        elif self.phys_var_type == "vx":
            return self.coor.grid_x_staggered
        elif self.phys_var_type == "vy":
            return self.coor.grid_y_staggered
        else:
            raise KeyError(f"{self.phys_var_type}")

    @property
    def file_list(self):
        return sorted(
            glob(
                os.path.join(self.output_dir, "*" + self.phys_var_type + "*[0-9].dat")
            ),
            key=get_frame_index,
        )

    @property
    def frames(self):
        return [FrameData(file, self._setup, self.grid) for file in self.file_list]

    @property
    def t(self):
        return np.array([frame.time for frame in self.frames])

    @property
    def values(self):
        # (NT, NY, NX, 1)
        return np.stack([frame.value for frame in self.frames], axis=0)

    @property
    def flt_xyt_value(self) -> np.ndarray:
        """the x, y, time and result of fargo outputs

            x -> theta, y-> r

        :return: (N, 4)
        """
        data_list = [frame.flt_xyt_value for frame in self.frames]
        return np.vstack(data_list)  # concatenate all the files (frames) vertically

    @property
    def flt_x_ymin_t_value(self) -> np.ndarray:
        data_list = [frame.x_ymin_t_value for frame in self.frames]
        return np.vstack(data_list)

    @property
    def flt_x_ymax_t_value(self) -> np.ndarray:
        data_list = [frame.x_ymax_t_value for frame in self.frames]
        return np.vstack(data_list)

    @property
    def flt_r_theta_t_value(self) -> np.ndarray:
        """the r, \theta, time and result of fargo outputs

            x -> theta, y-> r

        :return: (N, 4)
        """
        return self.flt_xyt_value[:, [1, 0, 2, 3]]

    @property
    def flt_rmin_theta_t_value(self) -> np.ndarray:
        return self.flt_x_ymin_t_value[:, [1, 0, 2, 3]]

    @property
    def flt_rmax_theta_t_value(self) -> np.ndarray:
        return self.flt_x_ymax_t_value[:, [1, 0, 2, 3]]

    def plot_mean_over_x(
        self,
        period_of_t_step,
        figsize=plt.rcParams["figure.figsize"],
        legend_prec: int = 3,
        ymin=None,
        ymax=None,
    ) -> matplotlib.figure.Figure:
        value_list = [frame.mean_value_over_x for frame in self.frames]
        value_list = value_list[::period_of_t_step]
        t_list = self.t[::period_of_t_step]

        fig, ax = plt.subplots(1, 1, figsize=figsize)
        # get x axis
        if self.phys_var_type == "vy":
            x_axis = self.coor.y_min
        else:
            x_axis = self.coor.y_center

        for i, (value, t) in enumerate(zip(value_list, t_list)):
            ax.plot(
                x_axis,
                value,
                "-",
                label=f"{t/(2.0 * np.pi):.{legend_prec}f} orbit",
            )
        ax.set_ylim(ymin, ymax)
        plt.legend()
        return fig

    def get_single_animation(self):
        fig = plt.figure()
        plt.xlabel(r"$\theta$")
        plt.ylabel(r"$R/R_0$")
        plt.xticks(
            ticks=[-np.pi, -np.pi / 2, 0, np.pi / 2, np.pi],
            labels=[r"$-\pi$", r"$-\pi/2$", "0", r"$\pi/2$", r"$\pi$"],
        )
        plt.title(f"{self.phys_var_type}")

        # get vmin, vmax
        values = self.flt_xyt_value[:, -1]
        vmin = np.min(values)
        vmax = np.max(values)

        artists = []
        for t_step, file in enumerate(self.file_list):
            frame = FrameData(file, self._setup, self.grid)
            im = plt.imshow(
                frame.value,
                aspect=self.grid.shape[1] / self.grid.shape[0],
                extent=[
                    np.min(self.grid[:, :, 0]),
                    np.max(self.grid[:, :, 0]),
                    np.max(self.grid[:, :, 1]),
                    np.min(self.grid[:, :, 1]),
                ],
                vmin=vmin,
                vmax=vmax,
            )
            annotation = plt.annotate(
                f"t = {frame.time:.2f}",
                xy=(0.1, 0.1),
                xycoords="axes fraction",
                c="white",
            )
            if t_step == 0:
                plt.colorbar()  # Colorbar do not change over time
            artists.append([im, annotation])

        ani = animation.ArtistAnimation(fig, artists, interval=180, repeat=False)
        ani.save(
            os.path.join(self.output_dir, self.phys_var_type + "-simulated" + ".mp4")
        )

    def get_single_frame_cartesian(self, nxy=1000):
        # get vmin, vmax
        values = self.flt_xyt_value[:, -1]
        vmin = np.min(values)
        vmax = np.max(values)

        for i_step, frame in enumerate(self.frames):
            plt.figure()
            plt.xlabel(r"$x/R_0$")
            plt.ylabel(r"$y/R_0$")
            plt.title(f"{self.phys_var_type}")

            plt.imshow(
                frame.to_cartesian(nxy),
                origin="lower",
                extent=[
                    -frame.ymax,
                    frame.ymax,
                    -frame.ymax,
                    frame.ymax,
                ],
                aspect="equal",
                vmin=vmin,
                vmax=vmax,
            )
            plt.annotate(
                f"t = {frame.time/(2*np.pi):.2f} orbit",
                xy=(0.1, 0.1),
                xycoords="axes fraction",
                c="white",
            )
            plt.colorbar()

            # save fig
            plt.savefig(
                fname=os.path.join(
                    self.output_dir,
                    self.phys_var_type + "-simulated-cartesian-" + str(i_step) + ".png",
                ),
                format="png",
            )
            plt.close()

    def get_single_animation_cartesian(self, nxy=1000):
        fig = plt.figure()
        plt.xlabel(r"$x/R_0$")
        plt.ylabel(r"$y/R_0$")
        plt.title(f"{self.phys_var_type}")

        # get vmin, vmax
        values = self.flt_xyt_value[:, -1]
        vmin = np.min(values)
        vmax = np.max(values)

        artists = []
        for t_step, file in enumerate(self.file_list):
            frame = FrameData(file, self._setup, self.grid)
            im = plt.imshow(
                frame.to_cartesian(nxy),
                origin="lower",
                extent=[
                    -frame.ymax,
                    frame.ymax,
                    -frame.ymax,
                    frame.ymax,
                ],
                aspect="equal",
                vmin=vmin,
                vmax=vmax,
            )
            annotation = plt.annotate(
                f"t = {frame.time:.2f}",
                xy=(0.1, 0.1),
                xycoords="axes fraction",
                c="white",
            )
            if t_step == 0:
                plt.colorbar()  # Colorbar do not change over time
            artists.append([im, annotation])

        ani = animation.ArtistAnimation(fig, artists, interval=180, repeat=False)
        ani.save(
            os.path.join(
                self.output_dir,
                self.phys_var_type + "-simulated" + "-cartesian" + ".mp4",
            )
        )
