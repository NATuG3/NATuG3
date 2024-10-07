import logging

import pandas as pd

from natug import settings
from natug.runner.managers.manager import Manager
from natug.structures.domains import Domains

logger = logging.getLogger(__name__)


class DomainsManager(Manager):
    """
    Manager for the application's domains.

    Attributes:
        current: The current double helices.
        runner: NATuG's current runner.

    Methods:
        restore: Load domains from default domains preset.
    """

    default_filepath = f"saves/domains/{settings.default_domain_preset}.csv"

    def restore(self):
        """Restore domains from the domains default preset file."""
        self.current = Domains.from_df(
            pd.read_csv(DomainsManager.default_filepath),
            self.runner.managers.nucleic_acid_profile.current,
        )
        logger.info("Restored previous domain editor state.")



