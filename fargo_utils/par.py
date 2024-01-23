import pathlib

import numpy as np


def args_to_lines(args: dict):
    """Converts a dictionary of arguments into a list of strings, each representing a key-value pair.

    Each key-value pair is formatted as 'key\tvalue\n'. Only pairs where value is not None are processed.
    For float values, they are converted to scientific notation without unnecessary trailing zeros.

    Example:
    >>> args_to_lines({'a': 1, 'b': None, 'c': 3.0})
    ['a\t1\n', 'c\t3e+00\n']
    """
    arg_list = []
    for k, v in args.items():
        if v is not None:
            if isinstance(v, float):
                # scientific notation like 1e-5 (rather than 1.0e-5) won't work with fargo3d
                v = np.format_float_scientific(v, trim="0")
            arg_list.append(k + "\t" + str(v) + "\n")
    return arg_list


def move_to_first(lines, startswith="Setup"):
    for i, line in enumerate(lines):
        if line.startswith(startswith):
            lines.pop(i)
            lines.insert(0, line)


def write_args(file_path, args: dict):
    lines = args_to_lines(args)
    # make the par file first line be Setup
    move_to_first(lines)
    file_path = pathlib.Path(file_path)
    # check file exits
    if file_path.exists():
        raise FileExistsError
    if not file_path.parent.exists():
        file_path.parent.mkdir()
    # open file and write
    with open(file_path, "w") as f:
        f.writelines(lines)


def get_frame_angular_velocity(frame, omegaframe, planet_distance, planet_mass):
    """Get the frame angular velocity.

    Currently only work for planets in circular orbits.
    """
    if frame == "F":
        return omegaframe
    elif frame in ["C", "G"]:
        # TODO check
        if np.isclose(planet_distance, 0.0):
            raise ValueError(
                f"planet_distance = {planet_distance} is close to zero. Can not set rotating frame."
            )
        # below two line is FARGO3D's unit system, see std/standard.units
        stellar_mass = 1.0
        gravity_constant = 1.0
        return np.sqrt(
            gravity_constant * (stellar_mass + planet_mass) / planet_distance**3
        )
    else:
        raise KeyError
