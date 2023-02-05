import atexit
import logging
import os

from structures.profiles import NucleicAcidProfile

logger = logging.getLogger(__name__)


class NucleicAcidProfileManager:
    """
    Manager for nucleic acid settings.

    Attributes:
        profiles_filepath: The path to the directory where profiles are stored.
        restored_filepath: The path to the file where the restored state is stored.
        default_profile_name: The name of the default profile.

    Methods:
        load: Load the nucleic acid profiles from files.
        dump: Dump the nucleic acid profiles into files.
    """

    profiles_filepath = f"saves/nucleic_acid"
    restored_filepath = f"saves/nucleic_acid/Restored.json"
    default_profile_name = "MFD B-DNA"

    def __init__(self):
        """Initialize the nucleic acid module."""
        # create a dictionary to store the profiles
        self.profiles = {}

        # load profiles from files
        self.current = None

    def setup(self):
        # load the profiles
        self.load()

        # dump profiles to files on exit
        atexit.register(self.dump)

    def load(self) -> None:
        """
        Load saved profiles and restored state from files.

        Each profile is loaded from a separate file in the profiles directory. The
        names of the files are the names of the profiles where underscores are
        replaced with spaces (dumping is the reverse of this).
        """
        profile_files = filter(
            lambda filename: filename.endswith(".json"),
            os.listdir(self.profiles_filepath),
        )

        # load all profiles from individual files in the profiles directory
        for name in profile_files:
            # load the profile from the file (we make sure to replace underscores
            # with spaces and ".json" with "")
            self.profiles[
                name.replace("_", " ").replace(".json", "")
            ] = NucleicAcidProfile.from_file(f"{self.profiles_filepath}/{name}")
            logger.info(
                f'Loaded "%s" from "%s"', name, f"{self.profiles_filepath}/{name}.json"
            )

        # attempt to load the restored state from the restored file
        try:
            self.current = NucleicAcidProfile.from_file(self.restored_filepath)
        # if unable to locate nucleic acid settings file then make no changes and
        # announce that the default settings will be used
        except FileNotFoundError:
            logger.warning("Restored profile file not found. Defaults restored.")
            # by default choose B type DNA as the profile
            self.current: NucleicAcidProfile = self.profiles["MFD B-DNA"]

        # log that profiles were loaded
        logger.debug("Loaded profiles. Profiles: %s", self.profiles)

    def dump(self) -> None:
        """
        Dump profiles and the current state to files.

        Each profile is dumped to a separate file in the profiles directory. The
        names of the files are the names of the profiles where spaces are replaced
        with underscores (loading is the reverse of this).
        """
        # dump all profiles into individual files
        for name, profile in self.profiles.items():
            name = name.replace(" ", "_")
            profile.to_file(f"{self.profiles_filepath}/{name}.json")
            logger.info(
                f'Dumped "%s" into "%s"', name, f"{self.profiles_filepath}/{name}.json"
            )

        # dump current settings into a separate "restored" file
        with open(self.restored_filepath, "wb") as settings_file:
            self.current.to_file(settings_file.name)
            logger.info(f'Dumped current nucleic_acid settings into "{settings_file}"')
