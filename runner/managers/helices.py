from structures.helices import DoubleHelices


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
        self.current = DoubleHelices(
            runner.managers.domains.current,
            runner.managers.nucleic_acid_profile.current,
        )

    def setup(self):


    def recompute(self):
        """
        Recompute the double helices.

        This uses double_helices.compute() to recompute all data for double helices
        in-place.

        Notes:
            This is a very expensive operation.
        """
        self.current.compute()
