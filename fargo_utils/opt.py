import argparse


def partial_match(l: list, word: str):
    """

    Returns:
        index or None
    """
    for i, elem in enumerate(l):
        if word in elem:
            return i
    return None


def update_opt_file(opt_file, opts: dict or argparse.Namespace):
    if isinstance(opts, argparse.Namespace):
        opts = opts.__dict__
    with open(opt_file, "r") as f:
        lines = f.readlines()

    for k, bool_value in opts.items():
        k = k.upper()
        # check
        matched_index = partial_match(lines, k)
        if bool_value and matched_index is None:
            # add
            lines.append("FARGO_OPT +=  -D" + k)
        elif (not bool_value) and matched_index is not None:
            # remove
            lines.pop(matched_index)

    with open(opt_file, "w") as f:
        f.writelines(lines)

    return lines


def write_opt_file(opt_file, opts: dict or argparse.Namespace):
    if isinstance(opts, argparse.Namespace):
        opts = opts.__dict__
    lines = []
    # fluid lines
    fluids = [str(i) for i in range(opts["NFLUIDS"])]
    lines.append(f"FLUIDS := {' '.join(fluids)}")
    lines.append(f"NFLUIDS = {opts['NFLUIDS']}")
    lines.append("FARGO_OPT += -DNFLUIDS=${NFLUIDS}")

    # switches
    for k, v in opts.items():
        if isinstance(v, bool) and v:
            lines.append(f"FARGO_OPT +=  -D{k}")

    # CUDA blocks
    cuda_blocks = [
        "#Cuda blocks",
        "ifeq (${GPU}, 1)",
        f"FARGO_OPT += -DBLOCK_X={opts['BLOCK_X']}",
        f"FARGO_OPT += -DBLOCK_Y={opts['BLOCK_Y']}",
        f"FARGO_OPT += -DBLOCK_Z={opts['BLOCK_Z']}",
        "endif",
    ]
    lines += cuda_blocks

    # MONITOR
    for k, v in opts.items():
        if k.startswith("MONITOR") and len(v) > 0:
            lines.append(f"{k} = {v}")

    with open(opt_file, "w") as f:
        f.write("\n".join(lines))
