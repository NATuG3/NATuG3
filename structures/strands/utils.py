from random import shuffle
from typing import Iterable


def shuffled(iterable: Iterable) -> list:
    """Shuffle an iterable and return a copy."""
    output = list(iterable)
    shuffle(output)
    return output
