import logging

from structures.strands.strands import Strands

logger = logging.getLogger(__name__)


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
        self.recompute()

    def recompute(self) -> Strands:
        """
        Recompute the strands.

        This method first recomputes the double helices, and then uses the double
        helices strand conversion functions to fetch a new strands object.

        Notes:
            This is a very expensive operation.
        """
        self.runner.managers.misc.currently_selected.clear()
        self.runner.managers.double_helices.recompute()
        self.current = self.runner.managers.double_helices.current.strands()
        logger.info("Recomputed strands.")
        return self.current
