import logging
from math import ceil

from PyQt6.QtCore import Qt, pyqtSlot
from PyQt6.QtWidgets import QLineEdit, QPushButton, QSizePolicy, QToolBar, QWidget

from natug import settings
from natug.ui.dialogs.action_repeater.action_repeater import ActionRepeaterDialog
from natug.ui.toolbar.actions import Actions

logger = logging.getLogger(__name__)


class Toolbar(QToolBar):
    """
    The main toolbar with the 'modes' to interact with the side view plot with.

    Also includes a label with the program name, and an "repeat" checkbox for
    repeating actions across many nucleosides.

    Attributes:
        actions: The Actions object that holds all the toolbar buttons.
        repeat: The checkbox that holds the "repeat" checkbox and indicates whether
            to repeat the action across many nucleosides.
        program_label: The label that holds the program name.
        save_button: A button alias to allow the user to save the current program state.
        spacer: The spacer that holds the space between the toolbar cations and the
            program label.
        runner: NATuG's runner.
    """

    def __init__(self, parent, runner) -> None:
        """
        Initialize the toolbar.

        Args:
            parent: The parent widget.
            runner: NATuG's runner.
        """
        super().__init__(parent)
        self.runner = runner

        self.actions = Actions()
        for button in self.actions.buttons.values():
            self.addWidget(button)

        self.repeat = QPushButton("Action Repetition Off")
        self.repeat.setCheckable(True)
        self.repeat.setStyleSheet(
            """
            QPushButton{
                background-color: rgb(255, 210, 210);
            }
            QPushButton::checked{background-color: rgb(210, 255, 210)}
            """
        )
        self.repeat.setFixedWidth(135)
        self.repeat.setChecked(False)
        self.repeat.clicked.connect(self._on_repeat_clicked)
        repeater_spacer = QWidget()
        repeater_spacer.setFixedWidth(4)
        self.addWidget(repeater_spacer)
        self.addWidget(self.repeat)

        self.spacer = QWidget()
        self.spacer.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        self.addWidget(self.spacer)

        self.save_button = QPushButton("Save All")
        self.save_button.clicked.connect(self.runner.save)
        self.addWidget(self.save_button)

        self.program_label = QLineEdit(f"{settings.name} {settings.version}")
        self.program_label.setEnabled(False)
        self.program_label.setStyleSheet(
            """
            QLineEdit::disabled{
                color: rgb(0, 0, 0); 
                background-color: rgb(245, 245, 245);
            }
            """
        )
        self.program_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.program_label.setFixedWidth(100)
        self.addWidget(self.program_label)

        self._prettify()

    def _prettify(self):
        self.setFloatable(False)
        self.setMovable(False)

    @pyqtSlot()
    def _on_repeat_clicked(self):
        """
        Worker for the "repeat" checkable button.

        If the action repeater button is clicked and is already checked, uncheck it
        and clear out the action repeater settings. Otherwise, open the action
        repeater dialog, and set the action repeater settings to the ones that
        were fetched from the dialog.
        """
        # Otherwise, open the action repeater dialog, and set the action repeater
        # settings to the ones that were fetched from the dialog.
        if self.repeat.isChecked():
            logger.debug("Opening action repeater dialog.")
            action_repeater = ActionRepeaterDialog(
                self,
                self.runner.managers.strands.current,
                self.runner.managers.nucleic_acid_profile.current,
            )

            def _on_action_repeater_dialog_accepted():
                """
                When the action repeater dialog is finished, set the action repeater
                profile to the one that was fetched from the dialog.
                """
                # fmt: off
                self.runner.managers.misc.action_repeater = profile = (
                    action_repeater.fetch_profile()
                )
                logger.debug("Action repeater profile fetched: %s.", profile)
                # fmt: on

                if profile.repeat_for is None:
                    times = "forever"
                else:
                    times = f"{profile.repeat_for} times"
                self.repeat.setText(
                    f"Repeating action every {profile.repeat_every}x"
                    f"{ceil(profile.repeat_every_multiplier/2)} NEMids,"
                    f" {times}, "
                    f"{profile.bidirectional and 'bidirectionally' or 'unidirectionally'}"
                )
                self.repeat.setFixedWidth(340)
                logger.debug(
                    "Action repeater settings set to %s.",
                    self.runner.managers.misc.action_repeater,
                )

            def _on_action_repeater_dialog_rejected():
                """
                When the action repeater dialog is rejected, uncheck the action
                repeater button.
                """
                self.repeat.setChecked(False)

            action_repeater.accepted.connect(_on_action_repeater_dialog_accepted)
            action_repeater.rejected.connect(_on_action_repeater_dialog_rejected)
            action_repeater.exec()

        # If the action repeater button is clicked and is already checked, uncheck
        # it and clear out the action repeater settings.
        else:
            logger.debug("Clearing action repeater settings.")
            self.runner.managers.misc.action_repeater = None
            self.repeat.setText("Action repetition off")
            self.repeat.setFixedWidth(135)
