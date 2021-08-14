import importlib.resources

from . import setup_base


def get_condinit_file(density_initial, vx_initial, vy_initial):
    print("=" * 10)
    print("Initial Condition")
    print(density_initial, vx_initial, vy_initial)
    print("=" * 10)
    choices = {
        ("POWERLAW2DDENS", "STATICPOWERLAW2DVAZIM", "STATICVY"): "fargo.c",
        ("RING2DDENS", "KEPLERIAN2DVAZIM", "KEPLERIANRINGVY"): "keplerian_ring.c",
        ("RING2DDENS", "STATICRING2DVAZIM", "STATICVY"): "static_ring.c",
    }
    key = (density_initial, vx_initial, vy_initial)
    if key in choices.keys():
        with importlib.resources.path(setup_base.condinit, choices[key]) as p:
            return p
    else:
        raise NotImplementedError
