import re
import os
import glob
import fargo_utils.planet


# old version
def read_planet_config(planet_config_file):
    def split_line(line):
        line = line.replace("\t", " ")
        line = line.replace("\n", "")
        return re.split(" +", line)

    keys = [
        "PLANETNAME",
        "PLANETDISTANCE",
        "PLANETMASS",
        "ACCRETION",
        "FEELSDISK",
        "FEELSOTHERS",
    ]

    with open(planet_config_file, "r") as f:
        lines = f.readlines()
    lines = [
        split_line(line) for line in lines if not (line.startswith("#") or line == "\n")
    ]
    if len(lines) > 2:
        raise IndexError("Missing planets information")
    else:
        line = lines[0]
    if len(keys) != len(line):
        raise IndexError("Keys and values are not one to one correspond")

    return [word for key, value in zip(keys, line) for word in ["--" + key, value]]


def test_read_single_planet_cfg_to_args():
    planet_files = glob.glob("./data/planets/*.cfg")
    # remove multi-planet files
    planet_files = [
        planet_file for planet_file in planet_files if "Kepler38" not in planet_file
    ]

    assert all(
        [
            read_planet_config(planet_file)
            == fargo_utils.planet.read_single_planet_cfg_to_args(planet_file)
            for planet_file in planet_files
        ]
    )
