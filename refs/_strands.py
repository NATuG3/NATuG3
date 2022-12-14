import atexit
import pickle

import refs
from structures.strands.strands import Strands


class _Strands:
    """
    Manager for the application's strands.

    Attributes:
        current: The current strands.

    Methods:
        load: Load the strands from a file.
        dump: Dump the strands into a file.
        recompute: Recompute the strands.
    """
    filename = "saves/sequencing/restored.nano"
    current: Strands

    def __init__(self):
        """Initialize the strands module."""
        self.current = None
        self.load()
        atexit.register(self.dump)
        assert isinstance(self.current, Strands)

    def load(self):
        """
        Dump the current sequencing into a file.

        The sequencing is loaded from a pickled file from a previous dump().
        """
        try:
            with open(self.filename, "rb") as file:
                self.current = pickle.load(file)
        except FileNotFoundError:
            self.recompute()

    def dump(self):
        """
        Dump the current strands into a file.

        The strands are dumped into a file using pickle, so that they can be loaded later.
        """
        with open(self.filename, "wb") as file:
            pickle.dump(self.current, file)

    def recompute(self) -> Strands:
        """
        Recompute the strands.

        This uses domains.strands() to recompute all data for strands.

        Notes:
            This is a very expensive operation.
        """
        refs.domains.current.strands.cache_clear()
        self.current = refs.domains.current.strands()
        return self.current
