import atexit
import logging
import pickle
from typing import Dict

import settings
from structures.profiles import NucleicAcidProfile

logger = logging.getLogger(__name__)


class _NucleicAcid:
    class filenames:
        profiles = f"saves/nucleic_acid/profiles.{settings.extension}"
        restored = f"saves/nucleic_acid/restored.{settings.extension}"

    defaults = {
        "B-DNA (MFD)": NucleicAcidProfile(
            D=2.2,
            H=3.549,
            T=2,
            B=21,
            Z_c=0.17,
            Z_s=1.26,
            theta_b=34.29,
            theta_c=17.1428,
            theta_s=2.343,
        )
    }

    def __init__(self):
        self.profiles: Dict[
            str, Profile
        ] = self.defaults  # by default set profiles to the defaults
        self.current: Profile = next(
            iter(self.defaults.values())
        )  # by default choose the first profiles in defaults

        self.load()
        atexit.register(self.dump)

    def load(self) -> None:
        try:
            # load all profiles
            with open(self.filenames.profiles, "rb") as file:
                self.profiles = pickle.load(file)
                assert isinstance(self.profiles, dict)

            # load restored settings
            with open(self.filenames.restored, "rb") as file:
                self.current = pickle.load(file)
                assert isinstance(self.current, NucleicAcidProfile)

            logger.debug("Saved profiles file loaded.")
        # if unable to locate nucleic acid settings file then
        except FileNotFoundError:
            logger.warning("Saved profiles file not found. Defaults restored.")

        # log that profiles were loaded
        logger.debug("Loaded profiles.")
        logger.debug(self.profiles)

    def dump(self) -> None:
        """Dump persisting attributes of this module to a file"""
        with open(self.filenames.profiles, "wb") as file:
            assert isinstance(self.profiles, dict)

            # perform data validation before save
            for name, profile in self.profiles.items():
                if not isinstance(profile, NucleicAcidProfile):
                    logger.critical(
                        "Data validation for nucleic_acid profiles dump failed."
                    )
                    raise TypeError(
                        f'profiles named "{name}" is not a profiles', profile
                    )

            pickle.dump(self.profiles, file)
            logger.info(f'Dumped all profiles into "{file}"')

        # dump current settings
        with open(self.filenames.restored, "wb") as settings_file:
            # perform data validation before save
            if not isinstance(self.current, NucleicAcidProfile):
                logger.critical(
                    "Data validation for nucleic_acid current profiles dump failed."
                )
                raise TypeError("current is not a profiles", profile)
            pickle.dump(self.current, settings_file)
            logger.info(f'Dumped current nucleic_acid settings into "{settings_file}"')
