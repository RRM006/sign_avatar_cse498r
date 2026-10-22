"""Motion JSON for the browser viewer and the always-produced skeleton video (design doc 04 §F-12)."""

from __future__ import annotations

import json
from pathlib import Path

import cv2
import numpy as np

from ..io import atomic_write_text
from .postprocess import one_euro, presence_weights
from .retarget import BONES, RETARGET_VER, canonical_rest, frame_targets, roundtrip_errors, solve

MOTION_FORMAT = "bdsl-motion-v1"
# VRM 1.0 expression presets ← mean of MediaPipe blendshapes (a coarse proposal; non-manual signals
# such as mouth shapes and brows matter in BdSL, but this mapping has not been checked by anyone).
EXPRESSIONS = {"aa": ["jawOpen"], "ou": ["mouthFunnel"], "oh": ["mouthPucker"], "blinkLeft": ["eyeBlinkLeft"],
               "blinkRight": ["eyeBlinkRight"], "happy": ["mouthSmileLeft", "mouthSmileRight"],
               "sad": ["mouthFrownLeft", "mouthFrownRight"], "angry": ["browDownLeft", "browDownRight"],
               "surprised": ["browInnerUp"]}
SMOOTH_COLS = slice(0, 153)   # body + hands are smoothed; blendshapes and head rotation are not


def build_motion(raw: np.ndarray, mask: np.ndarray, fps: float, blend_names: list[str], label: str,
                 meta: dict, smooth: dict | None = None) -> tuple[dict, dict]:
    """(motion JSON, round-trip summary) for raw frames (T, 208) with part masks (T, 4)."""
    x = raw.astype(np.float64).copy()
    if smooth is not None and len(x) > 1:
        x[:, SMOOTH_COLS] = one_euro(x[:, SMOOTH_COLS], fps, **smooth)
    w = {"left": presence_weights(mask[:, 1]), "right": presence_weights(mask[:, 2])}
    rest = canonical_rest()
    targets_out = {b: [] for b, _, k in BONES if k in ("dir", "frame", "quat")}
    quats = {b: [] for b, _, _ in BONES}
    errs = {"body": [], "hands": [], "fingers": [], "head": []}
    for t in range(len(x)):
        tg = frame_targets(x[t])
        hw = {s: float(w[s][t]) for s in w}
        model, local = solve(tg, rest, hw)
        e = roundtrip_errors(tg, model, rest, {s: hw[s] >= 1.0 for s in hw})
        for k in errs:
            errs[k] += e[k]
        for b in targets_out:
            v = tg[b]
            targets_out[b].append([np.round(np.asarray(a, dtype=float), 5).tolist() for a in v]
                                  if isinstance(v, tuple) else np.round(np.asarray(v, dtype=float), 5).tolist())
        for b in quats:
            quats[b].append(np.round(local[b], 6).tolist())
    blend = x[:, 153:205]
    idx = {n: i for i, n in enumerate(blend_names)}
    expr = {k: np.clip(np.mean([blend[:, idx[n]] for n in names], axis=0), 0, 1).round(4).tolist()
            for k, names in EXPRESSIONS.items()}
    kinds = {b: k for b, _, k in BONES}
    motion = {"format": MOTION_FORMAT, "retarget_ver": RETARGET_VER, "label": label, "fps": fps, "n_frames": len(x),
              "bones": [{"name": b, "parent": p, "kind": k} for b, p, k in BONES],
              "targets": {b: {"kind": kinds[b], "values": v} for b, v in targets_out.items()},
              "hand_weight": {s: np.round(w[s], 4).tolist() for s in w},
              "local_quat_canonical_rest": quats, "expressions": expr, "meta": meta,
              "axes": "VRM 1.0 model space: +X model's left, +Y up, +Z model's front"}
    summary = {k: {"n": len(v), "mean_deg": float(np.mean(v)) if v else None,
                   "p95_deg": float(np.percentile(v, 95)) if v else None,
                   "max_deg": float(np.max(v)) if v else None} for k, v in errs.items()}
    return motion, summary


def write_motion(path: Path, motion: dict) -> None:
    atomic_write_text(path, json.dumps(motion, ensure_ascii=False, separators=(",", ":")))


# ---- skeleton video (front view, the same axes as the avatar) ----
BODY_LINES = [(1, 2), (1, 3), (3, 5), (2, 4), (4, 6), (1, 7), (2, 8), (7, 8)]
HAND_LINES = [(0, 1), (1, 2), (2, 3), (3, 4), (0, 5), (5, 6), (6, 7), (7, 8), (5, 9), (9, 10), (10, 11), (11, 12),
              (9, 13), (13, 14), (14, 15), (15, 16), (13, 17), (0, 17), (17, 18), (18, 19), (19, 20)]


def _panel(raw: np.ndarray, mask_row: np.ndarray, size: tuple[int, int], shoulder_w_m: float, title: str,
           subtitle: str, note: str) -> np.ndarray:
    w, h = size
    img = np.full((h, w, 3), 255, np.uint8)
    scale = w / 4.0                                    # 4 shoulder widths across the panel
    origin = np.array([w / 2, h * 0.42])

    def px(p):  # model space (X left-of-model = screen right, Y up) → pixels
        return tuple(int(v) for v in origin + np.array([p[0], -p[1]]) * scale)

    body = raw[0:27].reshape(9, 3) * np.array([1.0, -1.0, -1.0])
    for a, b in BODY_LINES:
        cv2.line(img, px(body[a]), px(body[b]), (60, 60, 60), 3, cv2.LINE_AA)
    cv2.circle(img, px(body[0]), int(0.18 * scale), (60, 60, 60), 2, cv2.LINE_AA)
    for side, sl, wr, col, mcol in (("L", slice(27, 90), 5, (200, 90, 30), 1), ("R", slice(90, 153), 6, (30, 120, 230), 2)):
        if not mask_row[mcol]:
            continue
        hand = raw[sl].reshape(21, 3) * np.array([1.0, -1.0, -1.0]) / shoulder_w_m + body[wr]
        for a, b in HAND_LINES:
            cv2.line(img, px(hand[a]), px(hand[b]), col, 2, cv2.LINE_AA)
    cv2.putText(img, title, (10, 28), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2, cv2.LINE_AA)
    cv2.putText(img, subtitle, (10, 54), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (40, 40, 40), 1, cv2.LINE_AA)
    cv2.putText(img, note, (10, h - 14), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (90, 90, 90), 1, cv2.LINE_AA)
    return img


def skeleton_video(path: Path, panels: list[dict], fps: float, shoulder_w_m: float, footer: str,
                   size: tuple[int, int] = (480, 540)) -> int:
    """Side-by-side front-view skeletons; a panel that ends early holds its last frame, marked "(ended)".
    panels: [{"raw": (T,208), "mask": (T,4), "title": str, "subtitle": str}]. Returns the frame count."""
    n = max(len(p["raw"]) for p in panels)
    w, h = size
    out = cv2.VideoWriter(str(path), cv2.VideoWriter_fourcc(*"mp4v"), fps, (w * len(panels), h + 30))
    for t in range(n):
        tiles = []
        for p in panels:
            k = min(t, len(p["raw"]) - 1)
            note = f"frame {k + 1}/{len(p['raw'])}" + (" (ended)" if t >= len(p["raw"]) else "")
            tiles.append(_panel(p["raw"][k], p["mask"][k], size, shoulder_w_m, p["title"], p["subtitle"], note))
        frame = np.full((h + 30, w * len(panels), 3), 235, np.uint8)
        frame[:h] = np.concatenate(tiles, axis=1)
        cv2.line(frame, (w, 0), (w, h), (150, 150, 150), 1)
        cv2.putText(frame, footer, (10, h + 21), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 0, 0), 1, cv2.LINE_AA)
        out.write(frame)
    out.release()
    return n
