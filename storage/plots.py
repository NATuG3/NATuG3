import config.domains
import config.nucleic_acid
from computers.side_view import SideView
from computers.top_view import TopView


class Plots:
    @property
    def side_view(self):
        return SideView(
            config.domains.storage.current.domains,
            config.nucleic_acid.storage.current.T,
            config.nucleic_acid.storage.current.B,
            config.nucleic_acid.storage.current.H,
            config.nucleic_acid.storage.current.Z_s,
            config.nucleic_acid.storage.current.theta_s,
            config.nucleic_acid.storage.current.theta_b,
            config.nucleic_acid.storage.current.theta_c,
        )

    @property
    def top_view(self):
        return TopView(
            config.domains.storage.current.domains,
            config.nucleic_acid.storage.current.D,
            config.nucleic_acid.storage.current.theta_c,
            config.nucleic_acid.storage.current.theta_s,
        )
