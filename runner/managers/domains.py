import atexit
import logging

from structures.domains import Domains

logger = logging.getLogger(__name__)


class DomainsManager:
    """
    Manager for the application's domains.

    Attributes:
        current: The current domains.

    Methods:
        load: Load the domains from a file.
        dump: Dump the domains into a file.
        recompute: Recompute the domains.
    """

    restored_filepath: str = f"saves/domains/restored.csv"

    def __init__(self, runner: "Runner"):
        self.runner = runner
        self.current = None

    def setup(self):
        self.load()
        atexit.register(self.dump)

    def load(self):
        try:
            self.current = Domains.from_csv(
                self.restored_filepath,
                self.runner.managers.nucleic_acid_profile.current,
            )
            logger.info("Restored previous domain editor state.")
        except FileNotFoundError:
            self.current = Domains.from_csv(
                "saves/domains/presets/circle.csv",
                self.runner.managers.nucleic_acid_profile.current,
            )
            logger.warning(
                "Previous domain editor state save file not found. Defaults restored."
            )

    def dump(self):
        """Save current domains state for state restoration on load."""
        self.current.to_df().to_csv(self.restored_filepath)
