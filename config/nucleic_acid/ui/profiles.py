from weakref import KeyedRef
from config.nucleic_acid import storage
import logging
from contextlib import suppress


# set up logger
logger = logging.getLogger(__name__)


def setup(self):
    # function to obtain list of all items in profile_chooser
    self.profile_list = lambda: [
        self.profile_chooser.itemText(i) for i in range(self.profile_chooser.count())
    ]

    # easy access function to obtain index of a given profile
    self.profile_index = lambda name: self.profile_list().index(name)

    # add each profile from the save file to the combo box
    for profile_name in storage.profiles:
        self.profile_chooser.addItem(profile_name)

    # set the profile chooser to the last used profile
    logger.debug(
        f'Previously loaded profile name was "{storage.previous_profile_name}"'
    )
    self.profile_chooser.setCurrentIndex(
        self.profile_index(storage.previous_profile_name)
    )

    # when the save profile button is clicked call save_profile()
    self.save_profile_button.clicked.connect(lambda: save_profile(self))

    # when the delete profile button is clicked call delete_profile()
    self.delete_profile_button.clicked.connect(lambda: delete_profile(self))

    # when load profile button is clicked load storage.profiles
    self.load_profile_button.clicked.connect(lambda: load_profile(self))
    self.load_profile_button.clicked.connect(
        lambda: self.load_profile_button.setEnabled(False)
    )

    # load the restored settings profile
    load_profile(self)

    # hook all inputs to the following input_box_changed function
    for input in self.input_widgets:
        input.valueChanged.connect(lambda: input_box_changed(self, input))

    # hook profile chooser dropdown to input_box_changed function
    self.profile_chooser.currentTextChanged.connect(
        lambda: input_box_changed(self, None)
    )

    # save button needs to be locked right after it's clicked
    self.save_profile_button.clicked.connect(lambda: input_box_changed(self, None))
    # load button needs to be locked right after it's clicked
    self.load_profile_button.clicked.connect(lambda: input_box_changed(self, None))

    # set up button locking/other needed functions initially
    input_box_changed(self, None)


def save_profile(self):
    """Worker for the save profile button"""
    # obtain name of profile to save
    profile_name = self.profile_chooser.currentText()

    # save the profile with the current settings
    new_settings = self.fetch_settings()
    storage.profiles[profile_name] = new_settings
    logging.info(
        f'Saved new settings ({new_settings}) as profile named "{profile_name}"'
    )

    # if the profile is not already in the profile chooser...
    if profile_name not in self.profile_list():
        # add the new profile to the profile chooser
        self.profile_chooser.addItem(profile_name)

    # the previously loaded profile's name is now this profile
    storage.previous_profile_name = profile_name


def delete_profile(self):
    """Worker for the delete profile button"""
    # obtain name of profile to delete
    profile_name = self.profile_chooser.currentText()

    with suppress(KeyError):
        # delete stored profile
        del storage.profiles[profile_name]

        # index of profile in the profile chooser dropdown
        profile_index = self.profile_index(profile_name)

        # remove profile by index from profile chooser
        self.profile_chooser.removeItem(profile_index)

        # the profile with the name of the previous contents of the box has been deleted
        # so now empty the profile chooser's box
        self.profile_chooser.setCurrentText("")

        logger.info(f'Deleted profile named "{profile_name}"')


def load_profile(self):
    """Worker for the load profile button"""
    # obtain the name of profile to load
    profile_name = self.profile_chooser.currentText()

    # the previously loaded profile's name
    storage.previous_profile_name = profile_name

    # dump settings of profile chooser's text
    self.dump_settings(storage.profiles[profile_name])

    logger.info(f'Loaded profile named "{profile_name}"')


def input_box_changed(self, input):
    """Worker for when any input box is changed"""

    # fetch settings of input boxes
    storage.current = self.fetch_settings()

    # if B or T or H were changed Z_b also will have changed
    self.Z_b.setValue(storage.current.Z_b)

    # the currently chosen/inputted profile name
    chosen_profile_name = self.profile_chooser.currentText()
    logger.debug(f"Currently chosen profile name: {chosen_profile_name}")
    logger.debug(f"Previously loaded profile name: {storage.previous_profile_name}")
    # the chosen profile's name is NOT the name of an already existant profile
    chosen_profile_name_is_new = chosen_profile_name not in storage.profiles
    logger.debug(f"chosen-profile-is-new-is: {chosen_profile_name_is_new}")

    # the actual current settings match the current profile's settings
    try:
        chosen_profile_is_updated = not (
            storage.current == storage.profiles[storage.previous_profile_name]
        )
        logger.debug(f"chosen-profile-is-updated is: {chosen_profile_is_updated}")
        logger.debug(f"Current profile: {storage.current}")
        logger.debug(
            f"Previous profile: {storage.profiles[storage.previous_profile_name]}"
        )
    except KeyError:  # the previously loaded profile was deleted
        chosen_profile_is_updated = True
        logger.debug("Previous profile no longer exists.")

    # lock/unlock profile manager buttons according to state
    if chosen_profile_name_is_new:
        if chosen_profile_is_updated:  # and is new
            # can't load a profile that doesn't exist
            self.load_profile_button.setEnabled(False)
            self.load_profile_button.setStatusTip(
                "Cannot load a profile that does not exist."
            )
            # can save a profile that doesn't already exist
            self.save_profile_button.setEnabled(True)
            self.save_profile_button.setStatusTip(
                f'Save current settings to a new profile with name "{chosen_profile_name}."'
            )
            self.save_profile_button.setToolTip("Save Profile")
            # can't delete a profile that doesn't exist
            self.delete_profile_button.setEnabled(False)
            self.delete_profile_button.setStatusTip(
                "Cannot delete a profile that does not exist."
            )
        else:  # chosen profile is updated and is new
            # can't load a profile that doesn't exist
            self.load_profile_button.setEnabled(False)
            self.load_profile_button.setStatusTip(
                "Cannot load a profile that does not exist."
            )
            # new profile will be a copy of an existing one; that's fine
            self.save_profile_button.setEnabled(True)
            self.save_profile_button.setStatusTip(
                f'Clone profile "{storage.previous_profile_name}"\'s settings to new profile named "{chosen_profile_name}."'
            )
            self.save_profile_button.setToolTip("Clone Profile")
            # can't delete a profile that doesn't exist
            self.delete_profile_button.setEnabled(False)
            self.delete_profile_button.setStatusTip(
                "Cannot delete a profile that does not exist."
            )
    else:
        if chosen_profile_is_updated:  # and not new
            # can load back the saved state of an existing but changed profile
            self.load_profile_button.setEnabled(True)
            self.load_profile_button.setStatusTip(
                f'Overwrite current settings with the settings of the profile named "{chosen_profile_name}."'
            )
            # can overwrite existing profile with the new settings
            self.save_profile_button.setEnabled(True)
            self.save_profile_button.setStatusTip(
                f'Overwrite the profile named "{chosen_profile_name}"\'s saved settings with the current settings'
            )
            self.save_profile_button.setToolTip("Overwrite Profile")
            # can delete a profile no matter if it is updated or not
            self.delete_profile_button.setEnabled(True)
            self.delete_profile_button.setStatusTip(
                f'Delete the profile named "{chosen_profile_name}." This action cannot be undone.'
            )
        else:  # chosen profile is not updated and not new
            if storage.previous_profile_name == chosen_profile_name:
                logger.debug(
                    "The previously loaded profile name matches the currently chosen profile name."
                )
                # doesn't make sense to overwrite a profile with the exact same settings
                self.load_profile_button.setEnabled(False)
                self.load_profile_button.setStatusTip(
                    f'The current settings match "{chosen_profile_name}"\'s settings. ' +
                    '(cannot overwrite current settings with identical settings)'
                )
                # can overwrite existing profile with the new settings
                self.save_profile_button.setEnabled(False)
                self.save_profile_button.setStatusTip(
                    f'The current settings match "{chosen_profile_name}"\'s settings ' +
                    f'(cannot overwrite "{chosen_profile_name}"\'s settings with identical settings).'
                )
                self.save_profile_button.setToolTip("Save Profile")
            # the chosen profile hasn't changed and the settings are the same as the profile's
            # so we should disable the load profile button
            else:
                logger.debug(
                    "The previously loaded profile name does NOT match the currently chosen profile name."
                )
                self.load_profile_button.setEnabled(True)
                self.load_profile_button.setStatusTip(
                    f'Overwrite current settings with the settings of the profile named "{chosen_profile_name}."'
                )
                # can overwrite existing profile with the new settings
                self.save_profile_button.setEnabled(True)
                self.save_profile_button.setStatusTip(
                    f'Overwrite the profile named "{chosen_profile_name}"\'s saved settings with the current settings'
                )
                self.save_profile_button.setToolTip("Overwrite Profile")

            # can delete a profile no matter if it is updated or not
            self.delete_profile_button.setEnabled(True)
            self.delete_profile_button.setStatusTip(
                f'Delete the profile named "{chosen_profile_name}." This action cannot be undone.'
            )

    # No matter what we cannot save a profile with a blank name
    if chosen_profile_name == "":
        self.save_profile_button.setEnabled(False)
        self.save_profile_button.setStatusTip(
            "Cannot save a profile with a blank name."
        )
