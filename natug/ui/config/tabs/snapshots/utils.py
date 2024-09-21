import os
from contextlib import suppress

from natug import settings


def generate_snapshot_name(root_path) -> str:
    """
    Generate a snapshot name.

    Args:
        root_path (str): The root path of the snapshot save files. This is used to
            compute the ID of the snapshot.
    """
    snapshot_names = os.listdir(root_path)

    snapshot_ids = [0]
    for snapshot_name in snapshot_names:
        with suppress(ValueError):
            snapshot_ids.append(int(snapshot_name.split(f".{settings.extension}")[0]))

    return f"{str(max(snapshot_ids)+1).zfill(6)}"
