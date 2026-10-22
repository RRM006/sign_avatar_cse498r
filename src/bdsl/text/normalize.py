"""norm_v1 — the project's text normaliser.

Encoding clean-up only, never a spelling change (ADR-0008):
  1. Unicode NFC, so the same visible letters always have the same code points
     (990 of 5,010 sheet rows change under NFC; without it, equal sentences look different);
  2. the punctuation `। . ? ! ,` becomes a space;
  3. runs of whitespace collapse to one space; leading/trailing spaces are removed.
Digits (Bangla and Latin), Latin letters, hyphens and ZWNJ are kept as written.
"""

from __future__ import annotations

import re
import unicodedata

NORM_VER = "norm_v1"
_PUNCT = re.compile(r"[।.?!,]")
_SPACE = re.compile(r"\s+")


def normalize(text: str) -> str:
    t = unicodedata.normalize("NFC", str(text))
    t = _PUNCT.sub(" ", t)
    return _SPACE.sub(" ", t).strip()


def tokens(text: str) -> list[str]:
    """Whitespace tokens of the normalised text."""
    norm = normalize(text)
    return norm.split(" ") if norm else []
