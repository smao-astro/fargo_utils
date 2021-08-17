from .config import get_config
from .fargoData import TimeSeqData


def main(output_dir):

    sigma = TimeSeqData(output_dir, phys_var_type="dens")
    sigma.get_single_animation()
    sigma.get_single_animation_cartesian()
    v_r = TimeSeqData(output_dir, phys_var_type="vy")
    v_r.get_single_animation()
    v_theta = TimeSeqData(output_dir, phys_var_type="vx")
    v_theta.get_single_animation()


if __name__ == "__main__":
    main(get_config().output_dir)
