import logging
from dataclasses import field, dataclass

from structures.domains import Domains
from structures.helices import DoubleHelices
from structures.profiles import NucleicAcidProfile
from structures.strands import Strands

logger = logging.getLogger(__name__)


@dataclass
class Nanostructure:
    """
    An object representing an entire nanostructure.

    Attributes:
        strands: The strands in the nanostructure.
        helices: The helices in the nanostructure. Helices are strands that don't
            traverse multiple domains.
        domains: The domains in the nanostructure.
        nucleic_acid_profile: The nucleic acid settings that the nanostructure uses.
    """

    strands: field(default_factory=Strands)
    helices: field(default_factory=DoubleHelices)
    domains: field(default_factory=Domains)
    nucleic_acid_profile: field(default_factory=NucleicAcidProfile)