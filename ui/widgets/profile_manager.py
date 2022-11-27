import logging
from types import FunctionType
from typing import Iterable, Dict

from PyQt6 import uic
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QGroupBox

import helpers
from ui.resources import fetch_icon

logger = logging.getLogger(__name__)


class ProfileManager(QGroupBox):
    """A nucleic_acid_profile managing widget."""

    profile_loaded = pyqtSignal(str, object)
    profile_deleted = pyqtSignal(str)
    profile_saved = pyqtSignal(str, object)
    chosen_changed = pyqtSignal(str)

    def __init__(
            self,
            parent,
            extractor: FunctionType,
            dumper: FunctionType,
            title="Profile Manager",
            warning: str | None = None,
            defaults: Iterable[str] | None = None,
            default="",
            profiles: Dict[str, object] = None,
    ):
        """
        Initialize the nucleic_acid_profile manager.

        Args:
            parent: The parent QObject.
            extractor: The worker called to extract data for new profiles.
            dumper: The worker called to dump data for a loaded nucleic_acid_profile.
            title: The title of the group box containing the nucleic_acid_profile manager. Shows up above manager.
            warning: Warning shown when user attempts to load a nucleic_acid_profile.
            defaults: Profile names that are defaults. User cannot delete default profiles.
            default: The nucleic_acid_profile that is chosen by default.
            profiles: All possible profiles.

        Notes:
            When a nucleic_acid_profile is saved it is saved under a dict entry. The format is {new_name: extractor()}.
        """
        super().__init__(title, parent)
        uic.loadUi("ui/widgets/profile_manager.ui", self)
        self.extractor = extractor
        self.dumper = dumper
        self.default = self.current = default
        self.warning = warning

        # set up default profiles
        if defaults is None:
            self.defaults = dict()
        else:
            self.defaults = defaults

        # set up all possible profiles
        if profiles is None:
            self.profiles = dict()
        else:
            self.profiles = profiles

        # add nucleic_acid_profile options to nucleic_acid_profile chooser
        for profile in self.profiles.keys():
            self.profile_chooser.addItem(profile)

        # run setup workers
        self._prettify()
        self._signals()
        self.update()

    def listed(self):
        """Obtain list of all profiles in nucleic_acid_profile chooser's list."""
        profiles = []
        for profile_index in range(self.profile_chooser.count()):
            profiles.append(self.profile_chooser.itemText(profile_index))
        return profiles

    def profile_index(self, name: str):
        """Obtain the index of a given nucleic_acid_profile in the nucleic_acid_profile chooser."""
        return self.listed().index(name)

    def current_text(self):
        """Obtain current nucleic_acid_profile chooser text."""
        return self.profile_chooser.currentText()

    def approve(self) -> bool:
        """Present the user with a popup stating self.warning. If user approves request, return True."""
        if self.warning is not None:
            if not helpers.confirm(self.warning):
                return False
        return True

    def _prettify(self):
        # prettify profiles buttons
        self.load_profile_button.setIcon(fetch_icon("download-outline"))
        self.save_profile_button.setIcon(fetch_icon("save-outline"))
        self.delete_profile_button.setIcon(fetch_icon("trash-outline"))

        # set placeholder text of profiles chooser
        self.profile_chooser.lineEdit().setPlaceholderText("Profile Name Here")
        self.profile_chooser.setCurrentText("")

        if self.default is not None:
            self.profile_chooser.setCurrentText(self.default)

    def _signals(self):
        # hook main buttons
        self.save_profile_button.clicked.connect(lambda: self.save(self.current_text()))
        self.delete_profile_button.clicked.connect(
            lambda: self.delete(self.current_text())
        )
        self.load_profile_button.clicked.connect(lambda: self.load(self.current_text()))

        # some buttons need to be locked right after they're clicked
        self.save_profile_button.clicked.connect(self.update)
        self.load_profile_button.clicked.connect(self.update)

        # other signals
        self.profile_chooser.currentTextChanged.connect(self.update)
        self.profile_chooser.currentIndexChanged.connect(self.update)

    def save(self, name: str):
        if self.save_profile_button.toolTip() == "Overwrite Profile":
            if not self.approve():
                return

        # fetch current settings and store them under the chosen name
        self.profiles[name] = self.extractor()

        # clear profiles chooser to make placeholder text visable
        self.profile_chooser.setCurrentText("")

        # if the profiles name is not already in the profiles chooser...
        if name not in self.listed():
            # add the new profiles to the profiles chooser
            self.profile_chooser.addItem(name)

        # emit signal
        self.profile_saved.emit(name, self.profiles[name])

        logger.info(f'Saved new nucleic_acid_profile "{name}"')

    def delete(self, name: str):
        if not self.approve():
            return

        # remove profiles by index from profiles chooser
        self.profile_chooser.removeItem(self.profile_index(name))

        # delete stored profiles
        assert name in self.profiles
        del self.profiles[name]

        # the profiles with the name of the previous contents of the box has been deleted
        # so now empty the profiles chooser's box
        self.profile_chooser.setCurrentText("")

        # clear profiles chooser to make placeholder text visible
        self.profile_chooser.setCurrentText("")

        # emit signal
        self.profile_deleted.emit(name)

        # log that the profiles was deleted
        logger.info(f'Deleted profiles named "{name}"')

    def load(self, name: str):
        if not self.approve():
            return

        # dump settings of profiles chooser's text
        self.dumper(self.profiles[name])

        # clear profiles chooser to make placeholder text visable
        self.profile_chooser.setCurrentText("")

        # change current nucleic_acid_profile
        self.current = self.profiles[name]

        # emit signal
        self.profile_loaded.emit(name, self.profiles[name])

        # log that the profiles was loaded
        logger.debug(f"Settings that were loaded: {self.profiles[name]}")
        logger.info(f'Loaded profiles named "{name}"')

    def update(self):
        """Update the profile manager's buttons based on new inputs."""
        # the currently chosen/inputted profiles name
        chosen_profile_name = self.current_text()

        # if the chosen profiles name is in the saved profiles list:
        if chosen_profile_name in self.profiles:
            # if the chosen profiles name's settings match the current input box values
            if self.profiles[chosen_profile_name] == self.extractor():
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
            if chosen_profile_name in self.defaults:
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

        self.chosen_changed.emit(chosen_profile_name)
