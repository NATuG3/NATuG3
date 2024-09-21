from typing import Tuple

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFocusEvent, QKeyEvent, QKeySequence, QValidator
from PyQt6.QtWidgets import QLineEdit, QVBoxLayout, QWidget

from natug import settings
from natug.constants import bases
from natug.constants.bases import DNA


class BaseEntryBox(QWidget):
    def __init__(self, parent, base: str | None, has_complement: bool, index: int):
        super().__init__(parent)
        self._index = index
        self._base = base
        self.has_complement = has_complement

        # set up the index area
        self.index_area = InfoArea(self)
        self.index_area.setText(f"{index}")

        # set up the complement area
        self.complement_area = InfoArea(self)

        # set up the base area
        self.base_area = BaseArea(self)
        self.base = base

        # merge into one nice layout
        self.setLayout(QVBoxLayout())
        self.layout().addWidget(self.index_area)
        self.layout().addWidget(self.base_area)
        self.layout().addWidget(self.complement_area)

        # remove spacing
        self.layout().setSpacing(3)
        self.layout().setContentsMargins(3, 2, 3, 2)

    def setFocus(self):
        self.base_area.setFocus()

    def hasFocus(self):
        return self.base_area.hasFocus()

    @property
    def base(self):
        return self._base

    @base.setter
    def base(self, new_base: str):
        # set the base
        if new_base is None:
            self._base = None
            self.base_area.setText(" ")
        else:
            self._base = new_base
            self.base_area.setText(new_base)

        # set the complement
        if self._base in (None, " "):
            self.complement_area.setText(" ")
        else:
            self.complement_area.setText(
                bases.COMPLEMENTS[self._base] if self.has_complement else " "
            )

    @property
    def index(self):
        return self._index

    @index.setter
    def index(self, index):
        self._index = index
        self.index_area.setText(f"{self._index + 1}")


class BaseArea(QLineEdit):
    left_arrow_event = pyqtSignal()
    right_arrow_event = pyqtSignal()
    focused_in = pyqtSignal()

    def __init__(self, parent):
        super().__init__(parent)
        self.setFixedWidth(30)
        self.setValidator(Validator(self))
        self.setStyleSheet(
            f"""
            QLineEdit{{
                border-radius: 2px
            }}
            QLineEdit::focus{{
                background: rgb{settings.colors['success']}
            }}
        """
        )
        self.mousePressEvent = lambda i: self.setCursorPosition(1)

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if event.key not in (
            QKeySequence.StandardKey.Paste,
            QKeySequence.StandardKey.Copy,
            QKeySequence.StandardKey.CUT,
        ):
            return super().keyPressEvent(event)

    def focusInEvent(self, event: QFocusEvent) -> None:
        super().focusInEvent(event)
        self.focused_in.emit()

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if event.key() == Qt.Key.Key_Left:
            self.left_arrow_event.emit()
        elif event.key() == Qt.Key.Key_Right:
            self.right_arrow_event.emit()
        elif event.key() == Qt.Key.Key_Space:
            self.right_arrow_event.emit()
        else:
            super().keyPressEvent(event)


class InfoArea(QLineEdit):
    def __init__(self, parent):
        super().__init__(parent)
        self.setStyleSheet(
            """QLineEdit{
                    border-radius: 2px
                }
                QLineEdit::disabled{
                    background-color: rgb(210, 210, 210);
                    color: rgb(0, 0, 0)
                }
               """
        )
        self.setReadOnly(True)
        self.setEnabled(False)
        self.setFixedWidth(30)


class Validator(QValidator):
    def __init__(self, parent):
        super().__init__(parent)

    def validate(
        self, to_validate: str, index: int
    ) -> Tuple["QValidator.State", str, int]:
        # force uppercase
        to_validate = to_validate.upper()

        if to_validate in (" ", "") or to_validate[-1] in DNA:
            return QValidator.State.Acceptable, to_validate, index
        else:
            return QValidator.State.Invalid, to_validate, index
