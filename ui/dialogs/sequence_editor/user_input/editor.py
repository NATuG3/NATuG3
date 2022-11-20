from functools import partial
from typing import List, Iterable

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import (
    QWidget,
    QLineEdit,
    QHBoxLayout,
    QSizePolicy,
    QApplication,
)

from ui.dialogs.sequence_editor.user_input.entrybox import BaseEntryBox


class EditorArea(QWidget):
    updated = pyqtSignal()
    base_removed = pyqtSignal(int, str)
    base_added = pyqtSignal(int, str)
    selection_changed = pyqtSignal(int)

    def __init__(
        self,
        parent,
        bases: Iterable | None = None,
        max_length: int = 1000,
        fixed_length: bool = True,
    ):
        super().__init__(parent)
        self.fixed_length = fixed_length
        self.max_length = max_length
        self.widgets = None
        self.setLayout(QHBoxLayout(self))
        self.layout().setSpacing(0)

        if bases is None:
            if self.fixed_length:
                raise ValueError(
                    "Cannot create a fixed length sequence when the length is zero."
                )
            self.widgets: List[BaseEntryBox] = []
        else:
            self.widgets: List[BaseEntryBox] = []
            for base in bases:
                self.add_base(base)

        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.layout().addWidget(spacer)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

    def __len__(self):
        """Obtain number of bases in self."""
        return len(self.bases)

    def _renumber(self) -> None:
        """Add proper indexes next to their respective bases."""
        for index, base in enumerate(self.widgets):
            self.widgets[index].index = index

    @property
    def sequence(self) -> str:
        """Obtain our sequence as a string."""
        output = ""
        for base in self.bases:
            if base not in ("", None):
                output += base
            else:
                output += " "
        return output

    @property
    def bases(self) -> List[str]:
        """All bases as a list of strings."""
        bases = []
        for widget in self.widgets:
            bases.append(widget.base)
        return bases

    @bases.setter
    def bases(self, new_bases):
        """Replace the current bases with new ones."""
        # make/remove bases such that
        # len(new_bases) == len(our_bases)

        if len(new_bases) != len(self):
            while len(new_bases) > len(self):
                self.add_base()
                QApplication.processEvents()
            while len(new_bases) < len(self):
                self.remove_base()
                QApplication.processEvents()

        assert len(self) == len(new_bases)

        # set all our bases to be the new ones
        for index, base in enumerate(new_bases):
            if base == self.bases[index]:
                continue
            self.widgets[index].base = base

    def remove_base(self, index: int = None) -> None:
        """
        Remove a base from the editor area.

        Args:
            index: Index of base to remove. Defaults to removing the bottommost base.
        """
        if index is None:
            # index for removal will be last item in list
            index = -1

        self.widgets[index].deleteLater()
        self.base_removed.emit(index, self.widgets[index].base)
        del self.widgets[index]
        self._renumber()

    def add_base(self, base=None, index: int = None) -> QLineEdit:
        """
        Add a base to the bottom of the editor area.

        Args:
            base: The base to add. If None then a new empty area for the user to add a base is created.
            index: Inserts a base at the index provided. If None then a base is appended to the bottom of the editor.
        """
        if len(self.bases) == self.max_length:
            return

        if index is None:
            # new index will be one after the end of the bases list
            index = len(self)

        new_base = BaseEntryBox(self, base, index)
        new_base.base_area.textChanged.connect(
            lambda: self.base_text_changed(new_base.base_area.text(), new_base.index)
        )
        new_base.base_area.selectionChanged.connect(
            partial(new_base.base_area.setCursorPosition, 1)
        )
        new_base.base_area.focused_in.connect(
            partial(self.selection_changed.emit, index)
        )

        def new_base_left_arrow():
            self.widgets[new_base.index - 1].setFocus()

        new_base.base_area.left_arrow_event.connect(new_base_left_arrow)

        def new_base_right_arrow():
            try:
                self.widgets[new_base.index + 1].setFocus()
            except IndexError:
                self.widgets[0].setFocus()

        new_base.base_area.right_arrow_event.connect(new_base_right_arrow)

        self.layout().insertWidget(index, new_base)
        self.widgets.insert(index, new_base)
        self._renumber()

        self.base_added.emit(index, new_base.base)

        return new_base

    def base_text_changed(self, new_text: str, index: int):
        if len(new_text) == 0:
            if self.fixed_length:
                # clear the base
                self.widgets[index].base = None
            else:
                # remove the base
                self.remove_base(index=index)

            # make the previous base have focus
            if index == 0:
                self.widgets[0].setFocus()
            else:
                self.widgets[index - 1].setFocus()

            self.updated.emit()
        elif (len(new_text) == 2) and (" " in new_text):
            self.widgets[index].base = new_text.replace(" ", "")
            try:
                self.widgets[index + 1].setFocus()
            except IndexError:
                self.widgets[index].setFocus()
        elif len(new_text) == 2 and (" " not in new_text):
            # remove the excess text from the old line edit
            self.widgets[index].base = new_text[0]

            # create a new base with the excess text
            new_base = new_text[-1]

            if self.fixed_length:
                try:
                    self.widgets[index + 1].setFocus()
                    self.widgets[index].base = new_base
                except IndexError:
                    self.widgets[index].setFocus()
                    self.widgets[index].base = new_base
            else:
                # create a new base
                self.add_base(base=new_base, index=index + 1)

                # focus in on the new base
                new_base.setFocus()

            self.updated.emit()
