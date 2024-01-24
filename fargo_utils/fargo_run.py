"""
1. Write to setup file
2. run
"""
import math
import os
import pathlib
import subprocess

import numpy as np

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
    parser.add_argument(
        "--PlanetMassFile",
        type=str,
        choices=["par", "cfg"],
        default="cfg",
        help="The old version of this package use `par` as the default value.",
    )
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


def overwrite_planet_config_file_content(planet_mass: float, lines: list):
    """
    Overwrites the mass of a planet in a planetary system configuration file,
    under specific conditions.

    This function updates the mass of the planet in the file, only if the file
    contains exactly one line of planet data and this line is the last line in
    the file. The planet data line is identified as the first non-comment line
    (not starting with '#') and should be at the end of the file.

    Parameters:
    - planet_mass (float): The new mass of the planet to be written into the file.
    - file_lines (list): The lines of the file to be updated.

    Example:
    Original file content:
    ###########################################################
    #   Planetary system initial configuration
    ###########################################################

    # Planet Name   Distance        Mass     Accretion      Feels Disk      Feels Others
    Jupiter         1.0             0.001    0.0            NO              NO

    After calling overwrite_planet_config_file_content(0.002, pathlib.Path('path_to_your_file.txt')),
    the file content will change to:
    ###########################################################
    #   Planetary system initial configuration
    ###########################################################

    # Planet Name   Distance        Mass     Accretion      Feels Disk      Feels Others
    Jupiter         1.0             0.002    0.0            NO              NO
    """

    # Check for exactly one planet data line and that it is the last line
    planet_data_line_index = []
    for i, line in enumerate(lines):
        if line.strip() and not line.startswith("#"):
            planet_data_line_index.append(i)
    if len(planet_data_line_index) != 1 or planet_data_line_index[0] != len(lines) - 1:
        raise ValueError("The file does not meet the specified conditions.")

    # Update the mass in the last line
    parts = lines[-1].split()
    # what number format is accepted by FARGO3D?
    # 1.0e-05 is good
    # 1e-05 is good
    # 1.0e-5 is good
    parts[2] = np.format_float_scientific(
        planet_mass, trim="0"
    )  # Replace the mass value
    lines[-1] = "\t".join(parts) + "\n"  # Reconstruct the line

    return lines


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
    # the arg_groups contain a dict of Namespace objects
    # {'bc': Namespace(), 'ic': Namespace(), 'make': Namespace(), 'opt': Namespace(), 'optional arguments': Namespace(),
    # 'par': Namespace(), 'positional arguments': Namespace()}

    # append values to arg_groups
    arg_groups["par"] = args
    # delete old arg_groups.yml
    pathlib.Path.unlink(fargo_dir / "arg_groups.yml")
    config.save_arg_groups(
        arg_groups=arg_groups, file_path=fargo_dir / "arg_groups.yml"
    )

    par_file_content = {"Setup": arg_groups["optional arguments"].Setup}
    par_file_content.update(vars(arg_groups["par"]))
    if arg_groups["par"].PlanetConfig is None:
        raise ValueError("PlanetConfig is None")
    if arg_groups["par"].PlanetMassFile == "cfg":
        # We do not write PlanetMass to par file.
        par_file_content.pop("PlanetMass", None)
        # Instead, we use the value to overwrite the planet config file.
        if arg_groups["par"].PlanetMass is not None:
            # overwrite planet config file
            planet_config_file = fargo_dir / arg_groups["par"].PlanetConfig
            with open(planet_config_file, "r") as f:
                lines = f.readlines()
            lines = overwrite_planet_config_file_content(
                planet_mass=arg_groups["par"].PlanetMass, lines=lines
            )
            with open(planet_config_file, "w") as f:
                f.writelines(lines)
    # We do not write PlanetMassFile to par file, this parameter is only used in this package, not in FARGO3D
    par_file_content.pop("PlanetMassFile", None)
    par_file_content.update(vars(arg_groups["ic"]))

    # write par file
    par_file = fargo_dir / (arg_groups["optional arguments"].job_name + ".par")
    par.write_args(par_file, args=par_file_content)

    run(arg_groups)
