from computers.side_view import SideView
from computers.top_view import TopView
from constructor.panels import domains, nucleic_acid
import references


class _Plots:
    @property
    def side_view(self):
        return SideView(
            references.domains.current,
            references.nucleic_acid.current.T,
            references.nucleic_acid.current.B,
            references.nucleic_acid.current.H,
            references.nucleic_acid.current.Z_s,
            references.nucleic_acid.current.theta_s,
            references.nucleic_acid.current.theta_b,
            references.nucleic_acid.current.theta_c,
        )

    @property
    def top_view(self):
        return TopView(
            references.domains.current,
            references.nucleic_acid.current.D,
            references.nucleic_acid.current.theta_c,
            references.nucleic_acid.current.theta_s,
        )
