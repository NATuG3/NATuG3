from config.nucleic_acid import storage
import config.nucleic_acid.ui.profiles
import logging
from types import SimpleNamespace
from PyQt6 import uic
from PyQt6.QtWidgets import QWidget
from resources import fetch_icon


logger = logging.getLogger(__name__)


class panel(QWidget):
    """Nucleic Acid Config Tab"""

    def __init__(self) -> None:
        super().__init__()
        uic.loadUi("config/designer/nucleic_acid.ui", self)

        # store accesable reference of self in storage
        storage.panel_instance = self

        # prettify buttons
        self.load_profile_button.setIcon(fetch_icon("download-outline"))
        self.save_profile_button.setIcon(fetch_icon("save-outline"))
        self.delete_profile_button.setIcon(fetch_icon("trash-outline"))

        # create list of all input boxes for easier future access
        # (notably for when we link all the inputs to functions, we can itterate this tuple)
        self.input_widgets = (
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
        )

        # restore the current settinsg
        self.dump_settings(storage.current)

        # set up profile manager
        config.nucleic_acid.ui.profiles.setup(self)

        self._setting_descriptions()

    def dump_settings(self, profile: storage.profile) -> None:
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

    def fetch_settings(self) -> storage.profile:
        """Fetch a profile object with all current nucleic acid settings from inputs."""
        # fetch the value of each needed attribute to build a profile from their respective widgets
        return storage.profile(
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

    def _setting_descriptions(self):
        self.setting_descriptions = SimpleNamespace()

        self.setting_descriptions.D = (
            "Diameter of Domain",
            "The diameter of a given domain.",
        )

        self.setting_descriptions.H = (
            "Twist Height",
            "The height of one turn of the helix of a nucleic acid.",
        )

        self.setting_descriptions.T = (
            "Turns",
            "There are B bases per T turns of the helix.",
        )

        self.setting_descriptions.B = (
            "Bases",
            "There are B bases per T turns of the helix.",
        )

        self.setting_descriptions.Z_b = (
            "Base height",
            'The height between two bases on the helix axis. Equal to "(T*H)/B".',
        )

        self.setting_descriptions.Z_c = (
            "Characteristic Height",
            "The height a helix climbs as it rotates through the characteristic angle.",
        )

        self.setting_descriptions.Z_s = (
            "Strand Switch Height",
            "The vertical height between two NEMids on different helices of the same double helix.",
        )

        self.setting_descriptions.theta_b = (
            "Base Angle",
            "The angle that one base makes about the helix axis.",
        )

        self.setting_descriptions.theta_c = (
            "Characteristic Angle",
            "The smallest angle about the helix axis possible between two NEMids on the same helix.",
        )

        self.setting_descriptions.theta_s = (
            "Switch Angle",
            "The angle about the helix axis between two NEMids on different helices of a double helix.",
        )

        # set status tip/tool tip of all lables and input boxes
        # with the above setting descriptions
        for input_widget in self.input_widgets:
            input_widget = input_widget.objectName()
            exec(
                f"""
                self.{input_widget}.setToolTip(
                    self.setting_descriptions.{input_widget}[0]
                )
                self.{input_widget}.setStatusTip(
                    self.setting_descriptions.{input_widget}[1]
                )
                self.{input_widget}_label.setToolTip(
                    self.setting_descriptions.{input_widget}[0]
                )
                self.{input_widget}_label.setStatusTip(
                    self.setting_descriptions.{input_widget}[1]
                )
                """.replace(
                    "                ", ""
                )
            )
        logger.info("Set statusTips/toolTips for all input widgets.")
