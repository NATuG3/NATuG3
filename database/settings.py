import pickle
from types import SimpleNamespace
import ui.datatypes

filename = "settings.nano"

profiles = {}

current = ui.datatypes.profile(
    count=200,
    diameter=2.2,
    H=3.549,
    T=2,
    B=21,
    Z_c=0.17,
    Z_s=1.26,
    theta_b=34.29,
    theta_c=360 / 21,
    theta_s=2.3,
)


def refresh():
    """
    Refresh the settings variable with the current user-inputted settings.

    Grabs data from actual UI.
    """
    pass


def load():
    """Load persisting attributes of this module to a file"""
    storage = SimpleNamespace(
        current=current, profiles=profiles
    )  # store all variables in this container
    # dump settings to file
    with open(filename, "wb") as settings_file:
        pickle.dump(storage, settings_file)


def dump():
    """Dump persisting attributes of this module to a file"""
    storage = SimpleNamespace(
        current=current, profiles=profiles
    )  # store all variables in this container
    # dump settings to file
    with open(filename, "wb") as settings_file:
        pickle.dump(storage, settings_file)
