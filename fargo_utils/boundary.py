import argparse
import pathlib
import re


class BoundLinesReader:
    """Reader of `fargo.bound` files."""

    def __init__(self, file_path):
        self.lines = None
        self.args_dict = None

        with open(file_path, "r") as f:
            self.lines = f.readlines()
        self.args_dict = self.get_args()

    def get_args(self) -> dict:
        args = {}
        key = None
        for line in self.lines:
            if line[:1].isalpha():
                key = re.split(r"\W+", line)[0]
                args[key] = {}
            if line.startswith("\t"):
                subkey, value = re.split(r"\W+", line.strip())
                if key is None:
                    raise ValueError(f"`key` not assigned.")
                args[key][subkey] = value
        return args

    @property
    def args_list(self):
        return [
            word
            for key, subdict in self.args_dict.items()
            for subkey, value in subdict.items()
            for word in ["--" + key + subkey, value]
        ]


def args_list_to_nested_dict(args_list):
    """

    Args:
        args_list: e.g. ['--DensityYmin', 'KEPLERIAN2DDENS', '--DensityYmax', 'KEPLERIAN2DDENS', '--VxYmin', 'KEPLERIAN2DVAZIM', '--VxYmax', 'KEPLERIAN2DVAZIM', '--VyYmin', 'ANTISYMMETRIC', '--VyYmax', 'ANTISYMMETRIC']

    Returns:

    """
    args_dict = {}
    for i in range(0, len(args_list), 2):
        key = args_list[i].strip("-")
        key, subkey = key[:-4], key[-4:]
        if not key in args_dict:
            args_dict[key] = {}
        args_dict[key][subkey] = args_list[i + 1]

    return args_dict


def dict_to_nested_dict(args_dict):
    nested_dict = {}
    for key, value in args_dict.items():
        key, subkey = key[:-4], key[-4:]
        if not key in nested_dict:
            nested_dict[key] = {}
        if not subkey in ["Ymin", "Ymax"]:
            raise ValueError
        nested_dict[key][subkey] = value

    return nested_dict


def write_boundlines(args: dict, file_path, check_exists: bool = True):
    """

    Args:
        args: e.g. {'Density': {'Ymin': 'KEPLERIAN2DDENS', 'Ymax': 'KEPLERIAN2DDENS'}, 'Vx': {'Ymin':
        'KEPLERIAN2DVAZIM', 'Ymax': 'KEPLERIAN2DVAZIM'}, 'Vy': {'Ymin': 'ANTISYMMETRIC', 'Ymax': 'ANTISYMMETRIC'}}
        file_path:
        check_exists:

    Returns:

    """
    file_path = pathlib.Path(file_path)
    if check_exists:
        if file_path.exists():
            raise FileExistsError
    parent = file_path.parent
    if not parent.exists():
        parent.mkdir(parents=True)

    lines = []
    for key, subdict in args.items():
        lines.append(key + ":\n")
        for subkey, value in subdict.items():
            lines.append("\t" + subkey + ": " + value + "\n")

    with file_path.open("w") as f:
        f.writelines(lines)


def cfg_to_nested_dict(cfg: argparse.Namespace):
    bound_args = {}
    for key in cfg.__dict__.keys():
        if (key.endswith("Ymin") or key.endswith("Ymax")) and len(key) > 4:
            bound_args[key] = getattr(cfg, key)
    return dict_to_nested_dict(bound_args)
