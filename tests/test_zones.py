import json
from pathlib import Path

import pytest

from pawwatch import zones

SQUARE = [[0, 0], [10, 0], [10, 10], [0, 10]]
TRIANGLE = [[20, 0], [30, 0], [20, 10]]


def test_area_and_clip():
    assert zones.area(SQUARE) == 100
    assert zones.area(TRIANGLE) == 50
    assert zones.area(zones.clip_to_box(SQUARE, (5, 5, 20, 20))) == 25
    assert zones.clip_to_box(SQUARE, (50, 50, 60, 60)) == []


def test_overlap_is_a_share_of_the_smaller_shape():
    assert zones.overlap((0, 0, 100, 100), SQUARE) == 1.0  # a big cat box over a small bowl
    assert zones.overlap((5, 0, 15, 10), SQUARE) == 0.5
    assert zones.overlap((40, 40, 50, 50), SQUARE) == 0.0


def test_zone_for_box_picks_the_most_overlap_and_ignores_grazes():
    zs = [("food", SQUARE), ("water", TRIANGLE)]
    assert zones.zone_for_box((2, 2, 8, 8), zs) == "food"
    assert zones.zone_for_box((8, 0, 30, 10), zs) == "water"  # covers all of the triangle, a fifth of the square
    assert zones.zone_for_box((9.5, 0, 14, 10), zs) is None  # grazes the square: 11% of the box
    assert zones.zone_for_box((50, 50, 60, 60), zs) is None


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
    assert zones.load_zones(path) == (
        "cam_food",
        [
            ("food", [(10.0, 20.0), (300.0, 20.0), (300.0, 200.0)]),  # whole pixels
            ("water", [(310.0, 20.0), (600.0, 20.0), (600.0, 200.0), (310.0, 200.0)]),
        ],
    )


def test_save_zones_rejects_what_the_loader_would(tmp_path):
    with pytest.raises(ValueError, match="unknown zone"):
        zones.save_zones(tmp_path / "a.json", "cam", [("sofa", [(0, 0), (1, 0), (1, 1)])])
    with pytest.raises(ValueError, match="3 points"):
        zones.save_zones(tmp_path / "b.json", "cam", [("food", [(0, 0), (1, 0)])])
    assert not list(tmp_path.iterdir())
