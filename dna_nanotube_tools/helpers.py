from typing import Iterable
from types import FunctionType

def exec_on_innermost(iterable: Iterable, func: FunctionType):
    """
    Run func on all innermost contents of iterable.

    Args:
        iterable (Iterable): Main iterable to run func onto innermost values of.
        func (FunctionType): Func to run on innermost values.

    Returns:
        Iterable: iterable with identical schema but all innermost values are updated to func(value)
    """    
    for index in range(len(iterable)):
        if not isinstance(iterable[index], Iterable):
            iterable[index] = func(iterable[index])
        else:
            exec_on_innermost(iterable[index], func)
    
    return iterable