"""Smoothing and hand-presence weights for motion before retargeting (design doc 04 §F-12)."""

from __future__ import annotations

import math

import numpy as np


def _alpha(cutoff: float, fps: float) -> float:
    tau = 1.0 / (2 * math.pi * cutoff)
    return 1.0 / (1.0 + tau * fps)


def one_euro(x: np.ndarray, fps: float, min_cutoff: float = 1.0, beta: float = 0.3, d_cutoff: float = 1.0) -> np.ndarray:
    """One-Euro filter along time for every column of x (T, D): strong smoothing when a value moves
    slowly, less lag when it moves fast (Casiez et al., 2012)."""
    out = np.empty_like(x, dtype=np.float64)
    out[0] = x[0]
    dx_prev = np.zeros(x.shape[1])
    a_d = _alpha(d_cutoff, fps)
    for t in range(1, len(x)):
        dx = (x[t] - out[t - 1]) * fps
        dx_hat = a_d * dx + (1 - a_d) * dx_prev
        cutoff = min_cutoff + beta * np.abs(dx_hat)
        tau = 1.0 / (2 * math.pi * cutoff)
        a = 1.0 / (1.0 + tau * fps)
        out[t] = a * x[t] + (1 - a) * out[t - 1]
        dx_prev = dx_hat
    return out.astype(x.dtype)


def presence_weights(present: np.ndarray, ramp: int = 3) -> np.ndarray:
    """1 where a hand is present, falling linearly to 0 over `ramp` frames into a gap: the avatar's hand
    blends towards its rest pose instead of jumping."""
    w = present.astype(float)
    dist = np.full(len(w), np.inf)
    last = -np.inf
    for t in range(len(w)):
        if present[t]:
            last = t
        dist[t] = t - last
    last = np.inf
    for t in range(len(w) - 1, -1, -1):
        if present[t]:
            last = t
        dist[t] = min(dist[t], last - t)
    return np.clip(1.0 - dist / (ramp + 1), 0.0, 1.0) if ramp else w
