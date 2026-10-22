"""What one feature file (.npz) contains, its version hash, and the privacy check.

Per clip, on a uniform `fps` grid of T frames (NaN where a part is missing):
    t_ms, src_t_ms, src_frame (T,)       grid time, source frame time and index used
    pose_world, pose_img (T,33,3)        body landmarks (world metres / normalised image coords)
    pose_vis (T,33)                      pose landmark visibility
    lhand_world, rhand_world (T,21,3)    hand world landmarks, metres (not hand-centred: wrist ≈ 0.55 m from origin)
    lhand_img, rhand_img (T,21,3)        hand landmarks, normalised image coords
    blendshapes (T,52), blendshape_names (52,)
    head_rot (T,3)                       approx. yaw/pitch/roll in degrees from 4 face points
    mask (T,4) uint8                     present: pose, left hand, right hand, face
    meta                                 JSON string (Index, feat_ver, mode, timing, ts_cv, …)
The raw 478-point face mesh and any image data are never stored (ADR-0017).
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np

LAYOUT = "feat_layout_v1"
N_POSE, N_HAND, N_BLEND = 33, 21, 52
MASK_PARTS = ("pose", "left_hand", "right_hand", "face")
ALLOWED_KEYS = {
    "t_ms", "src_t_ms", "src_frame", "pose_world", "pose_img", "pose_vis", "lhand_world", "rhand_world",
    "lhand_img", "rhand_img", "blendshapes", "blendshape_names", "head_rot", "mask", "meta",
}
FACE_MESH_POINTS = 478


def feat_ver(fcfg: dict, mode: str, mediapipe_version: str, model_sha256: str) -> str:
    """12-hex version: layout + extraction config + mode + mediapipe version + model hash."""
    spec = {"layout": fcfg["layout"], "fps": fcfg["fps"], "landmarker": fcfg["landmarker"], "mode": mode,
            "mediapipe": mediapipe_version, "model_sha256": model_sha256}
    canonical = json.dumps(spec, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:12]


def privacy_problems(path: str | Path) -> list[str]:
    """Empty list = the file holds only allowed keys, no face mesh and no image-like arrays."""
    problems = []
    with np.load(path, allow_pickle=False) as z:
        extra = set(z.files) - ALLOWED_KEYS
        if extra:
            problems.append(f"unexpected keys {sorted(extra)}")
        for k in z.files:
            a = z[k]
            if FACE_MESH_POINTS in a.shape:
                problems.append(f"{k} has a {FACE_MESH_POINTS}-point axis (face mesh?) {a.shape}")
            if a.dtype == np.uint8 and a.ndim >= 3:
                problems.append(f"{k} looks like image data {a.shape}")
    return problems


def read_meta(path: str | Path) -> dict | None:
    try:
        with np.load(path, allow_pickle=False) as z:
            return json.loads(str(z["meta"]))
    except Exception:  # noqa: BLE001 — unreadable/partial file means "not done"
        return None
