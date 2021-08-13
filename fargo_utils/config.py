import argparse
import math


def get_parser():
    parser = argparse.ArgumentParser("setups", fromfile_prefix_chars="@")
    parser.add_argument("--setups_dir", type=str, required=True)
    parser.add_argument("--job_name", required=True)

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
    opt_group.add_argument("--stockholm", type=bool)

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
    par_group.add_argument("--Setup")

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
