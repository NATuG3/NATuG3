import ui.constructor
from ._application import _Application
from ._domains import _Domains
from ._mode import _Mode
from ._nucleic_acid import _NucleicAcid
from ._strands import _Strands

application = _Application()

nucleic_acid = _NucleicAcid()
domains = _Domains()

strands = _Strands()

constructor = ui.constructor.Window()

mode = _Mode()
