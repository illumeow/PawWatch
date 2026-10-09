"""Detections over time to visits. Owner: A. Pure logic: no model, no video, no database.

Rules (docs/Worklist.md):
- a visit counts only after the cat stays in one zone longer than a minimum dwell time;
- debounce: short detection dropouts don't close a visit, so a flickering box isn't counted twice;
- entering a forbidden zone must be reported immediately (for alarm.trigger), not only when the visit ends.
"""
