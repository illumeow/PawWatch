"""Zones per camera. Owner: A.

File format (config/zones/<camera>.json):
    {"camera": "cam_food", "zones": [{"name": "food", "polygon": [[x, y], ...]}]}
Zone names are store.ZONES. A cat is in a zone when its box center is inside the polygon.
"""


def load_zones(path):
    """Return (camera, [(zone_name, polygon), ...])."""
    raise NotImplementedError  # TODO(A)


def zone_at(point, zones):
    """Name of the zone containing point (x, y), or None."""
    raise NotImplementedError  # TODO(A)
