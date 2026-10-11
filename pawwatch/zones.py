"""Zones per camera. Owner: A.

File format (config/zones/<camera>.json):
    {"camera": "cam_food", "zones": [{"name": "food", "polygon": [[x, y], ...]}]}
Zone names are store.ZONES. A cat is in a zone when its box center is inside the polygon.
"""
import json
from pathlib import Path

from pawwatch import store


def load_zones(path):
    """Return (camera, [(zone_name, polygon), ...]). Raises ValueError on an unknown zone name or a bad polygon."""
    data = json.loads(Path(path).read_text())
    try:
        return data["camera"], [_zone(path, z["name"], z["polygon"]) for z in data["zones"]]
    except (KeyError, TypeError) as e:
        raise ValueError(f'{path}: expected {{"camera": ..., "zones": [{{"name": ..., "polygon": [[x, y], ...]}}]}}') from e


def save_zones(path, camera, zone_list):
    """Write [(zone_name, polygon), ...] as a zones file, vertices rounded to whole pixels.

    Validates like load_zones and writes nothing if a zone is invalid.
    """
    clean = [_zone(path, name, [(round(x), round(y)) for x, y in polygon]) for name, polygon in zone_list]
    lines = [json.dumps({"name": n, "polygon": [[int(x), int(y)] for x, y in p]}) for n, p in clean]
    body = ",\n    ".join(lines)  # one zone per line, like config/zones/cam_food.example.json
    Path(path).write_text(f'{{\n  "camera": {json.dumps(camera)},\n  "zones": [\n    {body}\n  ]\n}}\n')


def _zone(path, name, points):
    if name not in store.ZONES:
        raise ValueError(f"{path}: unknown zone {name!r}, expected one of {store.ZONES}")
    polygon = [(float(x), float(y)) for x, y in points]
    if len(polygon) < 3:
        raise ValueError(f"{path}: zone {name!r} needs at least 3 points")
    return name, polygon


def point_in_polygon(point, polygon):
    """Ray casting: count polygon edges crossed by a ray from the point to the right."""
    x, y = point
    inside = False
    for (x1, y1), (x2, y2) in zip(polygon, polygon[1:] + polygon[:1]):
        if (y1 > y) != (y2 > y) and x < x1 + (y - y1) * (x2 - x1) / (y2 - y1):
            inside = not inside
    return inside


def zone_at(point, zones):
    """Name of the first zone containing point (x, y), or None."""
    for name, polygon in zones:
        if point_in_polygon(point, polygon):
            return name
    return None
