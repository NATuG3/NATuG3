import constructor
from computers.side_view import SideView
from computers.side_view.strands.strands import Strands
from ._application import _Application
from ._domains import _Domains
from ._nucleic_acid import _NucleicAcid
from ._plots import _Plots

application = _Application()

nucleic_acid = _NucleicAcid()
domains = _Domains()

plots = _Plots()
strands: Strands = SideView(domains.current, nucleic_acid.current).compute()

constructor = constructor.Window()
