"""Zones per camera. Owner: A.

File format (config/zones/<camera>.json):
    {"camera": "cam_food", "zones": [{"name": "food", "polygon": [[x, y], ...]}]}
Zone names are store.ZONES. A cat is in the zone its box overlaps most, so a zone can be drawn tight around the bowl,
litter box or furniture: overlap is measured against the smaller of box and zone, and must be at least MIN_OVERLAP.
"""
import json
from pathlib import Path

from pawwatch import store

MIN_OVERLAP = 0.2  # a box grazing a zone's edge doesn't count


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


def area(polygon):
    """Shoelace area of a simple polygon."""
    return abs(sum(x1 * y2 - x2 * y1 for (x1, y1), (x2, y2) in zip(polygon, polygon[1:] + polygon[:1]))) / 2


def clip_to_box(polygon, box):
    """Part of the polygon inside box (x1, y1, x2, y2): Sutherland-Hodgman against each of the box's 4 edges."""
    x1, y1, x2, y2 = box
    inside = [lambda p: p[0] >= x1, lambda p: p[0] <= x2, lambda p: p[1] >= y1, lambda p: p[1] <= y2]
    cut = [lambda a, b: _at_x(a, b, x1), lambda a, b: _at_x(a, b, x2),
           lambda a, b: _at_y(a, b, y1), lambda a, b: _at_y(a, b, y2)]
    out = list(polygon)
    for keep, cross in zip(inside, cut):
        pts, out = out, []
        for a, b in zip(pts, pts[1:] + pts[:1]):
            if keep(a):
                out.append(a)
            if keep(a) != keep(b):
                out.append(cross(a, b))
        if not out:
            break
    return out


def _at_x(a, b, x):
    return x, a[1] + (x - a[0]) * (b[1] - a[1]) / (b[0] - a[0])


def _at_y(a, b, y):
    return a[0] + (y - a[1]) * (b[0] - a[0]) / (b[1] - a[1]), y


def overlap(box, polygon):
    """Overlap of a box and a zone, as a share of the smaller of the two (0 to 1)."""
    x1, y1, x2, y2 = box
    smaller = min((x2 - x1) * (y2 - y1), area(polygon))
    if smaller <= 0:
        return 0.0
    part = clip_to_box(polygon, box)
    return area(part) / smaller if len(part) >= 3 else 0.0


def zone_for_box(box, zones):
    """Name of the zone the box (x1, y1, x2, y2) overlaps most, or None if none reaches MIN_OVERLAP."""
    best, name = MIN_OVERLAP, None
    for zone_name, polygon in zones:
        share = overlap(box, polygon)
        if share >= best:
            best, name = share, zone_name
    return name
