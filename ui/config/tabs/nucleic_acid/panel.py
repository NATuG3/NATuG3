import logging
from copy import copy
from functools import partial
from typing import Dict

from PyQt6 import uic
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QWidget

from structures.profiles import NucleicAcidProfile
from ui.widgets.profile_manager import ProfileManager

logger = logging.getLogger(__name__)


class NucleicAcidPanel(QWidget):
    """
    Nucleic Acid Config Tab.

    Signals:
        updated: Emitted when a setting is changed. Sends a function to be called.
    """

    updated = pyqtSignal(object)

    def __init__(
        self, parent, runner: "runner.Runner", profiles: Dict[str, NucleicAcidProfile]
    ) -> None:
        self.runner = runner
        super().__init__(parent)
        self.profiles: Dict[str, NucleicAcidProfile] = profiles

        uic.loadUi("ui/config/tabs/nucleic_acid/panel.ui", self)

        # set all setting descriptions
        self._setting_descriptions()

        # set up nucleic_acid_profile manager
        self._profile_manager()

        # load defaults
        self.dump_settings(self.runner.managers.nucleic_acid_profile.current)

        # setup signals
        self._signals()

        logger.debug("Loaded nucleic acid settings tab of config panel.")

    def _signals(self):
        def on_input_updated():
            """Worker for when a widget is changed."""
            # Update the current nucleic_acid_profile with the new settings
            self.updated.emit(
                partial(
                    self.runner.managers.nucleic_acid_profile.current.update,
                    self.fetch_settings(),
                )
            )
            # Then dump the profile right back so that settings that need to be
            # computed get computed and displayed
            self.updated.emit(
                self.dump_settings(self.runner.managers.nucleic_acid_profile.current)
            )

        for input_ in (
            self.D,
            self.H,
            self.T,
            self.g,
            self.B,
            self.Z_b,
            self.Z_c,
            self.Z_mate,
        ):
            input_.editingFinished.connect(on_input_updated)

    def _profile_manager(self):
        """Set up nucleic_acid_profile manager."""
        self.profile_manager = ProfileManager(
            self,
            self.fetch_settings,
            self.dump_settings,
            profiles=copy(self.runner.managers.nucleic_acid_profile.profiles),
            defaults=self.runner.managers.nucleic_acid_profile.default_profile_name,
        )

        def profile_updated():
            """Slot for when a nucleic_acid_profile is loaded/saved."""
            self.runner.managers.nucleic_acid_profile.profiles = (
                self.profile_manager.profiles
            )
            name = self.profile_manager.current
            if len(name) > 0:
                profile = self.profile_manager.profiles[name]
                self.updated.emit(
                    partial(
                        self.runner.managers.nucleic_acid_profile.current.update,
                        profile,
                    )
                )

        # connect signals
        self.profile_manager.profile_loaded.connect(profile_updated)

        # add the nucleic_acid_profile manager to layout
        self.layout().insertWidget(0, self.profile_manager)

    def dump_settings(self, profile: NucleicAcidProfile) -> None:
        """Saves current settings to profiles with name in text edit input box."""
        self.D.setValue(profile.D)
        self.H.setValue(profile.H)
        self.g.setValue(profile.g)
        self.T.setValue(profile.T)
        self.B.setValue(profile.B)
        self.Z_c.setValue(profile.Z_c)
        self.Z_b.setValue(profile.Z_b)
        self.Z_mate.setValue(profile.Z_mate)
        self.theta_b.setValue(profile.theta_b)
        self.theta_c.setValue(profile.theta_c)

    def fetch_settings(self) -> NucleicAcidProfile:
        """Fetch a profiles object with all current nucleic acid settings from
        inputs."""
        profile = NucleicAcidProfile(
            D=self.D.value(),
            H=self.H.value(),
            g=self.g.value(),
            T=self.T.value(),
            B=self.B.value(),
            Z_c=self.Z_c.value(),
            Z_mate=self.Z_mate.value(),
        )
        logger.debug("Fetched nucleic acid settings from inputs. (%s)", profile)
        return profile

    def _setting_descriptions(self):
        self.D.setToolTip = "Diameter of Domain"
        self.D.setStatusTip("The diameter of a given domain.")

        self.H.setToolTip("Twist Height")
        self.H.setStatusTip("The height of one turn of the helix of a nucleic acid.")

        self.g.setToolTip("Nucleoside-Mate Angle")
        self.g.setStatusTip(
            "The angle between a nucleoside and its mate on the other helix."
        )

        self.T.setToolTip("Turns")
        self.T.setStatusTip("There are B bases per T turns of the helix.")

        self.B.setToolTip("Bases")
        self.B.setStatusTip("There are B bases per T turns of the helix.")

        self.Z_b.setToolTip("Base height")
        self.Z_b.setStatusTip(
            'The height between two bases on the helix axis. Equal to "(T*H)/B".'
        )

        self.Z_c.setToolTip("Characteristic Height")
        self.Z_c.setStatusTip(
            "The height a helix climbs as it rotates through the characteristic angle."
        )

        self.Z_mate.setToolTip("Nucleoside-Mate Vertical Distance")
        self.Z_mate.setStatusTip(
            "The vertical distance between a nucleoside and its mate on the other "
            "helix. "
        )

        self.theta_b.setToolTip("Base Angle")
        self.theta_b.setStatusTip("The angle that one base makes about the helix axis.")

        self.theta_c.setToolTip("Characteristic Angle")
        self.theta_c.setStatusTip(
            "The smallest angle about the helix axis possible between two NEMids on "
            "the same helix. "
        )

        logger.info("Set statusTips/toolTips for all input widgets.")
