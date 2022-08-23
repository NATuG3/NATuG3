from multiprocessing.sharedctypes import Value
from typing import Iterable
from types import FunctionType


def exec_on_innermost(iterable: Iterable, func: FunctionType) -> None:
    """
    Run func on all innermost contents of iterable.

    Args:
        iterable (Iterable): Main iterable to run func onto innermost values of.
        func (FunctionType): Func to run on innermost values.
    """
    for index in range(len(iterable)):
        # the equivalent of "if not isinstance(iterable[index], Iterable)"
        # except the try except statements are faster sincew it does not need to check every time
        try:
            iterable[index] = func(iterable[index])
        except TypeError:
            exec_on_innermost(iterable[index], func)
