from functools import cache
from PyQt6.QtGui import QIcon


@cache
def fetch_icon(name: str) -> QIcon:
    """Fetch an icon by name, and cache it."""
    return QIcon(f"resources/icons/{name}.svg")
