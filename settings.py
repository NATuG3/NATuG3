extension = "nano"

name = "NATuG"
version = 3.0
github = "https://github.com/404Wolf/NATuG"
debug = True

junction_threshold = 0.01
closed_threshold = 0.01

colors = {
    "grid_lines": (220, 220, 220),
    "background": (255, 255, 255),
    "nicks": (255, 0, 0),
    "highlighted": (245, 245, 0),
    "selected": (103, 184, 235),
    "success": (212, 229, 208),
    "domains": {
        "pen": (0, 0, 0, 120),
        "fill": (125, 125, 125),
        "plotted_numbers": (255, 255, 255),
    },
    "strands": {
        "greys": ((195, 195, 195), (70, 70, 70)),
        "colors": (
            (200, 0, 0),
            (0, 255, 0),
            (0, 0, 255),
            (233, 233, 0),
            (0, 255, 255),
            (225, 0, 127),
            (255, 162, 0),
        ),
    },
}

experimental = False
