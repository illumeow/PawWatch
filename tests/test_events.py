from pawwatch.events import Visit, visits


def samples(zone, start, end, step=1.0):
    """One sample per `step` seconds in [start, end]."""
    n = round((end - start) / step)
    return [(start + i * step, zone) for i in range(n + 1)]


def test_steady_visit():
    assert visits(samples(None, 0, 4) + samples("food", 5, 20) + samples(None, 21, 30)) == [Visit("food", 5, 20)]


def test_too_short_dwell_ignored():
    assert visits(samples("water", 0, 3) + samples(None, 4, 20)) == []


def test_flicker_within_tolerance_is_one_visit():
    stream = samples("food", 0, 10) + samples(None, 11, 12) + samples("food", 13, 20) + samples(None, 21, 30)
    assert visits(stream) == [Visit("food", 0, 20)]


def test_gap_beyond_tolerance_is_two_visits():
    stream = samples("food", 0, 10) + samples(None, 11, 15) + samples("food", 16, 25) + samples(None, 26, 35)
    assert visits(stream) == [Visit("food", 0, 10), Visit("food", 16, 25)]


def test_gap_without_samples_counts_too():
    # Frames missing entirely (e.g. between two files) behave like frames without a cat.
    assert visits(samples("food", 0, 10) + samples("food", 20, 30)) == [Visit("food", 0, 10), Visit("food", 20, 30)]


def test_zone_switch():
    stream = samples("food", 0, 10) + samples("water", 11, 20)
    assert visits(stream) == [Visit("food", 0, 10), Visit("water", 11, 20)]


def test_open_visit_closed_at_end_of_stream():
    assert visits(samples("litter", 100, 160)) == [Visit("litter", 100, 160)]


def test_dwell_and_tolerance_are_configurable():
    stream = samples("food", 0, 3) + samples(None, 4, 8) + samples("food", 9, 12)
    assert visits(stream, min_dwell=2, gap_tolerance=6) == [Visit("food", 0, 12)]
    assert visits(stream, min_dwell=4) == []
