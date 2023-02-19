import os
from contextlib import suppress
from datetime import datetime

from PyQt6 import uic
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QDialog

import settings


class RefreshConfirmer(QDialog):
    """
    A dialog that warns the user that they will lose any changes they have made if
    they continue, and gives them the option to either save their changes or continue
    without saving or abort.

    This dialog provides an entry space for the user to choose a custom filepath,
    and automatically generates a filepath. The dialog emits a finished signal when
    it closes, which can be hooked to easily.

    Attributes:
        runner: NATuG's runner.

    Signals:
        refreshed: Emitted when the user has chosen to refresh the file. The signal
            is emitted before recomputing the strands and refreshing the plots,
            so changes to the managers can be made first.
    """

    refreshed = pyqtSignal()

    def __init__(self, runner):
        """
        Initialize the refresh confirmer dialog.

        Args:
            parent: The strands widget.
        """
        super().__init__(runner.window)
        uic.loadUi("ui/dialogs/refresh_confirmer/refresh_confirmer.ui", self)
        self.runner = runner
        self.refreshed = None
        self._prettify()
        self._setup_fileselector()
        self._buttons()

    def _setup_fileselector(self):
        """Set up the file selector."""
        # The user will be prompted to either save their changes to a file at a
        # filepath of their choosing, cancel and not save, or save to a default
        # filepath of the following format: "NATuG\saves\mm-dd-yyyy_#.nano".

        # We must determine what the default filepath actually is. First we generate
        # a timestamp, which is easy with the datetime library, and then we must
        # determine what to set "#" (the counter) to. Since the timestamp is only
        # day-specific this is more tricky, and involves scanning through the save
        # directory, locating all saves that possess the same timestamp, and then
        # storing their counters (the _# part of the filename) in a list. After that,
        # we can simply take the max of that list and add 1 to it to get the new
        # counter (and, if the list is empty, we can just set it to 1).

        # create a timestamp as a placeholder name for the save
        timestamp = datetime.now().strftime("%m-%d-%Y")

        # create a list of counters
        counters = [1]
        for filename in os.listdir(f"saves"):
            # We don't care about the file extension, so we can remove it from the
            # end of the filename.
            filename = filename.replace(settings.extension, "")
            # If today's timestamp is in the filename and the seperator "_" is in the
            # filename, then, if everything that proceeds the "_" is a number, we can
            # assume that the filename is of the format "mm-dd-yyyy_#", and thus
            # store the number in the list of counters.
            if timestamp in filename and "_" in filename:
                with suppress(ValueError):
                    counters.append(int(filename[filename.find("_") + 1 :]))

        # The counter for THIS save is the maximum of the list, and then we add 1 to
        # it since this is the next save from the maximal previous save.
        counter = max(counters) + 1

        # create str of the new filepath
        self.filepath = f"saves/{timestamp}_{counter}.{settings.extension}"

        # create default filepath
        self.location.setText(
            f"NATuG/saves/{timestamp}_{counter}.{settings.extension}"
        )

    def _prettify(self):
        """Set the styles of the dialog."""
        # This is a small dialog, so we can set its size manually and prevent the user
        # from resizing it.
        self.setFixedWidth(340)
        self.setFixedHeight(200)

    def _cancel_button_clicked(self):
        """
        Runner for when the "cancel" button is clicked.

        1) Closes the dialog.
        """
        self.close()

    def _refresh_button_clicked(self):
        """
        Runner for when the "refresh" button is clicked.

        1) Closes the dialog.
        2) Refreshes the plots.
        """
        self.refreshed.emit()
        self.close()
        self.runner.managers.strands.recompute()
        self.runner.window.side_view.refresh()
        self.runner.window.top_view.refresh()

    def _save_and_refresh_button_clicked(self):
        """
        Runner for when the "save and refresh" button is clicked.

        1) Closes the dialog.
        2) Saves the file to the filepath specified by the user or the default
              filepath if the user has not changed it.
        3) Refreshes the plots.
        """
        self.close()
        self.refreshed.emit()
        self.runner.save(self.filepath)
        self.runner.window.side_view.refresh()
        self.runner.window.top_view.refresh()

    def _change_location_button_clicked(self):
        """
        Runner for when the "change location" button is clicked.

        1) Closes the dialog.
        2) Opens a normal save dialog.
        3) Refreshes the plots.
        """
        # Close the dialog and create a normal save dialog. However, ensure that the
        # plots refresh after the save has been completed.
        self.close()

        # if runner.save is called without a filepath, it will ask the user to choose
        # one and then save to that filepath automatically.
        if self.runner.save():  # returns True if the save was successful
            self.refreshed.emit()
            self.runner.window.side_view.refresh()
            self.runner.window.top_view.refresh()

    def _buttons(self):
        """
        Hook signals for the buttons of the dialog.

        Hooks the following signals:
            - change_location.clicked
            - cancel.clicked
            - refresh.clicked
            - save_and_refresh.clicked
        """
        self.change_location.clicked.connect(self._change_location_button_clicked)
        self.cancel.clicked.connect(self._cancel_button_clicked)
        self.refresh.clicked.connect(self._refresh_button_clicked)
        self.save_and_refresh.clicked.connect(self._save_and_refresh_button_clicked)
