import pickle
import fargo_utils.boundary

bound_file = "data/fargo.bound"
ground_truth_file = "data/fargo.bound.pkl"


def test_boundlines_reader():
    boundlines = fargo_utils.boundary.BoundLinesReader(bound_file)
    with open(ground_truth_file, "rb") as f:
        ground_truth = pickle.load(f)
    assert boundlines.args_list == ground_truth


def test_write_boundlines(tmp_path):
    # get args
    boundlines = fargo_utils.boundary.BoundLinesReader(bound_file)
    # write to tmp file
    tmp_file = tmp_path / "bound.txt"
    fargo_utils.boundary.write_boundlines(boundlines.args_dict, tmp_file)
    # laod back
    new_boundlines = fargo_utils.boundary.BoundLinesReader(tmp_file)
    # assert
    assert boundlines.args_list == new_boundlines.args_list
