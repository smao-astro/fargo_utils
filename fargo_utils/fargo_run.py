"""
1. Write to setup file
2. run
"""
import math
import os
import pathlib
import subprocess

from . import config
from . import par


def get_parser():
    """
    References:
        std/stdpar.par
    Returns:

    """
    parser = config.MyArgumentParser("run", fromfile_prefix_chars="%")

    parser.add_argument("--Nx", type=int)
    parser.add_argument("--Ny", type=int)
    parser.add_argument("--Nz", type=int)
    parser.add_argument("--Xmin", type=float, default=-math.pi)
    parser.add_argument("--Xmax", type=float, default=math.pi)
    parser.add_argument("--Ymin", type=float)
    parser.add_argument("--Ymax", type=float)
    parser.add_argument("--Zmin", type=float)
    parser.add_argument("--Zmax", type=float)
    parser.add_argument("--Oorta", type=float)
    parser.add_argument("--SigmaSlope", type=float)
    parser.add_argument("--Eccentricity", type=float)
    parser.add_argument("--Inclination")
    parser.add_argument("--ThicknessSmoothing", type=float)
    parser.add_argument("--RocheSmoothing", type=float)
    parser.add_argument("--AspectRatio", type=float)
    parser.add_argument("--Sigma0", type=float)
    parser.add_argument("--FlaringIndex", type=float)
    parser.add_argument("--Nu", type=float)
    parser.add_argument("--Cs", type=float)
    parser.add_argument("--Frame", choices=["F", "C", "G"])
    parser.add_argument("--OmegaFrame", type=float)
    parser.add_argument("--IndirectTerm", choices=["yes", "no"])
    parser.add_argument("--ExcludeHill", choices=["yes", "no"])
    parser.add_argument("--MassTaper", type=float)
    parser.add_argument("--Noise", type=float)
    parser.add_argument("--VerticalDamping", type=float)
    parser.add_argument("--Spacing")
    parser.add_argument("--Coordinates")
    parser.add_argument("--Gamma", type=float)
    parser.add_argument("--Alpha", type=float)
    parser.add_argument("--PlanetConfig", type=str)
    parser.add_argument("--PeriodicZ", choices=["yes", "no"])
    parser.add_argument("--PeriodicY", choices=["yes", "no"])

    parser.add_argument("--OhmicDiffusionCoeff", type=float)
    parser.add_argument("--HallEffectCoeff", type=float)
    parser.add_argument("--AmbipolarDiffusionCoeff", type=float)

    parser.add_argument("--Resonance", type=float)

    parser.add_argument("--DampingZone", type=float)
    parser.add_argument("--TauDamp", type=float)

    parser.add_argument("--KillingBCColatitude", type=float)

    parser.add_argument("--Beta", type=float)
    parser.add_argument("--CFL", type=float)

    parser.add_argument("--Vtk", choices=["yes", "no"])
    parser.add_argument("--RealType", choices=["Standard", "float", "double"])

    parser.add_argument("--PlanetMass", type=float)
    parser.add_argument("--Field")
    parser.add_argument("--Cmap")

    parser.add_argument("--PlotLog", choices=["yes", "no"])
    parser.add_argument("--Colorbar", choices=["yes", "no"])
    parser.add_argument("--Autocolor", choices=["yes", "no"])
    parser.add_argument("--Aspect")
    parser.add_argument("--vmin", type=float)
    parser.add_argument("--vmax", type=float)
    parser.add_argument("--PlotLine")

    parser.add_argument("--OrbitalRadius", type=float)
    parser.add_argument("--ReleaseDate", type=float)
    parser.add_argument("--ReleaseRadius", type=float)
    parser.add_argument("--SemiMajorAxis", type=float)

    parser.add_argument("--FuncArchFile")

    parser.add_argument("--Nsnap", type=int)
    parser.add_argument("--WriteDensity", choices=["yes", "no"])
    parser.add_argument("--WriteEnergy", choices=["yes", "no"])
    parser.add_argument("--WriteBx", choices=["yes", "no"])
    parser.add_argument("--WriteBy", choices=["yes", "no"])
    parser.add_argument("--WriteBz", choices=["yes", "no"])
    parser.add_argument("--WriteVx", choices=["yes", "no"])
    parser.add_argument("--WriteVy", choices=["yes", "no"])
    parser.add_argument("--WriteVz", choices=["yes", "no"])
    parser.add_argument("--WriteDivergence", choices=["yes", "no"])
    parser.add_argument("--WriteEnergyRad", choices=["yes", "no"])
    parser.add_argument("--WriteTau", choices=["yes", "no"])

    # not in std/stdpar.par
    parser.add_argument("--DT", type=float, default=math.pi / 100.0)
    parser.add_argument("--Ninterm", type=int)
    parser.add_argument("--Ntot", type=int)
    parser.add_argument("--OutputDir", type=str)

    # ring specific args
    parser.add_argument("--RingCenter", type=float)
    parser.add_argument("--RingWidth", type=float)

    return parser


def write_par_file(setup_dir: pathlib.Path, arg_groups):
    # # par file
    par_file = setup_dir / (arg_groups["optional arguments"].job_name + ".par")
    args = {"Setup": arg_groups["optional arguments"].Setup}
    args.update(vars(arg_groups["par"]))
    args.update(vars(arg_groups["ic"]))
    par.write_args(par_file, args=args)


def run(arg_groups):
    # run
    os.chdir("fargo3d")
    subprocess.run(
        [
            "./fargo3d",
            f"{arg_groups['optional arguments'].job_name}.par",
        ]
    )


if __name__ == "__main__":
    args = get_parser().parse_args()
    fargo_dir = pathlib.Path("fargo3d")
    arg_groups = config.load_arg_groups(fargo_dir / "arg_groups.yml")

    # append values to arg_groups
    arg_groups["par"] = args
    # delete old arg_groups.yml
    pathlib.Path.unlink(fargo_dir / "arg_groups.yml")
    config.save_arg_groups(
        arg_groups=arg_groups, file_path=fargo_dir / "arg_groups.yml"
    )

    write_par_file(setup_dir=fargo_dir, arg_groups=arg_groups)

    run(arg_groups)
