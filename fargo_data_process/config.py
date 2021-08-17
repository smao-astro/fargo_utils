import argparse


def get_config(args=None):
    parser = argparse.ArgumentParser("main")
    parser.add_argument("--output_dir", type=str)

    return parser.parse_args(args)
