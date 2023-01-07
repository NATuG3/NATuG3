import logging
import os
from contextlib import suppress
from datetime import datetime
from typing import List, Dict

from PyQt6 import uic
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QDialog

import refs
import refs.saver.save
import settings
from constants.tabs import *
from constants.toolbar import *
from structures.domains import Domains
from structures.profiles import NucleicAcidProfile
from ui.config.tabs import domains, nucleic_acid, sequencing
from ui.resources import fetch_icon

logger = logging.getLogger(__name__)
dialog = None


class Panel(QWidget):
    """
    The main config panel.

    This panel is for (almost) all user inputs.

    Attributes:
        nucleic_acid (NucleicAcidPanel): The nucleic acid tab.
        domains (DomainsPanel): The domains tab.
        sequencing (SequencingPanel): The strands tab.
    """

    def __init__(
        self, parent, profiles: Dict[str, NucleicAcidProfile], domains: Domains
    ) -> None:
        super().__init__(parent)
        self.auto_updating_plots = False
        self.profiles = profiles
        self.domains = domains
        uic.loadUi("ui/config/panel.ui", self)
        self.update_graphs.setIcon(fetch_icon("reload-outline"))

        self._tabs()
        self._signals()

    def _tabs(self):
        """Set up all tabs for config panel."""
        # create the tab bodies and store them as attributes
        self.nucleic_acid = nucleic_acid.NucleicAcidPanel(self, self.profiles)
        self.domains = domains.DomainsPanel(self)
        self.sequencing = sequencing.SequencingPanel(self)

        # set the nucleic acid tab
        self.nucleic_acid_tab.setLayout(QVBoxLayout())
        self.nucleic_acid_tab.layout().addWidget(self.nucleic_acid)

        # set the domains tab
        self.domains_tab.setLayout(QVBoxLayout())
        self.domains_tab.layout().addWidget(self.domains)

        # set the strands tab
        self.sequencing_tab.setLayout(QVBoxLayout())
        self.sequencing_tab.layout().addWidget(self.sequencing)

    def _signals(self):
        """Setup signals."""

        def warn_and_refresh(top_view, side_view, function):
            """Warn user if there are changes that will be lost and then update plots."""
            global dialog
            # determine if there are any strands that the user has made
            # (if there are not then we do not need to warn the user)
            for strand in refs.strands.current.strands:
                if strand.interdomain():
                    if (dialog is None) or (not dialog.isVisible()):
                        dialog = RefreshConfirmer(refs.constructor, function)
                        dialog.show()
                    elif (dialog is not None) and dialog.isVisible():
                        logger.info(
                            "User is attempting to update graphs even though"
                            " warning is visible. Ignoring button request."
                        )
                    return

            function()
            if side_view:
                refs.strands.recompute()
                refs.constructor.side_view.refresh()
            if top_view:
                refs.constructor.top_view.refresh()

        self.update_graphs.clicked.connect(
            lambda: warn_and_refresh(
                True, True, lambda: logger.info("Updating graphs...")
            )
        )

        def tab_updated(function):
            """Worker for when a tab is updated and wants to call a function"""
            warn_and_refresh(
                self.auto_update_top_view.isChecked(),
                self.auto_update_side_view.isChecked(),
                function,
            )

        self.domains.updated.connect(tab_updated)
        self.nucleic_acid.updated.connect(tab_updated)

        def tab_changed(index: int):
            """
            Update the plotting mode based on the currently opened tab.

            Args:
                index (int): The index of the tab that is currently open (the tab
                    that has been changed to).

            Performs the following actions:
                1) Updates the plotting mode and the enabled status of the buttons in
                    the toolbar.
            """
            # First set the toolbar and current plotting mode
            if index in (
                NUCLEIC_ACID,
                DOMAINS,
            ):
                # if the plot mode was not already NEMid make it NEMid
                if refs.misc.plot_mode != "NEMid":
                    refs.misc.plot_mode = "NEMid"
                    refs.constructor.side_view.refresh()
                refs.toolbar.actions.buttons[INFORMER].setEnabled(True)
                refs.toolbar.actions.buttons[NICKER].setEnabled(True)
                refs.toolbar.actions.buttons[LINKER].setEnabled(True)
                refs.toolbar.actions.buttons[JUNCTER].setEnabled(True)
            elif index in (STRANDS,):
                # if the plot mode was not already nucleoside make it nucleoside
                if refs.misc.plot_mode != "nucleoside":
                    refs.misc.plot_mode = "nucleoside"
                    refs.constructor.side_view.refresh()
                refs.toolbar.plot_mode = INFORMER
                refs.toolbar.actions.buttons[INFORMER].setEnabled(True)
                refs.toolbar.actions.buttons[NICKER].setEnabled(False)
                refs.toolbar.actions.buttons[LINKER].setEnabled(False)
                refs.toolbar.actions.buttons[JUNCTER].setEnabled(False)

        self.tab_area.currentChanged.connect(tab_changed)


class RefreshConfirmer(QDialog):
    """
    A dialog that warns the user that they will lose any changes they have made if
    they continue, and gives them the option to either save their changes or continue
    without saving or abort.

    Attributes:
        function: Function to execute if the user confirms that they would like to
            proceed (whether with or without saving).
    """

    def __init__(self, parent, function):
        """
        Initialize the refresh confirmer dialog.

        Args:
            parent: The parent widget.
            function: A function to be called if a non-cancel button is pressed.
        """
        super().__init__(parent)
        uic.loadUi("ui/config/refresh_confirmer.ui", self)
        self.function = function
        self._prettify()
        self._fileselector()
        self._buttons()
        self.finished.connect(self._finished)

    def _finished(self):
        """Runs when the dialog closes."""
        refs.constructor.side_view.setFocus()

    def _fileselector(self):
        """Set up the file selector."""
        # create a timestamp
        timestamp = datetime.now().strftime("%m-%d-%Y")
        counter: List[int] = [0]
        # check to see if there are other saves with the default filepath from today
        for filename in os.listdir(f"{os.getcwd()}/saves"):
            if timestamp in filename:
                with suppress(ValueError):
                    # if we find a save that contains a timestamp, see if it has a #
                    # at the end of it and if it does than append that number to the
                    # counter list
                    counter.append(
                        int(filename[filename.find("_") + 1 :].replace(".nano", ""))
                    )
        # let counter be the highest counter in the list of counters found
        counter: int = max(counter) + 1

        # create str of the new filepath
        self.default_path: str = (
            f"{os.getcwd()}\\saves\\{timestamp}_{counter}.{settings.extension}"
        )

        # create default filepath
        self.location.setText(
            f"NATuG\\saves\\{timestamp}_{counter}.{settings.extension}"
        )

    def _prettify(self):
        """Set the styles of the dialog."""
        self.setFixedWidth(340)
        self.setFixedHeight(200)

    def _buttons(self):
        """Set up and hook signals for the buttons of the refresh confirmer dialog."""
        # change location button
        self.change_location.clicked.connect(self.close)
        self.change_location.clicked.connect(
            lambda: refs.saver.save.runner(refs.constructor)
        )

        # cancel button
        self.cancel.clicked.connect(self.close)

        # close popup button
        self.refresh.clicked.connect(self.function)
        self.refresh.clicked.connect(self.close)
        self.refresh.clicked.connect(refs.strands.recompute)
        self.refresh.clicked.connect(refs.constructor.side_view.refresh)
        self.refresh.clicked.connect(refs.constructor.top_view.refresh)

        # save and refresh button
        self.save_and_refresh.clicked.connect(self.function)
        self.save_and_refresh.clicked.connect(self.close)
        self.save_and_refresh.clicked.connect(
            lambda: refs.saver.save.worker(self.default_path)
        )
        self.save_and_refresh.clicked.connect(refs.strands.recompute)
        self.save_and_refresh.clicked.connect(refs.constructor.side_view.refresh)
        self.save_and_refresh.clicked.connect(refs.constructor.top_view.refresh)
