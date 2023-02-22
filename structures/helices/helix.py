import itertools
from dataclasses import dataclass, field
from types import NoneType
from typing import Literal, Type, Iterable

import numpy as np

from constants.directions import UP, DOWN
from structures.points import NEMid, Nucleoside
from structures.profiles import NucleicAcidProfile
from structures.strands import Strand


@dataclass(slots=True)
class HelixData:
    """
    A container for the data of a helix.

    Attributes:
        helix: The helix that this data belongs to.
        x_coords: The x-coordinates of the points in the helix.
        z_coords: The z-coordinates of the points in the helix.
        angles: The angles of the points in the helix.
    """

    helix: Type["Helix"] | None = None

    x_coords: np.ndarray | None = None
    z_coords: np.ndarray | None = None
    angles: np.ndarray | None = None

    _data_arrays = ("x_coords", "z_coords", "angles")

    def __setattr__(self, key, value):
        """
        Set an attribute of the helix data.

        When a data array is set up, the parent helix's sequence is set to an empty
        array of the same size as the data array.
        """
        # Perform special processing if they are setting a data array.
        if key in self._data_arrays:
            # In initialization of the data arrays they are set to None, so we must
            # allow it.
            if value is None:
                super(HelixData, self).__setattr__(key, value)
            # If the value is a numpy array, we will set the sequence of the helix to
            # an array of the same size as the data array.
            else:
                if isinstance(value, np.ndarray):
                    self.helix.sequence = np.full(len(value), "X")
                    super(HelixData, self).__setattr__(key, value)
                else:
                    raise TypeError("The data arrays must be numpy arrays.")
        # Otherwise, just set the attribute.
        else:
            super(HelixData, self).__setattr__(key, value)

    def size(self) -> int:
        """
        Get the size of the helix.

        Returns:
            The size of the helix.
        """
        assert len(self.x_coords) == len(self.z_coords) == len(self.angles)
        return len(self.x_coords)

    def resize(self, size: int):
        """
        Resize the data arrays of the helix.

        Args:
            size: The new size of the helix.

        Notes:
            This method flushes the data of the helix. Use with caution.
        """
        self.x_coords = np.zeros(size)
        self.z_coords = np.zeros(size)
        self.angles = np.zeros(size)


@dataclass(slots=True)
class Helix:
    """
    A singular helix in a double helix.

    Attributes:
        direction: The direction of the helix. Either UP or DOWN.
        double_helix: The double helix that this helix belongs to.
        domain: The domain that this helix lies within.
        data: The data of the helix. This is a HelixData object, and contains the
            x-coordinates, z-coordinates, and angles of the points in the helix.
        sequence: The sequence of the nucleosides of the helix. This starts out as
            None, and is automatically made an empty numpy array of the same size as
            the data arrays when the data arrays are set.
    """

    direction: Literal[UP, DOWN]
    double_helix: Type["DoubleHelix"] | None
    data: HelixData = field(default_factory=HelixData)

    _sequence: np.ndarray = field(default=None, init=False)

    def __post_init__(self):
        self.data.helix = self

    def __len__(self):
        """Return the number of points in the helix."""
        assert (
            len(self.data.x_coords) == len(self.data.z_coords) == len(self.data.angles)
        )
        return len(self.data.angles)

    @property
    def sequence(self) -> np.ndarray | None:
        """
        The sequence of the nucleosides of the helix.

        This starts out as None, and is automatically made an empty numpy array of
        the same size as the data arrays when the data arrays are set. The empty
        array uses the letter "X" to represent unset bases.
        """
        return self._sequence

    @sequence.setter
    def sequence(self, value: Iterable[str] | None):
        """
        Set the sequence of the helix or clear the sequence.

        Args:
            value: The sequence of the helix. This must be an iterable of capital
                valid base strings or None. If None, the sequence is cleared.

        Raises:
            TypeError: If the sequence is not an iterable or None.
        """
        if not isinstance(value, (Iterable, NoneType)):
            raise TypeError("The sequence must be an iterable or None.")

        if value is None:
            self._sequence = np.full(self.data.size(), "X")
        else:
            if isinstance(value, np.ndarray):
                self._sequence = value
            else:
                self._sequence = np.array(value)

    @property
    def domain(self):
        """The domain that this helix lies within."""
        return self.double_helix.domain

    def point(self, type_: Literal[Type[Nucleoside], Type[NEMid]] = Nucleoside):
        """
        Obtain a specific point in the helix.

        Args:
            type_: The type of the point to return. Either Nucleoside or NEMid.
        """
        domain = self.double_helix.domain if self.double_helix else None
        return type_(
            angle=self.data.angles[0],  # type: ignore
            x_coord=self.data.x_coords[0],  # type: ignore
            z_coord=self.data.z_coords[0],  # type: ignore
            direction=self.direction,  # type: ignore
            domain=domain,  # type: ignore
        )

    def points(self, begin=Nucleoside):
        """
        Yield alternating NEMids and Nucleosides from the data in the arrays.

        Args:
            begin: The type of the first item yielded. Either Nucleoside or NEMid.

        Yields:
            Nucleoside or NEMid: The next item in the strand.
        """
        domain = self.double_helix.domain if self.double_helix else None
        for index, cls, angle, x_coord, z_coord in zip(
            itertools.count(),
            itertools.cycle(
                (NEMid, Nucleoside) if begin == NEMid else (Nucleoside, NEMid)
            ),
            self.data.angles,
            self.data.x_coords,
            self.data.z_coords,
        ):
            yield cls(  # type: ignore
                angle=angle,
                x_coord=round(x_coord, 5),
                z_coord=round(z_coord, 5),
                direction=self.direction,
                domain=domain,
                helix=self,
                helical_index=index,
            )

    def strand(
        self,
        nucleic_acid_profile: NucleicAcidProfile,
        begin: Literal[Nucleoside, NEMid] = Nucleoside,
        strand: Strand = None,
        **kwargs
    ) -> Strand:
        """
        Convert the strand builder to a Strand object.

        Args:
            nucleic_acid_profile: The nucleic acid profile to use for the strand.
            strand: The strand to fill with the data in the arrays. If None, a new
                strand is created and returned.
            begin: The type of the first item in the strand. Either Nucleoside or
                NEMid.
            **kwargs: Keyword arguments to pass to the Strand constructor.

        Returns:
            Strand: The strand with the data in the arrays. Either a new strand or
                the strand passed in.
        """
        strand = strand or Strand(nucleic_acid_profile=nucleic_acid_profile, **kwargs)
        strand.extend(tuple(self.points(begin=begin)))
        return strand
