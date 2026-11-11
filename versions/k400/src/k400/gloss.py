"""Notebook 03: G0 pseudo-glosses for all 400 sentences + vocabularies built from TRAIN only.

G0 (`bdsl.text.gloss_rules`, v0.1) is a deterministic rule drafter: it never reorders words and never
guesses a lemma. Its output is a PSEUDO-GLOSS with status `auto_draft`; nobody has checked it against
the videos and it is NOT a BdSL annotation (ADR-0015). Applying the rule to test sentences uses no
model and makes no decision, so it does not touch the test lock; the files are only read by training
for train and val.

The G0 genitive rule (R5) needs the set of words of the whole sheet; it is stored in
`processed/glosses/g0_corpus_v1.txt` (one normalised word per line, from all 5,010 sheet sentences of
manifest_v1), so the same drafts can be produced on Kaggle without the sheet.
"""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from bdsl.io import atomic_write_json, atomic_write_text, sha256_text_canonical
from bdsl.text.annotations import build_drafts, write_csv
from bdsl.text.normalize import tokens

SPLITS = ("train", "val", "test")
CORPUS_FILE = "g0_corpus_v1.txt"


def write_corpus(manifest: pd.DataFrame, path: Path) -> int:
    words = sorted({t for s in manifest["sentence_raw"] for t in tokens(s)})
    atomic_write_text(path, "\n".join(words) + "\n")
    return len(words)


def read_corpus(path: Path) -> set[str]:
    return {ln.strip() for ln in path.read_text(encoding="utf-8").splitlines() if ln.strip()}


def make_glosses(data_dir: Path, gloss_dir: Path, corpus: set[str], g0_ver: str) -> dict:
    out = {}
    for sp in SPLITS:
        man = pd.read_csv(data_dir / sp / f"{sp}_manifest.csv", dtype={"sentence_raw": str}, encoding="utf-8-sig")
        drafts, rules = build_drafts(man[["index", "split", "sentence_raw"]], corpus, g0_ver)
        f = gloss_dir / f"gloss_g0_{sp}.csv"
        write_csv(drafts, f)
        out[sp] = {"file": f.name, "rows": len(drafts), "tokens_per_rule": rules, "sha256_canonical": sha256_text_canonical(f),
                   "status": drafts["status"].value_counts().to_dict()}
    return out


def _vocab(tokens_list) -> list[str]:
    from bdsl.models.text2gloss import SPECIALS

    return SPECIALS + sorted({t for toks in tokens_list for t in toks} - set(SPECIALS))


def build_vocabs(gloss_dir: Path, vocab_dir: Path) -> dict:
    """Vocabularies from TRAIN only (exactly as the training code builds them) + val OOV rates."""
    from bdsl.models.baselines import g0_gloss, g0_tags
    from bdsl.models.text2gloss import tag_token

    g = {sp: pd.read_csv(gloss_dir / f"gloss_g0_{sp}.csv", dtype=str, keep_default_na=False, encoding="utf-8-sig")
         for sp in ("train", "val")}

    def model_b_gloss(r):
        return [f"<{t}>" for t in sorted(g0_tags(r["tags_auto"]))] + g0_gloss(r["gloss_auto"])

    def model_a_tgt(r):
        return [tag_token(t) for t in sorted(g0_tags(r["tags_auto"]))] + g0_gloss(r["gloss_auto"])

    views = {"modelB_gloss_input": model_b_gloss, "modelB_text_input": lambda r: r["sentence_norm"].split(),
             "modelA_source": lambda r: r["sentence_norm"].split(), "modelA_target_G0": model_a_tgt}
    report = {"built_from": "train only", "note": "val OOV = share of val tokens that become <unk>"}
    for name, fn in views.items():
        train_toks = [fn(r) for r in g["train"].to_dict("records")]
        vocab = _vocab(train_toks)
        atomic_write_json(vocab_dir / f"vocab_{name}.json", {"name": name, "built_from": "train", "size": len(vocab),
                                                             "itos": vocab})
        known = set(vocab)
        val_toks = [t for r in g["val"].to_dict("records") for t in fn(r)]
        report[name] = {"size": len(vocab), "val_tokens": len(val_toks),
                        "val_oov_tokens": sum(t not in known for t in val_toks),
                        "val_oov_rate": round(sum(t not in known for t in val_toks) / max(len(val_toks), 1), 4)}
    atomic_write_json(vocab_dir / "vocab_report.json", report)
    return report


def compare(gloss_dir: Path, reference_dir: Path) -> dict:
    """Canonical-hash comparison with the committed copies (line endings ignored)."""
    out = {}
    for sp in SPLITS:
        a, b = gloss_dir / f"gloss_g0_{sp}.csv", reference_dir / f"gloss_g0_{sp}.csv"
        out[sp] = "missing reference" if not b.is_file() else (
            "IDENTICAL" if sha256_text_canonical(a) == sha256_text_canonical(b) else "DIFFERENT")
    return out


def summary_json(d: dict) -> str:
    return json.dumps(d, indent=1, ensure_ascii=False)
