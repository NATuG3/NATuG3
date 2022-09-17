from pprint import pprint
import dna_nanotube_tools

# define domains to generate sideview for
domains = [
    dna_nanotube_tools.domain(9, 0),
    dna_nanotube_tools.domain(9, 0),
    dna_nanotube_tools.domain(9, 0),
    dna_nanotube_tools.domain(9, 0),
    dna_nanotube_tools.domain(9, 0),
    dna_nanotube_tools.domain(9, 0),
    dna_nanotube_tools.domain(9, 0),
    dna_nanotube_tools.domain(9, 0),
    dna_nanotube_tools.domain(9, 0),
    dna_nanotube_tools.domain(9, 0),
    dna_nanotube_tools.domain(9, 0),
    dna_nanotube_tools.domain(9, 0),
    dna_nanotube_tools.domain(9, 0),
    dna_nanotube_tools.domain(9, 0),
]

# initilize side view class
side_view = dna_nanotube_tools.plot.side_view(domains, 3.38, 12.6, 2.3)
data = side_view.compute(21)[0]
pprint(data)
