import atexit
import logging
import os

from structures.profiles import NucleicAcidProfile

logger = logging.getLogger(__name__)


class _NucleicAcid:
    """
    Manager for the application's nucleic acid settings.

    Attributes:
        current: The current nucleic acid profile.
        profiles: The nucleic acid profiles.

    Methods:
        load: Load the nucleic acid profiles from files.
        dump: Dump the nucleic acid profiles into files.
    """
    class filenames:
        profiles = f"saves/nucleic_acid"
        restored = f"saves/nucleic_acid/Restored.json"

    defaults = {
        "MFD B-DNA": NucleicAcidProfile(
            D=2.2,
            H=3.549,
            g=134.8,
            T=2,
            B=21,
            Z_c=0.17,
            Z_s=1.26,
            Z_mate=0.094,
            theta_b=34.29,
            theta_c=17.1428,
            theta_s=2.343,
        )
    }

    def __init__(self):
        """Initialize the nucleic acid module."""
        # by default set profiles to the defaults
        self.profiles = self.defaults

        # by default choose B type DNA as the profile
        self.current: NucleicAcidProfile = self.profiles["MFD B-DNA"]

        # load profiles from files
        self.load()

        # dump profiles to files on exit
        atexit.register(self.dump)

    def load(self) -> None:
        """
        Load saved profiles and restored state from files.

        Each profile is loaded from a separate file in the profiles directory. The names of the files are the
        names of the profiles where underscores are replaced with spaces (dumping is the reverse of this).
        """
        # load all profiles from individual files in the profiles directory
        for name in filter(
            lambda filename: filename.endswith(".json"),
            os.listdir(self.filenames.profiles),
        ):
            # load the profile from the file (we make sure to replace underscores with spaces and ".json" with "")
            self.profiles[name.replace("_", " ").replace(".json", "")] = NucleicAcidProfile.from_file(
                "json", f"{self.filenames.profiles}/{name}"
            )
            logger.info(
                f'Loaded "%s" from "%s"', name, f"{self.filenames.profiles}/{name}.json"
            )

        # attempt to load the restored state from the restored file
        try:
            self.current = NucleicAcidProfile.from_file(
                "json", self.filenames.restored
            )
        # if unable to locate nucleic acid settings file then make no changes and announce that
        # the default settings will be used
        except FileNotFoundError:
            logger.warning("Saved profiles file not found. Defaults restored.")

        # log that profiles were loaded
        logger.debug("Loaded profiles. Profiles: %s", self.profiles)

    def dump(self) -> None:
        """
        Dump profiles and the current state to files.

        Each profile is dumped to a separate file in the profiles directory. The names of the files are the
        names of the profiles where spaces are replaced with underscores (loading is the reverse of this).
        """
        # dump all profiles into individual files
        for name, profile in self.profiles.items():
            name = name.replace(" ", "_")
            profile.to_file("json", f"{self.filenames.profiles}/{name}.json")
            logger.info(
                f'Dumped "%s" into "%s"', name, f"{self.filenames.profiles}/{name}.json"
            )

        # dump current settings into a separate "restored" file
        with open(self.filenames.restored, "wb") as settings_file:
            self.current.to_file("json", settings_file.name)
            logger.info(f'Dumped current nucleic_acid settings into "{settings_file}"')
