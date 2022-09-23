import atexit
from dataclasses import dataclass
from os import listdir
import pickle

config_filename = "config.pickle"

def load_config():
    """Attempt to load the config, or return a new copy of config() if no such file exists"""
    if config_filename in listdir():
        with open(config_filename, mode="rb") as config_file:
            return pickle.load(config_file)
    else:
        return config()

@dataclass
class config:
    """Dataclass to store all program configurations in."""

    # define a dataclass for a single setting
    @dataclass
    class setting:
        """A setting"""
        name: str
        description: str
        value: any = None

    # all settings
    strand_switch_distance = setting(
        "Strand Switch Distance",
        "Unsure what this represents")
    strand_switch_angle = setting(
        "Strand Switch Angle",
        "The angle about the helix axis between two NEMids on different helices of a double helix")
    domain_distance = setting(
        "Domain Distance",
        "Distance between two domains")
    NEMid_height = setting(
        "NEMid Height",
        "Vertical height between two NEMids on different helices of the same double helix")
    generate_count = setting(
        "Generate Count",
        "Number of NEMids/nucleosides to generate"
    )
    characteristic_angle = setting(
        "Characteristic Angle",
        "Smallest possible angle about the helix axis possible between two NEMids on the same helix."
    )

    def __init__(self) -> None:
        """When the program closes make sure to pickle and dump the instance"""
        atexit.register(self.dump)

    def dump(self) -> None:
        """When scripts end make sure to dump config no matter what"""
        with open(config_filename, mode="wb") as config_file:
            pickle.dump(self, config_file)