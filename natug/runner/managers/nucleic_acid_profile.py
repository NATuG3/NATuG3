import atexit
import logging
import os

from natug import settings
from natug.runner.managers.manager import Manager
from natug.structures.profiles import NucleicAcidProfile

logger = logging.getLogger(__name__)


class NucleicAcidProfileManager(Manager):
    """
    Manager for the program's current NucleicAcidProfile instance.

    Attributes:
        current: The current NucleicAcidProfile instance.
        runner: NATuG's program runner.
        profiles_filepath: The path to the directory where profiles are stored.
        restored_filepath: The path to the file where the restored state is stored.
        default_profile_name: The name of the default profile.

    Methods:
        load_profiles: Load the nucleic acid profiles from files.
        dump_profiles: Dump the nucleic acid profiles into files.
        restore: Load default NucleicAcidProfile
    """

    profiles_filepath = f"saves/nucleic_acid"
    default_filepath = (
        f"saves/nucleic_acid/{settings.default_nucleic_acid_profile}.json"
    )

    def __init__(self, runner: object, current: object = None, profiles=None):
        super().__init__(runner, current)
        if profiles:
            self.profiles = profiles
        else:
            self.profiles = {}
            self.load_profiles()
        atexit.register(self.dump)

    def restore(self):
        """Load the default nucleic acid profile as the current one."""
        self.current = self.profiles[settings.default_nucleic_acid_profile]
        logger.debug(
            f"Loaded current nucleic acid profile {settings.default_nucleic_acid_profile}"
        )

    def load_profiles(self) -> None:
        """
        Load saved profiles and restored state from files.

        Each profile is loaded from a separate file in the profiles directory. The
        names of the files are the names of the profiles where underscores are
        replaced with spaces (dumping is the reverse of this).

        No specific current profile is set because when the program loads an entire
        program state is reloaded which includes the current nucleic acid profile.
        """
        profile_files = filter(
            lambda filename: filename.endswith(".json"),
            os.listdir(self.profiles_filepath),
        )

        # Load all profiles from individual files in the profiles directory
        for name in profile_files:
            # Load the profile from the file (we make sure to replace underscores
            # with spaces and ".json" with "")
            self.profiles[name.replace("_", " ").replace(".json", "")] = (
                NucleicAcidProfile.from_file(f"{self.profiles_filepath}/{name}")
            )
            logger.info(
                f'Loaded "%s" from "%s"', name, f"{self.profiles_filepath}/{name}.json"
            )

        # Log that profiles were loaded
        logger.debug("Loaded profiles. Profiles: %s", self.profiles)

    def dump(self) -> None:
        """
        Dump profiles and the current state to files.

        Each profile is dumped to a separate file in the profiles directory. The
        names of the files are the names of the profiles where spaces are replaced
        with underscores (loading is the reverse of this).
        """
        # Dump all profiles into individual files
        for filename in os.listdir(self.profiles_filepath):
            filepath = f"{self.profiles_filepath}/{filename}"
            os.remove(filepath)
            logger.debug(f'Deleted nucleic acid profile file "%s"', filepath)
        for name, profile in self.profiles.items():
            name = name.replace(" ", "_")
            profile.to_file(f"{self.profiles_filepath}/{name}.json")
            logger.info(
                f'Dumped "%s" into "%s"', name, f"{self.profiles_filepath}/{name}.json"
            )
