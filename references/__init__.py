# import main QApplication
from ._application import _Application

application = _Application()

# import config modules

from ._domains import _Domains
from ._nucleic_acid import _NucleicAcid

nucleic_acid = _NucleicAcid()
domains = _Domains()

# import all other modules
from ._plots import _Plots
import constructor

plots = _Plots()
constructor = constructor.Window()
