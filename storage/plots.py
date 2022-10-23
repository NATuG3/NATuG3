import domains.storage
import nucleic_acid.storage
from computers.side_view import SideView
from computers.top_view import TopView


class Plots:
    @property
    def side_view(self):
        return SideView(
            domains.storage.current.domains,
            nucleic_acid.storage.current.T,
            nucleic_acid.storage.current.B,
            nucleic_acid.storage.current.H,
            nucleic_acid.storage.current.Z_s,
            nucleic_acid.storage.current.theta_s,
            nucleic_acid.storage.current.theta_b,
            nucleic_acid.storage.current.theta_c,
        )

    @property
    def top_view(self):
        return TopView(
            domains.storage.current.domains,
            nucleic_acid.storage.current.D,
            nucleic_acid.storage.current.theta_c,
            nucleic_acid.storage.current.theta_s,
        )
