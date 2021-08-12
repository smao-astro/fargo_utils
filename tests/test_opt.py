import pathlib
import shutil

import pytest

import fargo_utils.opt


@pytest.fixture
def base_file():
    return pathlib.Path("../fargo_utils/setup_base/opt/base.opt")


@pytest.fixture
def opt_file(base_file, tmp_path):
    new_file = tmp_path / "new.opt"
    shutil.copy(base_file, new_file)
    return new_file


@pytest.mark.parametrize("stockholm", [True, False])
def test_update_opt_file(base_file, opt_file, stockholm):
    fargo_utils.opt.update_opt_file(opt_file, {"STOCKHOLM": stockholm})
    content = opt_file.read_text()

    assert (
        (content == base_file.read_text()) and ("STOCKHOLM" in content) and stockholm
    ) or ((not "STOCKHOLM" in content) and not stockholm)
