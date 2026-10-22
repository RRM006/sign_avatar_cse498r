"""Model A metrics (ADR-0020): gloss WER, exact match, tag accuracy, BLEU-4 and chrF (sacreBLEU).

Glosses are lists of tokens (tag tokens already removed). Percentages are 0–100. On a 5-item pilot
split one item moves a score by up to 20 points: these numbers show that the code runs, nothing more.
"""

from __future__ import annotations


def edit_distance(ref: list[str], hyp: list[str]) -> int:
    """Token-level Levenshtein distance (substitutions + deletions + insertions)."""
    prev = list(range(len(hyp) + 1))
    for i, r in enumerate(ref, 1):
        cur = [i]
        for j, h in enumerate(hyp, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (r != h)))
        prev = cur
    return prev[-1]


def item_wer(ref: list[str], hyp: list[str]) -> float:
    return 100.0 * edit_distance(ref, hyp) / max(len(ref), 1)


def wer(refs: list[list[str]], hyps: list[list[str]]) -> float:
    """Corpus WER: all edits divided by all reference tokens."""
    edits = sum(edit_distance(r, h) for r, h in zip(refs, hyps, strict=True))
    return 100.0 * edits / max(sum(len(r) for r in refs), 1)


def exact_match(refs: list[list[str]], hyps: list[list[str]]) -> float:
    return 100.0 * sum(r == h for r, h in zip(refs, hyps, strict=True)) / max(len(refs), 1)


def tag_accuracy(ref_tags: list[set[str]], hyp_tags: list[set[str]]) -> float:
    """Share of sentences whose whole tag set (neg / q-wh / q-yn) is right, including "no tag"."""
    return 100.0 * sum(r == h for r, h in zip(ref_tags, hyp_tags, strict=True)) / max(len(ref_tags), 1)


def bleu_chrf(refs: list[list[str]], hyps: list[list[str]]) -> dict:
    """Corpus BLEU-4 on the given tokens (no re-tokenisation) and character chrF."""
    import sacrebleu

    r = [" ".join(t) for t in refs]
    h = [" ".join(t) for t in hyps]
    return {"bleu4": sacrebleu.corpus_bleu(h, [r], tokenize="none").score,
            "chrf": sacrebleu.corpus_chrf(h, [r]).score}


def score(refs, hyps, ref_tags, hyp_tags) -> dict:
    return {"n": len(refs), "wer": wer(refs, hyps), "exact_match": exact_match(refs, hyps),
            "tag_accuracy": tag_accuracy(ref_tags, hyp_tags), **bleu_chrf(refs, hyps)}
