import atexit
import pickle
from types import NoneType
from typing import Union

import refs
from structures.domains.domains.worker import DomainStrandWorker
from structures.strands.strands import Strands


class _Strands:
    filename = "saves/sequencing/restored.nano"

    def __init__(self, strands: Union[NoneType, Strands] = None):
        if strands is None:
            self.load()
        else:
            self.current: Strands = strands

        atexit.register(self.dump)

    def load(self):
        """Dump the current sequencing into a file."""
        try:
            with open(self.filename, "rb") as file:
                self.current = pickle.load(file)
        except FileNotFoundError:
            self.recompute()

    def dump(self):
        """Dump the current sequencing into a file."""
        with open(self.filename, "wb") as file:
            pickle.dump(self.current, file)

    def recompute(self) -> Strands:
        self.current: Strands = DomainStrandWorker(
            refs.domains.current, refs.nucleic_acid.current
        ).compute()
        return self.current
