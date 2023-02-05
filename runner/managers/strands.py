import atexit
import pickle

from structures.strands.strands import Strands


class StrandsManager:
    """
    Manager for the application's strands.

    Attributes:
        current: The current strands.

    Methods:
        load: Load the strands from a file.
        dump: Dump the strands into a file.
        recompute: Recompute the strands.
    """

    restored_filepath = "saves/strands/restored.nano"

    def __init__(self, runner: "runner.Runner"):
        """Initialize the strands module."""
        self.runner = runner
        self.current = None

    def setup(self):
        self.load()
        atexit.register(self.dump)

    def load(self):
        """
        Dump the current strands into a file.

        The strands is loaded from a pickled file from a previous dump().
        """
        try:
            with open(self.restored_filepath, "rb") as file:
                self.current = pickle.load(file)
        except FileNotFoundError:
            self.recompute()

    def dump(self):
        """
        Dump the current strands into a file.

        The strands are dumped into a file using pickle, so that they can be loaded later.
        """
        with open(self.restored_filepath, "wb") as file:
            pickle.dump(self.current, file)

    def recompute(self) -> Strands:
        """
        Recompute the strands.

        This uses domains.strands() to recompute all data for strands.

        Notes:
            This is a very expensive operation.
        """
        self.current = self.runner.managers.domains.current.strands()
        return self.current
