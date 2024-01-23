import argparse
import pickle

import numpy as np
import pytest

import fargo_utils.par


@pytest.fixture
def args():
    parser = argparse.ArgumentParser("main")
    parser.add_argument("--a")
    parser.add_argument("--b")
    return parser.parse_args(["--a", "1"])


def test_args_to_lines(args):
    lines = fargo_utils.par.args_to_lines(vars(args))
    assert lines == ["a\t1\n"]


def test_move_to_first():
    with open("./data/lines.pkl", "rb") as f:
        lines = pickle.load(f)
    origin_lines = lines.copy()
    fargo_utils.par.move_to_first(lines)
    assert (lines[0].startswith("Setup")) and (origin_lines.sort() == lines.sort())


def test_get_frame_angular_velocity():
    planet_mass = 1e-5
    frame_angular_velocity = fargo_utils.par.get_frame_angular_velocity(
        frame="G",
        omegaframe=1.0005,
        planet_distance=1.0,
        planet_mass=planet_mass,
    )
    expected_frame_angular_velocity = np.sqrt(1.0 + planet_mass)
    assert np.isclose(frame_angular_velocity, expected_frame_angular_velocity)
