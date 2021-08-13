import argparse

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
