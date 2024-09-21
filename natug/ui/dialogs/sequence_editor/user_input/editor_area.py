from functools import partial
from threading import Thread
from typing import Iterable, List

from PyQt6.QtCore import QTimer, pyqtSignal
from PyQt6.QtWidgets import QApplication, QHBoxLayout, QLineEdit, QSizePolicy, QWidget

from natug.ui.dialogs.sequence_editor.user_input.entry_box import BaseEntryBox


class SequenceEditorArea(QWidget):
    """
    A sequence editor area.

    Attributes:
        bases: The bases in the editor area.
        widgets: The entry boxes for bases in the editor area.
        selected: The index of the currently selected widget.

    Signals:
        updated: When any bases are updated in the editor area.
        selection_changed(previous_index, new_index): When the selected base changes.
        base_removed(index, base): When a base is removed.
        base_added(index, base): When a base is added.
        base_reset(index): When a nonblank base is changed.
        base unset(index): When a nonblank base is made blank.
        base_set(index): When a blank base is set.
    """

    updated = pyqtSignal(int, arguments=("Index",))  # when anything is updated
    selection_changed = pyqtSignal(
        int, int, arguments=("Previous Index, New Index",)
    )  # when the currently chosen base changes

    base_removed = pyqtSignal(
        int,
        str,
        arguments=(
            "Index",
            "Base",
        ),
    )  # when a base is removed
    base_added = pyqtSignal(
        int,
        str,
        arguments=(
            "Index",
            "Base",
        ),
    )  # when a new base is added

    base_reset = pyqtSignal(int, arguments=("Index",))  # when a nonblank box is changed
    base_unset = pyqtSignal(
        int, arguments=("Index",)
    )  # when a nonblank box is made blank
    base_set = pyqtSignal(
        int, arguments=("Index",)
    )  # when a blank box is made nonblank

    def __init__(
        self,
        parent,
        bases: Iterable[str | None],
        has_complements: Iterable[bool],
        selected: int = 0,
    ):
        """
        Initialize the editor area.

        Args:
            parent: The strands widget.
            bases: The bases for the editor area.
            complements: Whether each base has a complement that can be set. Must be
                the same length as bases.
            selected: The currently selected base.
        """
        super().__init__(parent)
        self._selected: int = selected
        self.setLayout(QHBoxLayout(self))
        self.layout().setSpacing(0)

        self.has_complements = tuple(has_complements)
        assert len(bases) == len(has_complements)

        self.widgets: List[BaseEntryBox] = []
        if len(bases) <= 0:
            raise ValueError("Not enough bases", bases)
        for index, base in enumerate(bases):
            Thread(
                target=lambda: QTimer.singleShot(1, partial(self.add_base, base))
            ).run()

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
    def selected(self):
        """The selected base."""
        return self._selected

    @selected.setter
    def selected(self, index):
        """A different base to select."""
        self.selection_changed.emit(self._selected, index)
        self._selected = index
        self.widgets[index].setFocus()

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

    def update_base(self, index: int, base: str):
        """
        Update a base.

        Args:
            index: Index of base to update.
            base: The new base.
        """
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
            base: The base to add. If None then a new empty area for the user to add a
                base is created.
            index: Inserts a base at the index provided. If None then a base is
                appended to the bottom of the editor.
        """
        if index is None:
            # new index will be one after the end of the bases list
            index = len(self)

        new_base = BaseEntryBox(self, base, self.has_complements[index], index)
        new_base.base_area.textChanged.connect(
            lambda: self.base_text_changed(new_base.base_area.text(), new_base.index)
        )
        new_base.base_area.selectionChanged.connect(
            partial(new_base.base_area.setCursorPosition, 1)
        )

        def selection_changed():
            self.selected = new_base.index

        new_base.base_area.focused_in.connect(selection_changed)

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
            # clear the base
            self.update_base(index, None)

            # make the previous base have focus
            if index == 0:
                self.selected = 0
            else:
                self.selected = index - 1

            self.base_unset.emit(index)
            self.updated.emit(index)

        elif (len(new_text) == 2) and (" " in new_text):
            self.update_base(index, new_text.replace(" ", ""))
            try:
                self.selected = index + 1
            except IndexError:
                self.selected = index

            self.base_set.emit(index)
            self.updated.emit(index)

        elif (len(new_text) == 2) and (" " not in new_text):
            # remove the excess text from the old line edit
            self.update_base(index, new_text[0])

            # create a new base with the excess text
            new_base = new_text[-1]

            # change the focus
            try:
                self.selected = index + 1
            except IndexError:
                self.selected = index
            finally:
                self.update_base(index, new_base)

            # note that the updated base is the NEXT base over
            self.base_set.emit(index + 1)
            self.updated.emit(index + 1)
