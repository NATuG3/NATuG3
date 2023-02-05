class MiscManager:
    """
    Container for miscellaneous settings.

    Attributes:
        plot_mode: The current plot mode.
        currently_selected: The currently selected point(s).
    """

    def __init__(self):
        self.plot_mode = "NEMid"
        self.currently_selected = []
