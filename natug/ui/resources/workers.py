import logging
import os
import platform
import tempfile
from functools import cache

if platform.system() == "Linux":
    from cairosvg import svg2png

from PyQt6.QtGui import QIcon

from natug.runner import Runner

logger = logging.getLogger(__name__)


def convert_svg_to_png(svg_path: str):
    """Convert an SVG file to a PNG file with pillow, save to temp directory, return path."""
    png_path = tempfile.mktemp(suffix=".png")
    svg2png(url=svg_path, write_to=png_path)
    return png_path


def convert_with_cairosvg_simple(args):
    svg2png(open(args.file, "rb").read(), write_to=open(args.out, "wb"))


@cache
def fetch_icon(name: str, folder="generic_icons") -> QIcon:
    """Fetch an icon by name, and cache it."""
    icon_path = str(Runner.root() / f"./ui/resources/icons/{folder}/{name}.svg")
    if not os.path.exists(icon_path):
        logger.warning(f"Icon not found: {icon_path}")
        return QIcon()
    if platform.system() == "Linux":
        icon_path = convert_svg_to_png(icon_path)
    return QIcon(icon_path)
