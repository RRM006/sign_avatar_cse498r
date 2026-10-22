"""G0 v0.1 — the rule-based gloss drafter (annotations/GLOSS_CONVENTION_v0.1.md, ADR-0015).

G0 writes `auto_draft` pseudo-glosses for a human reviewer. It never reorders words, never guesses
a lemma it has no rule for, and marks how sure it is:
    no marker  a closed-list rule applied (pronoun kept, negation, question word)
    `~`        suggested by the corpus-backed genitive rule — check it
    `?`        no rule: written as in the sentence (or a NUM()/FS() candidate)
Rules, first match wins:
    R0 pronoun/demonstrative → kept        R1 negation → NOT / NOT.BE / NOT.HAVE (+ tag neg)
    R2 wh-word → kept (+ tag q-wh)         R2b কি/কী → kept (+ tag q?: reviewer picks q-wh or q-yn)
    R3 digits → NUM(token)?                R4 Latin letters → FS(token)?
    R5 genitive ending (য়ের/ের/র) whose stem (≥ 2 characters) is itself a word in the sheet → stem~
    R6 anything else → token?
"""

from __future__ import annotations

import re

from .normalize import normalize

G0_VER = "G0-v0.1"

PRONOUNS = {normalize(w) for w in (
    "আমি", "তুমি", "আপনি", "সে", "তিনি", "আমরা", "তোমরা", "আপনারা", "তারা", "আমার", "তোমার", "আপনার",
    "তার", "তাঁর", "আমাদের", "তোমাদের", "আপনাদের", "তাদের", "এটা", "ওটা", "সেটা", "এই", "ওই", "সেই",
)}
NEGATION = {normalize(k): v for k, v in {
    "না": "NOT", "নয়": "NOT.BE", "নই": "NOT.BE", "নও": "NOT.BE", "নন": "NOT.BE", "নেই": "NOT.HAVE", "নাই": "NOT.HAVE",
}.items()}
NEGATION_UNSURE = {normalize("নি"): "NOT"}
WH_WORDS = {normalize(w) for w in (
    "কে", "কাকে", "কার", "কারা", "কোথায়", "কোথা", "কখন", "কেন", "কিভাবে", "কীভাবে", "কেমন", "কত", "কতো",
    "কোন", "কোনটা", "কোনটি", "কয়টা", "কয়", "কিসে", "কিসের",
)}
KI = {normalize(w) for w in ("কি", "কী")}
GENITIVE = tuple(normalize(s) for s in ("য়ের", "ের", "র"))
_DIGIT = re.compile(r"[0-9০-৯]")
_LATIN = re.compile(r"[A-Za-z][A-Za-z\-]*")


def gloss_token(tok: str, corpus: set[str]) -> tuple[str, set[str], str]:
    """(gloss text, sentence tags, rule id) for one norm_v1 token."""
    if tok in PRONOUNS:
        return tok, set(), "R0"
    if tok in NEGATION:
        return NEGATION[tok], {"neg"}, "R1"
    if tok in NEGATION_UNSURE:
        return NEGATION_UNSURE[tok] + "?", {"neg"}, "R1"
    if tok in WH_WORDS:
        return tok, {"q-wh"}, "R2"
    if tok in KI:
        return tok, {"q?"}, "R2b"
    if _DIGIT.search(tok):
        return f"NUM({tok})?", set(), "R3"
    if _LATIN.fullmatch(tok):
        return f"FS({tok})?", set(), "R4"
    for suffix in GENITIVE:
        stem = tok[: -len(suffix)]
        if tok.endswith(suffix) and len(stem) >= 2 and stem in corpus:
            return stem + "~", set(), "R5"
    return tok + "?", set(), "R6"


def g0(sentence_norm: str, corpus: set[str]) -> tuple[str, str, list[str]]:
    """(gloss_auto, tags_auto, rule per token). Word order is kept; tags are sorted, ';'-joined."""
    glosses, tags, rules = [], set(), []
    for tok in sentence_norm.split():
        g, t, r = gloss_token(tok, corpus)
        glosses.append(g)
        tags |= t
        rules.append(r)
    return " ".join(glosses), ";".join(sorted(tags)), rules
