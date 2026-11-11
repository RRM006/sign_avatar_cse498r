"""One plotting style for every kaggle400 figure (paper-ready PNG, light surface).

Colours follow a validated categorical order (identity, never rank): slot 1 blue, 2 orange, 3 aqua; the
first three pass colour-vision-deficiency checks as a set. Baselines/pool use neutral greys, so a
fourth hue is never needed. Text is always dark ink, never a series colour.
"""

from __future__ import annotations

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

SURFACE = "#fcfcfb"
INK = "#0b0b0b"
INK_2 = "#52514e"
GRID = "#e4e3df"
SLOT = {1: "#2a78d6", 2: "#eb6834", 3: "#1baf7a"}
NEUTRAL = "#9a9890"
NEUTRAL_DARK = "#5f5e59"
SPLIT_COLOURS = {"train": SLOT[1], "val": SLOT[2], "test": SLOT[3], "pool": NEUTRAL}
METHOD_COLOURS = {"model_b_gloss": SLOT[1], "model_b_text": SLOT[2], "B1": SLOT[3], "B0": NEUTRAL,
                  "model_a": SLOT[1]}
METHOD_NAMES = {"model_b_gloss": "Model B (G0 gloss)", "model_b_text": "Model B (Bangla words, ablation T)",
                "B0": "B0 mean motion", "B1": "B1 retrieval"}


def apply() -> None:
    plt.rcParams.update({
        "figure.facecolor": SURFACE, "axes.facecolor": SURFACE, "savefig.facecolor": SURFACE,
        "axes.edgecolor": GRID, "axes.labelcolor": INK_2, "axes.titlecolor": INK, "axes.titlesize": 10,
        "axes.labelsize": 9, "xtick.color": INK_2, "ytick.color": INK_2, "xtick.labelsize": 8,
        "ytick.labelsize": 8, "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.6,
        "axes.axisbelow": True, "axes.spines.top": False, "axes.spines.right": False,
        "legend.frameon": False, "legend.fontsize": 8, "font.size": 9, "lines.linewidth": 2.0,
        "savefig.dpi": 200, "savefig.bbox": "tight",
    })


def footer(fig, text: str) -> None:
    fig.text(0.01, 0.005, text, fontsize=7, color=INK_2, ha="left", va="bottom")
