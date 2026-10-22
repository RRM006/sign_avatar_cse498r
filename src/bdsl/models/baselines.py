"""Baselines (no training). Model A: G0, the auto draft with its review markers removed.
Model B (design doc 04 §F-10), in standardised feature space (missing values = 0 = training mean):
    B0  mean motion: every training clip time-normalised, averaged over present values, then stretched
        to the median training length
    B1  retrieval: the real motion of the training sentence with the highest token overlap (Jaccard;
        ties → lowest Index)
"""

from __future__ import annotations

import numpy as np


def g0_gloss(gloss_auto: str) -> list[str]:
    """`আমার খালা~ রান্না?` → ["আমার", "খালা", "রান্না"]."""
    return [t.rstrip("?~") for t in gloss_auto.split() if t.rstrip("?~")]


def g0_tags(tags_auto: str) -> set[str]:
    """G0's own tags; an undecided `q?` stays `q?` and is therefore never counted as right."""
    return {t for t in tags_auto.split(";") if t}


def b0_mean_motion(train_z: list[np.ndarray], train_m: list[np.ndarray], grid: int = 64) -> np.ndarray:
    """Masked mean of the time-normalised training clips, at the median training length."""
    from ..eval.motion_metrics import resample

    num = np.zeros((grid, train_z[0].shape[1]))
    den = np.zeros_like(num)
    for z, m in zip(train_z, train_m, strict=True):
        num += resample(z * m, grid)
        den += resample(m.astype(float), grid)
    mean = np.where(den > 0, num / np.maximum(den, 1e-9), 0.0)
    return resample(mean, int(np.median([len(z) for z in train_z]))).astype(np.float32)


def b1_retrieve(query: list[str], train_tokens: list[list[str]], train_index: list[int]) -> int:
    """Position (in the training list) of the sentence with the highest token Jaccard overlap."""
    q = set(query)

    def key(i):
        t = set(train_tokens[i])
        return (-(len(q & t) / max(len(q | t), 1)), train_index[i])

    return min(range(len(train_tokens)), key=key)
