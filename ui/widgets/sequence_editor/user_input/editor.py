import itertools
import typing
from typing import List, Iterable

from PyQt6.QtCore import pyqtSignal, Qt

import settings
from constants import bases
from constants.bases import DNA

from PyQt6.QtGui import QValidator, QKeyEvent, QFocusEvent
from PyQt6.QtWidgets import (
    QWidget,
    QLineEdit,
    QHBoxLayout,
    QVBoxLayout,
    QSizePolicy,
)


class EditorArea(QWidget):
    updated = pyqtSignal(object)
    base_removed = pyqtSignal(int, str)
    base_added = pyqtSignal(int, str, object)
    selection_changed = pyqtSignal(int, object)

    def __init__(self, parent, bases: Iterable | None = None):
        super().__init__(parent)
        self._bases = None
        self.setLayout(QHBoxLayout(self))
        self.layout().setSpacing(0)

        if bases is None:
            self._bases: List[BaseEntryBox] = []
        else:
            self._bases = []
            for base in bases:
                self.add_base(base)

        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.layout().addWidget(spacer)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

    def _renumber(self) -> None:
        """Add proper indexes next to their respective bases."""
        for index, base in enumerate(self._bases):
            self._bases[index].index = index

    @property
    def widgets(self):
        """Obtain a list of all the EntryBox widgets."""
        return self._bases

    @property
    def bases(self) -> List[str]:
        """
        Obtain a list of all bases contained within.

        Returns:
            list: List of all bases contained within.
        """
        bases = []
        for base in self._bases:
            bases.append(base.base)
        return bases

    @bases.setter
    def bases(self, new_bases):
        """
        Replace the current bases with new ones.

        Args:
            new_bases: The new bases.

        Notes:
            Deletes all old bases.
        """
        i = 0
        # for old_base, new_base in itertools.zip_longest(self.bases, new_bases, fillvalue=None):
        #     if new_base is None:
        #
        #
        #     if new_base != old_base:
        #         self.remove_base(i)
        #     i += 1

    def fetch_base(self, index: int) -> str:
        """
        Obtain the base of a specific index.

        Args:
            index: Index of the base.

        Returns:
            str: The base.
        """
        return self._bases[index].base

    def remove_base(self, index: int = None) -> None:
        """
        Remove a base from the editor area.

        Args:
            index: Index of base to remove. Defaults to removing the bottommost base.
        """
        if index is None:
            # index for removal will be last item in list
            index = -1

        self._bases[index].deleteLater()
        self.base_removed.emit(index, self._bases[index].base)
        del self._bases[index]

        self._renumber()

    def add_base(self, base=None, index: int = None) -> QLineEdit:
        """
        Add a base to the bottom of the editor area.

        Args:
            base: The base to add. If None then a new empty area for the user to add a base is created.
            index: Inserts a base at the index provided. If None then a base is appended to the bottom of the editor.
        """
        if index is None:
            # new index will be one after the end of the bases list
            index = len(self._bases)

        new_base = BaseEntryBox(self, base, index)
        new_base.base_area.textChanged.connect(
            lambda new_text: self.base_text_changed(new_text, index)
        )
        new_base.base_area.selectionChanged.connect(
            lambda: new_base.base_area.setCursorPosition(1)
        )
        new_base.base_area.focused_in.connect(lambda: self.selection_changed.emit(new_base.index, new_base))

        @new_base.base_area.left_arrow_event.connect
        def new_base_left_arrow():
            self._bases[new_base.index - 1].setFocus()

        @new_base.base_area.right_arrow_event.connect
        def new_base_right_arrow():
            try:
                self._bases[new_base.index + 1].setFocus()
            except IndexError:
                self._bases[0].setFocus()

        self.layout().insertWidget(index, new_base)
        self._bases.insert(index, new_base)
        self._renumber()

        self.base_added.emit(index, new_base.base, new_base)

        return new_base

    def base_text_changed(self, new_text: str, index: int):
        new_base = None

        if len(new_text) == 0:
            # remove the base
            self.remove_base(index=index)

            # make the previous base have focus
            if index == 0:
                self._bases[0].setFocus()
            else:
                self._bases[index - 1].setFocus()
        if len(new_text) == 2:
            # remove the excess text from the old line edit
            self._bases[index].base = new_text[0]

            # create a new base with the excess text
            new_base: str = new_text[-1]
            new_base: BaseEntryBox = self.add_base(base=new_base, index=index + 1)
            new_base.setFocus()

        self.updated.emit(new_base)


class BaseEntryBox(QWidget):
    def __init__(self, parent, base: str, index: int):
        super().__init__(parent)
        self._index = index
        self._base = base

        # set up the index area
        self.index_area = self.InfoArea(self)
        self.index_area.setText(f"{index}")

        # set up the base area
        self.base_area = self.BaseArea(self)
        if base in DNA:
            self.base_area.setText(base)

        # set up the complement area
        self.complement_area = self.InfoArea(self)
        self.complement_area.setText(bases.COMPLEMENTS[self.base])
        self.complement_area.textChanged.connect(lambda: self.complement_area.setText(bases.COMPLEMENTS[self.base]))

        # merge into one nice layout
        self.setLayout(QVBoxLayout())
        self.layout().addWidget(self.index_area)
        self.layout().addWidget(self.base_area)
        self.layout().addWidget(self.complement_area)

        # remove spacing
        self.layout().setSpacing(3)
        self.layout().setContentsMargins(3, 2, 3, 2)

    class BaseArea(QLineEdit):
        left_arrow_event = pyqtSignal()
        right_arrow_event = pyqtSignal()
        focused_in = pyqtSignal()

        class Validator(QValidator):
            def __init__(self, parent):
                super().__init__(parent)

            def validate(
                self, to_validate: str, index: int
            ) -> typing.Tuple["QValidator.State", str, int]:
                # force uppercase
                to_validate = to_validate.upper()

                if to_validate in (" ", "") or to_validate[-1] in DNA:
                    return QValidator.State.Acceptable, to_validate, index
                else:
                    return QValidator.State.Invalid, to_validate, index

        def __init__(self, parent):
            super().__init__(parent)
            self.setFixedWidth(30)
            self.setValidator(self.Validator(self))
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

        def focusInEvent(self, event: QFocusEvent) -> None:
            super().focusInEvent(event)
            self.focused_in.emit()

        def keyPressEvent(self, event: QKeyEvent) -> None:
            if event.key() == Qt.Key.Key_Left:
                self.left_arrow_event.emit()
            elif event.key() == Qt.Key.Key_Right:
                self.right_arrow_event.emit()
            else:
                super().keyPressEvent(event)

    class InfoArea(QLineEdit):
        def __init__(self, parent):
            super().__init__(parent)
            self.setStyleSheet(
                """QLineEdit{border-radius: 2px}
                   QLineEdit::disabled{background-color: rgb(210, 210, 210); color: rgb(0, 0, 0)}
                   """
            )
            self.setReadOnly(True)
            self.setEnabled(False)
            self.setFixedWidth(30)

    def setFocus(self):
        self.base_area.setFocus()

    @property
    def base(self):
        return self._base

    @base.setter
    def base(self, base):
        self._base = base
        self.base_area.setText(base)

    @property
    def index(self):
        return self._index

    @index.setter
    def index(self, index):
        self._index = index
        self.index_area.setText(f"{self._index + 1}")
