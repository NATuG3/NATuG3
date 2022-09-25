import atexit
from copyreg import pickle
from dataclasses import dataclass
from os import listdir
import pickle


def save(presets, filename) -> None:
    """Save the preset()s dictonary into filename"""
    with open(filename, "wb") as database:
        pickle.dump(presets, database)


@dataclass
class preset:
    """
    A settings preset.

    Attributes:
        count (int): Number of NEMids to initially generate per strand.
        diameter (float): Diameter of a domain.
        H (float): Height of a turn.
        T (float): There are T turns every B bases.
        B (float): There are B bases every T turns.
        Z_c (float): Characteristic height.
        Z_s (float): Switch height.
        Z_b (float): Base height.
        theta_b (float): Base angle.
        theta_c (float): Characteristic angle.
        theta_s (float): Switch angle.
    """

    count: int = 300
    diameter: float = 0
    H: float = 0.0
    T: int = 0
    B: int = 0
    Z_c: float = 0.0
    Z_s: float = 0.0
    theta_b: float = 0.0
    theta_c: float = 0.0
    theta_s: float = 0.0

    def __post_init__(self):
        self.Z_b = (self.T * self.H) / self.B


def presets():
    """Initiation function to load and return presets"""

    global presets
    filename = "settings.nano"

    if filename in listdir():
        with open(filename, mode="rb") as file:
            presets = pickle.load(file)
    else:
        presets = {
            "last_used": "MFD B-DNA",
            "MFD B-DNA": preset(
                count=150,
                diameter=2.2,
                H=3.549,
                T=2,
                B=21,
                Z_c=0.17,
                Z_s=12.6,
                theta_b=34.29,
                theta_c=360 / 21,
                theta_s=2.3
            ),
        }

    atexit.register(lambda: save(presets, "settings.nano"))

    return presets  # return reference to presets


presets()
