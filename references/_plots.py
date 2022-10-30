import references
from constructor.panels.top_view.worker import TopView


class _Plots:
    @property
    def side_view(self):
        return references.strands

    @property
    def top_view(self):
        return TopView(
            references.domains.current,
            references.nucleic_acid.current
        )
