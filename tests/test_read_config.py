import pickle
import fargo_utils.read_config


def test_read_config():
    with open("./data/variables.pkl", "rb") as f:
        ground_truth = pickle.load(f)
    variables = fargo_utils.read_config.read_config("./data/variables.par", "\t")
    assert variables == ground_truth
