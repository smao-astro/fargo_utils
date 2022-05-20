import argparse
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
    parser.add_argument("--job_name", required=True, help="The name of par file.")

    ic_group = parser.add_argument_group("ic")
    ic_group.add_argument("--DensityInitial", choices=["RING2DDENS", "POWERLAW2DDENS"])
    ic_group.add_argument(
        "--VxInitial",
        choices=["STATICPOWERLAW2DVAZIM", "KEPLERIAN2DVAZIM", "STATICRING2DVAZIM"],
    )
    ic_group.add_argument("--VyInitial", choices=["STATICVY", "KEPLERIANRINGVY"])

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
    opt_group.add_argument("--STANDARD", type=bool)
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

    # par (reference: std/stdpar.par)
    par_group = parser.add_argument_group("par")
    par_group.add_argument("--Nx", type=int)
    par_group.add_argument("--Ny", type=int)
    par_group.add_argument("--Nz", type=int)
    par_group.add_argument("--Xmin", type=float, default=-math.pi)
    par_group.add_argument("--Xmax", type=float, default=math.pi)
    par_group.add_argument("--Ymin", type=float)
    par_group.add_argument("--Ymax", type=float)
    par_group.add_argument("--Zmin", type=float)
    par_group.add_argument("--Zmax", type=float)
    par_group.add_argument("--Oorta", type=float)
    par_group.add_argument("--SigmaSlope", type=float)
    par_group.add_argument("--Eccentricity", type=float)
    par_group.add_argument("--Inclination")
    par_group.add_argument("--ThicknessSmoothing", type=float)
    par_group.add_argument("--RocheSmoothing", type=float)
    par_group.add_argument("--AspectRatio", type=float)
    par_group.add_argument("--Sigma0", type=float)
    par_group.add_argument("--FlaringIndex", type=float)
    par_group.add_argument("--Nu", type=float)
    par_group.add_argument("--Cs", type=float)
    par_group.add_argument("--Frame", choices=["F", "C", "G"])
    par_group.add_argument("--OmegaFrame", type=float)
    par_group.add_argument("--IndirectTerm", choices=["yes", "no"])
    par_group.add_argument("--ExcludeHill", choices=["yes", "no"])
    par_group.add_argument("--MassTaper", type=float)
    par_group.add_argument("--Noise", type=float)
    par_group.add_argument("--VerticalDamping", type=float)
    par_group.add_argument("--Spacing")
    par_group.add_argument("--Coordinates")
    par_group.add_argument("--Gamma", type=float)
    par_group.add_argument("--Alpha", type=float)
    par_group.add_argument("--PlanetConfig", type=str)
    par_group.add_argument("--PeriodicZ", choices=["yes", "no"])
    par_group.add_argument("--PeriodicY", choices=["yes", "no"])

    par_group.add_argument("--OhmicDiffusionCoeff", type=float)
    par_group.add_argument("--HallEffectCoeff", type=float)
    par_group.add_argument("--AmbipolarDiffusionCoeff", type=float)

    par_group.add_argument("--Resonance", type=float)

    par_group.add_argument("--DampingZone", type=float)
    par_group.add_argument("--TauDamp", type=float)

    par_group.add_argument("--KillingBCColatitude", type=float)

    par_group.add_argument("--Beta", type=float)
    par_group.add_argument("--CFL", type=float)

    par_group.add_argument("--Vtk", choices=["yes", "no"])
    par_group.add_argument("--RealType", choices=["Standard", "float", "double"])

    par_group.add_argument("--PlanetMass", type=float)
    par_group.add_argument("--Field")
    par_group.add_argument("--Cmap")

    par_group.add_argument("--PlotLog", choices=["yes", "no"])
    par_group.add_argument("--Colorbar", choices=["yes", "no"])
    par_group.add_argument("--Autocolor", choices=["yes", "no"])
    par_group.add_argument("--Aspect")
    par_group.add_argument("--vmin", type=float)
    par_group.add_argument("--vmax", type=float)
    par_group.add_argument("--PlotLine")

    par_group.add_argument("--OrbitalRadius", type=float)
    par_group.add_argument("--ReleaseDate", type=float)
    par_group.add_argument("--ReleaseRadius", type=float)
    par_group.add_argument("--SemiMajorAxis", type=float)

    par_group.add_argument("--FuncArchFile")
    par_group.add_argument(
        "--Setup", required=True, help="The name of the whole setup directory."
    )

    par_group.add_argument("--Nsnap", type=int)
    par_group.add_argument("--WriteDensity", choices=["yes", "no"])
    par_group.add_argument("--WriteEnergy", choices=["yes", "no"])
    par_group.add_argument("--WriteBx", choices=["yes", "no"])
    par_group.add_argument("--WriteBy", choices=["yes", "no"])
    par_group.add_argument("--WriteBz", choices=["yes", "no"])
    par_group.add_argument("--WriteVx", choices=["yes", "no"])
    par_group.add_argument("--WriteVy", choices=["yes", "no"])
    par_group.add_argument("--WriteVz", choices=["yes", "no"])
    par_group.add_argument("--WriteDivergence", choices=["yes", "no"])
    par_group.add_argument("--WriteEnergyRad", choices=["yes", "no"])
    par_group.add_argument("--WriteTau", choices=["yes", "no"])

    # not in std/stdpar.par
    par_group.add_argument("--DT", type=float, default=math.pi / 100.0)
    par_group.add_argument("--Ninterm", type=int)
    par_group.add_argument("--Ntot", type=int)
    par_group.add_argument("--OutputDir", type=str)

    # ring specific args
    par_group.add_argument("--RingCenter", type=float)
    par_group.add_argument("--RingWidth", type=float)

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

    check_dampling_setup(args)

    arg_groups = {}

    for group in parser._action_groups:
        group_dict = {a.dest: getattr(args, a.dest, None) for a in group._group_actions}
        arg_groups[group.title] = argparse.Namespace(**group_dict)

    return arg_groups
