import os

from scipy.io import savemat

from .config import get_config
from .fargoData import TimeSeqData


def main(output_dir):
    """convert fargo outputs to npz file with (N, 4) shape."""

    dens = TimeSeqData(output_dir, phys_var_type="dens").flt_r_theta_t_value
    print(f"dens shape {dens.shape}")
    vx = TimeSeqData(output_dir, phys_var_type="vx").flt_r_theta_t_value
    print(f"vx shape {vx.shape}")
    vy = TimeSeqData(output_dir, phys_var_type="vy").flt_r_theta_t_value
    print(f"vy shape {vy.shape}")
    # np.savez(os.path.join(output_dir, 'test_data.npz'), dens=dens, vx=vx, vy=vy)
    savemat(
        file_name=os.path.join(output_dir, "test_data.mat"),
        mdict={"dens": dens, "vx": vx, "vy": vy},
    )


if __name__ == "__main__":
    main(get_config().output_dir)
