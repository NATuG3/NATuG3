from dataclasses import dataclass


@dataclass(slots=True)
class NucleicAcidProfile:
    """
    A container for all geometrical parameters for a nucleic acid.

    Attributes:
        D: Diameter of a domain.
        H: Height of a turn.
        g: Nucleoside-Mate Angle.
        T: There are T turns every B bases.
        B: There are B bases every T turns.
        Z_c: Characteristic height.
        Z_s: Switch height.
        Z_b: Base height.
        Z_mate: Nucleoside-Mate Vertical Distance.
        theta_b: Base angle.
        theta_c: Characteristic angle.
        theta_s: Switch angle.
    """

    D: float = 2.2
    H: float = 3.549
    g: float = 134.8
    T: int = 2
    B: int = 21
    Z_c: float = 0.17
    Z_s: float = 1.26
    theta_b: float = 34.29
    theta_c: float = 17.1428
    theta_s: float = 2.343

    @property
    def Z_b(self):
        return (self.T * self.H) / self.B

    @property
    def Z_mate(self):
        return (self.g / 360) * self.Z_s

    def __eq__(self, other: object) -> bool:
        """Whether our nucleic_acid_profile is the same as theirs."""
        if isinstance(other, type(self)):
            return vars(self) == vars(other)
        else:
            return False
