import logging

from natug.runner.managers.manager import Manager
from natug.structures.strands.strands import Strands

logger = logging.getLogger(__name__)


class StrandsManager(Manager):
    """
    Manager for the application's strands.

    Attributes:
        runner: NATuG's current runner.
        current: The current strands.

    Methods:
        recompute: Recompute the strands from the current doule helices.
    """

    def recompute(self) -> Strands:
        """
        Recompute the strands.

        This method first recomputes the double helices, and then uses the double
        helices strand conversion functions to fetch a new strands object.

        Notes:
            This is a very expensive operation.
        """
        # Clear all currently selected points since all the points are about to change.
        self.runner.managers.misc.currently_selected.clear()
        # Recompute the double helices based off of the current domains.
        self.runner.managers.double_helices.recompute()
        # Generate new strands using the strands() method of double helices.
        self.current = self.runner.managers.double_helices.current.strands()
        # Log that the strands have been recomputed and return the new strands.
        logger.info("Recomputed strands.")
        return self.current
