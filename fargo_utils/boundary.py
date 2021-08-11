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


def args_to_nested_dict(args_list):
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


def write_boundlines(args: dict, file_path, check_exists=True):
    """

    Args:
        args: e.g. {'Density': {'Ymin': 'KEPLERIAN2DDENS', 'Ymax': 'KEPLERIAN2DDENS'}, 'Vx': {'Ymin':
        'KEPLERIAN2DVAZIM', 'Ymax': 'KEPLERIAN2DVAZIM'}, 'Vy': {'Ymin': 'ANTISYMMETRIC', 'Ymax': 'ANTISYMMETRIC'}}
        file_path:

    Returns:

    """
    p = pathlib.Path(file_path)
    if check_exists:
        if p.exists():
            raise FileExistsError

    lines = []
    for key, subdict in args.items():
        lines.append(key + ":\n")
        for subkey, value in subdict.items():
            lines.append("\t" + subkey + ": " + value + "\n")

    with p.open("w") as f:
        f.writelines(lines)
