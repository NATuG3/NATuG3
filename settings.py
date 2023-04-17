name = "NATuG"
version = 3.0
github = "https://github.com/404Wolf/NATuG"
debug = True

extension = "natug"
snapshot_path = "saves/snapshots"
default_snapshot_max_capacity = 12

# Threshold to determine whether a tube is closed.
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
            (120, 227, 123),  # green
            (164, 224, 253),  # blue
            (255, 252, 160),  # yellow
            (248, 200, 255),  # purple
            (255, 160, 161),  # orange
            (255, 182, 192),  # pink
            (255, 204, 153)  # peach
        )
    },
    "linkages": {
        "color": (255, 192, 203),
        "grey": (50, 50, 50),
    },
}
