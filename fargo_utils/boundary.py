import re


class BoundLines:
    """Reader of `fargo.bound` files."""
    def __init__(self, file_path):
        self.lines = None
        self._args = None

        with open(file_path, "r") as f:
            self.lines = f.readlines()
        self._args = self.get_args()

    def get_args(self) -> dict:
        i = 0
        args = {}
        while i < len(self.lines):
            line = self.lines[i]
            # if line starts with alphabetic characters
            if line[:1].isalpha():
                name = re.split(r"\W+", line)[0]
                for next_line in self.lines[i + 1 : i + 3]:
                    next_line = re.split(r"\W+", next_line.strip())
                    args[name + next_line[0]] = next_line[1]
                i += 3
            else:
                i += 1
        return args

    @property
    def args(self):
        return [word for kv in self._args.items() for word in ["--" + kv[0], kv[1]]]
