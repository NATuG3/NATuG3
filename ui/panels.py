import atexit
import database.settings
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QErrorMessage
from PyQt6 import uic


class settings(QWidget):
    """Settings area"""

    def __init__(self):
        super().__init__()
        uic.loadUi("ui/settings.ui", self)

        # add all presets (except the preset which is literally named "last_used")
        for preset in database.settings.presets:
            if preset != "last_used":
                self.preset_list.addItem(preset)

        # set the current preset of whichever was "last_used"
        last_used_preset = database.settings.presets["last_used"]
        self.inject_settings_data(database.settings.presets[last_used_preset])
        self.preset_list.setCurrentText(last_used_preset)

        def inject_preset_if_existing():
            """If the preset selector box was changed to an existing preset then update inputs to it"""
            if self.preset_input.currentText() != "":
                self.inject_settings_data(
                    database.settings.presets[self.preset_list.currentText()]
                )
        self.preset_list.currentIndexChanged.connect(inject_preset_if_existing)
        self.save_preset_button.clicked.connect(self.save_button)
        self.delete_preset_button.clicked.connect(self.delete_button)

        # store the current state as "last_used" on exit
        def on_exit():
            database.settings.presets["last_used"] = self.preset_list.currentText()
        atexit.register(on_exit)

    def save_button(self):
        selected_preset_name = self.preset_input.text()

        # ensure that the preset being added has a name of length >0
        if len(selected_preset_name) > 0:
            # store the preset/overwrite the stored preset
            database.settings.presets[selected_preset_name] = self.fetch_settings_data()
            if selected_preset_name not in database.settings.presets:
                # only add a new entry to the combo box if the preset name doesn't exist already
                self.preset_list.addItem(selected_preset_name)
            # set the preset box to the most recently added preset (it is the new active preset)
            self.preset_list.setCurrentIndex(self.preset_list.count())            
        else:
            # give warning if preset box was empty
            error = QErrorMessage(self.parent())
            error.showMessage("Preset name is empty!")

        # empty out the preset input box
        self.preset_input.setText("")

    def delete_button(self):
        selected_preset_name = self.preset_input.text()
        preset_list_items = [
            self.preset_list.itemText(_) for _ in range(self.preset_list.count())
        ]

        if selected_preset_name not in preset_list_items:
            # give warning if the preset they are trying to delete doesn't exist
            error = QErrorMessage(self.parent())
            error.showMessage("You can't delete a preset that doesn't exist!")

        del database.settings.presets[selected_preset_name]
        self.preset_list.removeItem(preset_list_items.index(selected_preset_name))

        # empty out the preset input box
        self.preset_input.setText("")

    def fetch_settings_data(self):
        """Obtain a preset object from input boxes' values"""
        return database.settings.preset(
            count=self.count_input.value(),
            diameter=self.diameter_input.value(),
            H=self.H_input.value(),
            T=self.T_input.value(),
            B=self.B_input.value(),
            Z_c=self.Z_c_input.value(),
            Z_s=self.Z_s_input.value(),
            theta_b=self.theta_b_input.value(),
            theta_c=self.theta_c_input.value(),
            theta_s=self.theta_s_input.value(),
        )

    def inject_settings_data(self, preset):
        """Inject a preset object's data into the input boxes"""
        self.count_input.setValue(preset.count)
        self.diameter_input.setValue(preset.diameter)
        self.H_input.setValue(preset.H)
        self.T_input.setValue(preset.T)
        self.B_input.setValue(preset.B)
        self.Z_c_input.setValue(preset.Z_c)
        self.Z_s_input.setValue(preset.Z_s)
        self.theta_b_input.setValue(preset.theta_b)
        self.theta_c_input.setValue(preset.theta_c)
        self.theta_s_input.setValue(preset.theta_s)


class domains(QWidget):
    """Placeholder for domains editor"""

    def __init__(self):
        super().__init__()
        self.setLayout(QVBoxLayout())
        self.layout().addWidget(QLabel("Placeholder for domains editor"))
