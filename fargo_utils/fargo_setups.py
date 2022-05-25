import os
import pathlib
import subprocess
import pickle
import shutil

from . import boundary
from . import config
from . import ic
from . import opt
from . import par


def create_setups(arg_groups: dict):
    # set setups dir
    p = (
        pathlib.Path(arg_groups["optional arguments"].setups_dir)
        / arg_groups["par"].Setup
    )
    # check exists
    if p.exists():
        raise FileExistsError
    # create
    p.mkdir(parents=True)

    # bound file
    bound_args = boundary.cfg_to_nested_dict(arg_groups["bc"])
    bound_file = p / (arg_groups["par"].Setup + ".bound")
    boundary.write_boundlines(bound_args, bound_file)

    # copy bound to bound.0
    shutil.copy(bound_file, p / (arg_groups["par"].Setup + ".bound.0"))

    # ic file (move matched file from setup_base)
    ic_file = ic.get_condinit_file(
        arg_groups["ic"].DensityInitial,
        arg_groups["ic"].VxInitial,
        arg_groups["ic"].VyInitial,
    )
    shutil.copy(ic_file, p / "condinit.c")

    # opt file
    opt_file = p / (arg_groups["par"].Setup + ".opt")
    # with importlib.resources.path(setup_base.opt, "base.opt") as base_opt:
    #     shutil.copy(base_opt, opt_file)
    # opt.update_opt_file(opt_file, arg_groups["opt"])
    opt.write_opt_file(opt_file, arg_groups["opt"])

    # par file
    par_file = p / (arg_groups["optional arguments"].job_name + ".par")
    par.write_args(par_file, args={**vars(arg_groups["par"]), **vars(arg_groups["ic"])})

    # save arg_groups
    with open(p / "arg_groups.pkl", "wb") as f:
        pickle.dump(arg_groups, f)

    return p


if __name__ == "__main__":
    arg_groups = config.get_arg_groups()
    print(arg_groups)
    p = create_setups(arg_groups)
    config.save_arg_groups(arg_groups, p / "arg_groups.yml")
    # cd fargo3d
    os.chdir("fargo3d")
    # make
    make_command = [
        "make",
        f"SETUP={arg_groups['par'].Setup}",
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
    # run
    subprocess.run(
        [
            "./fargo3d",
            f"setups/{arg_groups['par'].Setup}/{arg_groups['optional arguments'].job_name}.par",
        ]
    )
