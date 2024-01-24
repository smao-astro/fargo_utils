from fargo_utils import fargo_run


def test_overwrite_planet_config_file_content():
    original_lines = [
        "###########################################################\n",
        "#   Planetary system initial configuration\n",
        "###########################################################\n",
        "\n",
        "# Planet Name \tDistance\tMass\t Accretion\tFeels Disk\tFeels Others\n",
        "Jupiter\t\t1.0\t\t1.0e-5\t 0.0\t  \tNO\t\tNO\n",
    ]
    planet_mass = 1.0e-5
    new_lines_expected = [
        "###########################################################\n",
        "#   Planetary system initial configuration\n",
        "###########################################################\n",
        "\n",
        "# Planet Name \tDistance\tMass\t Accretion\tFeels Disk\tFeels Others\n",
        "Jupiter\t1.0\t1.0e-05\t0.0\tNO\tNO\n",
    ]
    new_lines = fargo_run.overwrite_planet_config_file_content(
        planet_mass, original_lines
    )
    assert new_lines == new_lines_expected
