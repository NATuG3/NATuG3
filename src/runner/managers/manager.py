class Manager:
    """
    A template manager.

    A manager is a container for a specific instance of a part of a nanotube. Domains,
    Helices, NucleicAcidProfiles, and more have dedicated managers that store the
    program's current instance. Managers may provide additional utility methods, but
    their core ability is to store an instance.

    Attributes:
        runner: NATuG's current program runner instance.
        current: The current instance of what is being managed.
    """

    def __init__(self, runner: "Runner", manager: object = None):
        """
        Create an instance of a manager.

        Args:
            managee: The current instance of the thing being managed.
        """
        self._current = None
        self._manager_type = None
        self.current = manager
        self.runner = runner

    @property
    def current(self):
        """Fetch the current managee instance"""
        return self._current

    @current.setter
    def current(self, value: object):
        """
        Update the current managee instance.

        Args:
            value: The new managee instance. Must be of the same type of the manage
                that was set at init.
        """
        if self._manager_type is None and value is not None:
            self._manager_type = type(value)
        if self._manager_type is not None and not isinstance(value, self._manager_type):
            raise TypeError(
                f"Cannot set {self.__class__}.current to type other than "
                f"{self._manager_type}. Got {type(value)}."
            )
        self._current = value
