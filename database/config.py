import atexit
from os import listdir
from types import SimpleNamespace
from typing import Any, Iterator
import json
from copy import deepcopy as copy
import dna_nanotube_tools.datatypes

template_preset = {
    "H": 0.0,
    "T": 0,
    "B": 0,
    "RADIUS": 0.0,
    "Z_BASE": 0.0,
    "THETA_BASE": 0.0,
    "Z_C": 0.0,
    "THETA_C": 0.0,
    "Z_S": 0.0,
    "THETA_S": 0.0,
    "domains": [[9, 0] for i in range(14)],
}


class config:
    def __init__(self, filename: str = "presets.nano") -> None:
        """
        The configuration's database.

        There can be multiple "presets" for config, which are stored in a SimpleNamespace.

        Args:
            filename (str): Name of the subdatabase file.
        """

        self.filename = filename

        # create database if it does not exist
        if filename not in listdir():
            with open(self.filename, "w") as database:
                json.dump({"default": template_preset}, database, indent=4)

        # load in database
        with open(self.filename) as database:
            self.presets = json.loads(database.read())

        # ensure database saves on program exit
        atexit.register(self.save)

    def add_preset(self, name: str) -> dict:
        """Add a config preset."""
        self.presets[name] = copy(template_preset)
        return self.presets[name]

    def remove_preset(self, name: str) -> None:
        """Remove a config preset."""
        del self.presets[name]

    def update_preset(self, name: str, setting: Any, value: Any):
        """Update a setting of a preset with a new value"""
        self.presets[name][setting] = value
        return self.presets[name]

    def fetch_preset(self, name: str):
        """Fetch a preset."""
        preset = self.presets[name]
        preset = SimpleNamespace(**preset)

        domains = []
        for theta_interior, theta_switch in preset.domains:
            domains.append(
                dna_nanotube_tools.datatypes.domain(theta_interior, theta_switch)
            )
        preset.domains = domains
        return preset

    def save(self) -> None:
        """Dump the database dict into the database json file."""
        with open(self.filename, "w") as database:
            json.dump(self.presets, database, indent=2)

    def __iter__(self) -> Iterator:
        for name in self.presets:
            yield self.fetch_preset(name)
