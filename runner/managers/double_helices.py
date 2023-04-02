import logging
from contextlib import suppress

from structures.helices import DoubleHelices

logger = logging.getLogger(__name__)


class DoubleHelicesManager:
    """
    Manager for the application's double helices.

    Attributes:
        current: The current double helices.

    Methods:
        recompute: Recompute the strands.
    """

    def __init__(self, runner: "runner.Runner"):
        """Initialize the double helices module."""
        self.runner = runner
        self.current = None

    def setup(self):
        """
        Setup the double helices manager.

        This method creates the double helices object. The .compute() method of the
        DoubleHelices must be called to obtain actual data, but the StrandsManager
        calls that method automatically.
        """
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
        with suppress(AttributeError):
            self.runner.window.toolbar.repeat.setChecked(False)
            self.runner.window.toolbar.repeat.clicked.emit()
        self.current = DoubleHelices.from_domains(
            domains=self.runner.managers.domains.current,
            nucleic_acid_profile=self.runner.managers.nucleic_acid_profile.current,
        )
        self.current.compute()
        logger.info("Recomputed double helices.")
