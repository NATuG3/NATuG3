from natug.runner.managers.manager import Manager
from natug.structures.points import NEMid


class MiscManager(Manager):
    """
    Container for miscellaneous settings.

    Attributes:
        plot_types: The types of currently plotted points.
        currently_selected: The currently selected point(s).
        action_repeater: The ActionRepeaterProfile that holds the settings for the
            action repeater.
    """

    def __init__(self):
        self.plot_types = (NEMid,)
        self.currently_selected = []
        self.action_repeater = None
