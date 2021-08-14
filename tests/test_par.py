import argparse
import pickle

import pytest

import fargo_utils.par


@pytest.fixture
def args():
    parser = argparse.ArgumentParser("main")
    parser.add_argument("--a")
    parser.add_argument("--b")
    return parser.parse_args(["--a", "1"])


def test_args_to_lines(args):
    lines = fargo_utils.par.args_to_lines(args)
    assert lines == ["a\t1\n"]


def test_move_to_first():
    with open("./data/lines.pkl", "rb") as f:
        lines = pickle.load(f)
    origin_lines = lines.copy()
    fargo_utils.par.move_to_first(lines)
    assert (lines[0].startswith("Setup")) and (origin_lines.sort() == lines.sort())
