import logging
from contextlib import suppress

from natug.runner.managers.manager import Manager
from natug.structures.helices import DoubleHelices

logger = logging.getLogger(__name__)


class DoubleHelicesManager(Manager):
    """
    Manager for the application's double helices.

    Attributes:
        current: The current double helices.
        runner: NATuG's current runner.

    Methods:
        restore: Load in a default DoubleHelices instance based on the domains or their
            restored file.
        recompute: Recompute and update the manager's current double helices.
    """

    def restore(self):
        """
        Setup the double helices manager from a blank program state.

        This method creates the double helices object. The .compute() method of the
        DoubleHelices must be called to obtain actual data, but the StrandsManager
        calls that method automatically.
        """
        # If the domains need to be loaded in, load them in.
        if self.runner.managers.domains.current is None:
            self.runner.managers.domains.restore()

        # Create an instance of DoubleHelices from the current domains.
        self.current = DoubleHelices.from_domains(
            self.runner.managers.domains.current,
            self.runner.managers.nucleic_acid_profile.current,
        )

    def recompute(self):
        """
        Recompute the double helices.

        This uses double_helices.compute() to recompute all data for double helices
        in-place.

        Notes:
            This is a very expensive operation.
        """
        # Remove the current action repetition settings.
        with suppress(AttributeError):
            self.runner.window.toolbar.repeat.setChecked(False)
            self.runner.window.toolbar.repeat.clicked.emit()
        # Regenerate the double helices based off of the current domains.
        self.current = DoubleHelices.from_domains(
            domains=self.runner.managers.domains.current,
            nucleic_acid_profile=self.runner.managers.nucleic_acid_profile.current,
        )
        # Compute the points based off of the newly computed double helices.
        # (.from_domains()
        self.current.compute()
        # Log that the double helices have been computed.
        logger.info("Recomputed double helices.")
        return self.current
