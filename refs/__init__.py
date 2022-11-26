import ui.constructor
from ._application import _Application
from ._domains import _Domains
from ._toolbar import _Toolbar
from ._nucleic_acid import _NucleicAcid
from ._strands import _Strands
from ._plot_mode import _PlotMode

application = _Application()

plot_mode = _PlotMode()

nucleic_acid = _NucleicAcid()

domains = _Domains()

strands = _Strands()

constructor = ui.constructor.Window()

toolbar = _Toolbar()
