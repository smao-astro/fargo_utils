def partial_match(l: list, word: str):
    """

    Returns:
        index or None
    """
    for i, elem in enumerate(l):
        if word in elem:
            return i
    return None


def update_opt_file(opt_file, opts: dict):
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
