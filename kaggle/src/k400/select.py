"""Choose the 400 clips of kaggle400 from manifest_v1 + split S1 v0 (owner rules, 2026-10-23).

Rules, in order (every "random" choice is an ordering by SHA-256 of (seed, …): the same inputs always
give the same 400 clips):
  0. Pool: representative clips only (no exact copies), decodable, no label conflict, assigned to
     train/val/test in S1 v0; one clip per normalised sentence. A clip keeps its S1 partition.
  1. The colour cluster 3456/3457/3458 (one recording edited onto three endings, ADR-0018) is one unit:
     all three go to train, their S1 partition. Val/test sentences of the same minimal-pair family
     ("আমার পছন্দের রং _") are not used at all: they may share that footage too (G2 unscanned).
  2. Minimal pairs: per held-out split, N clips whose sentence differs by exactly one word from a train
     clip (the "train sibling", added to train). If a held-out word is still missing from the train
     selection, one "vocabulary support" train clip that contains it is added. These items measure
     "unseen combination of seen words".
  3. Stratified fill: val and test, then train, are filled greedily so that each split's distribution
     of length bucket, question/negation words (indicative), orientation, resolution bucket and duration
     quartile stays as close as possible to the whole pool (sum of absolute differences of shares).
Leakage safety comes from S1 v0 itself (group-disjoint: same sentence, same SHA-256, known links) and
is re-checked by verify.py. Known limits are written into SPLIT_REPORT.md.
"""

from __future__ import annotations

import hashlib
from collections import defaultdict

import numpy as np
import pandas as pd

from bdsl.text.normalize import tokens
from bdsl.text.tags import has_number_or_time, is_negation, is_question, length_bucket

SPLITS = ("train", "val", "test")
MANIFEST_COLUMNS = [
    "index", "filename", "split", "s1_split", "sentence_raw", "sentence_norm", "sha256", "orientation", "duration_s",
    "fps", "resolution_bucket", "display_w", "display_h", "codec", "bytes", "sentence_length", "length_bucket",
    "duration_quartile", "tags", "question", "negation", "group_id", "mp_family", "mp_role", "mp_partner",
    "has_train_minimal_pair_sibling", "all_words_in_train", "oov_words", "in_pilot50", "source_relpath", "reason",
]


def hkey(*parts) -> str:
    return hashlib.sha256("|".join(str(p) for p in parts).encode("utf-8")).hexdigest()


def resolution_bucket(w: int, h: int, low: int) -> str:
    s = min(int(w), int(h))
    return f"low(<{low})" if s < low else ("720" if s < 800 else ("1080" if s < 1200 else "higher"))


def build_pool(manifest: pd.DataFrame, split_df: pd.DataFrame, kcfg: dict) -> pd.DataFrame:
    """Rule 0. One row per normalised sentence, with the stratification columns."""
    m = manifest.merge(split_df[["index", "split"]], on="index", suffixes=("", "_s1"))
    m = m[m["is_representative"] & m["decode_ok"] & ~m["label_conflict"] & m["split"].isin(SPLITS)].copy()
    m["_order"] = [hkey(kcfg["seed"], "clip", i) for i in m["index"]]
    m = m.sort_values("_order").drop_duplicates("sentence_norm", keep="first").drop(columns="_order")
    m["tokens"] = m["sentence_norm"].map(tokens)
    m["sentence_length"] = m["tokens"].map(len)
    m["length_bucket"] = m["sentence_length"].map(length_bucket)
    m["question"] = m["tokens"].map(is_question)
    m["negation"] = m["tokens"].map(is_negation)
    m["number_time"] = m["tokens"].map(has_number_or_time)
    m["resolution_bucket"] = [resolution_bucket(w, h, kcfg["low_res_short_side"]) for w, h in zip(m["display_w"], m["display_h"])]
    m["duration_quartile"] = pd.qcut(m["duration_s"], 4, labels=["q1", "q2", "q3", "q4"]).astype(str)
    m["tags"] = [";".join(t for t, on in (("question", q), ("negation", n), ("number_time", nt)) if on)
                 for q, n, nt in zip(m["question"], m["negation"], m["number_time"])]
    m["s1_split"] = m["split"]
    return m.sort_values("index").set_index("index", drop=False)


def minimal_pair_families(pool: pd.DataFrame) -> dict[str, list[int]]:
    """"<length>|<pattern with _ at the differing slot>" → clip indices (≥ 2 members)."""
    fam = defaultdict(list)
    for i, toks in zip(pool["index"], pool["tokens"]):
        for pos in range(len(toks)):
            fam[f"{len(toks)}|{' '.join(toks[:pos] + ['_'] + toks[pos + 1:])}"].append(int(i))
    return {k: v for k, v in fam.items() if len(v) >= 2}


def _slot_word(key: str, toks: list[str]) -> str:
    pattern = key.split("|", 1)[1].split(" ")
    return toks[pattern.index("_")]


class _Strata:
    """Greedy distribution matching against the pool's shares (vectorised one-hot counts)."""

    def __init__(self, pool: pd.DataFrame, cols: list[str]):
        self.cols = cols
        dummies = [pd.get_dummies(pool[c].astype(str), prefix=c) for c in cols]
        self.onehot = pd.concat(dummies, axis=1).astype(float)
        self.target = self.onehot.mean(axis=0).to_numpy()
        self.pos = {i: n for n, i in enumerate(pool.index)}

    def best(self, chosen: list[int], candidates: list[int], seed, salt: str) -> int:
        X = self.onehot.to_numpy()
        counts = X[[self.pos[i] for i in chosen]].sum(0) if chosen else np.zeros(X.shape[1])
        cand = X[[self.pos[i] for i in candidates]]
        score = np.abs((counts + cand) / (len(chosen) + 1) - self.target).sum(1)
        order = sorted(range(len(candidates)), key=lambda k: (round(float(score[k]), 12), hkey(seed, salt, candidates[k])))
        return candidates[order[0]]


def select_subset(manifest: pd.DataFrame, split_df: pd.DataFrame, kcfg: dict,
                  links: list[list[int]] | None, pilot_indices: set[int] | None = None
                  ) -> tuple[pd.DataFrame, dict, pd.DataFrame]:
    """(selection, report, pool). `pilot_indices` only fills the `in_pilot50` column (no influence)."""
    pool = build_pool(manifest, split_df, kcfg)
    seed, targets = kcfg["seed"], {k: int(v) for k, v in kcfg["targets"].items()}
    link_members = {int(i) for link in (links or []) for i in link}
    chosen: dict[int, dict] = {}

    def take(i: int, split: str, reason: str, **kw):
        if i in chosen:
            raise RuntimeError(f"clip {i} chosen twice")
        if pool.loc[i, "s1_split"] != split:
            raise RuntimeError(f"clip {i} is in S1 {pool.loc[i, 's1_split']}, not {split}")
        chosen[i] = {"index": i, "split": split, "reason": reason, "mp_family": kw.get("family", ""),
                     "mp_role": kw.get("role", ""), "mp_partner": str(kw["partner"]) if "partner" in kw else ""}

    def in_split(split):
        return [i for i, c in chosen.items() if c["split"] == split]

    # 1. Colour cluster (known shared-segment link) as one unit, in its S1 partition.
    families = minimal_pair_families(pool)
    excluded_heldout = set()
    for link in links or []:
        members = [int(i) for i in link if int(i) in pool.index]
        if not members:
            continue
        parts = set(pool.loc[members, "s1_split"])
        if len(parts) != 1:
            raise RuntimeError(f"known link {link} crosses S1 partitions {parts}")
        sp = parts.pop()
        for i in members:
            take(i, sp, f"colour cluster {'/'.join(map(str, link))} (known shared-segment link, ADR-0018): "
                        f"kept together in {sp}, its S1 v0 partition")
        for key, fam in families.items():
            if set(fam) & set(members):
                excluded_heldout |= {i for i in fam if pool.loc[i, "s1_split"] != sp}
    # 2. Minimal-pair held-out clips with a train sibling (+ vocabulary support where needed).
    train_pool = [int(i) for i in pool.index[pool["s1_split"] == "train"]]
    word_index = defaultdict(list)
    for i in train_pool:
        for t in set(pool.loc[i, "tokens"]):
            word_index[t].append(i)
    fam_of = defaultdict(list)
    for key, fam in families.items():
        for i in fam:
            fam_of[i].append(key)
    used_families = set()
    unsupported = []
    for split in ("val", "test"):
        n_needed = int(kcfg["minimal_pair_heldout"][split])
        cands = []
        for i in pool.index[pool["s1_split"] == split]:
            i = int(i)
            if i in excluded_heldout or i in link_members:
                continue
            for key in fam_of.get(i, []):
                sibs = [t for t in families[key] if pool.loc[t, "s1_split"] == "train" and t not in link_members]
                if not sibs or key in used_families or set(families[key]) & link_members:
                    continue
                word = _slot_word(key, pool.loc[i, "tokens"])
                supported = any(t not in families[key] for t in word_index.get(word, []))
                cands.append((not supported, hkey(seed, "mp", split, i, key), i, key, sibs))
        cands.sort()
        picked = 0
        for _, _, i, key, sibs in cands:
            if picked >= n_needed:
                break
            if i in chosen or key in used_families:
                continue
            free_sibs = sorted((t for t in sibs if t not in chosen), key=lambda t: hkey(seed, "sib", key, t))
            if not free_sibs:
                continue
            sib = free_sibs[0]
            used_families.add(key)
            take(i, split, f"minimal pair ({split}): differs by one word from train clip {sib} (family '{key}'); "
                           "measures an unseen combination of seen words", family=key, role="heldout", partner=sib)
            take(sib, "train", f"minimal-pair sibling (train) of {split} clip {i} (family '{key}')",
                 family=key, role="train_sibling", partner=i)
            picked += 1
        if picked < n_needed:
            raise RuntimeError(f"only {picked} minimal-pair clips available for {split} (wanted {n_needed})")
    # vocabulary support: every word of a minimal-pair held-out clip should occur in the train selection
    for i, c in sorted(chosen.items()):
        if c["mp_role"] != "heldout":
            continue
        for w in pool.loc[i, "tokens"]:
            vocab = {t for j in in_split("train") for t in pool.loc[j, "tokens"]}
            if w in vocab:
                continue
            opts = [j for j in word_index.get(w, []) if j not in chosen and j not in link_members]
            if not opts:
                unsupported.append((i, w))
                continue
            j = min(opts, key=lambda j: (pool.loc[j, "sentence_length"], hkey(seed, "support", w, j)))
            take(j, "train", f"vocabulary support (train): contains '{w}', a word of {c['split']} minimal-pair clip {i}",
                 family=c["mp_family"], role="vocab_support", partner=i)
    # 3. Stratified fill: val, test, then train.
    strata = _Strata(pool, list(kcfg["strata"]))
    for split in ("val", "test", "train"):
        cands = [int(i) for i in pool.index[pool["s1_split"] == split]
                 if int(i) not in chosen and int(i) not in excluded_heldout and int(i) not in link_members]
        if len(in_split(split)) > targets[split]:
            raise RuntimeError(f"{split}: {len(in_split(split))} clips before filling, target {targets[split]}")
        while len(in_split(split)) < targets[split]:
            best = strata.best(in_split(split), cands, seed, f"fill|{split}")
            cands.remove(best)
            r = pool.loc[best]
            take(best, split, f"stratified fill ({split}): keeps {split} close to the pool on "
                              f"{', '.join(kcfg['strata'])} (this clip: {r['length_bucket']} words, {r['orientation']}, "
                              f"{r['resolution_bucket']}, duration {r['duration_quartile']}{', ' + r['tags'] if r['tags'] else ''})")
    sel = pd.DataFrame(chosen.values()).merge(pool.reset_index(drop=True), on="index", suffixes=("", "_pool"))
    sel = sel.drop(columns=[c for c in ("split_pool",) if c in sel])
    # Final per-clip vocabulary / minimal-pair facts (computed on the final selection).
    train_vocab = {t for toks in sel.loc[sel["split"] == "train", "tokens"] for t in toks}
    train_set = set(sel.loc[sel["split"] == "train", "index"])
    sel["oov_words"] = [" ".join(t for t in toks if t not in train_vocab) if sp != "train" else ""
                        for toks, sp in zip(sel["tokens"], sel["split"])]
    sel["all_words_in_train"] = [sp == "train" or not o for sp, o in zip(sel["split"], sel["oov_words"])]
    sel["has_train_minimal_pair_sibling"] = [
        sp != "train" and any(set(families[k]) & (train_set - {i}) for k in fam_of.get(i, []))
        for i, sp in zip(sel["index"], sel["split"])]
    sel["filename"] = [f"{i}.mp4" for i in sel["index"]]
    sel["in_pilot50"] = sel["index"].isin(pilot_indices or set())
    sel["fps"] = sel["fps_avg"]
    sel["source_relpath"] = sel["relpath"]
    report = {"pool_size": int(len(pool)), "pool_per_s1": pool["s1_split"].value_counts().to_dict(),
              "counts": sel["split"].value_counts().to_dict(), "unsupported_words": unsupported,
              "excluded_heldout_colour_family": sorted(int(i) for i in excluded_heldout),
              "minimal_pair_families_used": sorted(used_families), "targets": targets}
    order = {"train": 0, "val": 1, "test": 2}
    sel = sel.sort_values(["split", "index"], key=lambda c: c.map(order) if c.name == "split" else c).reset_index(drop=True)
    return sel, report, pool


def oov_stats(sel: pd.DataFrame) -> dict:
    """Share of val/test word tokens (and sentences) not in the train vocabulary."""
    train_vocab = {t for toks in sel.loc[sel["split"] == "train", "tokens"] for t in toks}
    out = {"train_vocabulary_size": len(train_vocab)}
    for sp in ("val", "test"):
        toks = [t for ts in sel.loc[sel["split"] == sp, "tokens"] for t in ts]
        sents = sel.loc[sel["split"] == sp, "tokens"]
        out[sp] = {"tokens": len(toks), "oov_tokens": sum(t not in train_vocab for t in toks),
                   "oov_token_rate": round(sum(t not in train_vocab for t in toks) / max(len(toks), 1), 4),
                   "types": len(set(toks)), "oov_types": len({t for t in toks if t not in train_vocab}),
                   "sentences": int(len(sents)),
                   "sentences_with_oov": int(sum(any(t not in train_vocab for t in ts) for ts in sents)),
                   "sentences_all_words_seen": int(sum(all(t in train_vocab for t in ts) for ts in sents))}
    return out
