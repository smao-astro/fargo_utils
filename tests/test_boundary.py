import pickle

import pytest

import fargo_utils.boundary
import fargo_utils.config

bound_file = "data/fargo.bound"
ground_truth_file = "data/fargo.bound.pkl"


@pytest.fixture
def boundlines():
    return fargo_utils.boundary.BoundLinesReader(bound_file)


def test_boundlines_reader(boundlines):
    with open(ground_truth_file, "rb") as f:
        ground_truth = pickle.load(f)
    assert boundlines.args_list == ground_truth


def test_write_boundlines(tmp_path, boundlines):
    # write to tmp file
    tmp_file = tmp_path / "bound.txt"
    fargo_utils.boundary.write_boundlines(boundlines.args_dict, tmp_file)
    # laod back
    new_boundlines = fargo_utils.boundary.BoundLinesReader(tmp_file)
    # assert
    assert boundlines.args_list == new_boundlines.args_list


def test_args_to_nested_dict(boundlines):
    args_dict = fargo_utils.boundary.args_list_to_nested_dict(boundlines.args_list)
    assert args_dict == boundlines.args_dict


def test_dict_to_nested_dict(boundlines):
    args_dict = fargo_utils.boundary.dict_to_nested_dict(
        {
            "DensityYmin": "KEPLERIAN2DDENS",
            "DensityYmax": "KEPLERIAN2DDENS",
            "VxYmin": "KEPLERIAN2DVAZIM",
            "VxYmax": "KEPLERIAN2DVAZIM",
            "VyYmin": "ANTISYMMETRIC",
            "VyYmax": "ANTISYMMETRIC",
        }
    )
    assert args_dict == boundlines.args_dict


def test_create_boundlines(tmp_path, boundlines):
    parser = fargo_utils.config.get_parser()
    cfg = parser.parse_args(
        [
            "--setups_dir",
            str(tmp_path),
            "--setup_name",
            "main",
            "--DensityYmin",
            "KEPLERIAN2DDENS",
            "--DensityYmax",
            "KEPLERIAN2DDENS",
            "--VxYmin",
            "KEPLERIAN2DVAZIM",
            "--VxYmax",
            "KEPLERIAN2DVAZIM",
            "--VyYmin",
            "ANTISYMMETRIC",
            "--VyYmax",
            "ANTISYMMETRIC",
        ]
    )
    new_file = fargo_utils.boundary.create_boundlines(cfg)
    new_bl = fargo_utils.boundary.BoundLinesReader(new_file)
    assert boundlines.args_dict == new_bl.args_dict
