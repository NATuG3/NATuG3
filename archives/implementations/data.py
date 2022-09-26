from pprint import pprint
import dna_nanotube_tools.graph

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
side_view = dna_nanotube_tools.graph.side_view(domains, 3.38, 12.6, 2.3)
side_view.data = side_view.compute(21)[0]
pprint(str(side_view.data))

top_view = dna_nanotube_tools.graph.top_view(domains, 2.2)
top_view.data = top_view.compute()
pprint(str(top_view.data))
