"""Model B metrics (ADR-0020), computed on raw (unstandardised) 208-value frames.

Units: body in shoulder widths (sw); hands in millimetres (wrist-relative hand shape, not global position);
face = mean absolute blendshape error (0–1). GT frames where a part is missing are left out.
- MPJPE: the prediction is linearly resampled to the GT length (time-normalised), then mean joint error.
- DTW-MJE: mean joint error along the dynamic-time-warping path between prediction and GT.
- Duration error: |predicted − true| frames / fps, in seconds.
- Velocity / jerk ratio, hand-energy ratio (wrist speed²): prediction ÷ GT, 1.0 = same amount of motion.
- Diversity: mean pairwise distance between the body motions of different items, prediction ÷ GT.
  Close to 0 means "mean collapse" (every sentence gets the same motion).
"""

from __future__ import annotations

import itertools

import numpy as np

from ..features.normalize import PARTS, WRISTS


def resample(x: np.ndarray, n: int) -> np.ndarray:
    """Linear resampling along time to n frames."""
    if len(x) == n:
        return x
    src = np.linspace(0, 1, len(x))
    dst = np.linspace(0, 1, n)
    return np.stack([np.interp(dst, src, x[:, d]) for d in range(x.shape[1])], axis=1)


def _joints(x: np.ndarray, part: str) -> np.ndarray:
    return x[:, PARTS[part]].reshape(len(x), -1, 3)


def _frame_error(p: np.ndarray, g: np.ndarray, part: str) -> np.ndarray:
    """Per-frame error between aligned frames (T, ·) of one part."""
    if part == "face":
        return np.abs(p[:, PARTS["face"]][:, :52] - g[:, PARTS["face"]][:, :52]).mean(1)
    err = np.linalg.norm(_joints(p, part) - _joints(g, part), axis=-1).mean(1)
    return err * 1000.0 if part in ("lhand", "rhand") else err


def mpjpe(pred: np.ndarray, gt: np.ndarray, gt_mask: np.ndarray) -> dict:
    p = resample(pred, len(gt))
    out = {}
    for j, part in enumerate(PARTS):
        keep = gt_mask[:, j]
        out[part] = float(_frame_error(p[keep], gt[keep], part).mean()) if keep.any() else float("nan")
    return out


def dtw_cost(cost: np.ndarray) -> float:
    """Mean cost along the optimal monotonic alignment path (anti-diagonal sweep; ties: diagonal first)."""
    n, m = cost.shape
    acc = np.full((n + 1, m + 1), np.inf)
    steps = np.zeros((n + 1, m + 1))
    acc[0, 0] = 0.0
    for k in range(2, n + m + 1):
        i = np.arange(max(1, k - m), min(n, k - 1) + 1)
        j = k - i
        cand = np.stack([acc[i - 1, j - 1], acc[i - 1, j], acc[i, j - 1]])
        best = cand.argmin(0)
        prev_steps = np.stack([steps[i - 1, j - 1], steps[i - 1, j], steps[i, j - 1]])
        acc[i, j] = cand[best, np.arange(len(i))] + cost[i - 1, j - 1]
        steps[i, j] = prev_steps[best, np.arange(len(i))] + 1
    return float(acc[n, m] / steps[n, m])


def _cost_matrix(p: np.ndarray, g: np.ndarray, part: str) -> np.ndarray:
    """Error between every predicted frame and every GT frame of one part."""
    if part == "face":
        return np.abs(p[:, None, PARTS["face"]][..., :52] - g[None, :, PARTS["face"]][..., :52]).mean(-1)
    d = np.linalg.norm(_joints(p, part)[:, None] - _joints(g, part)[None], axis=-1).mean(-1)
    return d * 1000.0 if part in ("lhand", "rhand") else d


def dtw_mje(pred: np.ndarray, gt: np.ndarray, gt_mask: np.ndarray) -> dict:
    out = {}
    for j, part in enumerate(PARTS):
        g = gt[gt_mask[:, j]]
        out[part] = dtw_cost(_cost_matrix(pred, g, part)) if len(g) else float("nan")
    return out


def motion_amount(x: np.ndarray) -> dict:
    b = _joints(x, "body")
    v = np.diff(b, axis=0)
    jerk = np.diff(b, n=3, axis=0)
    w = np.diff(b[:, list(WRISTS)], axis=0)
    return {"velocity": float(np.linalg.norm(v, axis=-1).mean()) if len(v) else 0.0,
            "jerk": float(np.linalg.norm(jerk, axis=-1).mean()) if len(jerk) else 0.0,
            "hand_energy": float((w ** 2).sum(-1).mean()) if len(w) else 0.0}


def diversity(xs: list[np.ndarray], n: int = 32) -> float:
    if len(xs) < 2:
        return float("nan")
    flat = [resample(x[:, PARTS["body"]], n).ravel() for x in xs]
    return float(np.mean([np.linalg.norm(a - b) for a, b in itertools.combinations(flat, 2)]))


def item_metrics(pred: np.ndarray, gt: np.ndarray, gt_mask: np.ndarray, fps: float, dtw: bool) -> dict:
    a, b = motion_amount(pred), motion_amount(gt)
    out = {f"mpjpe_{k}": v for k, v in mpjpe(pred, gt, gt_mask).items()}
    if dtw:
        out |= {f"dtw_{k}": v for k, v in dtw_mje(pred, gt, gt_mask).items()}
    return out | {"duration_err_s": abs(len(pred) - len(gt)) / fps, "pred_frames": len(pred), "gt_frames": len(gt),
                  **{f"{k}_ratio": a[k] / b[k] if b[k] else float("nan") for k in a}}


def summarize(items: list[dict], preds: list[np.ndarray], gts: list[np.ndarray]) -> dict:
    keys = [k for k in items[0] if k not in ("pred_frames", "gt_frames")]
    out = {k: float(np.nanmean([it[k] for it in items])) for k in keys}
    d_gt = diversity(gts)
    out["diversity_ratio"] = diversity(preds) / d_gt if d_gt else float("nan")
    out["n"] = len(items)
    return out
