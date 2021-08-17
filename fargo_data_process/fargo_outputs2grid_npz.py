import os

import numpy as np

from .config import get_config
from .fargoData import TimeSeqData


def main(output_dir):

    for phys_var_type in ["dens", "vy", "vx"]:
        var = TimeSeqData(output_dir, phys_var_type)
        np.savez(
            os.path.join(output_dir, phys_var_type + "_" + "grid.npz"),
            t=var.t,
            y=var.y,
            x=var.x,
            values=var.values,
        )


if __name__ == "__main__":
    main(get_config().output_dir)
