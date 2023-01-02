from .misc import _Misc

misc = _Misc()

from ._application import _Application

application = _Application()

from ._nucleic_acid import _NucleicAcid

nucleic_acid = _NucleicAcid()

from ._domains import _Domains

domains = _Domains()

from ._strands import _Strands

strands = _Strands()

import ui.constructor

constructor = ui.constructor.Window()

from ._toolbar import _Toolbar

toolbar = _Toolbar()
