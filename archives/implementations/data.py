from pprint import pprint
import workers.graph

# define domains to generate sideview for
domains = [
    workers.domain(9, 0),
    workers.domain(9, 0),
    workers.domain(9, 0),
    workers.domain(9, 0),
    workers.domain(9, 0),
    workers.domain(9, 0),
    workers.domain(9, 0),
    workers.domain(9, 0),
    workers.domain(9, 0),
    workers.domain(9, 0),
    workers.domain(9, 0),
    workers.domain(9, 0),
    workers.domain(9, 0),
    workers.domain(9, 0),
]

# initilize side view class
side_view = workers.graph.side_view(domains, 3.38, 12.6, 2.3)
side_view.data = side_view.compute(21)[0]
pprint(str(side_view.data))

top_view = workers.graph.top_view(domains, 2.2)
top_view.data = top_view.compute()
pprint(str(top_view.data))
