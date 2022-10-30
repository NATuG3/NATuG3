from constructor.panels.side_view.strands import Strands
from constructor.panels.side_view.worker import SideView


class _Strands:
    def __init__(self, strands):
        self.current: Strands = strands

    def recompute(self) -> Strands:
        self.current: Strands = SideView().compute()
        return self.current
