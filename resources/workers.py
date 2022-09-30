from functools import cache
from PyQt6.QtGui import QIcon


@cache
def fetch_icon(name: str, folder="pack") -> QIcon:
    """Fetch an icon by name, and cache it."""
    return QIcon(f"resources/icons/{folder}/{name}.svg")
