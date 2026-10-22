"""Quality control of extracted features (design doc 04 §F-9).

Values are reported, not judged: no pass/fail thresholds are set here (they are chosen later, from
these numbers, by the owner). Pose indices: 11/12 shoulders, 13/14 elbows, 15/16 wrists (subject's
left/right in MediaPipe Pose naming).
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from .layout import MASK_PARTS

L_SH, R_SH, L_EL, R_EL, L_WR, R_WR = 11, 12, 13, 14, 15, 16


def longest_run(flags: np.ndarray) -> int:
    """Length of the longest run of True values."""
    best = cur = 0
    for f in flags:
        cur = cur + 1 if f else 0
        best = max(best, cur)
    return best


def _bone_cv(pw: np.ndarray, vis: np.ndarray, a: int, b: int) -> float | None:
    ok = ~np.isnan(pw[:, a, 0]) & ~np.isnan(pw[:, b, 0]) & (vis[:, a] > 0.5) & (vis[:, b] > 0.5)
    if ok.sum() < 3:
        return None
    lengths = np.linalg.norm(pw[ok, a] - pw[ok, b], axis=1)
    return float(lengths.std() / lengths.mean()) if lengths.mean() > 0 else None


def _jitter(pw: np.ndarray, joint: int, fps: float) -> float | None:
    """Mean |second difference| of a joint, in m/s² (consecutive valid frames only)."""
    p = pw[:, joint]
    acc = p[2:] - 2 * p[1:-1] + p[:-2]
    ok = ~np.isnan(acc).any(axis=1)
    if ok.sum() < 3:
        return None
    return float(np.linalg.norm(acc[ok], axis=1).mean() * fps * fps)


def _handedness_agreement(z, hw) -> dict:
    """Share of frames where each hand's wrist is nearer the same-side pose wrist (pixel distance)."""
    h, w = hw
    scale = np.array([w, h])
    out = {}
    for side, key, same, other in (("left", "lhand_img", L_WR, R_WR), ("right", "rhand_img", R_WR, L_WR)):
        hand = z[key][:, 0, :2] * scale
        same_p, other_p = z["pose_img"][:, same, :2] * scale, z["pose_img"][:, other, :2] * scale
        ok = ~np.isnan(hand).any(axis=1) & ~np.isnan(same_p).any(axis=1) & ~np.isnan(other_p).any(axis=1)
        if ok.sum() == 0:
            out[side] = None
            continue
        nearer = np.linalg.norm(hand[ok] - same_p[ok], axis=1) < np.linalg.norm(hand[ok] - other_p[ok], axis=1)
        out[side] = float(nearer.mean())
    vals = [v for v in out.values() if v is not None]
    out["mean"] = float(np.mean(vals)) if vals else None
    return out


def qc_row(path: Path) -> dict:
    with np.load(path, allow_pickle=False) as z:
        meta = json.loads(str(z["meta"]))
        mask = z["mask"].astype(bool)
        fps = float(meta["fps"])
        row = {"index": meta["index"], "feat_ver": meta["feat_ver"], "mode": meta["mode"], "frames": meta["frames"],
               "src_frames": meta["src_frames"], "src_fps": meta["src_fps"], "ts_cv": meta["ts_cv"],
               "detect_ms_per_frame": meta["detect_ms_per_frame"], "seconds": meta["seconds"]}
        for n, part in enumerate(MASK_PARTS):
            row[f"cov_{part}"] = float(mask[:, n].mean())
        row["cov_both_hands"] = float((mask[:, 1] & mask[:, 2]).mean())
        row["cov_any_hand"] = float((mask[:, 1] | mask[:, 2]).mean())
        for n, side in ((1, "left"), (2, "right")):
            gap = longest_run(~mask[:, n])
            row[f"longest_gap_{side}_hand_s"] = round(gap / fps, 3)
        pw, vis = z["pose_world"], z["pose_vis"]
        row["cv_upper_arm_left"] = _bone_cv(pw, vis, L_SH, L_EL)
        row["cv_upper_arm_right"] = _bone_cv(pw, vis, R_SH, R_EL)
        row["cv_forearm_left"] = _bone_cv(pw, vis, L_EL, L_WR)
        row["cv_forearm_right"] = _bone_cv(pw, vis, R_EL, R_WR)
        row["jitter_wrist_left"] = _jitter(pw, L_WR, fps)
        row["jitter_wrist_right"] = _jitter(pw, R_WR, fps)
        agree = _handedness_agreement(z, meta["frame_hw"])
        row["hand_side_agree_left"] = agree["left"]
        row["hand_side_agree_right"] = agree["right"]
        row["hand_side_agree_mean"] = agree["mean"]
        head = z["head_rot"]
        row["head_abs_yaw_median"] = float(np.nanmedian(np.abs(head[:, 0]))) if (~np.isnan(head[:, 0])).any() else None
    return row


def write_qc(out_dir: Path, expected: list[int], failures: list[dict]) -> pd.DataFrame:
    """qc.csv for every .npz in out_dir; failures.csv for failed or missing clips."""
    from ..io import atomic_write_text

    rows = [qc_row(out_dir / f"{i}.npz") for i in expected if (out_dir / f"{i}.npz").exists()]
    qc = pd.DataFrame(rows).sort_values("index") if rows else pd.DataFrame()
    atomic_write_text(out_dir / "qc.csv", qc.to_csv(index=False, lineterminator="\n"))
    have = set(qc["index"]) if len(qc) else set()
    fail = {f["index"]: f["error"] for f in failures}
    missing = [{"index": i, "error": fail.get(i, "no output file")} for i in expected if i not in have]
    atomic_write_text(out_dir / "failures.csv",
                      pd.DataFrame(missing, columns=["index", "error"]).to_csv(index=False, lineterminator="\n"))
    return qc


def summarise(qc: pd.DataFrame) -> dict:
    cols = ["cov_pose", "cov_left_hand", "cov_right_hand", "cov_face", "cov_both_hands", "cov_any_hand",
            "longest_gap_left_hand_s", "longest_gap_right_hand_s", "jitter_wrist_left", "jitter_wrist_right",
            "cv_forearm_left", "cv_forearm_right", "hand_side_agree_mean", "ts_cv", "detect_ms_per_frame"]
    out = {"clips": int(len(qc)), "frames": int(qc["frames"].sum())}
    for c in cols:
        s = pd.to_numeric(qc[c], errors="coerce").dropna()
        out[c] = {"mean": round(float(s.mean()), 4), "median": round(float(s.median()), 4),
                  "min": round(float(s.min()), 4), "max": round(float(s.max()), 4)} if len(s) else None
    return out


def compare_modes(qc_by_mode: dict[str, pd.DataFrame]) -> dict:
    """Side-by-side summary of the modes, plus per-clip any-hand coverage differences."""
    out = {mode: summarise(qc) for mode, qc in qc_by_mode.items()}
    if {"video", "image"} <= set(qc_by_mode):
        m = qc_by_mode["video"].merge(qc_by_mode["image"], on="index", suffixes=("_video", "_image"))
        d = m["cov_any_hand_video"] - m["cov_any_hand_image"]
        out["any_hand_video_minus_image"] = {"mean": round(float(d.mean()), 4), "clips_video_higher": int((d > 0).sum()),
                                             "clips_image_higher": int((d < 0).sum()), "clips_equal": int((d == 0).sum())}
        b = m["cov_both_hands_video"] - m["cov_both_hands_image"]
        out["both_hands_video_minus_image"] = {"mean": round(float(b.mean()), 4)}
    return out
