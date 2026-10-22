"""Per-clip MediaPipe Holistic extraction on a uniform time grid (design doc 04 §F-8).

One clip = one worker process with a fresh HolisticLandmarker (reusing one across clips of
different sizes crashed in the earlier project). Frames are decoded with OpenCV (rotation applied),
each frame's timestamp is read, and for every grid time the nearest source frame is processed:
VIDEO mode passes the grid timestamp (tracking), IMAGE mode treats every frame independently.
Only one decoded frame is kept in memory at a time.

Outputs are written atomically; a clip whose .npz already carries the current feat_ver is skipped,
so an interrupted run resumes where it stopped.
"""

from __future__ import annotations

import json
import os
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

from ..io import atomic_write_json, sha256_file
from .layout import LAYOUT, N_BLEND, N_HAND, N_POSE, feat_ver, read_meta

# Face-mesh points used for the head-rotation estimate: eye outer corners, forehead top, chin.
_EYE_R, _EYE_L, _FOREHEAD, _CHIN = 33, 263, 10, 152
# Canonical head frame expressed in image axes for an upright, frontal face (columns x, y, z):
# x → image right, y → image up (= -image y), z → towards the camera (= -MediaPipe z).
_R0 = np.array([[1.0, 0.0, 0.0], [0.0, -1.0, 0.0], [0.0, 0.0, -1.0]])


def resample_nearest(src_t: list[float], fps: float) -> list[tuple[float, int]]:
    """(grid time, index of the nearest source frame) for grid times 0 … last source time."""
    out, step, k, n = [], 1000.0 / fps, 0, len(src_t)
    if not n:
        return out
    j = 0
    while k * step <= src_t[-1] + 1e-9:
        g = k * step
        while j + 1 < n and abs(src_t[j + 1] - g) < abs(src_t[j] - g):
            j += 1
        out.append((g, j))
        k += 1
    return out


def timestamp_cv(src_t: list[float]) -> float | None:
    """Coefficient of variation of frame-to-frame time differences (0 = perfectly regular)."""
    d = np.diff(np.asarray(src_t, dtype=float))
    if len(d) < 2 or d.mean() <= 0:
        return None
    return float(d.std() / d.mean())


def head_rotation(points_px: np.ndarray) -> np.ndarray:
    """Approximate (yaw, pitch, roll) in degrees from 4 face points in pixel-scaled coords.

    points_px rows: right eye outer, left eye outer, forehead, chin. Frontal upright face → (0, 0, 0).
    Signs follow this module's convention; use for QC and as a coarse avatar head pose only.
    """
    eye_r, eye_l, top, chin = points_px
    x = eye_l - eye_r
    x /= np.linalg.norm(x)
    y = top - chin
    y -= y.dot(x) * x
    y /= np.linalg.norm(y)
    z = np.cross(x, y)
    rel = _R0.T @ np.stack([x, y, z], axis=1)
    yaw = np.degrees(np.arctan2(rel[0, 2], rel[2, 2]))
    pitch = np.degrees(np.arcsin(np.clip(-rel[1, 2], -1.0, 1.0)))
    roll = np.degrees(np.arctan2(rel[1, 0], rel[1, 1]))
    return np.array([yaw, pitch, roll], dtype=np.float32)


def _flat(v):
    """Holistic results may be flat lists or a one-element list of lists."""
    if v and isinstance(v[0], list):
        return v[0]
    return v or []


def _xyz(points, n: int) -> np.ndarray:
    pts = _flat(points)
    if len(pts) != n:
        return np.full((n, 3), np.nan, np.float32)
    return np.array([[p.x, p.y, p.z] for p in pts], np.float32)


def _landmarker(model_path: str, mode: str, lcfg: dict):
    from mediapipe.tasks import python as mp_python
    from mediapipe.tasks.python import vision

    running = vision.RunningMode.VIDEO if mode == "video" else vision.RunningMode.IMAGE
    opts = vision.HolisticLandmarkerOptions(
        base_options=mp_python.BaseOptions(model_asset_path=model_path),
        running_mode=running, output_face_blendshapes=True, output_segmentation_mask=False, **lcfg)
    return vision.HolisticLandmarker.create_from_options(opts)


def extract_clip(video_path: str, out_path: str, mode: str, fps: float, lcfg: dict, model_path: str,
                 meta_extra: dict) -> dict:
    """Extract one clip and write its .npz atomically. Returns a small status dict."""
    import cv2
    import mediapipe as mp

    t_start = time.perf_counter()
    # Pass 1: timestamps of every frame (needed to pick the nearest frame per grid time).
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise RuntimeError("OpenCV cannot open the file")
    src_t = []
    while cap.grab():
        src_t.append(float(cap.get(cv2.CAP_PROP_POS_MSEC)))
    rotation = int(cap.get(cv2.CAP_PROP_ORIENTATION_META))
    cap.release()
    plan = resample_nearest(src_t, fps)
    if not plan:
        raise RuntimeError("no decodable frames")
    wanted: dict[int, list[float]] = {}
    for g, j in plan:
        wanted.setdefault(j, []).append(g)

    T = len(plan)
    rows = {k: [] for k in ("t_ms", "src_t_ms", "src_frame", "pose_world", "pose_img", "pose_vis", "lhand_world",
                            "rhand_world", "lhand_img", "rhand_img", "blendshapes", "head_rot", "mask")}
    names = None
    detect_s = 0.0
    hw = None
    # Pass 2: decode again, run the landmarker only on the frames the grid needs.
    cap = cv2.VideoCapture(video_path)
    with _landmarker(model_path, mode, lcfg) as lm:
        j = 0
        while True:
            ok = cap.grab()
            if not ok:
                break
            if j in wanted:
                ok, frame = cap.retrieve()
                if not ok:
                    raise RuntimeError(f"retrieve failed at frame {j}")
                hw = frame.shape[:2]
                rgb = np.ascontiguousarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
                for g in wanted[j]:
                    t0 = time.perf_counter()
                    res = lm.detect_for_video(image, int(round(g))) if mode == "video" else lm.detect(image)
                    detect_s += time.perf_counter() - t0
                    pose = _flat(res.pose_landmarks)
                    face = _flat(res.face_landmarks)
                    lh, rh = _flat(res.left_hand_landmarks), _flat(res.right_hand_landmarks)
                    rows["t_ms"].append(g)
                    rows["src_t_ms"].append(src_t[j])
                    rows["src_frame"].append(j)
                    rows["pose_world"].append(_xyz(res.pose_world_landmarks, N_POSE))
                    rows["pose_img"].append(_xyz(res.pose_landmarks, N_POSE))
                    rows["pose_vis"].append(np.array([p.visibility if p.visibility is not None else np.nan
                                                      for p in pose], np.float32) if len(pose) == N_POSE
                                            else np.full(N_POSE, np.nan, np.float32))
                    rows["lhand_world"].append(_xyz(res.left_hand_world_landmarks, N_HAND))
                    rows["rhand_world"].append(_xyz(res.right_hand_world_landmarks, N_HAND))
                    rows["lhand_img"].append(_xyz(res.left_hand_landmarks, N_HAND))
                    rows["rhand_img"].append(_xyz(res.right_hand_landmarks, N_HAND))
                    blend = _flat(res.face_blendshapes)
                    if len(blend) == N_BLEND:
                        rows["blendshapes"].append(np.array([c.score for c in blend], np.float32))
                        names = names or [c.category_name for c in blend]
                    else:
                        rows["blendshapes"].append(np.full(N_BLEND, np.nan, np.float32))
                    if len(face) >= 468:
                        h, w = hw
                        pts = np.array([[face[i].x * w, face[i].y * h, face[i].z * w]
                                        for i in (_EYE_R, _EYE_L, _FOREHEAD, _CHIN)], dtype=float)
                        rows["head_rot"].append(head_rotation(pts))
                    else:
                        rows["head_rot"].append(np.full(3, np.nan, np.float32))
                    rows["mask"].append(np.array([len(pose) == N_POSE, len(lh) == N_HAND,
                                                  len(rh) == N_HAND, len(face) >= 468], np.uint8))
            j += 1
    cap.release()
    if len(rows["t_ms"]) != T:
        raise RuntimeError(f"processed {len(rows['t_ms'])} of {T} grid frames")

    arrays = {k: np.asarray(v, dtype=np.float32 if k not in ("mask", "src_frame") else None)
              for k, v in rows.items()}
    arrays["src_frame"] = arrays["src_frame"].astype(np.int32)
    arrays["mask"] = arrays["mask"].astype(np.uint8)
    arrays["blendshape_names"] = np.array(names or [""] * N_BLEND)
    meta = {**meta_extra, "mode": mode, "fps": fps, "frames": T, "src_frames": len(src_t),
            "src_fps": round(1000.0 * (len(src_t) - 1) / src_t[-1], 3) if len(src_t) > 1 and src_t[-1] > 0 else None,
            "ts_cv": timestamp_cv(src_t), "rotation": rotation, "frame_hw": list(hw) if hw else None,
            "detect_ms_per_frame": round(1000 * detect_s / T, 2), "seconds": round(time.perf_counter() - t_start, 2)}
    arrays["meta"] = np.array(json.dumps(meta))

    out = Path(out_path)
    tmp = out.with_name(f".{out.name}.{os.getpid()}.tmp")
    try:
        with open(tmp, "wb") as f:
            np.savez_compressed(f, **arrays)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, out)
    finally:
        if tmp.exists():
            tmp.unlink()
    return {"index": meta_extra["index"], "frames": T, "seconds": meta["seconds"]}


def _task(args):
    i, *rest = args
    try:
        return i, extract_clip(*rest), None
    except Exception as exc:  # noqa: BLE001 — every failure is logged, never silently skipped
        return i, None, f"{type(exc).__name__}: {exc}"


def run_extraction(cfg: dict, clips: list[tuple[int, Path]], mode: str, out_root: Path | None = None,
                   workers: int | None = None, log=print) -> dict:
    """Extract all clips for one mode into <out_root>/<feat_ver>/. Returns a run summary."""
    import mediapipe as mp

    fcfg = cfg["features"]
    model = Path(cfg["paths"]["models_dir"]) / cfg["mediapipe"]["model_file"]
    model_sha = sha256_file(model)
    if model_sha != cfg["mediapipe"].get("model_sha256", model_sha):
        raise RuntimeError("model file SHA-256 differs from configs/base.yaml")
    mp_version = mp.__version__
    fv = feat_ver(fcfg, mode, mp_version, model_sha)
    out_dir = Path(out_root or cfg["paths"]["features_dir"]) / fv
    out_dir.mkdir(parents=True, exist_ok=True)
    for stale in out_dir.glob(".*.tmp"):  # left by a killed run; never a finished file
        stale.unlink()
    atomic_write_json(out_dir / "feature_meta.json", {
        "feat_ver": fv, "layout": LAYOUT, "mode": mode, "fps": fcfg["fps"], "landmarker": fcfg["landmarker"],
        "mediapipe": mp_version, "model_file": model.name, "model_sha256": model_sha,
        "config_hash": cfg["_meta"]["config_hash"]})

    todo = []
    for i, path in clips:
        out = out_dir / f"{i}.npz"
        meta = read_meta(out) if out.exists() else None
        if meta and meta.get("feat_ver") == fv:
            continue
        todo.append((i, str(path), str(out), mode, float(fcfg["fps"]), dict(fcfg["landmarker"]), str(model),
                     {"index": i, "feat_ver": fv}))
    log(f"[{mode}] feat_ver {fv}: {len(clips) - len(todo)} done already, {len(todo)} to extract")
    started = datetime.now(timezone.utc)
    t0 = time.perf_counter()
    failures = []
    with ProcessPoolExecutor(max_workers=workers or int(fcfg["workers"])) as pool:
        futures = [pool.submit(_task, args) for args in todo]
        for n, fut in enumerate(as_completed(futures), 1):
            i, res, err = fut.result()
            if err:
                failures.append({"index": i, "error": err})
                log(f"  FAILED {i}: {err}")
            if n % 10 == 0 or n == len(todo):
                log(f"  {n}/{len(todo)} clips ({time.perf_counter() - t0:.0f} s)")
    return {"mode": mode, "feat_ver": fv, "out_dir": out_dir, "extracted_this_run": len(todo) - len(failures),
            "failures": failures, "seconds": round(time.perf_counter() - t0, 1),
            "started_utc": started.isoformat(timespec="seconds")}
