from natug.runner.managers.domains import DomainsManager
from natug.runner.managers.double_helices import DoubleHelicesManager
from natug.runner.managers.misc import MiscManager
from natug.runner.managers.nucleic_acid_profile import NucleicAcidProfileManager
from natug.runner.managers.snapshots import SnapshotsManager
from natug.runner.managers.strands import StrandsManager
from natug.runner.managers.toolbar import ToolbarManager


class Managers:
    """
    A container for all of NATuG's managers.
    """

    def __init__(self, runner: "Runner"):
        """
        Initialize a container for all of NATuG's managers.

        Args:
            runner: NATuG's current runner.
        """
        self.runner = runner

        # Load in the various individual properties
        self.nucleic_acid_profile = NucleicAcidProfileManager(self.runner)
        self.domains = DomainsManager(self.runner)
        self.double_helices = DoubleHelicesManager(self.runner)
        self.strands = StrandsManager(self.runner)
        self.snapshots = SnapshotsManager(self.runner)

        # Load in other data managers
        self.toolbar = ToolbarManager(self.runner)
        self.misc = MiscManager()

    def fill_with_dummies(self):
        """Fill current manager instances with dummy instances of various datatypes."""
        # First load blank data structures
        from natug.structures.domains import Domains
        from natug.structures.helices import DoubleHelices
        from natug.structures.profiles import NucleicAcidProfile

        # fmt: off
        self.nucleic_acid_profile.current = nucleic_acid_profile = NucleicAcidProfile()
        self.domains.current = domains = Domains.dummy(nucleic_acid_profile)
        self.double_helices.current = double_helices = DoubleHelices.from_domains(
            domains, nucleic_acid_profile)
        self.strands.current = double_helices.strands()
        # fmt: on
