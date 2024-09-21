import pickle


class Save:
    """
    Create a package to pickle and save.

    Attributes:
        domains (list): List of domain objects.
    """

    def __init__(self):
        self.domains = runner.domains.current
        self.strands = runner.strands.current

    @classmethod
    def from_file(cls, filename):
        """
        Load a save from a file.

        Args:
            filename (str): The name of the file to load from.
        """

        with open(filename, "rb") as load_file:
            package = pickle.load(load_file)
            if not isinstance(package, cls):
                raise TypeError(f"Package loaded from file is not of type {cls}!")

        return package
