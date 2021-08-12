import pathlib
import shutil

from . import boundary
from . import ic
from . import opt


def create_setups(cfg):
    # set setups dir
    p = pathlib.Path(cfg.setups_dir)
    # check exists
    if p.exists():
        raise FileExistsError
    # create
    p.mkdir()

    # bound file
    bound_args = boundary.cfg_to_nested_dict(cfg)
    bound_file = p / (cfg.setup_name + ".bound")
    boundary.write_boundlines(bound_args, bound_file)

    # copy bound to bound.0
    shutil.copy(bound_file, bound_file / ".0")

    # ic file (move matched file from setup_base)
    ic_file = ic.get_condinit_file(cfg.DensityInitial, cfg.VxInitial, cfg.VyInitial)
    shutil.copy(ic_file, p / "condinit.c")

    # opt file
    opt_file = p / (cfg.setup_name + ".opt")
    shutil.copy("./setup_base/opt/base.opt", opt_file)
    opts = {k: getattr(cfg, k) for k in opt.opts}
    opt.update_opt_file(opt_file, opts)

    # par file
