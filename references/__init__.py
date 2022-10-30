import constructor
from constructor.panels.side_view.worker import SideView
from ._application import _Application
from ._domains import _Domains
from ._nucleic_acid import _NucleicAcid
from ._plots import _Plots
from ._strands import _Strands

application = _Application()

nucleic_acid = _NucleicAcid()
domains = _Domains()

plots = _Plots()
strands = _Strands(SideView().compute())

constructor = constructor.Window()
