import typing
from typing import List, Iterable

from PyQt6.QtCore import pyqtSignal

from constants.bases import DNA

from PyQt6.QtGui import QValidator
from PyQt6.QtWidgets import (
    QWidget,
    QLineEdit,
    QHBoxLayout,
    QVBoxLayout,
    QSizePolicy,
    QGroupBox,
    QScrollArea,
)


class EditorArea(QGroupBox):
    updated = pyqtSignal()
    base_removed = pyqtSignal(int, str)
    base_added = pyqtSignal(int, str)

    def __init__(self, parent, bases: Iterable | None = None):
        super().__init__(parent)

        self.setLayout(QVBoxLayout(self))
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
        self.setFixedWidth(80)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

    def _renumber(self) -> None:
        """Add proper indexes next to their respective bases."""
        for index, base in enumerate(self._bases):
            self._bases[index].index = index

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

        self.layout().insertWidget(index, new_base)
        self._bases.insert(index, new_base)
        self._renumber()

        return new_base

    def base_text_changed(self, new_text: str, index: int):
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
        self.updated.emit()


class BaseEntryBox(QWidget):
    def __init__(self, parent, base: str, index: int):
        super().__init__(parent)
        self._index = index
        self._base = base

        # set up the base area
        self.base_area = self.BaseArea(self)
        if base in DNA:
            self.base_area.setText(base)

        # set up the index area
        self.index_area = self.IndexArea(self)
        self.index_area.setText(f"{index}")

        # merge into one nice layout
        self.setLayout(QHBoxLayout())
        self.layout().addWidget(self.index_area)
        self.layout().addWidget(self.base_area)

        # remove spacing
        self.layout().setSpacing(2)
        self.layout().setContentsMargins(2, 2, 2, 2)

    class BaseArea(QLineEdit):
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
            self.setFixedWidth(25)
            self.setValidator(self.Validator(self))
            self.setStyleSheet("QLineEdit{border-radius: 2px}")

    class IndexArea(QLineEdit):
        def __init__(self, parent):
            super().__init__(parent)
            self.setStyleSheet(
                """QLineEdit{border-radius: 2px};
                QLineEdit::disabled{background-color: rgb(255, 255, 255); color: rgb(0, 0, 0)}"""
            )
            self.setReadOnly(True)
            self.setEnabled(False)
            self.setFixedWidth(25)

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
