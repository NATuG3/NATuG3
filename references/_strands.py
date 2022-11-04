from types import NoneType
from typing import Union

import references
from constructor.panels.side_view.worker import SideView
from structures.strands.strands import Strands


class _Strands:
    def __init__(self, strands: Union[NoneType, Strands] = None):
        if strands is None:
            self.recompute()
        else:
            self.current: Strands = strands

    def recompute(self) -> Strands:
        self.current: Strands = SideView(
            references.domains.current, references.nucleic_acid.current
        ).compute()
        return self.current
