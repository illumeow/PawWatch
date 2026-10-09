"""CLI: video files + zones -> events in SQLite. Owner: A.

Planned usage:
    uv run python -m pawwatch.run --video data/videos/food_2026-10-09T1830.mp4 --zones config/zones/cam_food.json

Per frame: detector.infer -> box center -> zones.zone_at -> events -> store.insert_event for finished visits,
alarm.trigger + red box on forbidden-zone entry. Timestamps come from the file's start time plus frame offset.
"""


def main():
    raise NotImplementedError  # TODO(A)


if __name__ == "__main__":
    main()
