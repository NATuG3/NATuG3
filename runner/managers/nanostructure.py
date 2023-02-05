from structures.nanostructures.nanostructure import Nanostructure


class NanostructureManager:
    """
    Manager for the application's domains.

    Attributes:
        current: The current domains.

    Methods:
        load: Load the domains from a file.
        dump: Dump the domains into a file.
        recompute: Recompute the domains.
    """

    def __init__(self, runner: "Runner"):
        """
        Set up the nanostructure manager.

        Args:
            runner (Runner): NATuG's runner.
        """
        self.runner = runner
        self.current = None

    def setup(self):
        self.current = Nanostructure(
            strands=self.runner.managers.strands.current,
            nucleic_acid_profile=self.runner.managers.nucleic_acid_profile.current,
            domains=self.runner.managers.domains.current,
            helices=self.runner.managers.strands.current.double_helices,
        )
