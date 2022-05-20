import os

import numpy as np

from .config import get_config
from .fargoData import TimeSeqData


def main(output_dir):
    """convert fargo outputs to npz file with (N, 4) shape."""

    dens = TimeSeqData(output_dir, phys_var_type="dens")
    vx = TimeSeqData(output_dir, phys_var_type="vx")
    vy = TimeSeqData(output_dir, phys_var_type="vy")
    for var, name in zip((dens, vx, vy), ("sigma", "vtheta", "vr")):
        diff = np.abs(var.values[1:] - var.values[0])
        diff_max = np.max(diff, axis=(1, 2, 3))
        diff_mean = np.mean(diff, axis=(1, 2, 3))
        print("=" * 20)
        print(f"shape of diff = {diff.shape}")
        print(f"{name}: mean of diff = {diff_mean}")
        print(np.mean(diff))
        print(f"{name}: max of diff = {diff_max}")
        print(np.max(diff))
        print("=" * 20)


if __name__ == "__main__":
    main(get_config().output_dir)
