"""Bootstrap 95% confidence intervals over test (or val) items (owner request, 2026-10-23).

Percentile bootstrap: resample the items with replacement `resamples` times (default 1,000), recompute
the statistic, and report the 2.5th and 97.5th percentiles. The random generator is seeded, so the same
inputs always give the same interval. With 40 items the intervals are wide; that is the honest result.
"""

from __future__ import annotations

from typing import Callable

import numpy as np


def resample_indices(n: int, resamples: int, seed: int) -> np.ndarray:
    """(resamples, n) item indices drawn with replacement."""
    rng = np.random.default_rng(seed)
    return rng.integers(0, n, size=(resamples, n))


def bootstrap_stat(n: int, stat: Callable[[np.ndarray], float], resamples: int = 1000, ci: float = 95.0,
                   seed: int = 0) -> dict:
    """CI of `stat(indices)` where `indices` selects items (with repeats)."""
    if n == 0:
        return {"estimate": float("nan"), "low": float("nan"), "high": float("nan"), "n": 0,
                "resamples": resamples, "ci": ci, "seed": seed}
    full = float(stat(np.arange(n)))
    vals = np.array([stat(idx) for idx in resample_indices(n, resamples, seed)], dtype=float)
    vals = vals[np.isfinite(vals)]
    a = (100.0 - ci) / 2
    low, high = (np.percentile(vals, [a, 100.0 - a]) if len(vals) else (np.nan, np.nan))
    return {"estimate": full, "low": float(low), "high": float(high), "n": int(n), "resamples": resamples,
            "valid_resamples": int(len(vals)), "ci": ci, "seed": seed}


def bootstrap_mean(values, resamples: int = 1000, ci: float = 95.0, seed: int = 0) -> dict:
    """CI of the mean of per-item values (NaN items are left out before resampling)."""
    v = np.asarray(values, dtype=float)
    v = v[np.isfinite(v)]
    return bootstrap_stat(len(v), lambda idx: float(v[idx].mean()), resamples, ci, seed)


def bootstrap_paired_diff(a, b, resamples: int = 1000, ci: float = 95.0, seed: int = 0) -> dict:
    """CI of mean(a − b) over items where both are finite. `excludes_zero` says whether the interval
    lies entirely on one side of 0 (a difference the data can resolve at this sample size)."""
    a, b = np.asarray(a, dtype=float), np.asarray(b, dtype=float)
    ok = np.isfinite(a) & np.isfinite(b)
    out = bootstrap_mean(a[ok] - b[ok], resamples, ci, seed)
    out["excludes_zero"] = bool(np.isfinite(out["low"]) and (out["low"] > 0 or out["high"] < 0))
    return out
