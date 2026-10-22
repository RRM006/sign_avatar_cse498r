"""Indicative sentence tags used only to stratify splits and the pilot.

These are small hand-written word lists, NOT linguistic annotation: a sentence tagged "question" is
only *likely* a question (the sheet contains no `?` at all). Glosses and their [neg]/[q-*] tags come
later from the gloss convention and human review (ADR-0015).
"""

from __future__ import annotations

import re

from .normalize import normalize

QUESTION_WORDS = {normalize(w) for w in (
    "কি", "কী", "কে", "কাকে", "কার", "কারা", "কেন", "কোথায়", "কোথা", "কখন", "কিভাবে", "কীভাবে",
    "কেমন", "কত", "কতো", "কয়", "কয়টা", "কোন", "কোনটা", "কোনটি", "কিসে", "কিসের",
)}
NEGATION_WORDS = {normalize(w) for w in ("না", "নয়", "নেই", "নাই", "নি")}
TIME_WORDS = {normalize(w) for w in (
    "সকাল", "দুপুর", "বিকাল", "বিকেল", "সন্ধ্যা", "রাত", "আজ", "কাল", "আগামীকাল", "গতকাল", "সময়",
    "ঘণ্টা", "মিনিট", "দিন", "সপ্তাহ", "মাস", "বছর",
)}
_DIGIT = re.compile(r"[0-9০-৯]")

STRATA_PRIORITY = ("question", "negation", "number_time", "long", "short", "other")


def is_question(toks: list[str]) -> bool:
    return any(t in QUESTION_WORDS for t in toks)


def is_negation(toks: list[str]) -> bool:
    return any(t in NEGATION_WORDS for t in toks)


def has_number_or_time(toks: list[str]) -> bool:
    return any(_DIGIT.search(t) or t in TIME_WORDS for t in toks)


def stratum(toks: list[str], long_min: int = 7, short_max: int = 2) -> str:
    """First matching tag in STRATA_PRIORITY order."""
    if is_question(toks):
        return "question"
    if is_negation(toks):
        return "negation"
    if has_number_or_time(toks):
        return "number_time"
    if len(toks) >= long_min:
        return "long"
    if len(toks) <= short_max:
        return "short"
    return "other"


def length_bucket(n_tokens: int) -> str:
    if n_tokens <= 2:
        return "1-2"
    if n_tokens <= 4:
        return "3-4"
    if n_tokens <= 6:
        return "5-6"
    return "7+"
