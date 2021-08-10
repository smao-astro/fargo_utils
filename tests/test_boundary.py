import pickle
import fargo_utils.boundary


def test_boundlines():
    bound_file = "/Users/kyika/project/pinn/fargo_utils/tests/data/fargo.bound"
    ground_truth_file = (
        "/Users/kyika/project/pinn/fargo_utils/tests/data/fargo.bound.pkl"
    )
    boundlines = fargo_utils.boundary.BoundLines(bound_file)
    with open(ground_truth_file, "rb") as f:
        ground_truth = pickle.load(f)
    assert boundlines.args_list == ground_truth
