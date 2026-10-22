"""Read-only probing of one video file: SHA-256 plus OpenCV header data and a first-frame decode."""

from __future__ import annotations

import os
import time
from pathlib import Path

from ..io import sha256_file


def _fourcc(code: float) -> str:
    v = int(code)
    return "".join(chr((v >> 8 * i) & 0xFF) for i in range(4)).strip("\x00 ")


def probe_video(path: str | os.PathLike) -> dict:
    """Header data for one clip. Display size comes from the decoded (auto-rotated) first frame."""
    import cv2

    cv2.setNumThreads(1)  # one clip per process; avoid oversubscribing the CPU
    p = Path(path)
    st = p.stat()
    t0 = time.perf_counter()
    out: dict = {"bytes": st.st_size, "mtime_ns": st.st_mtime_ns, "sha256": sha256_file(p)}
    cap = cv2.VideoCapture(str(p))
    try:
        out["opened"] = bool(cap.isOpened())
        out["codec"] = _fourcc(cap.get(cv2.CAP_PROP_FOURCC))
        out["rotation"] = int(cap.get(cv2.CAP_PROP_ORIENTATION_META))
        out["fps_avg"] = round(float(cap.get(cv2.CAP_PROP_FPS)), 3)
        out["n_frames"] = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        out["prop_w"] = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        out["prop_h"] = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        ok, frame = cap.read()
    finally:
        cap.release()
    out["decode_ok"] = bool(ok)
    if ok:
        out["display_h"], out["display_w"] = (int(x) for x in frame.shape[:2])
    else:
        out["display_w"], out["display_h"] = out["prop_w"], out["prop_h"]
    rotated = out["rotation"] in (90, 270)
    out["stored_w"], out["stored_h"] = (out["display_h"], out["display_w"]) if rotated else (out["display_w"], out["display_h"])
    out["orientation"] = "portrait" if out["display_h"] > out["display_w"] else "landscape"
    out["duration_s"] = round(out["n_frames"] / out["fps_avg"], 3) if out["fps_avg"] > 0 else None
    out["probe_seconds"] = round(time.perf_counter() - t0, 3)
    return out
