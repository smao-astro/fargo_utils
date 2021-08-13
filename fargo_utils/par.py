import argparse


def args_to_lines(args: argparse.Namespace):
    """Only process args that not None."""
    arg_list = []
    for k, v in args.__dict__.items():
        if v is not None:
            arg_list.append(k + "\t" + str(v) + "\n")
    return arg_list


def join_args(args: dict):
    # todo check whether include unneeded keys
    arg_list = []
    # include Setup
    arg_list.append("Setup" + "\t" + args["optional arguments"].Setup + "\n")
    # include ic
    arg_list += args_to_lines(args["ic"])
    # include planet
    arg_list += args_to_lines(args["planet"])
    # include par, fargo, ring
    arg_list += args_to_lines(args["par"])
    fargo_list = args_to_lines(args["fargo"])
    ring_list = args_to_lines(args["ring"])
    # xor
    if (fargo_list and ring_list) or (not fargo_list and not ring_list):
        raise ValueError(f"fargo_list = {fargo_list}, ring_list = {ring_list}")
    arg_list += fargo_list
    arg_list += ring_list
    return arg_list


def write_args(file_path, args):
    # check file exits

    # open file and write
    pass
