from dataclasses import dataclass


@dataclass
class NucleicAcidProfile:
    """
    A settings profiles.

    Attributes:
        D (float): Diameter of a domain.
        H (float): Height of a turn.
        T (float): There are T turns every B bases.
        B (float): There are B bases every T turns.
        Z_c (float): Characteristic height.
        Z_s (float): Switch height.
        Z_b (float): Base height.
        theta_b (float): Base angle.
        theta_c (float): Characteristic angle.
        theta_s (float): Switch angle.
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
        """Runs after init"""
        # compute Z_b based on T, H, and B
        self.Z_b = (self.T * self.H) / self.B

    def __eq__(self, other: object) -> bool:
        """Returns true if identical profiles is returned"""
        if isinstance(other, type(self)):
            return vars(self) == vars(other)
        else:
            return False
