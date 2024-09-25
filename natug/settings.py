name = "NATuG"
version = 3.0
github = "https://github.com/404Wolf/NATuG"
debug = True

extension = "natug"
snapshot_path = "saves/snapshots"
default_snapshot_max_capacity = 16

# Threshold to determine whether a tube is closed.
closed_threshold = 0.01
cross_screen_line_length = 0.3
domain_line_point_shift = 0.04
default_domain_preset = "12-sigmagon"
default_nucleic_acid_profile = "MFD B-DNA"
default_nucleic_acid_profiles = ["MFD B-DNA"]

colors = {
    "grid_lines": {
        "default": (220, 220, 220),
        "unstable": (240, 217, 216),
    },
    "background": (255, 255, 255),
    "nicks": (255, 0, 0),
    "highlighted": (245, 245, 0),
    "selected": (103, 184, 235),
    "success": (212, 229, 208),
    "failure": (245, 0, 0),
    "domains": {
        "pen": (0, 0, 0, 120),
        "fill": (125, 125, 125),
        "plotted_numbers": (255, 255, 255),
        "buttons": (150, 50, 50),
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
            (255, 204, 153),  # peach
        ),
    },
    "linkages": {
        "color": (255, 192, 203),
        "grey": (50, 50, 50),
    },
}
