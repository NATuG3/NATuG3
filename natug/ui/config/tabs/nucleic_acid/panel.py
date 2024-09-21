import logging
from copy import copy
from typing import Dict

from PyQt6.QtCore import pyqtSignal, pyqtSlot
from PyQt6.QtWidgets import QPlainTextEdit, QWidget
from PyQt6 import uic

from natug import settings
from natug.structures.profiles import NucleicAcidProfile
from natug.ui.dialogs.refresh_confirmer.refresh_confirmer import RefreshConfirmer
from natug.ui.widgets.profile_manager import ProfileManager

logger = logging.getLogger(__name__)


class NucleicAcidPanel(QWidget):
    """
    The "Nucleic Acid" tab of the config panel.

    This tab has all the settings for the given nucleic acid. The settings can be
    accessed as a NucleicAcidProfile object through the fetch_nucleic_acid_profile()
    method of the class. The settings can be changed by calling the
    dump_nucleic_acid_profile() method of the class. Some settings are not editable,
    and are instead calculated from other settings automatically.

    When a setting is updated, the _push_updates() method is called, which,
    if needed, cautions the user that the current helix graph will be overwritten if
    they proceed with the update, and then updates the helix graph and refreshes the
    plots.

    Signals:
        updated: Emitted by _push_updates() when the settings are updated. This
            triggers the plots to be refreshed, and is picked up on by the parent
            ConfigPanel widget
    """

    updated = pyqtSignal()

    def __init__(
        self, parent, runner: "runner.Runner", profiles: Dict[str, NucleicAcidProfile]
    ) -> None:
        self.runner = runner
        super().__init__(parent)
        self.profiles: Dict[str, NucleicAcidProfile] = profiles
        self._pushing_updates = False

        uic.loadUi("./ui/config/tabs/nucleic_acid/panel.ui", self)

        # set all setting descriptions
        self._setting_descriptions()

        # set up nucleic_acid_profile manager
        self._profile_manager()

        # load defaults
        self.dump_nucleic_acid_profile(
            self.runner.managers.nucleic_acid_profile.current
        )

        # setup signals
        self._hook_signals()

        logger.debug("Loaded nucleic acid settings tab of config panel.")

    def _inputs(self):
        """Obtain a list of all the input widgets."""
        return (
            self.D,
            self.H,
            self.T,
            self.g,
            self.B,
            self.Z_b,
            self.Z_c,
            self.Z_mate,
            self.notes_area,
        )

    def dump_nucleic_acid_profile(self, profile: NucleicAcidProfile) -> None:
        """Saves current settings to profiles with name in text edit input box."""
        try:
            for input in self._inputs():
                input.blockSignals(True)
            if profile != self.fetch_nucleic_acid_profile():
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
                self.notes_area.setPlainText(profile.notes)
                self.runner.snapshot()
        finally:
            for input in self._inputs():
                input.blockSignals(False)

    def fetch_nucleic_acid_profile(self) -> NucleicAcidProfile:
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
            notes=self.notes_area.toPlainText(),
        )
        logger.debug("Fetched nucleic acid settings from inputs. (%s)", profile)
        return profile

    def _push_updates(self):
        """
        Warn the user if they are about to overwrite strand data, and if they are
        okay with that, then update the nucleic acid profile and refresh the current
        strands. Otherwise, revert to the old nucleic acid profile.
        """
        if self._pushing_updates:
            return
        self._pushing_updates = True
        # Warn the user if they are about to overwrite strand data, and give them the
        # opportunity to save the current state and then update the domains.
        if RefreshConfirmer.run(self.runner):
            self.runner.managers.nucleic_acid_profile.current.update(
                self.fetch_nucleic_acid_profile()
            )
            self.updated.emit()
            logger.debug("Updated nucleic acid profile.")
        # They rather not update the domains, so revert to the old domains.
        else:
            self.dump_nucleic_acid_profile(
                self.runner.managers.nucleic_acid_profile.current
            )
            logger.debug(
                "Did not update nucleic acid profile settings because user chose not"
                "to."
            )
        self._pushing_updates = False

    def _hook_signals(self):
        """
        Hook all signals to their respective slots.

        Hooks each input to the _on_input_updated slot. This slot is called when the
        user changes the value of an input and then clicks away from it. The slot
        automatically handles updating the helix graph.
        """
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
            input_.editingFinished.connect(self._on_input_updated)

        def notes_area_altered_focus_out_event(*args, **kwargs):
            super(QPlainTextEdit, self.notes_area).focusOutEvent(*args, **kwargs)
            self._on_input_updated()

        self.notes_area.focusOutEvent = notes_area_altered_focus_out_event

    def _profile_manager(self):
        """
        Set up profile manager.

        The profile manager is a widget that allows the user to save and load
        profiles. It is a separate widget that is added to the layout of this widget.
        Within the profile manager, the user can save the current settings as a
        profile, load a profile, and delete a profile. The profile manager also
        contains various default profiles that the user can load easily.
        """
        self.profile_manager = ProfileManager(
            self,
            self.fetch_nucleic_acid_profile,
            self.dump_nucleic_acid_profile,
            profiles=copy(self.runner.managers.nucleic_acid_profile.profiles),
            defaults=settings.default_nucleic_acid_profiles,
        )

        # When a profile is loaded, update the domains. That's because it is possible
        # that when they load the profile is different from the profile
        # that the current strand graph uses.
        self.profile_manager.profile_loaded.connect(self._push_updates)

        def profiles_dict_update():
            self.runner.managers.nucleic_acid_profile.profiles = (
                self.profile_manager.profiles
            )

        self.profile_manager.profile_saved.connect(profiles_dict_update)
        self.profile_manager.profile_deleted.connect(profiles_dict_update)

        # Add the profile manager to the top of the layout by inserting it at index 0.
        self.layout().insertWidget(0, self.profile_manager)

    def _setting_descriptions(self):
        """
        Set the statusTip and toolTip for all input widgets. These descriptions are
        hardcoded here.
        """

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

    @pyqtSlot()
    def _on_input_updated(self):
        """
        Worker for when a nucleic acid parameter is updated.

        1) Fetches and dumps the current nucleic acid profile, to automatically
            update some nucleic acid settings that are dependent on other nucleic acid
            settings.
        2) Runs the push_updates() method.
        """
        new_nucleic_acid_profile = self.fetch_nucleic_acid_profile()
        self.dump_nucleic_acid_profile(new_nucleic_acid_profile)
        self._push_updates()
