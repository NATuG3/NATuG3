from typing import Iterable
from types import FunctionType


def exec_on_innermost(iterable: Iterable, func: FunctionType) -> None:
    """
    Run func on all innermost contents of iterable. Less optmized but won't exec on iterables.

    Args:
        iterable (Iterable): Main iterable to run func onto innermost values of.
        func (FunctionType): Func to run on innermost values.
    """
    for index in range(len(iterable)):
        if not isinstance(iterable[index], Iterable):
            iterable[index] = func(iterable[index])
        else:
            exec_on_innermost(iterable[index], func)


def visualize_widget(widget):
    """
    Quickly display a PyQt widget as a full window. For testing purposes only.

    Args:
        widget (PyQt): widget to display
    """
    # only import these libraries if ui is being used
    from PyQt6.QtWidgets import QApplication
    import sys

    app = QApplication(sys.argv)
    widget.show()
    app.exec()
