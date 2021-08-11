import argparse
import math


def get_parser():
    parser = argparse.ArgumentParser("setups", fromfile_prefix_chars="@")
    parser.add_argument("--setups_dir", type=str, required=True)
    parser.add_argument("--setup_name", type=str, default="main")

    ic_group = parser.add_argument_group("ic")
    ic_group.add_argument("--DensityInitial")
    ic_group.add_argument("--VxInitial")
    ic_group.add_argument("--VyInitial")

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
    # TODO choice
    par_group.add_argument("--Frame", choices=[""])
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
    ring_group = parser.add_argument_group("ring")
    ring_group.add_argument("--RingCenter", type=float)
    ring_group.add_argument("--RingWidth", type=float)

    # TODO unrecognised args should go to par?

    return parser
