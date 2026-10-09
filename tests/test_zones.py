import json
from pathlib import Path

import pytest

from pawwatch import zones

SQUARE = [[0, 0], [10, 0], [10, 10], [0, 10]]
TRIANGLE = [[20, 0], [30, 0], [20, 10]]


def test_point_in_polygon():
    assert zones.point_in_polygon((5, 5), SQUARE)
    assert not zones.point_in_polygon((15, 5), SQUARE)
    assert zones.point_in_polygon((21, 2), TRIANGLE)
    assert not zones.point_in_polygon((29, 9), TRIANGLE)  # inside the bounding box, outside the triangle


def test_zone_at():
    zs = [("food", SQUARE), ("water", TRIANGLE)]
    assert zones.zone_at((5, 5), zs) == "food"
    assert zones.zone_at((21, 2), zs) == "water"
    assert zones.zone_at((50, 50), zs) is None


def write(tmp_path, data):
    path = tmp_path / "cam.json"
    path.write_text(json.dumps(data))
    return path


def test_load_zones(tmp_path):
    path = write(tmp_path, {"camera": "cam_food", "zones": [{"name": "food", "polygon": SQUARE}]})
    camera, zs = zones.load_zones(path)
    assert camera == "cam_food"
    assert zs == [("food", [(0, 0), (10, 0), (10, 10), (0, 10)])]


def test_load_example_file():
    camera, zs = zones.load_zones(Path(__file__).parent.parent / "config/zones/cam_food.example.json")
    assert camera == "cam_food" and [name for name, _ in zs] == ["food"]


def test_load_zones_rejects_unknown_name(tmp_path):
    path = write(tmp_path, {"camera": "cam_food", "zones": [{"name": "sofa", "polygon": SQUARE}]})
    with pytest.raises(ValueError, match="sofa"):
        zones.load_zones(path)


def test_load_zones_rejects_malformed_file(tmp_path):
    path = write(tmp_path, {"camera": "cam_food", "zones": [{"polygon": SQUARE}]})
    with pytest.raises(ValueError, match="expected"):
        zones.load_zones(path)


def test_load_zones_rejects_degenerate_polygon(tmp_path):
    path = write(tmp_path, {"camera": "cam_food", "zones": [{"name": "food", "polygon": [[0, 0], [1, 1]]}]})
    with pytest.raises(ValueError, match="3 points"):
        zones.load_zones(path)
