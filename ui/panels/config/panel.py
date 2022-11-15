import logging
import os
from contextlib import suppress
from datetime import datetime
from time import time
from types import SimpleNamespace
from typing import List

from PyQt6 import uic
from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QDialog

import refs
import refs.saver.save
import settings
from ui.panels import domains, nucleic_acid
from ui.resources import fetch_icon

logger = logging.getLogger(__name__)


class Panel(QWidget):
    """Config panel."""

    def __init__(self, parent) -> None:
        super().__init__(parent)
        uic.loadUi("ui/panels/config/panel.ui", self)
        self.update_graphs.setIcon(fetch_icon("reload-outline"))
        self._tabs()

    def _tabs(self):
        """Set up all tabs for config panel."""
        logger.debug("Building config panel...")

        # container to store tabs in
        self.tabs = SimpleNamespace()

        # set the nucleic acid tab
        # store actual widget in the tabs container
        self.tabs.nucleic_acid = nucleic_acid.Panel(self)
        self.nucleic_acid_tab.setLayout(QVBoxLayout())
        self.nucleic_acid_tab.layout().addWidget(self.tabs.nucleic_acid)

        # set the domains tab
        # store actual widget in the tabs container
        self.tabs.domains = domains.Panel(self.parent())
        self.domains_tab.setLayout(QVBoxLayout())
        self.domains_tab.layout().addWidget(self.tabs.domains)

        def warn_and_refresh(self):
            # determine if there are any strands that the user has made
            # (if there are not then we do not need to warn the user)
            for strand in refs.strands.current.strands:
                if strand.interdomain:
                    dialog = RefreshConfirmer(refs.constructor)
                    dialog.show()
                    break
            return False

        self.update_graphs.clicked.connect(warn_and_refresh)
        self.auto_update_graph.updating = False

        def auto_graph_updater():
            for strand in refs.strands.current.strands:
                if strand.interdomain:
                    return
            if self.auto_update_graph.isChecked():
                if not self.auto_update_graph.updating:
                    self.auto_update_graph.updating = True
                    timer = QTimer(refs.application)
                    timer.setInterval(200)
                    timer.setSingleShot(True)

                    @timer.timeout.connect
                    def _():
                        logger.info("Auto updating...")
                        refs.strands.recompute()
                        refs.constructor.top_view.refresh()
                        refs.constructor.side_view.refresh()
                        self.auto_update_graph.updating = False

                    timer.start()

        self.tabs.domains.updated.connect(auto_graph_updater)
        self.tabs.nucleic_acid.updated.connect(auto_graph_updater)


class RefreshConfirmer(QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        uic.loadUi("ui/panels/config/refresh_confirmer.ui", self)
        self._prettify()
        self._fileselector()
        self._buttons()

    def _fileselector(self):
        # create a timestamp
        timestamp = datetime.now().strftime('%m-%d-%Y')
        counter: List[int] = [0]
        # check to see if there are other saves with the default filename from today
        for filename in os.listdir(f"{os.getcwd()}/saves"):
            if timestamp in filename:
                with suppress(ValueError):
                    # if we find a save that contains a timestamp, see if it has a # at the end of it
                    # and if it does than append that number to the counter list
                    counter.append(int(filename[filename.find("_")+1:].replace(".nano", "")))
        # let counter be the highest counter in the list of counters found
        counter: int = max(counter)+1

        # create str of the new filepath
        self.default_path: str = f"{os.getcwd()}\\saves\\{timestamp}_{counter}.{settings.extension}"

        # create default filename
        self.location.setText(
            f"NATuG\\saves\\{timestamp}_{counter}.{settings.extension}"
        )

    def _prettify(self):
        # set default sizes
        self.setFixedWidth(310)
        self.setFixedHeight(170)

    def _buttons(self):
        # change location button
        self.change_location.clicked.connect(self.close)
        self.change_location.clicked.connect(lambda: refs.saver.save.runner(refs.constructor))

        # cancel button
        self.cancel.clicked.connect(self.close)

        # close popup button
        self.refresh.clicked.connect(self.close)
        self.refresh.clicked.connect(refs.strands.recompute)
        self.refresh.clicked.connect(refs.constructor.side_view.refresh)

        # save and refresh button
        self.save_and_refresh.clicked.connect(self.close)
        self.save_and_refresh.clicked.connect(lambda: refs.saver.save.worker(self.default_path))
        self.save_and_refresh.clicked.connect(refs.strands.recompute)
        self.save_and_refresh.clicked.connect(refs.constructor.side_view.refresh)
