import pathlib
import shutil

from . import boundary
from . import ic
from . import opt
from . import par


def create_setups(arg_groups: dict):
    # set setups dir
    p = pathlib.Path(arg_groups["optional arguments"].setups_dir)
    # check exists
    if p.exists():
        raise FileExistsError
    # create
    p.mkdir()

    # bound file
    bound_args = boundary.cfg_to_nested_dict(arg_groups["bc"])
    bound_file = p / (arg_groups["par"].Setup + ".bound")
    boundary.write_boundlines(bound_args, bound_file)

    # copy bound to bound.0
    shutil.copy(bound_file, bound_file / ".0")

    # ic file (move matched file from setup_base)
    ic_file = ic.get_condinit_file(
        arg_groups["ic"].DensityInitial,
        arg_groups["ic"].VxInitial,
        arg_groups["ic"].VyInitial,
    )
    shutil.copy(ic_file, p / "condinit.c")

    # opt file
    opt_file = p / (arg_groups["par"].Setup + ".opt")
    shutil.copy("./setup_base/opt/base.opt", opt_file)
    opt.update_opt_file(opt_file, arg_groups["opt"])

    # par file
    par_file = p / (arg_groups["'optional arguments'"].job_name + ".par")
    par.write_args(par_file, args=arg_groups["par"])
