import logging
from typing import Dict

from PyQt6 import uic
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QWidget

import helpers
import refs
from structures.misc import Profile
from ui.resources import fetch_icon

logger = logging.getLogger(__name__)


class Panel(QWidget):
    """Nucleic Acid Config Tab."""

    updated = pyqtSignal(Profile)

    def __init__(self, parent, profiles: Dict[str, Profile]) -> None:
        super().__init__(parent)
        self.profiles: Dict[str, Profile] = profiles
        uic.loadUi("ui/panels/nucleic_acid/panel.ui", self)

        # prettify profiles buttons
        self.load_profile_button.setIcon(fetch_icon("download-outline"))
        self.save_profile_button.setIcon(fetch_icon("save-outline"))
        self.delete_profile_button.setIcon(fetch_icon("trash-outline"))

        # set all setting descriptions
        self._setting_descriptions()

        # set up the profiles manager
        self._profile_manager()

        logger.debug("Loaded nucleic acid settings tab of config panel.")

    def dump_settings(self, profile: Profile) -> None:
        """Saves current settings to profiles with name in text edit input box."""
        self.D.setValue(profile.D)
        self.H.setValue(profile.H)
        self.T.setValue(profile.T)
        self.B.setValue(profile.B)
        self.Z_c.setValue(profile.Z_c)
        self.Z_s.setValue(profile.Z_s)
        self.Z_b.setValue(profile.Z_b)
        self.theta_b.setValue(profile.theta_b)
        self.theta_c.setValue(profile.theta_c)
        self.theta_s.setValue(profile.theta_s)

    def fetch_settings(self) -> Profile:
        """Fetch a profiles object with all current nucleic acid settings from inputs."""
        return Profile(
            D=self.D.value(),
            H=self.H.value(),
            T=self.T.value(),
            B=self.B.value(),
            Z_c=self.Z_c.value(),
            Z_s=self.Z_s.value(),
            theta_b=self.theta_b.value(),
            theta_c=self.theta_c.value(),
            theta_s=self.theta_s.value(),
        )

    def _profile_manager(self):
        self.profile_chooser.list = lambda: [
            self.profile_chooser.itemText(i)
            for i in range(self.profile_chooser.count())
        ]

        self.profile_chooser.index = lambda name: self.profile_chooser.list().index(
            name
        )

        def save_profile(self):
            """Worker for the save profiles button"""
            if self.save_profile_button.toolTip() == "Overwrite Profile":
                if not helpers.confirm(
                    self,
                    "Overwrite confirmation",
                    f'Are you sure you want to overwrite the profiles named "'
                    + self.profile_chooser.currentText()
                    + '" with the currently chosen nucleic acid settings?',
                ):
                    return

            # obtain name of profiles to save
            profile_name = self.profile_chooser.currentText()
            assert len(profile_name) > 0

            # fetch current settings and store them under the chosen name
            self.profiles[profile_name] = self.fetch_settings()

            # clear profiles chooser to make placeholder text visable
            self.profile_chooser.setCurrentText("")

            # log that the profiles was saved (and print the name/repr of the saved profiles)
            logger.debug(
                f"Current settings: {self.profiles[profile_name]}"
            )
            logger.info(f'Saved current settings as profiles named "{profile_name}"')

            # if the profiles name is not already in the profiles chooser...
            if profile_name not in self.profile_chooser.list():
                # add the new profiles to the profiles chooser
                self.profile_chooser.addItem(profile_name)

        def delete_profile(self):
            """Worker for the delete profiles button"""
            if not helpers.confirm(
                self,
                "Delete profiles confirmation",
                f'Are you sure you want to delete the profiles named "'
                + self.profile_chooser.currentText()
                + '"?\nNote that this action cannot be undone!',
            ):
                return

            # obtain name of profiles to delete
            profile_name = self.profile_chooser.currentText()

            # delete stored profiles
            assert profile_name in self.profiles
            del self.profiles[profile_name]

            # remove profiles by index from profiles chooser
            self.profile_chooser.removeItem(self.profile_chooser.index(profile_name))

            # the profiles with the name of the previous contents of the box has been deleted
            # so now empty the profiles chooser's box
            self.profile_chooser.setCurrentText("")

            # clear profiles chooser to make placeholder text visable
            self.profile_chooser.setCurrentText("")

            # log that the profiles was deleted
            logger.info(f'Deleted profiles named "{profile_name}"')

        def load_profile(self):
            """Worker for the load profiles button"""
            if not helpers.confirm(
                self,
                "Load profiles confirmation",
                f"Are you sure you want to overwrite all currently chosen settings"
                + ' with those of the profiles named "'
                + self.profile_chooser.currentText()
                + '"?',
            ):
                return

            # obtain the name of profiles to load
            profile_name = self.profile_chooser.currentText()

            # dump settings of profiles chooser's text
            self.dump_settings(self.profiles[profile_name])

            # clear profiles chooser to make placeholder text visable
            self.profile_chooser.setCurrentText("")

            # log that the profiles was loaded
            logger.debug(
                f"Settings that were loaded: {self.profiles[profile_name]}"
            )
            logger.info(f'Loaded profiles named "{profile_name}"')

        def input_box_changed():
            """Worker for when any input box is changed"""
            # fetch settings of input boxes
            self.updated.emit(self.fetch_settings())

            # if B or T or H were changed Z_b also will have changed
            self.Z_b.setValue(self.fetch_settings().Z_b)

            # the currently chosen/inputted profiles name
            chosen_profile_name = self.profile_chooser.currentText()

            # if the chosen profiles name is in the saved profiles list:
            if chosen_profile_name in self.profiles:
                # if the chosen profiles name's settings match the current input box values
                if (
                    self.profiles[chosen_profile_name]
                    == self.fetch_settings()
                ):
                    self.load_profile_button.setEnabled(False)
                    self.load_profile_button.setStatusTip(
                        f'Current settings match saved settings of profiles named "{chosen_profile_name}."'
                    )

                    self.save_profile_button.setEnabled(False)
                    self.save_profile_button.setToolTip("Save Profile")
                    self.save_profile_button.setStatusTip(
                        f'Current settings match saved settings of profiles named "{chosen_profile_name}.".'
                    )

                    self.delete_profile_button.setEnabled(True)
                    self.delete_profile_button.setStatusTip(
                        f'Delete the profiles named "{chosen_profile_name}." This action is irreversible.'
                    )
                # if the chosen profiles name is not in
                else:
                    self.load_profile_button.setEnabled(True)
                    self.load_profile_button.setStatusTip(
                        f'Load back the settings of "{chosen_profile_name}."'
                    )

                    self.save_profile_button.setEnabled(True)
                    self.save_profile_button.setToolTip("Overwrite Profile")
                    self.save_profile_button.setStatusTip(
                        f'Overwrite profiles named "{chosen_profile_name}" with current settings.'
                    )

                    self.delete_profile_button.setEnabled(True)
                    self.delete_profile_button.setStatusTip(
                        f'Delete the profiles named "{chosen_profile_name}." This action is irreversible.'
                    )

                # no matter what, do not let the user alter default profiles
                if chosen_profile_name in refs.nucleic_acid.defaults:
                    self.save_profile_button.setEnabled(False)
                    self.save_profile_button.setToolTip("Save Profile")
                    self.save_profile_button.setStatusTip(
                        f'Cannot alter a default profiles. "{chosen_profile_name}." is a default profiles.'
                    )

                    self.delete_profile_button.setEnabled(False)
                    self.delete_profile_button.setStatusTip(
                        f'Cannot delete a default profiles. "{chosen_profile_name}." is a default profiles.'
                    )

            # the chosen profiles name is a brand-new profiles name (that has not already been saved)
            else:
                self.load_profile_button.setEnabled(False)
                self.load_profile_button.setStatusTip(
                    f'No saved profiles is named "{chosen_profile_name}." Cannot load a profiles that does not exist.'
                )

                self.save_profile_button.setEnabled(True)
                self.save_profile_button.setToolTip("Save Profile")
                self.save_profile_button.setStatusTip(
                    f'Save current as a new profiles named "{chosen_profile_name}.".'
                )

                self.delete_profile_button.setEnabled(False)
                self.delete_profile_button.setStatusTip(
                    f'No saved profiles is named "{chosen_profile_name}." Cannot delete a profiles that does not exist.'
                )

            # No matter what we cannot save a profiles with a blank name
            if chosen_profile_name == "":
                self.load_profile_button.setEnabled(False)
                self.load_profile_button.setStatusTip(
                    "Profile chooser entry box is empty. Enter the name of the profiles to load."
                )

                self.save_profile_button.setEnabled(False)
                self.save_profile_button.setStatusTip(
                    "Profile chooser entry box is empty. Enter the name of the profiles to save."
                )

                self.delete_profile_button.setEnabled(False)
                self.delete_profile_button.setStatusTip(
                    "Profile chooser entry box is empty. Enter the name of the profiles to delete."
                )

        def hook_widgets():
            # when the save profiles button is clicked call save_profile()
            self.save_profile_button.clicked.connect(lambda: save_profile(self))
            # save button needs to be locked right after it's clicked
            self.save_profile_button.clicked.connect(input_box_changed)

            # when the delete profiles button is clicked call delete_profile()
            self.delete_profile_button.clicked.connect(lambda: delete_profile(self))

            # when load profiles button is clicked load profiles
            self.load_profile_button.clicked.connect(lambda: load_profile(self))
            # load button needs to be locked right after it's clicked
            self.load_profile_button.clicked.connect(input_box_changed)

            # hook all inputs to the following input_box_changed function
            for input in (
                self.D,
                self.H,
                self.T,
                self.B,
                self.Z_b,
                self.Z_c,
                self.Z_s,
                self.theta_b,
                self.theta_c,
                self.theta_s,
            ):
                input.valueChanged.connect(input_box_changed)
            self.profile_chooser.currentTextChanged.connect(input_box_changed)

            # add each profiles from the save file to the combo box
            for profile_name in self.profiles:
                self.profile_chooser.addItem(profile_name)

        # hook all buttons to their workers
        hook_widgets()

        # set placeholder text of profiles chooser
        self.profile_chooser.lineEdit().setPlaceholderText("Profile Name Here")
        self.profile_chooser.setCurrentText("")

        # set up button locking/other needed functions initially
        input_box_changed()

    def _setting_descriptions(self):
        self.D.setToolTip = "Diameter of Domain"
        self.D.setStatusTip("The diameter of a given domain.")

        self.H.setToolTip("Twist Height")
        self.H.setStatusTip("The height of one turn of the helix of a nucleic acid.")

        self.T.setToolTip("Turns")
        self.T.setStatusTip("There are B bases per T turns of the helix.")

        self.B.setToolTip = "Bases"
        self.B.setStatusTip("There are B bases per T turns of the helix.")

        self.Z_b.setToolTip = "Base height"
        self.Z_b.setStatusTip = (
            'The height between two bases on the helix axis. Equal to "(T*H)/B".'
        )

        self.Z_c.setToolTip = "Characteristic Height"
        self.Z_c.setStatusTip = (
            "The height a helix climbs as it rotates through the characteristic angle."
        )

        self.Z_s.setToolTip("Strand Switch Height")
        self.Z_s.setStatusTip(
            "The vertical height between two NEMids on different helices of the same double helix."
        )

        self.theta_b.setToolTip("Base Angle")
        self.theta_b.setStatusTip("The angle that one base makes about the helix axis.")

        self.theta_c.setToolTip("Characteristic Angle")
        self.theta_c.setStatusTip(
            "The smallest angle about the helix axis possible between two NEMids on the same helix."
        )

        self.theta_s.setToolTip = "Switch Angle"
        self.theta_s.setStatusTip(
            "The angle about the helix axis between two NEMids on different helices of a double helix."
        )

        logger.info("Set statusTips/toolTips for all input widgets.")
