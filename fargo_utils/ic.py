import pathlib


def get_condinit_file(density_initial, vx_initial, vy_initial):
    print(density_initial, vx_initial, vy_initial)
    choices = {
        ("POWERLAW2DDENS", "STATICPOWERLAW2DVAZIM", "STATICVY"): "fargo.c",
        ("RING2DDENS", "KEPLERIAN2DVAZIM", "KEPLERIANRINGVY"): "keplerian_ring.c",
        ("RING2DDENS", "STATICRING2DVAZIM", "STATICVY"): "static_ring.c",
    }
    key = (density_initial, vx_initial, vy_initial)
    if key in choices.keys():
        return pathlib.Path("setup_base") / choices[key]
    else:
        raise NotImplementedError
