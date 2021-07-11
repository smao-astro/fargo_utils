def read_planet_cfg(file_path) -> list:

    with open(file_path, "r") as f:
        lines = f.readlines()

    planet_info = []
    for line in lines:
        if line[:1].isalpha():
            planet_info.append(line.split())

    return planet_info


def read_single_planet_cfg_to_args(file_path) -> list:
    keys = [
        "PLANETNAME",
        "PLANETDISTANCE",
        "PLANETMASS",
        "ACCRETION",
        "FEELSDISK",
        "FEELSOTHERS",
    ]
    planet_info = read_planet_cfg(file_path)[0]
    return [
        word for key, value in zip(keys, planet_info) for word in ["--" + key, value]
    ]
