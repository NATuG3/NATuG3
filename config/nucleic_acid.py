import pickle
import logging
from PyQt6 import uic
from PyQt6.QtWidgets import QWidget
from resources import fetch_icon
from dataclasses import dataclass
from contextlib import suppress
import references


filename = "config/saves/nucleic_acid.nano"
current = None  # current profile
profiles = None  # all profiles
logger = logging.getLogger(__name__)


@dataclass
class profile:
    """
    A settings profile.

    Attributes:
        D (float): Diameter of a domain.
        H (float): Height of a turn.
        T (float): There are T turns every B bases.
        B (float): There are B bases every T turns.
        Z_c (float): Characteristic height.
        Z_s (float): Switch height.
        Z_b (float): Base height.
        theta_b (float): Base angle.
        theta_c (float): Characteristic angle.
        theta_s (float): Switch angle.
    """

    D: float = 0
    H: float = 0.0
    T: int = 0
    B: int = 0
    Z_c: float = 0.0
    Z_s: float = 0.0
    theta_b: float = 0.0
    theta_c: float = 0.0
    theta_s: float = 0.0

    def __post_init__(self) -> None:
        # compute Z_b based on T, H, and B
        self.Z_b = (self.T * self.H) / self.B
        self.Z_b = round(self.Z_b, 4)

    def __eq__(self, other: object) -> bool:
        """Returns true if identical profile is returned"""
        return vars(self) == vars(other)


def load() -> None:
    global current
    global profiles

    # attempt to load the nucleic acid settings file
    try:
        logger.debug("Settings file found. Loading setting profiles...")
        # attempt to open the settings file, or create a new settings file with
        # DNA-B settings (as a default/example)
        with open(filename, "rb") as settings_file:
            profiles = pickle.load(settings_file)
        # if profile dict was empty then reset to default
        # (by triggering the exception which causes a default reload)
        if profiles == {}:
            raise FileNotFoundError
        # let the current settings be the first item in profiles
        current = profiles[next(iter(profiles))]
    # if the file does not exist then create a new one with default settings
    except FileNotFoundError:
        logger.debug("Settings file not found. Restoring defaults...")
        # default profile is for B-DNA
        current = profile(
            D=2.2,
            H=3.549,
            T=2,
            B=21,
            Z_c=0.17,
            Z_s=1.26,
            theta_b=34.29,
            theta_c=17.1428,
            theta_s=2.3,
        )
        # this will be the only profile in the master list
        # (since the master list of profiles is being created now)
        profiles = {"B-DNA": current}

    # log that profiles were loaded
    logger.debug("Loaded profiles.")
    logger.debug(profiles)


def dump() -> None:
    """Dump persisting attributes of this module to a file"""
    # dump settings to file in format current-profile, all-profiles
    with open(filename, "wb") as settings_file:
        pickle.dump(profiles, settings_file)


class widget(QWidget):
    """Nucleic Acid Config Tab"""

    def __init__(self) -> None:
        super().__init__()
        uic.loadUi("config/ui/nucleic_acid.ui", self)

        # prettify buttons
        self.load_profile_button.setIcon(fetch_icon("download-outline"))
        self.load_profile_button.setStyleSheet(
            "QPushButton::disabled{background-color: rgb(210, 210, 210)}"
        )
        self.save_profile_button.setIcon(fetch_icon("save-outline"))
        self.save_profile_button.setStyleSheet(
            "QPushButton::disabled{background-color: rgb(210, 210, 210)}"
        )
        self.delete_profile_button.setIcon(fetch_icon("trash-outline"))
        self.delete_profile_button.setStyleSheet(
            "QPushButton::disabled{background-color: rgb(210, 210, 210)}"
        )

        # create list of all input boxes for easier future access
        # (notably for when we link all the inputs to functions, we can itterate this tuple)
        self.input_widgets = (
            self.D,
            self.H,
            self.T,
            self.B,
            self.Z_c,
            self.Z_s,
            self.theta_b,
            self.theta_c,
            self.theta_s,
        )

        # restore the current settinsg
        self.dump_settings(current)

        # set up the profile manager
        self._profile_manager()

    def _profile_manager(self) -> None:
        """Set up the profile manager."""
        # function to obtain list of all items in profile_chooser
        self.profile_list = lambda: [
            self.profile_chooser.itemText(i)
            for i in range(self.profile_chooser.count())
        ]

        # easy access function to obtain index of a given profile
        self.profile_index = lambda name: self.profile_list().index(name)

        # add each profile from the save file to the combo box
        for profile_name in profiles:
            self.profile_chooser.addItem(profile_name)

        # save the currently loaded profile name as the previously loaded profile name
        self.previous_profile_name = self.profile_chooser.currentText()

        # Worker for the save button
        def save_profile():
            # obtain name of profile to save
            profile_name = self.profile_chooser.currentText()
            # don't allow blank profile names
            if profile_name == "":
                logger.debug("Cannot create profile with blank name")
                return
            # save the profile with the current settings
            profiles[profile_name] = self.fetch_settings()
            if profile_name not in self.profile_list():
                # add the new profile to the profile chooser
                self.profile_chooser.addItem(profile_name)
            # the currently saved profile will become the last profile state
            self.self.previous_profile_name = profile_name

        # when the save profile button is clicked call save_profile()
        self.save_profile_button.clicked.connect(save_profile)

        # Worker for the delete button
        def delete_profile():
            # obtain name of profile to delete
            profile_name = self.profile_chooser.currentText()
            with suppress(KeyError):
                del profiles[profile_name]
                # index of profile in the profile chooser dropdown
                profile_index = self.profile_index(profile_name)
                # remove profile by index from profile chooser
                self.profile_chooser.removeItem(profile_index)

        # when the delete profile button is clicked call delete_profile()
        self.delete_profile_button.clicked.connect(delete_profile)

        def load_profile():
            # load profile button worker
            # previously_loaded_name is a global variable
            # which indicates the name of the previously located profile
            global previously_loaded_name

            # since we just loaded a profile the button gets disabled
            # (since there's no point in loading it again until settings have changed)
            self.load_profile_button.setEnabled(False)

            # dump settings of profile chooser's text
            self.dump_settings(profiles[self.profile_chooser.currentText()])

        # when load profile button is clicked load profiles
        self.load_profile_button.clicked.connect(load_profile)
        self.load_profile_button.clicked.connect(
            lambda: self.load_profile_button.setEnabled(False)
        )

        # load the restored settings profile
        load_profile()

        # Called when any of the input boxes values are changed
        def settings_updater(input):
            # we are modifying the global input variable
            global current

            # fetch settings of input boxes
            current = self.fetch_settings()

            # if B or T or H were changed Z_b also will have changed
            self.Z_b.setValue(current.Z_b)

        def button_locker():
            """Lock profile manager button(s) based on chosen profile's updatedness and newness."""
            # the chosen profile's name is NOT the name of an already existant profile
            chosen_profile_name_is_new = (
                self.profile_chooser.currentText() not in profiles
            )
            logger.debug(f"chosen-profile-is-new-is: {chosen_profile_name_is_new}")

            # the actual current settings match the current profile's settings
            try:
                chosen_profile_is_updated = not (
                    current == profiles[self.previous_profile_name]
                )
                logger.debug(
                    f"chosen-profile-is-updated is: {chosen_profile_is_updated}"
                )
            except KeyError:  # the previously loaded profile was deleted
                chosen_profile_is_updated = True

            # lock/unlock profile manager buttons according to state
            if chosen_profile_name_is_new:
                if chosen_profile_is_updated:  # and is new
                    # can't load a profile that doesn't exist
                    self.load_profile_button.setEnabled(False)
                    # can save a profile that doesn't already exist
                    self.save_profile_button.setEnabled(True)
                    # can't delete a profile that doesn't exist
                    self.delete_profile_button.setEnabled(False)
                else:  # chosen profile is updated and is new
                    # can't load a profile that doesn't exist
                    self.load_profile_button.setEnabled(False)
                    # new profile will be a copy of an existing one; that's fine
                    self.save_profile_button.setEnabled(True)
                    # can't delete a profile that doesn't exist
                    self.delete_profile_button.setEnabled(False)
            else:
                if chosen_profile_is_updated:  # and not new
                    # can load back the saved state of an existing but changed profile
                    self.load_profile_button.setEnabled(True)
                    # can overwrite existing profile with the new settings
                    self.save_profile_button.setEnabled(True)
                    # can delete a profile no matter if it is updated or not
                    self.delete_profile_button.setEnabled(True)
                else:  # chosen profile is not updated and not new
                    # doesn't make sense to overwrite current settings with identical ones
                    self.load_profile_button.setEnabled(False)
                    # doesn't make sense to overwrite a profile with the exact same settings
                    self.save_profile_button.setEnabled(False)
                    # can delete a profile no matter if it is updated or not
                    self.delete_profile_button.setEnabled(True)

        # hook all inputs to the following functions...
        for input in self.input_widgets:
            input.valueChanged.connect(lambda: settings_updater(input))
            input.valueChanged.connect(button_locker)

        self.profile_chooser.currentTextChanged.connect(button_locker)
        button_locker()

    def dump_settings(self, profile: profile) -> None:
        """Saves current settings to profile with name in text edit input box."""
        # set the value of all widgets to their respective profile attribute
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

    def fetch_settings(self) -> profile:
        """Fetch a profile object with all current nucleic acid settings from inputs."""
        # fetch the value of each needed attribute to build a profile from their respective widgets
        return profile(
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
