from config.nucleic_acid import storage
import logging
from contextlib import suppress


# set up logger
logger = logging.getLogger(__name__)


def setup(panel):
    # function to obtain list of all items in profile_chooser
    panel.profile_list = lambda: [
        panel.profile_chooser.itemText(i) for i in range(panel.profile_chooser.count())
    ]

    # easy access function to obtain index of a given profile
    panel.profile_index = lambda name: panel.profile_list().index(name)

    # add each profile from the save file to the combo box
    for profile_name in storage.profiles:
        panel.profile_chooser.addItem(profile_name)

    # the currently saved profile will become the last profile state
    panel.previous_profile_name = profile_name

    # when the save profile button is clicked call save_profile()
    panel.save_profile_button.clicked.connect(lambda: save_profile(panel))

    # when the delete profile button is clicked call delete_profile()
    panel.delete_profile_button.clicked.connect(lambda: delete_profile(panel))

    # when load profile button is clicked load storage.profiles
    panel.load_profile_button.clicked.connect(lambda: load_profile(panel))
    panel.load_profile_button.clicked.connect(
        lambda: panel.load_profile_button.setEnabled(False)
    )
    # load the restored settings profile
    load_profile(panel)

    # hook all inputs to the following input_box_changed function
    for input in panel.input_widgets:
        input.valueChanged.connect(lambda: input_box_changed(panel, input))

    # force profile manager to always be title case
    panel.profile_chooser.currentTextChanged.connect(
        lambda: panel.profile_chooser.setCurrentText(
            panel.profile_chooser.currentText().title()
        )
    )

    # hook profile chooser dropdown to input_box_changed function
    panel.profile_chooser.currentTextChanged.connect(
        lambda: input_box_changed(panel, None)
    )

    # set up button locking/other needed functions initially
    input_box_changed(panel, None)


def save_profile(panel):
    """Worker for the save profile button"""
    # obtain name of profile to save
    profile_name = panel.profile_chooser.currentText()
    # save the profile with the current settings
    storage.profiles[profile_name] = panel.fetch_settings()
    if profile_name not in panel.profile_list():
        # add the new profile to the profile chooser
        panel.profile_chooser.addItem(profile_name)


def delete_profile(panel):
    """Worker for the delete profile button"""
    # obtain name of profile to delete
    profile_name = panel.profile_chooser.currentText()
    with suppress(KeyError):
        del storage.profiles[profile_name]
        # index of profile in the profile chooser dropdown
        profile_index = panel.profile_index(profile_name)
        # remove profile by index from profile chooser
        panel.profile_chooser.removeItem(profile_index)


def load_profile(panel):
    """Worker for the load profile button"""
    # obtain the name of profile to load
    profile_name = panel.profile_chooser.currentText()

    # the previously loaded profile's name
    storage.previously_loaded_name = profile_name

    # dump settings of profile chooser's text
    panel.dump_settings(storage.profiles[profile_name])


def input_box_changed(panel, input):
    """Worker for when any input box is changed"""

    # fetch settings of input boxes
    storage.current = panel.fetch_settings()

    # if B or T or H were changed Z_b also will have changed
    panel.Z_b.setValue(storage.current.Z_b)

    # the currently chosen/inputted profile name
    chosen_profile_name = panel.profile_chooser.currentText()

    # the chosen profile's name is NOT the name of an already existant profile
    chosen_profile_name_is_new = chosen_profile_name not in storage.profiles
    logger.debug(f"chosen-profile-is-new-is: {chosen_profile_name_is_new}")

    # the actual current settings match the current profile's settings
    try:
        chosen_profile_is_updated = not (
            storage.current == storage.profiles[storage.previous_profile_name]
        )
        logger.debug(f"chosen-profile-is-updated is: {chosen_profile_is_updated}")
    except KeyError:  # the previously loaded profile was deleted
        chosen_profile_is_updated = True

    # lock/unlock profile manager buttons according to state
    if chosen_profile_name_is_new:
        if chosen_profile_is_updated:  # and is new
            # can't load a profile that doesn't exist
            panel.load_profile_button.setEnabled(False)
            panel.load_profile_button.setStatusTip(
                "Cannot load a profile that does not exist."
            )
            # can save a profile that doesn't already exist
            panel.save_profile_button.setEnabled(True)
            panel.save_profile_button.setStatusTip(
                f'Save current settings as new profile with name "{chosen_profile_name}."'
            )
            # can't delete a profile that doesn't exist
            panel.delete_profile_button.setEnabled(False)
            panel.delete_profile_button.setStatusTip(
                "Cannot delete a profile that does not exist."
            )
        else:  # chosen profile is updated and is new
            # can't load a profile that doesn't exist
            panel.load_profile_button.setEnabled(False)
            panel.load_profile_button.setStatusTip(
                "Cannot load a profile that does not exist."
            )
            # new profile will be a copy of an existing one; that's fine
            panel.save_profile_button.setEnabled(True)
            panel.save_profile_button.setStatusTip(
                f'Clone profile "{storage.previous_profile_name}" to new profile named "{chosen_profile_name}."'
            )
            # can't delete a profile that doesn't exist
            panel.delete_profile_button.setEnabled(False)
            panel.delete_profile_button.setStatusTip(
                "Cannot delete a profile that does not exist."
            )
    else:
        if chosen_profile_is_updated:  # and not new
            # can load back the saved state of an existing but changed profile
            panel.load_profile_button.setEnabled(True)
            panel.load_profile_button.setStatusTip(
                f'Overwrite current settings with the settings of the profile named "{chosen_profile_name}."'
            )
            # can overwrite existing profile with the new settings
            panel.save_profile_button.setEnabled(True)
            panel.save_profile_button.setStatusTip(
                f'Overwrite the profile named "{chosen_profile_name}." with the current settings'
            )
            # can delete a profile no matter if it is updated or not
            panel.delete_profile_button.setEnabled(True)
            panel.delete_profile_button.setStatusTip(
                f'Delete the profile named "{chosen_profile_name}." This action cannot be undone.'
            )
        else:  # chosen profile is not updated and not new
            # doesn't make sense to overwrite current settings with identical ones
            panel.load_profile_button.setEnabled(False)
            panel.load_profile_button.setStatusTip(
                f'Current settings match the saved settings of profile named "{chosen_profile_name}."'
                + " (cannot overwrite the save with identical settings)"
            )
            # doesn't make sense to overwrite a profile with the exact same settings
            panel.save_profile_button.setEnabled(False)
            panel.save_profile_button.setStatusTip(
                f'Current settings match the saved settings of profile named "{chosen_profile_name}."'
                + " (cannot load saved settings onto identical current settings)"
            )
            # can delete a profile no matter if it is updated or not
            panel.delete_profile_button.setEnabled(True)
            panel.delete_profile_button.setStatusTip(
                f'Delete the profile named "{chosen_profile_name}". This action cannot be undone.'
            )

    # No matter what we cannot save a profile with a blank name
    if chosen_profile_name == "":
        panel.save_profile_button.setEnabled(False)
        panel.save_profile_button.setStatusTip(
            "Cannot save a profile with a blank name."
        )
