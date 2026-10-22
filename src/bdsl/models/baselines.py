"""G0 as a Model A baseline: the auto draft with its review markers removed (no training)."""

from __future__ import annotations


def g0_gloss(gloss_auto: str) -> list[str]:
    """`আমার খালা~ রান্না?` → ["আমার", "খালা", "রান্না"]."""
    return [t.rstrip("?~") for t in gloss_auto.split() if t.rstrip("?~")]


def g0_tags(tags_auto: str) -> set[str]:
    """G0's own tags; an undecided `q?` stays `q?` and is therefore never counted as right."""
    return {t for t in tags_auto.split(";") if t}
