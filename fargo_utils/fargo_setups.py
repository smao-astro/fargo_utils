import os
import pathlib
import pickle
import shutil
import subprocess
import importlib.resources
from . import par

from . import setup_base
from . import boundary
from . import config
from . import ic
from . import opt


def create_setups(arg_groups: dict):
    # set setups dir
    p = (
        pathlib.Path(arg_groups["optional arguments"].setups_dir)
        / arg_groups["optional arguments"].Setup
    )
    # check exists
    if p.exists():
        raise FileExistsError
    # create
    p.mkdir(parents=True)

    # bound file
    bound_args = boundary.cfg_to_nested_dict(arg_groups["bc"])
    bound_file = p / (arg_groups["optional arguments"].Setup + ".bound")
    boundary.write_boundlines(bound_args, bound_file)

    # copy bound to bound.0
    shutil.copy(bound_file, p / (arg_groups["optional arguments"].Setup + ".bound.0"))

    with importlib.resources.path(setup_base, "boundaries.txt") as base_par_file:
        shutil.copy(base_par_file, p)

    # ic file (move matched file from setup_base)
    ic_file = ic.get_condinit_file(
        arg_groups["ic"].DensityInitial,
        arg_groups["ic"].VxInitial,
        arg_groups["ic"].VyInitial,
    )
    shutil.copy(ic_file, p / "condinit.c")

    # opt file
    opt_file = p / (arg_groups["optional arguments"].Setup + ".opt")
    # with importlib.resources.path(setup_base.opt, "base.opt") as base_opt:
    #     shutil.copy(base_opt, opt_file)
    # opt.update_opt_file(opt_file, arg_groups["opt"])
    opt.write_opt_file(opt_file, arg_groups["opt"])

    # write default par file
    par_file = p / f"{arg_groups['optional arguments'].Setup}.par"
    with importlib.resources.path(setup_base, "setup.par") as base_par_file:
        shutil.copyfile(base_par_file, par_file)
    # Setup and ic related parameters are needed in the par file at make time
    # to make sure these parameters are in the file `outputs/variables.par`.
    paramters = {"Setup": arg_groups["optional arguments"].Setup}
    paramters.update(vars(arg_groups["ic"]))
    lines = par.args_to_lines(paramters)
    with par_file.open("a") as f:
        f.writelines(lines)

    # save arg_groups
    with open(p / "arg_groups.pkl", "wb") as f:
        pickle.dump(arg_groups, f)

    return p


if __name__ == "__main__":
    arg_groups = config.get_arg_groups()
    print(arg_groups)
    setup_dir = create_setups(arg_groups)
    config.save_arg_groups(arg_groups, "fargo3d/arg_groups.yml")
    # cd fargo3d
    os.chdir("fargo3d")
    # make
    make_command = [
        "make",
        f"SETUP={arg_groups['optional arguments'].Setup}",
        f"BIGMEM={arg_groups['make'].BIGMEM}",
        f"RESCALE={arg_groups['make'].RESCALE}",
        f"PROFILING={arg_groups['make'].PROFILING}",
        f"PARALLEL={arg_groups['make'].PARALLEL}",
        f"MPICUDA={arg_groups['make'].MPICUDA}",
        f"GPU={arg_groups['make'].GPU}",
        f"DEBUG={arg_groups['make'].DEBUG}",
        f"FULLDEBUG={arg_groups['make'].FULLDEBUG}",
        f"FARGO_DISPLAY={arg_groups['make'].FARGO_DISPLAY}",
        f"UNITS={arg_groups['make'].UNITS}",
        f"GHOSTSX={arg_groups['make'].GHOSTSX}",
        f"LONGSUMMARY={arg_groups['make'].LONGSUMMARY}",
    ]
    print(make_command)
    subprocess.run(make_command)
    # make clean
    subprocess.run(["make", "clean"])
