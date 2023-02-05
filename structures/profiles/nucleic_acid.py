import dataclasses
import json
from dataclasses import dataclass
from typing import Type


@dataclass(kw_only=True)
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
        Z_mate: Nucleoside-Mate Vertical Distance.
        theta_s: Switch angle.
    """

    D: float = 2.2
    H: float = 3.549
    g: float = 134.8
    T: int = 2
    B: int = 21
    Z_c: float = 0.17
    Z_mate: float = 0.094
    theta_s: float = 2.343

    @property
    def Z_b(self) -> float:
        """The base height."""
        return (self.T * self.H) / self.B

    @property
    def theta_b(self) -> float:
        """The base angle."""
        return 360 * (self.T / self.B)

    @property
    def theta_c(self) -> float:
        """The characteristic angle."""
        return 360 / self.B

    def update(self, profile: Type["NucleicAcidProfile"]) -> None:
        """
        Update our nucleic_acid_profile with theirs.

        Updates all of our attributes with the attributes of the given
        nucleic_acid_profile.

        This is useful for updating profiles in-place.
        """
        for attr in self.__dataclass_fields__:
            setattr(self, attr, getattr(profile, attr))

    def to_file(self, filepath: str) -> None:
        """
        Write the nucleic acid nucleic_acid_profile to a file.

        Args:
            filepath: The path to the file to write to.
        """
        with open(filepath, "w") as file:
            json.dump(dataclasses.asdict(self), file, indent=3)

    @classmethod
    def from_file(cls, filepath: str) -> "NucleicAcidProfile":
        """
        Load a NucleicAcidProfile from a file.

        Args:
            filepath: The path to the file to read from.
        """
        with open(filepath, "r") as file:
            return cls(**json.load(file))

    def __eq__(self, other: object) -> bool:
        """
        Whether our nucleic_acid_profile is the same as theirs.

        Checks all of our attributes against theirs.
        """
        if not isinstance(other, NucleicAcidProfile):
            return False

        return all(
            getattr(self, attr) == getattr(other, attr)
            for attr in self.__dataclass_fields__
        )
