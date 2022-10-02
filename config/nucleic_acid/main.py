from types import SimpleNamespace
from config.nucleic_acid import storage
import logging
from PyQt6 import uic
from PyQt6.QtWidgets import QWidget
from resources import fetch_icon


logger = logging.getLogger(__name__)


class panel(QWidget):
    """Nucleic Acid Config Tab"""

    def __init__(self) -> None:
        super().__init__()
        uic.loadUi("config/nucleic_acid/panel.ui", self)

        # place the current settings into their respective boxes
        self.dump_settings(storage.current)

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

        # set all setting descriptions
        self._setting_descriptions()

        # set up the profile manager
        self._profile_manager()

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

    def _profile_manager(self):
        self.profile_chooser.list = lambda: [
            self.profile_chooser.itemText(i)
            for i in range(self.profile_chooser.count())
        ]

        self.profile_chooser.index = lambda name: self.profile_chooser.list().index(
            name
        )

        def save_profile(self):
            """Worker for the save profile button"""
            # obtain name of profile to save
            profile_name = self.profile_chooser.currentText()
            assert len(profile_name) > 0

            # fetch current settings and store them under the chosen name
            storage.profiles[profile_name] = self.fetch_settings()

            # log that the profile was saved (and print the name/repr of the saved profile)
            logger.debug(f"Current settings: {storage.profiles[profile_name]}")
            logger.info(f'Saved current settings as profile named "{profile_name}"')

            # if the profile name is not already in the profile chooser...
            if profile_name not in self.profile_chooser.list():
                # add the new profile to the profile chooser
                self.profile_chooser.addItem(profile_name)

        def delete_profile(self):
            """Worker for the delete profile button"""
            # obtain name of profile to delete
            profile_name = self.profile_chooser.currentText()

            # delete stored profile
            assert profile_name in storage.profiles
            del storage.profiles[profile_name]

            # remove profile by index from profile chooser
            self.profile_chooser.removeItem(self.profile_chooser.index(profile_name))

            # the profile with the name of the previous contents of the box has been deleted
            # so now empty the profile chooser's box
            self.profile_chooser.setCurrentText("")

            # log that the profile was deleted
            logger.info(f'Deleted profile named "{profile_name}"')

        def load_profile(self):
            """Worker for the load profile button"""
            # obtain the name of profile to load
            profile_name = self.profile_chooser.currentText()

            # dump settings of profile chooser's text
            self.dump_settings(storage.profiles[profile_name])

            # log that the profile was loaded
            logger.debug(f"Settings that were loaded: {storage.profiles[profile_name]}")
            logger.info(f'Loaded profile named "{profile_name}"')

        def input_box_changed(self, input):
            """Worker for when any input box is changed"""

            # fetch settings of input boxes
            storage.current = self.fetch_settings()

            # if B or T or H were changed Z_b also will have changed
            self.Z_b.setValue(storage.current.Z_b)

            # the currently chosen/inputted profile name
            chosen_profile_name = self.profile_chooser.currentText()

            # if the chosen profile name is in the saved profiles list:
            if chosen_profile_name in storage.profiles:
                # if the chosen profile name's settings match the current input box values
                if storage.profiles[chosen_profile_name] == storage.current:
                    self.save_profile_button.setEnabled(False)
                    self.save_profile_button.setToolTip("Save Profile")
                    self.save_profile_button.setStatusTip(
                        f'Current settings match saved settings of profile named "{chosen_profile_name}.".'
                    )

                    self.load_profile_button.setEnabled(False)
                    self.load_profile_button.setStatusTip(
                        f'Current settings match saved settings of profile named "{chosen_profile_name}."'
                    )

                    self.delete_profile_button.setEnabled(True)
                    self.delete_profile_button.setStatusTip(
                        f'Delete the profile named "{chosen_profile_name}." This action is irreversible.'
                    )
                # if the chosen profile name is not in
                else:
                    self.save_profile_button.setEnabled(True)
                    self.save_profile_button.setToolTip("Overwrite Profile")
                    self.save_profile_button.setStatusTip(
                        f'Overwrite profile named "{chosen_profile_name}" with current settings.'
                    )

                    self.load_profile_button.setEnabled(True)
                    self.load_profile_button.setStatusTip(
                        f'Load back the settings of "{chosen_profile_name}."'
                    )

                    self.delete_profile_button.setEnabled(True)
                    self.delete_profile_button.setStatusTip(
                        f'Delete the profile named "{chosen_profile_name}." This action is irreversible.'
                    )
            # the chosen profile name is a brand new profile name (that has not already been saved)
            else:
                self.save_profile_button.setEnabled(True)
                self.save_profile_button.setToolTip("Save Profile")
                self.save_profile_button.setStatusTip(
                    f'Save current as a new profile named "{chosen_profile_name}.".'
                )

                self.load_profile_button.setEnabled(False)
                self.load_profile_button.setStatusTip(
                    f'No saved profile is named "{chosen_profile_name}." Cannot load a profile that does not exist.'
                )

                self.delete_profile_button.setEnabled(False)
                self.delete_profile_button.setStatusTip(
                    f'No saved profile is named "{chosen_profile_name}." Cannot delete a profile that does not exist.'
                )

            # No matter what we cannot save a profile with a blank name
            if chosen_profile_name == "":
                self.save_profile_button.setEnabled(False)
                self.save_profile_button.setStatusTip(
                    "Profile chooser entry box is empty. Enter the name of the profile to save."
                )

                self.load_profile_button.setEnabled(False)
                self.load_profile_button.setStatusTip(
                    "Profile chooser entry box is empty. Enter the name of the profile to load."
                )

                self.delete_profile_button.setEnabled(False)
                self.delete_profile_button.setStatusTip(
                    "Profile chooser entry box is empty. Enter the name of the profile to delete."
                )

        def hook_widgets():
            # when the save profile button is clicked call save_profile()
            self.save_profile_button.clicked.connect(lambda: save_profile(self))
            # save button needs to be locked right after it's clicked
            self.save_profile_button.clicked.connect(
                lambda: input_box_changed(self, None)
            )

            # when the delete profile button is clicked call delete_profile()
            self.delete_profile_button.clicked.connect(lambda: delete_profile(self))

            # when load profile button is clicked load storage.profiles
            self.load_profile_button.clicked.connect(lambda: load_profile(self))
            # load button needs to be locked right after it's clicked
            self.load_profile_button.clicked.connect(
                lambda: input_box_changed(self, None)
            )

            # hook all inputs to the following input_box_changed function
            for input in self.input_widgets:
                input.valueChanged.connect(lambda: input_box_changed(self, input))

            # hook profile chooser dropdown to input_box_changed function
            self.profile_chooser.currentTextChanged.connect(
                lambda: input_box_changed(self, None)
            )

            # add each profile from the save file to the combo box
            for profile_name in storage.profiles:
                self.profile_chooser.addItem(profile_name)

        # hook all buttons to their workers
        hook_widgets()

        # set up button locking/other needed functions initially
        input_box_changed(self, None)

        # set placeholder text of profile chooser
        # (this text gets cleared on the first click of the profile chooser)
        self.profile_chooser.setCurrentText("Name to save/load/delete")
        self.save_profile_button.setEnabled(False)
        self.firstClickOnSave = True
        self.profile_chooser.typical_focus_in = self.profile_chooser.focusInEvent
        def _(focusEvent):
            self.profile_chooser.typical_focus_in(focusEvent)
            if self.firstClickOnSave:
                self.profile_chooser.setCurrentText("")
            self.firstClickOnSave = False
        self.profile_chooser.focusInEvent = _


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
