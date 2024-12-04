import argparse
import pathlib
import yaml
import math
import re


def split_quoted_line(arg_line):
    starts = [m.start() for m in re.finditer("'", arg_line)]
    if len(starts) != 2:
        raise ValueError(f"Can not preprocess arg_line = {arg_line}")
    value = arg_line[starts[0] : starts[1] + 1]
    key = arg_line[: starts[0]].split()[0]
    return ["--" + key, value]


class MyArgumentParser(argparse.ArgumentParser):
    def convert_arg_line_to_args(self, arg_line: str):
        if arg_line.startswith(("#", "\n")) or arg_line == "":
            return []
        if "'" in arg_line:
            return split_quoted_line(arg_line)
        arg_line = arg_line.split()
        return ["--" + arg_line[0], arg_line[1]]


def get_parser():
    parser = MyArgumentParser("setups", fromfile_prefix_chars="%")
    parser.add_argument(
        "--setups_dir", type=str, required=True, help="the path of setups/"
    )
    parser.add_argument(
        "--Setup", required=True, help="The name of the whole setup directory."
    )
    parser.add_argument("--job_name", required=True, help="The name of par file.")

    ic_group = parser.add_argument_group("ic")
    ic_group.add_argument("--DensityInitial", choices=["RING2DDENS", "POWERLAW2DDENS"])
    ic_group.add_argument(
        "--VxInitial",
        choices=[
            "STATICPOWERLAW2DVAZIM",
            "KEPLERIAN2DVAZIM",
            "STATICRING2DVAZIM",
            "FUNG2DVAZIM",
        ],
    )
    ic_group.add_argument(
        "--VyInitial", choices=["STATICVY", "KEPLERIANRINGVY", "FUNG2DVY"]
    )

    bc_group = parser.add_argument_group("bc")
    # TODO add choices
    bc_group.add_argument("--DensityYmin")
    bc_group.add_argument("--DensityYmax")
    bc_group.add_argument("--VxYmin")
    bc_group.add_argument("--VxYmax")
    bc_group.add_argument("--VyYmin")
    bc_group.add_argument("--VyYmax")

    # opt
    opt_group = parser.add_argument_group("opt")
    ## Fluids
    opt_group.add_argument("--NFLUIDS", type=int, required=True)
    opt_group.add_argument("--DRAGFORCE", type=bool)
    opt_group.add_argument("--STOKESNUMBER", type=bool)
    ## Performance
    opt_group.add_argument("--FLOAT", type=bool)
    ## Dimensions
    opt_group.add_argument("--X", type=bool)
    opt_group.add_argument("--Y", type=bool)
    opt_group.add_argument("--Z", type=bool)
    ## Equation of state
    opt_group.add_argument("--ADIABATIC", type=bool)
    opt_group.add_argument("--ISOTHERMAL", type=bool)
    ## Additional Physics:
    opt_group.add_argument("--MHD", type=bool)
    ### MHD
    opt_group.add_argument("--STRICTSYM", type=bool)
    opt_group.add_argument("--OHMICDIFFUSION", type=bool)
    opt_group.add_argument("--AMBIPOLARDIFFUSION", type=bool)
    opt_group.add_argument("--HALLEFFECT", type=bool)
    ###
    opt_group.add_argument("--VISCOSITY", type=bool)
    opt_group.add_argument("--ALPHAVISCOSITY", type=bool)
    opt_group.add_argument("--POTENTIAL", type=bool)
    opt_group.add_argument("--STOCKHOLM", type=bool)
    opt_group.add_argument("--HILLCUT", type=bool)
    ## Coordinates
    opt_group.add_argument("--CARTESIAN", type=bool)
    opt_group.add_argument("--CYLINDRICAL", type=bool)
    opt_group.add_argument("--SPHERICAL", type=bool)
    ## Transport
    opt_group.add_argument(
        "--RAM",
        type=bool,
        help="Rapid Advection Algorithm on Arbitrary Meshes (Benítez-Llambay et al. 2023)",
    )
    opt_group.add_argument("--STANDARD", type=bool, help="Forces the standard advection algorithm in x.")
    ### If both above are OFF, use the default---orbital advection (FARGO) algorithm.
    ## Slopes
    opt_group.add_argument("--DONOR", type=bool)
    ## Artificial Viscosity
    opt_group.add_argument("--NOSUBSTEP2", type=bool)
    opt_group.add_argument("--STRONG_SHOCK", type=bool)
    ## Boundaries
    opt_group.add_argument("--HARDBOUNDARIES", type=bool)
    ## Outputs
    opt_group.add_argument("--LEGACY", type=bool)
    ## Cuda blocks
    opt_group.add_argument("--BLOCK_X", type=int, default=16)
    opt_group.add_argument("--BLOCK_Y", type=int, default=16)
    opt_group.add_argument("--BLOCK_Z", type=int, default=1)
    ## MONITOR
    opt_group.add_argument("--MONITOR_2D", type=str, default="")
    opt_group.add_argument("--MONITOR_Y", type=str, default="")
    opt_group.add_argument("--MONITOR_Y_RAW", type=str, default="")
    opt_group.add_argument("--MONITOR_Z", type=str, default="")
    opt_group.add_argument("--MONITOR_Z_RAW", type=str, default="")
    opt_group.add_argument("--MONITOR_SCALAR", type=str, default="")

    # make
    make_group = parser.add_argument_group("make")
    make_group.add_argument("--BIGMEM", type=int, default=1)
    make_group.add_argument("--RESCALE", type=int, default=0)
    make_group.add_argument("--PROFILING", type=int, default=0)
    make_group.add_argument("--PARALLEL", type=int, default=0)
    make_group.add_argument("--MPICUDA", type=int, default=0)
    make_group.add_argument("--GPU", type=int, default=0)
    make_group.add_argument("--DEBUG", type=int, default=0)
    make_group.add_argument("--FULLDEBUG", type=int, default=0)
    make_group.add_argument(
        "--FARGO_DISPLAY", choices=["NONE", "MATPLOTLIB"], default="NONE"
    )
    make_group.add_argument("--UNITS", choices=["0", "MKS", "CGS"], default="0")
    make_group.add_argument("--GHOSTSX", type=int, default=0)
    make_group.add_argument("--LONGSUMMARY", type=int, default=0)

    # TODO unrecognised args should go to par?

    return parser


def check_dampling_setup(args):
    if (args.STOCKHOLM and args.DampingZone is None) or (
        not args.STOCKHOLM and args.DampingZone is not None
    ):
        raise ValueError(
            f"args.STOCKHOLM = {args.STOCKHOLM}, args.DampingZone = {args.DampingZone}"
        )


def get_arg_groups(args=None):
    """https://stackoverflow.com/a/46929320/16589166

    Returns:

    """
    parser = get_parser()
    args = parser.parse_args(args)

    # check_dampling_setup(args)

    arg_groups = {}

    for group in parser._action_groups:
        group_dict = {a.dest: getattr(args, a.dest, None) for a in group._group_actions}
        arg_groups[group.title] = argparse.Namespace(**group_dict)

    # compatible with python/3.10
    if "options" in arg_groups:
        arg_groups["optional arguments"] = arg_groups.pop("options")

    return arg_groups


def save_arg_groups(arg_groups: dict, file_path):
    # to dict
    arg_groups = {k: vars(v) for k, v in arg_groups.items()}

    file_path = pathlib.Path(file_path)

    if file_path.exists():
        raise FileExistsError(f"{file_path}")
    if not file_path.parent.is_dir():
        raise NotADirectoryError()

    with file_path.open("w") as f:
        yaml.safe_dump(arg_groups, f)


def load_arg_groups(file_path):
    file_path = pathlib.Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(f"{file_path}")

    with file_path.open("r") as f:
        arg_groups: dict = yaml.safe_load(f)

    # to namespace
    return {k: argparse.Namespace(**v) for k, v in arg_groups.items()}
