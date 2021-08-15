import argparse
import pathlib
import numpy as np

def args_to_lines(args: argparse.Namespace):
    """Only process args that not None."""
    arg_list = []
    for k, v in args.__dict__.items():
        if v is not None:
            if isinstance(v, float):
                # scientific notation like 1e-5 (rather than 1.0e-5) won't work with fargo3d
                v = np.format_float_scientific(v, trim='0')
            arg_list.append(k + "\t" + str(v) + "\n")
    return arg_list


def move_to_first(lines, startswith="Setup"):
    for i, line in enumerate(lines):
        if line.startswith("Setup"):
            lines.pop(i)
            lines.insert(0, line)


def write_args(file_path, args: argparse.Namespace):
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
