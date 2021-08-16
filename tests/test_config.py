import fargo_utils.config


def test_check_dampling_setup():
    assert False


def test_split_quoted_line():
    a = "MONITOR_SCALAR	'MASS | MOM_X | TORQ'"
    arg_line = fargo_utils.config.split_quoted_line(a)
    assert arg_line == ["--MONITOR_SCALAR", "'MASS | MOM_X | TORQ'"]
