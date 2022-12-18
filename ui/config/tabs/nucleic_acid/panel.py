import logging
from copy import copy
from functools import partial
from typing import Dict

from PyQt6 import uic
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QWidget

import refs
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

    def __init__(self, parent, profiles: Dict[str, NucleicAcidProfile]) -> None:
        super().__init__(parent)
        self.profiles: Dict[str, NucleicAcidProfile] = profiles

        uic.loadUi("ui/config/tabs/nucleic_acid/panel.ui", self)

        # set all setting descriptions
        self._setting_descriptions()

        # set up nucleic_acid_profile manager
        self._profile_manager()

        # load defaults
        self.dump_settings(refs.nucleic_acid.current)

        # setup signals
        self._signals()

        logger.debug("Loaded nucleic acid settings tab of config panel.")

    def _signals(self):
        def on_input_updated():
            """Worker for when a widget is changed."""
            self.updated.emit(
                partial(refs.nucleic_acid.current.update, self.fetch_settings())
            )

        for input in (
            self.D,
            self.H,
            self.T,
            self.g,
            self.B,
            self.Z_b,
            self.Z_c,
            self.Z_s,
            self.Z_mate,
            self.theta_b,
            self.theta_c,
            self.theta_s,
        ):
            input.editingFinished.connect(on_input_updated)

    def _profile_manager(self):
        """Set up nucleic_acid_profile manager."""
        self.profile_manager = ProfileManager(
            self,
            self.fetch_settings,
            self.dump_settings,
            profiles=copy(refs.nucleic_acid.profiles),
            defaults=refs.nucleic_acid.defaults,
        )

        def profile_updated():
            """Slot for when a nucleic_acid_profile is loaded/saved."""
            refs.nucleic_acid.profiles = self.profile_manager.profiles
            name = self.profile_manager.current
            if len(name) > 0:
                profile = self.profile_manager.profiles[name]
                self.updated.emit(partial(refs.nucleic_acid.current.update, profile))

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
        self.Z_s.setValue(profile.Z_s)
        self.Z_b.setValue(profile.Z_b)
        self.Z_mate.setValue(profile.Z_mate)
        self.theta_b.setValue(profile.theta_b)
        self.theta_c.setValue(profile.theta_c)
        self.theta_s.setValue(profile.theta_s)

    def fetch_settings(self) -> NucleicAcidProfile:
        """Fetch a profiles object with all current nucleic acid settings from
        inputs. """
        return NucleicAcidProfile(
            D=self.D.value(),
            H=self.H.value(),
            g=self.g.value(),
            T=self.T.value(),
            B=self.B.value(),
            Z_c=self.Z_c.value(),
            Z_s=self.Z_s.value(),
            Z_mate=self.Z_mate.value(),
            theta_b=self.theta_b.value(),
            theta_c=self.theta_c.value(),
            theta_s=self.theta_s.value(),
        )

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

        self.Z_s.setToolTip("Strand Switch Height")
        self.Z_s.setStatusTip(
            "The vertical height between two NEMids on different helices of the same "
            "double helix. "
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

        self.theta_s.setToolTip("Switch Angle")
        self.theta_s.setStatusTip(
            "The angle about the helix axis between two NEMids on different helices "
            "of a double helix. "
        )

        logger.info("Set statusTips/toolTips for all input widgets.")
