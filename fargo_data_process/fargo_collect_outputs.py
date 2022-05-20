import os
import yaml
import argparse


def get_config():
    parser = argparse.ArgumentParser()
    parser.add_argument("--yaml_file", type=str, default="./fargo_runs.yml")
    config = parser.parse_args()
    return config


def main(config):
    """Collect all fargo runs, concat data to one file.

    Args:
        config:

    Returns:

    """
    parameters = []
    runs = []

    # load xarrays
    xarrays = []

    # concat xarrays

    # save to file


if __name__ == "__main__":
    config = get_config()
    main(config)
