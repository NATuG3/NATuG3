import logging

from PyQt6.QtCore import pyqtSlot
from PyQt6.QtWidgets import QVBoxLayout, QWidget
from PyQt6 import uic

from natug.constants.tabs import *
from natug.constants.toolbar import *
from natug.structures.points import NEMid, Nucleoside
from natug.ui.config.tabs import domains, nucleic_acid, sequencing
from natug.ui.dialogs.plot_exporter.plot_exporter import PlotExporter
from natug.ui.dialogs.refresh_confirmer.refresh_confirmer import RefreshConfirmer
from natug.ui.resources import fetch_icon

logger = logging.getLogger(__name__)
dialog = None


class Panel(QWidget):
    """
    The main config panel.

    This panel is for (almost) all user inputs.

    Attributes:
        runner: NATuG's runner.
    """

    def __init__(
        self,
        parent,
        runner: "runner.Runner",
    ) -> None:
        super().__init__(parent)
        self.runner = runner

        # Create placeholders for tabs
        self.nucleic_acid = None
        self.domains = None
        self.sequencing = None
        self.snapshots = None

        # Load the panel
        uic.loadUi("./ui/config/panel.ui", self)
        self.update_graphs.setIcon(fetch_icon("reload-outline"))

        # Set up tabs and hook signals
        self._tabs()
        self._hook_signals()

    def _tabs(self):
        """Set up all tabs for config panel."""
        # create the tab bodies and store them as attributes
        self.nucleic_acid = nucleic_acid.NucleicAcidPanel(
            self, self.runner, self.runner.managers.nucleic_acid_profile.current
        )
        self.domains = domains.DomainsPanel(self, self.runner)
        self.sequencing = sequencing.SequencingPanel(self, self.runner)
        self.snapshots = self.runner.managers.snapshots.current
        self.snapshots.setParent(self)

        # set the nucleic acid tab
        self.nucleic_acid_tab.setLayout(QVBoxLayout())
        self.nucleic_acid_tab.layout().addWidget(self.nucleic_acid)

        # set the domains tab
        self.domains_tab.setLayout(QVBoxLayout())
        self.domains_tab.layout().addWidget(self.domains)

        # set the strands tab
        self.sequencing_tab.setLayout(QVBoxLayout())
        self.sequencing_tab.layout().addWidget(self.sequencing)

        # set the snapshots tab
        self.snapshots_tab.setLayout(QVBoxLayout())
        self.snapshots_tab.layout().addWidget(self.snapshots)

    def _hook_signals(self):
        """
        Set up all signals for the configuration panel.

        Sets up the following signals:
            self.domains.updated: When the domains tab has been updated.
            self.nucleic_acid.updated: When the nucleic acid tab has been updated.
            self.tab_area.currentChanged: When the current tab has been changed.
            self.update_graphs.clicked: When the update graphs button has been clicked.
        """
        self.domains.updated.connect(self._on_tab_update)
        self.nucleic_acid.updated.connect(self._on_tab_update)
        self.tab_area.currentChanged.connect(self._on_tab_change)
        self.update_graphs.clicked.connect(self._on_update_graphs)
        self.export_graphs.clicked.connect(self._on_export_graphs)

    @pyqtSlot()
    def _on_update_graphs(self):
        """Update the graphs and recompute the helix graph."""
        if RefreshConfirmer.run(self.runner):
            self.runner.managers.strands.recompute()
            self.runner.window.side_view.refresh()
            self.runner.window.top_view.refresh()

    @pyqtSlot()
    def _on_export_graphs(self):
        """Export the graphs to a file."""
        PlotExporter(self.runner).show()

    @pyqtSlot()
    def _on_tab_update(self):
        """Worker for when a tab is updated and wants to call a function"""
        self.runner.managers.strands.recompute()
        if self.auto_update_side_view.isChecked():
            self.runner.window.side_view.refresh()
        if self.auto_update_top_view.isChecked():
            self.runner.window.top_view.refresh()

    @pyqtSlot()
    def _on_tab_change(self):
        """
        Worker for when the current config tab is changed.

        Updates the plotting mode and the enabled status of the buttons in
        the toolbar.
        """
        index = self.tab_area.currentIndex()

        # First set the toolbar and current plotting mode
        if index in (NUCLEIC_ACID, DOMAINS, SNAPSHOTS):
            logger.info("The current tab has been changed to Nucleic Acid or Domains")

            # If the plot mode was not already NEMid make it NEMid
            if not isinstance(NEMid, self.runner.managers.misc.plot_types):
                self.runner.managers.misc.plot_types = (NEMid,)
                self.runner.window.side_view.refresh()  # Refresh the side view to
                # ensure that it displays the correct type of point

            # Enable all the potential modes for the toolbar
            self.runner.managers.toolbar.actions.buttons[INFORMER].setEnabled(True)
            self.runner.managers.toolbar.actions.buttons[NICKER].setEnabled(True)
            self.runner.managers.toolbar.actions.buttons[LINKER].setEnabled(True)
            self.runner.managers.toolbar.actions.buttons[JUNCTER].setEnabled(True)

        elif index in (STRANDS,):
            logger.info("The current tab has been changed to Strands")

            # If the plot mode was not already nucleoside make it nucleoside
            if not isinstance(Nucleoside, self.runner.managers.misc.plot_types):
                self.runner.managers.misc.plot_types = (Nucleoside,)
                self.runner.window.side_view.refresh()  # Refresh the side view to
                # ensure that it displays the correct type of point

            # Change the current interaction mode to informer mode.
            self.runner.managers.toolbar.current = INFORMER

            # Enable all the potential modes for the toolbar
            self.runner.managers.toolbar.actions.buttons[INFORMER].setEnabled(True)
            self.runner.managers.toolbar.actions.buttons[NICKER].setEnabled(False)
            self.runner.managers.toolbar.actions.buttons[LINKER].setEnabled(False)
            self.runner.managers.toolbar.actions.buttons[JUNCTER].setEnabled(False)
