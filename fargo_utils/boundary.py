import re


class BoundLines:
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
