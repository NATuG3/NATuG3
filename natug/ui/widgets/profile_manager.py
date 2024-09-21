import logging
from copy import copy
from typing import Callable, Dict, Iterable

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QGroupBox
from PyQt6 import uic

from natug import utils
from natug.ui.resources import fetch_icon

logger = logging.getLogger(__name__)


class ProfileManager(QGroupBox):
    """
    A profile managing widget.

    This allows for easy management of settings profiles, and automates
    loading/saving/deleting of profiles. Profiles are stored in a dict under string
    names, and functions for loading/saving are customizable.

    Signals:
        profile_loaded: Emitted when a profile is loaded.
        profile_saved: Emitted when a profile is saved.
        profile_deleted: Emitted when a profile is deleted.
        updated: Emitted when any of the above signals are emitted.
    """

    updated = pyqtSignal()
    profile_loaded = pyqtSignal(str, object)
    profile_deleted = pyqtSignal(str)
    profile_saved = pyqtSignal(str, object)
    chosen_changed = pyqtSignal(str)

    def __init__(
        self,
        parent,
        extractor: Callable,
        dumper: Callable,
        title="Profile Manager",
        warning: str | None = None,
        defaults: Iterable[str] | None = None,
        default="",
        profiles: Dict[str, object] = None,
    ):
        """
        Initialize the profile manager.

        Args:
            parent: The strands QObject.
            extractor: The worker called to extract data for new profiles.
            dumper: The worker called to dump data for a loaded profile.
            title: The title of the group box containing the profile manager. Shows up
                above manager.
            warning: Warning shown when user attempts to load a profile.
            defaults: Profile names that are defaults. User cannot delete default profiles.
            default: The profile that is chosen by default.
            profiles: The profiles in the profile manager.

        Notes:
            When a profile is saved it is saved under a dict entry. The format is
                {new_name: extractor()}.
        """
        super().__init__(title, parent)
        uic.loadUi("./ui/widgets/profile_manager.ui", self)
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

        # clone all profiles in the array
        # so that we don't accidentally mutate the originals
        for name, profile in self.profiles.items():
            self.profiles[name] = copy(profile)

        # add profile options to profile chooser
        for profile in self.profiles.keys():
            self.profile_chooser.addItem(profile)

        # run setup workers
        self._prettify()
        self._signals()
        self.update()

        logger.debug("Profile Manager initialized.")

    def listed(self) -> list[str]:
        """Obtain list of all profiles in profile chooser's list."""
        profiles = []
        for profile_index in range(self.profile_chooser.count()):
            profiles.append(self.profile_chooser.itemText(profile_index))
        return profiles

    def profile_index(self, name: str):
        """Obtain the index of a given profile in the profile chooser."""
        return self.listed().index(name)

    def current_text(self) -> str:
        """Obtain current profile chooser text."""
        return self.profile_chooser.currentText()

    def approve(self) -> bool:
        """Present the user with a popup stating self.warning. If user approves
        request, return True."""
        if self.warning is not None:
            if not utils.confirm(
                self.parent(), "Profile Manager Warning", self.warning
            ):
                return False
        return True

    def _prettify(self) -> None:
        # prettify profiles buttons
        self.load_profile_button.setIcon(fetch_icon("download-outline"))
        self.save_profile_button.setIcon(fetch_icon("save-outline"))
        self.delete_profile_button.setIcon(fetch_icon("trash-outline"))

        # set placeholder text of profiles chooser
        self.profile_chooser.lineEdit().setPlaceholderText("Profile Name Here")
        self.profile_chooser.setCurrentText("")

        if self.default is not None:
            self.profile_chooser.setCurrentText(self.default)

    def _signals(self) -> None:
        # hook main buttons
        self.save_profile_button.clicked.connect(lambda: self.save(self.current_text()))
        self.delete_profile_button.clicked.connect(
            lambda: self.delete(self.current_text())
        )
        self.load_profile_button.clicked.connect(lambda: self.load(self.current_text()))

        # some buttons need to be locked right after they're clicked
        self.save_profile_button.clicked.connect(self.update)
        self.delete_profile_button.clicked.connect(self.update)
        self.load_profile_button.clicked.connect(self.update)

        # other signals
        self.profile_chooser.currentTextChanged.connect(self.update)
        self.profile_chooser.currentIndexChanged.connect(self.update)

        # hook all signals to the updated signal
        self.profile_loaded.connect(self.updated.emit)
        self.profile_deleted.connect(self.updated.emit)
        self.profile_saved.connect(self.updated.emit)

        logger.debug("Profile Manager signals hooked.")

    def save(self, name: str, override=False) -> None:
        if self.save_profile_button.toolTip() == "Overwrite Profile":
            if not self.approve() and not override:
                return

        # fetch current settings and store them under the chosen name
        self.profiles[name] = self.extractor()

        # clear profiles chooser to make placeholder text visable
        self.profile_chooser.setCurrentText("")

        # if the profiles name is not already in the profiles chooser...
        if name not in self.listed():
            # add the new profiles to the profiles chooser
            self.profile_chooser.addItem(name)

        # change current profile
        self.current = name

        # emit signal
        self.profile_saved.emit(name, self.profiles[name])

        logger.info(f'Saved new profile "%s"', name)

    def delete(self, name: str, override=False) -> None:
        if not self.approve() and not override:
            return

        # remove profiles by index from profiles chooser
        self.profile_chooser.removeItem(self.profile_index(name))

        # delete stored profiles
        assert name in self.profiles
        del self.profiles[name]

        # the profiles with the name of the previous contents of the box has been
        # deleted so now empty the profiles chooser's box
        self.profile_chooser.setCurrentText("")

        # clear profiles chooser to make placeholder text visible
        self.profile_chooser.setCurrentText("")

        # change current profile
        self.current = self.default

        # emit signal
        self.profile_deleted.emit(name)

        # log that the profiles was deleted
        logger.info(f'Deleted profiles named "%s"', name)

    def load(self, name: str, override=False) -> None:
        if not self.approve() and not override:
            return
        # dump settings of profiles chooser's text
        self.dumper(self.profiles[name])

        # clear profiles chooser to make placeholder text visable
        self.profile_chooser.setCurrentText("")

        # change current profile
        self.current = name

        # emit signal
        self.profile_loaded.emit(name, self.profiles[name])

        # log that the profiles was loaded
        logger.debug(f"Settings that were loaded: %s", self.profiles[name])
        logger.info(f'Loaded profiles named "%s"', name)

    def update(self) -> None:
        """Update the profile manager's buttons based on new inputs."""
        # the currently chosen/inputted profiles name
        chosen_profile_name = self.current_text()

        # if the chosen profiles name is in the saved profiles list:
        if chosen_profile_name in self.profiles:
            # if the chosen profiles name's settings match the current input box values
            if self.profiles.get(self.current) == self.extractor():
                logger.debug(
                    "Current profiles settings match the input box values\nprevious: "
                    "%s; inputted: %s",
                    self.profiles.get(self.current),
                    self.extractor(),
                )
                self.load_profile_button.setEnabled(False)
                self.load_profile_button.setStatusTip(
                    f"Current settings match saved settings of profiles named "
                    f'"{chosen_profile_name}."'
                )

                self.save_profile_button.setEnabled(False)
                self.save_profile_button.setToolTip("Save Profile")
                self.save_profile_button.setStatusTip(
                    f"Current settings match saved settings of profiles named "
                    f'"{chosen_profile_name}.".'
                )

                self.delete_profile_button.setEnabled(True)
                self.delete_profile_button.setStatusTip(
                    f'Delete the profiles named "{chosen_profile_name}." This action '
                    f"is irreversible. "
                )
            # if the chosen profiles name is not in
            else:
                logger.debug(
                    "Current profiles settings do not match the input box "
                    "values\nprevious: %s; inputted: %s",
                    self.profiles.get(self.current),
                    self.extractor(),
                )
                self.load_profile_button.setEnabled(True)
                self.load_profile_button.setStatusTip(
                    f'Load back the settings of "{chosen_profile_name}."'
                )

                self.save_profile_button.setEnabled(True)
                self.save_profile_button.setToolTip("Overwrite Profile")
                self.save_profile_button.setStatusTip(
                    f'Overwrite profiles named "{chosen_profile_name}" with current '
                    f"settings. "
                )

                self.delete_profile_button.setEnabled(True)
                self.delete_profile_button.setStatusTip(
                    f'Delete the profiles named "{chosen_profile_name}." This action '
                    f"is irreversible. "
                )

            # no matter what, do not let the user alter default profiles
            if chosen_profile_name in self.defaults:
                logger.debug(
                    "Current profiles is a default profile. "
                    "Disabling save and delete buttons and enabling load button."
                )
                self.load_profile_button.setEnabled(True)
                self.load_profile_button.setStatusTip(
                    f'Load back the settings of "{chosen_profile_name}."'
                )

                self.save_profile_button.setEnabled(False)
                self.save_profile_button.setToolTip("Save Profile")
                self.save_profile_button.setStatusTip(
                    f'Cannot alter a default profiles. "{chosen_profile_name}." is a '
                    f"default profile. "
                )

                self.delete_profile_button.setEnabled(False)
                self.delete_profile_button.setStatusTip(
                    f'Cannot delete a default profiles. "{chosen_profile_name}." is a '
                    f"default profile. "
                )

        # the chosen profiles name is a brand-new profiles name (that has not already
        # been saved)
        else:
            self.load_profile_button.setEnabled(False)
            self.load_profile_button.setStatusTip(
                f'No saved profiles is named "{chosen_profile_name}." Cannot load a '
                f"profiles that does not exist. "
            )

            self.save_profile_button.setEnabled(True)
            self.save_profile_button.setToolTip("Save Profile")
            self.save_profile_button.setStatusTip(
                f'Save current as a new profiles named "{chosen_profile_name}.".'
            )

            self.delete_profile_button.setEnabled(False)
            self.delete_profile_button.setStatusTip(
                f'No saved profiles is named "{chosen_profile_name}." Cannot delete a '
                f"profiles that does not exist. "
            )

        # No matter what we cannot save a profiles with a blank name
        if chosen_profile_name == "":
            self.load_profile_button.setEnabled(False)
            self.load_profile_button.setStatusTip(
                "Profile chooser entry box is empty. Enter the name of the profiles "
                "to load. "
            )

            self.save_profile_button.setEnabled(False)
            self.save_profile_button.setStatusTip(
                "Profile chooser entry box is empty. Enter the name of the profiles "
                "to save. "
            )

            self.delete_profile_button.setEnabled(False)
            self.delete_profile_button.setStatusTip(
                "Profile chooser entry box is empty. Enter the name of the profiles "
                "to delete. "
            )

        self.chosen_changed.emit(chosen_profile_name)
