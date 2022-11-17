import atexit
import pickle
from types import NoneType
from typing import Union

import refs
from structures.strands.strands import Strands
from workers.side_view import SideViewWorker


class _Strands:
    filename = "saves/strands/restored.nano"

    def __init__(self, strands: Union[NoneType, Strands] = None):
        if strands is None:
            self.load()
        else:
            self.current: Strands = strands

        atexit.register(self.dump)

    def load(self):
        """Dump the current strands into a file."""
        try:
            with open(self.filename, "rb") as file:
                self.current = pickle.load(file)
        except FileNotFoundError:
            self.recompute()

    def dump(self):
        """Dump the current strands into a file."""
        with open(self.filename, "wb") as file:
            pickle.dump(self.current, file)

    def recompute(self) -> Strands:
        self.current: Strands = SideViewWorker(
            refs.domains.current, refs.nucleic_acid.current
        ).compute()
        return self.current
