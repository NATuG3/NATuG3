from runner.managers.domains import DomainsManager
from runner.managers.misc import MiscManager
from runner.managers.nucleic_acid_profile import NucleicAcidProfileManager
from runner.managers.strands import StrandsManager
from runner.managers.toolbar import ToolbarManager


class Managers:
    def __init__(self, runner: "Runner"):
        self.runner = runner

        # Load in the various individual properties
        self.nucleic_acid_profile = NucleicAcidProfileManager()
        self.domains = DomainsManager(self.runner)
        self.strands = StrandsManager(self.runner)

        # Load in other data managers
        self.toolbar = ToolbarManager(self.runner)
        self.misc = MiscManager()

    def setup(self):
        """
        Calls the setup methods of the various managers.

        The order in which managers are set up is very important, since some rely on
        others being already set up (for example, we can't load the strands manager
        until the nucleic acid profile manager has been loaded).
        """
        self.nucleic_acid_profile.setup()
        self.domains.setup()
        self.strands.setup()
        self.toolbar.setup()
        # self.misc doesn't require setup()
