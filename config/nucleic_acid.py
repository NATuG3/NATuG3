import pickle
import logging
from PyQt6 import uic
from PyQt6.QtWidgets import QWidget, QCompleter
from PyQt6.QtCore import QStringListModel, Qt
from dataclasses import dataclass
from contextlib import suppress


filename = "nucleic_acid_profiles.nano"
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

def load() -> None:
    global current
    global profiles

    try:
        logger.debug("Settings file found. Loading setting profiles...")
        # attempt to open the settings file, or create a new settings file with
        # DNA-B settings (as a default/example)
        with open(filename, "rb") as settings_file:
            current, profiles = pickle.load(settings_file)

    except FileNotFoundError:
        logger.debug("Settings file not found. Restoring defaults...")
        current = profile(
            D=2.2,
            H=3.549,
            T=2,
            B=21,
            Z_c=0.17,
            Z_s=1.26,
            theta_b=34.29,
            theta_c=360 / 21,
            theta_s=2.3,
        )
        profiles = {"B-DNA": current}

    logger.debug("Loaded profiles.")
    logger.debug(profiles)


def dump() -> None:
    """Dump persisting attributes of this module to a file"""
    # dump settings to file in format current-profile, all-profiles
    with open(filename, "wb") as settings_file:
        pickle.dump((current, profiles), settings_file)


class widget(QWidget):
    """Nucleic Acid Config Tab"""

    def __init__(self) -> None:
        super().__init__()
        uic.loadUi("config/ui/nucleic_acid.ui", self)


        # restore the current settinsg
        self.dump_settings(current)
        profiles["Restored Settings"] = current
        self.profile_chooser.addItem("Restored Settings")

        # blacklist of profile names
        self.profile_name_blacklist = ("Restored Settings", "B-DNA")

        # hook all input boxes to respective functions
        self._inputs()

        # set up the profile manager
        self._profile_manager()

    def _profile_manager(self) -> None:
        """Set up the profile manager"""
        # function to obtain list of all items in profile_chooser
        profile_list = self.profile_chooser.item_list = lambda: [self.profile_chooser.itemText(i) for i in range(self.profile_chooser.count())]
        # add each profile to the combo box
        for profile_name in profiles:
            self.profile_chooser.addItem(profile_name)

        def save_profile():
            """Save profile button worker"""
            # obtain name of profile to save
            profile_name = self.profile_editor.text()
            if profile_name not in self.profile_name_blacklist:
                # save the profile with the current settings
                profiles[profile_name] = self.fetch_settings()
                if profile_name not in profile_list():
                    # add the new profile to the profile chooser
                    self.profile_chooser.addItem(profile_name)
                    # index of profile in the profile chooser dropdown
                    profile_index = profile_list().index(profile_name)
                    # set the current chosen profile to the new one
                    self.profile_chooser.setCurrentIndex(profile_index)
            self.profile_editor.setText("")
            # add profile to autocomplete
            update_profile_editor_autocomplete()
        # connect save profile button to save profile function
        self.save_profile_button.clicked.connect(save_profile)

        def delete_profile():
            """Delete profile button worker"""
            # obtain name of profile to delete
            profile_name = self.profile_editor.text()
            if profile_name not in self.profile_name_blacklist:
                with suppress(KeyError):
                    del profiles[profile_name]
                    # index of profile in the profile chooser dropdown
                    profile_index = profile_list().index(profile_name)
                    # remove profile by index from profile chooser
                    self.profile_chooser.removeItem(profile_index)
                    # clear text in profile chooser
                    self.profile_chooser.setCurrentText("")
            self.profile_editor.setText("")
            # remove profile from autocomplete
            update_profile_editor_autocomplete()
        # connect delete profile button to delete profile function
        self.delete_profile_button.clicked.connect(delete_profile)

        def load_profile():
            """Current-profile-changed worker."""
            current_profile = self.profile_chooser.currentText()
            self.dump_settings(profiles[current_profile])
        # connect profile chooser combo box to update profile function
        self.load_profile_button.clicked.connect(load_profile)

        # enable auto fill suggestions for profile editor text edit box
        def update_profile_editor_autocomplete(): 
            """Set up/update profile editor entry box autocomplete."""
            autocomplete = QCompleter(
                profile_list(),
                self,
                caseSensitivity=Qt.CaseSensitivity(0) # 0 = case insensitive
            )
            model = QStringListModel(autocomplete)
            autocomplete.setModel(model)
            self.profile_editor.setCompleter(autocomplete)
        update_profile_editor_autocomplete()


    def _inputs(self) -> None:
        """Link input boxes to their respective functions."""
        # if the value of any input is changed then update
        # nucliec_acid.current to match the new settings
        # and Z_b will be recomputed if T or B was changed
        def input_changed():
            global current
            # fetch settings of input boxes
            current = self.fetch_settings()
            # if B or T or H were changed Z_b also will have changed
            self.Z_b.setValue(current.Z_b)
        # hook all inputs to the above function
        self.D.valueChanged.connect(input_changed)
        self.H.valueChanged.connect(input_changed)
        self.T.valueChanged.connect(input_changed)
        self.B.valueChanged.connect(input_changed)
        self.Z_c.valueChanged.connect(input_changed)
        self.Z_s.valueChanged.connect(input_changed)
        self.theta_b.valueChanged.connect(input_changed)
        self.theta_c.valueChanged.connect(input_changed)
        self.theta_s.valueChanged.connect(input_changed)

    def dump_settings(self, profile: profile) -> None:
        """Saves current settings to profile with name in text edit input box."""
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
