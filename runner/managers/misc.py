from structures.points import NEMid


class MiscManager:
    """
    Container for miscellaneous settings.

    Attributes:
        plot_types: The types of currently plotted points.
        currently_selected: The currently selected point(s).
    """

    def __init__(self):
        self.plot_types = (NEMid,)
        self.currently_selected = []
