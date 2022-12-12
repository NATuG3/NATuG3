import logging
import os
from contextlib import suppress
from datetime import datetime
from types import SimpleNamespace
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
    """Config panel."""

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
        logger.debug("Building config panel...")

        # initalize the container with the proper panels
        self.tabs = SimpleNamespace(
            nucleic_acid=nucleic_acid.Panel(self, self.profiles),
            domains=domains.Panel(self),
            sequencing=sequencing.Panel(self),
        )

        # set the nucleic acid tab
        self.nucleic_acid_tab.setLayout(QVBoxLayout())
        self.nucleic_acid_tab.layout().addWidget(self.tabs.nucleic_acid)

        # set the domains tab
        self.domains_tab.setLayout(QVBoxLayout())
        self.domains_tab.layout().addWidget(self.tabs.domains)

        # set the sequencing tab
        self.sequencing_tab.setLayout(QVBoxLayout())
        self.sequencing_tab.layout().addWidget(self.tabs.sequencing)

    def _signals(self):
        """Setup signals."""

        def warn_and_refresh(top_view, side_view, function):
            """Warn user if there are changes that will be lost and then update plots."""
            global dialog
            # determine if there are any sequencing that the user has made
            # (if there are not then we do not need to warn the user)
            for strand in refs.strands.current.strands:
                if strand.interdomain:
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

        self.tabs.domains.updated.connect(tab_updated)
        self.tabs.nucleic_acid.updated.connect(tab_updated)

        def tab_changed(index: int):
            """Update the plotting mode based on the currently opened tab."""
            if index in (
                NUCLEIC_ACID,
                DOMAINS,
            ):
                # if the plot mode was not already NEMid make it NEMid
                if refs.plot_mode.current != "NEMid":
                    refs.plot_mode.current = "NEMid"
                    refs.constructor.side_view.refresh()
                refs.toolbar.actions.buttons[INFORMER].setEnabled(True)
                refs.toolbar.actions.buttons[NICKER].setEnabled(True)
                refs.toolbar.actions.buttons[HAIRPINNER].setEnabled(True)
                refs.toolbar.actions.buttons[JUNCTER].setEnabled(True)
            elif index in (STRANDS,):
                # if the plot mode was not already nucleoside make it nucleoside
                if refs.plot_mode.current != "nucleoside":
                    refs.plot_mode.current = "nucleoside"
                    refs.constructor.side_view.refresh()
                refs.toolbar.current = INFORMER
                refs.toolbar.actions.buttons[INFORMER].setEnabled(True)
                refs.toolbar.actions.buttons[NICKER].setEnabled(False)
                refs.toolbar.actions.buttons[HAIRPINNER].setEnabled(False)
                refs.toolbar.actions.buttons[JUNCTER].setEnabled(False)

        self.tab_area.currentChanged.connect(tab_changed)


class RefreshConfirmer(QDialog):
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

    def _fileselector(self):
        # create a timestamp
        timestamp = datetime.now().strftime("%m-%d-%Y")
        counter: List[int] = [0]
        # check to see if there are other saves with the default filepath from today
        for filename in os.listdir(f"{os.getcwd()}/saves"):
            if timestamp in filename:
                with suppress(ValueError):
                    # if we find a save that contains a timestamp, see if it has a # at the end of it
                    # and if it does than append that number to the counter list
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
        # set default sizes
        self.setFixedWidth(340)
        self.setFixedHeight(200)

    def _buttons(self):
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
