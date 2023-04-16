from datetime import datetime
from random import randint


def generate_snapshot_name() -> str:
    """
    Generate a snapshot name.
    """
    return datetime.now().strftime(f"%Y.%m.%d-{randint(0, 99999):04d}")
