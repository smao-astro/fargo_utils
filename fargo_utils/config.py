import argparse
import math


def get_parser():
    parser = argparse.ArgumentParser("setups", fromfile_prefix_chars="@")
    parser.add_argument("--setups_dir", type=str, required=True)
    parser.add_argument("--Setup", type=str, default="main")

    ic_group = parser.add_argument_group("ic")
    ic_group.add_argument("--DensityInitial", choices=["RING2DDENS", "POWERLAW2DDENS"])
    ic_group.add_argument(
        "--VxInitial",
        choices=["STATICPOWERLAW2DVAZIM", "KEPLERIAN2DVAZIM", "STATICRING2DVAZIM"],
    )
    ic_group.add_argument("--VyInitial", choices=["STATICVY", "KEPLERIANRINGVY"])

    bc_group = parser.add_argument_group("bc")
    bc_group.add_argument("--DensityYmin")
    bc_group.add_argument("--DensityYmax")
    bc_group.add_argument("--VxYmin")
    bc_group.add_argument("--VxYmax")
    bc_group.add_argument("--VyYmin")
    bc_group.add_argument("--VyYmax")

    # planet
    planet_group = parser.add_argument_group("planet")
    planet_group.add_argument(
        "--PlanetConfig", type=str, help="Gives planet configuration file name."
    )
    planet_group.add_argument("--ThicknessSmoothing", type=float)
    planet_group.add_argument("--RocheSmoothing", type=float)
    planet_group.add_argument("--Eccentricity", type=float)
    planet_group.add_argument("--ExcludeHill", choices=["yes", "no"])
    planet_group.add_argument("--IndirectTerm", choices=["yes", "no"])

    # opt
    opt_group = parser.add_argument_group("opt")
    opt_group.add_argument("--stockholm", type=bool)

    # par
    par_group = parser.add_argument_group("par")
    par_group.add_argument("--AspectRatio", type=float)
    par_group.add_argument("--Sigma0", type=float)
    par_group.add_argument("--Nu", type=float)
    par_group.add_argument("--FlaringIndex", type=float)
    # TODO only apply when --stockholm = True
    par_group.add_argument("--DampingZone", type=float)
    par_group.add_argument("--Nx", type=int)
    par_group.add_argument("--Ny", type=int)
    par_group.add_argument("--Xmin", type=float, default=-math.pi)
    par_group.add_argument("--Xmax", type=float, default=math.pi)
    par_group.add_argument("--Ymin", type=float)
    par_group.add_argument("--Ymax", type=float)
    par_group.add_argument("--OmegaFrame", type=float)
    par_group.add_argument("--Frame", choices=["F", "C", "G"])
    par_group.add_argument("--DT", type=float, default=math.pi / 100.0)
    par_group.add_argument("--Ninterm", type=int)
    par_group.add_argument("--Ntot", type=int)
    par_group.add_argument("--OutputDir", type=str)
    par_group.add_argument("--PlotLog", choices=["yes", "no"])

    # TODO the two group below is mutually exclusive
    # fargo specific args
    fargo_group = parser.add_argument_group("fargo")
    fargo_group.add_argument("--SigmaSlope", type=float)

    # ring specific args
    # TODO check all given or all not given
    ring_group = parser.add_argument_group("ring")
    ring_group.add_argument("--RingCenter", type=float)
    ring_group.add_argument("--RingWidth", type=float)

    # TODO unrecognised args should go to par?

    return parser


def check_dampling_setup(args):
    if (args.stockholm and args.DampingZone is None) or (
        not args.stockholm and args.DampingZone is not None
    ):
        raise ValueError(
            f"args.stockholm = {args.stockholm}, args.DampingZone = {args.DampingZone}"
        )


def get_arg_groups(args=None):
    """https://stackoverflow.com/a/46929320/16589166

    Returns:

    """
    parser = get_parser()
    args = parser.parse_args(args)

    check_dampling_setup(args)

    arg_groups = {}

    for group in parser._action_groups:
        group_dict = {a.dest: getattr(args, a.dest, None) for a in group._group_actions}
        arg_groups[group.title] = argparse.Namespace(**group_dict)

    return arg_groups
