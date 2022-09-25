import atexit
from types import SimpleNamespace
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
        # database.settings.current_preset.name is the name of the current preset (or last used one)
        self.inject_settings_data(database.settings.current_preset.data)
        self.preset_list.setCurrentText(database.settings.current_preset.name)

        def current_preset_changed():
            """If the preset selector box was changed to an existing preset then update inputs to it"""
            current_preset_name = self.preset_list.currentText()
            try:
                self.inject_settings_data(
                    database.settings.presets[current_preset_name]
                )
                # store the new preset change in database.settings.current_preset
                # current_preset_format is a namedtuple[name, data]
                database.settings.current_preset = SimpleNamespace(
                    name=current_preset_name,
                    data=database.settings.presets[current_preset_name],
                )
            except KeyError:
                pass

        # hook functions to buttons
        self.preset_list.currentIndexChanged.connect(current_preset_changed)
        self.save_preset_button.clicked.connect(self.save_preset_button_func)
        self.delete_preset_button.clicked.connect(self.delete_preset_button_func)
        self.restore_preset_button.clicked.connect(
            lambda: self.inject_settings_data(database.settings.current_preset.data)
        )

        # store the current state as "last_used" on exit
        def on_exit():
            database.settings.presets["last_used"] = self.preset_list.currentText()

        atexit.register(on_exit)

    def save_preset_button_func(self):
        """Called when "save preset" button is clicked."""
        selected_preset_name = self.preset_input.text()

        # only add a new entry to the combo box if the preset name doesn't exist already
        if selected_preset_name not in database.settings.presets:
            self.preset_list.addItem(selected_preset_name)

        # actually save the new preset:
        # store the preset/overwrite the stored preset
        database.settings.presets[selected_preset_name] = self.fetch_settings_data()

        self.preset_list.setCurrentText(selected_preset_name)

    def delete_preset_button_func(self):
        """Called when "delete preset" button is clicked."""
        selected_preset_name = self.preset_input.text()
        preset_list_items = [
            self.preset_list.itemText(_) for _ in range(self.preset_list.count())
        ]

        # give warning if the preset they are trying to delete doesn't exist
        if selected_preset_name not in preset_list_items:
            error = QErrorMessage(self.parent())
            error.showMessage("You can't delete a preset that doesn't exist")
            return

        # obtain list of names of all presets being listed
        preset_list_items = [
            self.preset_list.itemText(_) for _ in range(self.preset_list.count())
        ]
        # delete preset from combo box by index
        del database.settings.presets[selected_preset_name]
        self.preset_list.removeItem(preset_list_items.index(selected_preset_name))

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
        """Inject <preset>'s data into the input boxes"""
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
