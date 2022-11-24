from dataclasses import dataclass


@dataclass
class NucleicAcidProfile:
    """
    A settings profiles.

    Attributes:
        D: Diameter of a domain.
        H: Height of a turn.
        T: There are T turns every B bases.
        B: There are B bases every T turns.
        Z_c: Characteristic height.
        Z_s: Switch height.
        Z_b: Base height.
        theta_b: Base angle.
        theta_c: Characteristic angle.
        theta_s: Switch angle.
    """

    D: float = 2.2
    H: float = 3.549
    T: int = 2
    B: int = 21
    Z_c: float = 0.17
    Z_s: float = 1.26
    theta_b: float = 34.29
    theta_c: float = 17.1428
    theta_s: float = 2.343

    def __post_init__(self) -> None:
        """Compute Z_b based on T, H, and B."""
        self.Z_b = (self.T * self.H) / self.B

    def __eq__(self, other: object) -> bool:
        """Whether our profile is the same as theirs."""
        if isinstance(other, type(self)):
            return vars(self) == vars(other)
        else:
            return False
