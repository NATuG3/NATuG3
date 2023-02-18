from runner.managers.domains import DomainsManager
from runner.managers.helices import DoubleHelicesManager
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
        self.double_helices = DoubleHelicesManager(self.runner)
        self.strands = StrandsManager(self.runner)

        # Load in other data managers
        self.toolbar = ToolbarManager(self.runner)
        self.misc = MiscManager()
