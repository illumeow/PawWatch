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


def test_save_zones_round_trips_through_the_loader(tmp_path):
    path = tmp_path / "cam_food.json"
    drawn = [("food", [(10.4, 20), (300, 20), (300, 200)]), ("water", [(310, 20), (600, 20), (600, 200), (310, 200)])]
    zones.save_zones(path, "cam_food", drawn)
    assert zones.load_zones(path) == ("cam_food", [
        ("food", [(10.0, 20.0), (300.0, 20.0), (300.0, 200.0)]),  # whole pixels
        ("water", [(310.0, 20.0), (600.0, 20.0), (600.0, 200.0), (310.0, 200.0)]),
    ])


def test_save_zones_rejects_what_the_loader_would(tmp_path):
    with pytest.raises(ValueError, match="unknown zone"):
        zones.save_zones(tmp_path / "a.json", "cam", [("sofa", [(0, 0), (1, 0), (1, 1)])])
    with pytest.raises(ValueError, match="3 points"):
        zones.save_zones(tmp_path / "b.json", "cam", [("food", [(0, 0), (1, 0)])])
    assert not list(tmp_path.iterdir())
