"""Training-time motion features for Model B (design doc 04 §F-9/§C1; Day 4 Step 1).

One frame = 208 values, in four parts (each with its own presence mask):
    body   27  9 upper-body pose world points (nose, shoulders, elbows, wrists, hips; owner 2026-10-22),
               centred on the shoulder midpoint and divided by the clip's mean shoulder width
    lhand  63  MediaPipe "left" hand world landmarks minus the hand's own wrist point (hand shape in
               metres; labels as given, G8). The stored hand world points are NOT hand-centred: the
               wrist lies ≈ 0.55 m from their origin (median, pilot, 2026-10-22); the hand's global
               position comes from the body wrist instead (design doc 04 §C1).
    rhand  63  MediaPipe "right" hand, the same way
    face   55  52 blendshapes + head yaw/pitch/roll (degrees)
Hand gaps of at most `max_gap` frames between two detections are filled by linear interpolation and
flagged; longer gaps stay missing (masked, never zero-filled into a loss). No clip is excluded (G9).
"""

from __future__ import annotations

from pathlib import Path

import numpy as np

UPPER_POSE = (0, 11, 12, 13, 14, 15, 16, 23, 24)   # nose, L/R shoulder, L/R elbow, L/R wrist, L/R hip
WRISTS = (5, 6)                                      # positions of pose 15/16 inside UPPER_POSE
PARTS = {"body": slice(0, 27), "lhand": slice(27, 90), "rhand": slice(90, 153), "face": slice(153, 208)}
N_FEAT = 208
FEAT_VER_KEY = "fa89892d4908"


def interpolate_gaps(x: np.ndarray, present: np.ndarray, max_gap: int) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Fill interior runs of missing frames no longer than `max_gap` linearly.
    Returns (filled x, new presence, interpolated flag)."""
    x, present = x.copy(), present.copy()
    interp = np.zeros(len(x), dtype=bool)
    idx = np.flatnonzero(present)
    for a, b in zip(idx[:-1], idx[1:]):
        gap = b - a - 1
        if 0 < gap <= max_gap:
            w = (np.arange(1, gap + 1) / (gap + 1))[:, None]
            x[a + 1:b] = (1 - w) * x[a] + w * x[b]
            present[a + 1:b] = True
            interp[a + 1:b] = True
    return x, present, interp


def clip_motion(path: str | Path, max_gap: int = 5) -> dict:
    """Raw (unstandardised) 208-value frames, part masks and interpolation flags for one clip."""
    with np.load(path, allow_pickle=False) as z:
        pose, mask = z["pose_world"], z["mask"].astype(bool)
        lh = (z["lhand_world"] - z["lhand_world"][:, :1]).reshape(-1, 63)
        rh = (z["rhand_world"] - z["rhand_world"][:, :1]).reshape(-1, 63)
        face = np.concatenate([z["blendshapes"], z["head_rot"]], axis=1)
    t = len(pose)
    centre = (pose[:, 11] + pose[:, 12]) / 2
    width = np.nanmean(np.linalg.norm(pose[:, 11] - pose[:, 12], axis=-1))
    body = ((pose[:, UPPER_POSE] - centre[:, None]) / width).reshape(t, 27)
    lh, lp, li = interpolate_gaps(lh, mask[:, 1], max_gap)
    rh, rp, ri = interpolate_gaps(rh, mask[:, 2], max_gap)
    x = np.concatenate([body, lh, rh, face], axis=1).astype(np.float32)
    m = np.stack([mask[:, 0], lp, rp, mask[:, 3]], axis=1)
    x[~expand_mask(m)] = 0.0
    return {"x": x, "mask": m, "interp": np.stack([li, ri], axis=1), "shoulder_width_m": float(width)}


def expand_mask(m: np.ndarray) -> np.ndarray:
    """(T, 4) part mask → (T, 208) value mask."""
    out = np.zeros((len(m), N_FEAT), dtype=bool)
    for j, sl in enumerate(PARTS.values()):
        out[:, sl] = m[:, j:j + 1]
    return out


class Standardizer:
    """Per-value mean/sd from the present training frames only."""

    def __init__(self, mean: np.ndarray, sd: np.ndarray):
        self.mean, self.sd = mean.astype(np.float32), sd.astype(np.float32)

    @classmethod
    def fit(cls, clips: list[dict], floor: float = 1e-3) -> "Standardizer":
        x = np.concatenate([c["x"] for c in clips])
        m = np.concatenate([expand_mask(c["mask"]) for c in clips])
        n = np.maximum(m.sum(0), 1)
        mean = (x * m).sum(0) / n
        sd = np.sqrt((((x - mean) * m) ** 2).sum(0) / n)
        return cls(mean, np.maximum(sd, floor))

    def apply(self, x: np.ndarray, m: np.ndarray) -> np.ndarray:
        z = (x - self.mean) / self.sd
        return np.where(expand_mask(m), z, 0.0).astype(np.float32)

    def invert(self, z: np.ndarray) -> np.ndarray:
        return z * self.sd + self.mean
