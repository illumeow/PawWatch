# UGen300 notes

Notes for porting PawWatch detection to the ASUS UGen300, taken from the reference repo
[erp0917-stack/ugen300-demos](https://github.com/erp0917-stack/ugen300-demos) (written for Windows 11, Python 3.10, HailoRT 5.3.x; we deploy on Linux, so take the patterns, not the setup).

## Hardware

- ASUS AI accelerator on the Hailo-10H: 40 TOPS, 8 GB, USB or M.2.
- It's a card plugged into a host, not a standalone computer. The host decodes video, runs the event logic and serves the dashboard.
- Only finalists receive hardware, so the MVP runs on a laptop with Ultralytics and UGen300 is a documented target.

## Python version

Our code supports Python 3.10–3.13 and is developed on 3.12. The HailoRT Python package (`hailo_platform`) supports
the same range (`requires-python = ">=3.10,<3.14"` in HailoRT v5.4.0), but each prebuilt package is compiled for
**one** Python version, shown as `cpXY` in its filename (`cp312` = Python 3.12). Use the Python the package was built for.

The host runs **Linux** (x86_64 mini PC or Raspberry Pi); Windows isn't supported. Get the package from the
[Hailo Developer Zone](https://hailo.ai/developer-zone/software-downloads) (filter by Python version) and match the
host's system Python: Ubuntu 22.04 = 3.10, 24.04 = 3.12, Pi OS Bookworm = 3.11, Trixie = 3.13.
If no package exists for that version, HailoRT's Python binding can be built from source.

When the hardware arrives:

```bash
uv venv -p 3.XY          # XY from the package's cpXY tag
uv sync
uv pip install path/to/hailort-*-cpXY-*.whl
```

## Files worth copying

| File in ugen300-demos | Use for PawWatch |
| --- | --- |
| `HeadCount/hailo_detect.py` | `ObjectDetector(hef)` on the InferModel API, YOLO `.hef` with built-in NMS. Returns `(label, score, (x1, y1, x2, y2))` in original-image pixels, the same contract as our detector. COCO index 15 = `cat`. |
| `*/hailo_vdevice.py` | VDevice singleton, keep-alive and hard exit (see gotchas). |
| `Traffic/tracker.py` | Simple IoU/centroid tracker, if per-cat track IDs are needed. |
| `OfflineChat/llm_engine.py` | On-device LLM via `hailo_platform.genai.LLM` (e.g. `Qwen2.5-1.5B-Instruct.hef`), for an on-device daily report. |

## Gotchas

- One `VDevice` per process; share it across models.
- Keep every HailoRT object alive until exit (`keep()`) and exit with `os._exit` (`exit_now()`). The demos needed this because on Windows, releasing HailoRT objects over USB dropped the device (`LIBUSB_ERROR_IO`) until it was replugged. It may not be needed on Linux, but the pattern is harmless; keep it until tested on hardware.
- Right after a previous process exits, the device re-enumerates for 2 to 4 s; retry `VDevice()` and `create_infer_model` on transient errors.
- Models are `.hef` files from the Hailo Model Zoo (hailo10h target). They're large and stay out of git.
