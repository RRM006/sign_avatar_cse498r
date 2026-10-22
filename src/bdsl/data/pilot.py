"""pilot50_v1 selection and copying (design doc 04 §F-6, ADR-0017/0018).

Selection is deterministic: every "random" choice is an ordering by SHA-256 of (seed, …), so the same
manifest, split and config always give the same 50 clips. The pilot is drawn from split S1, so pilot
test clips are real S1 test clips.

  1. core train  — minimal-pair families (same length, one word different): 4 train clips each;
  2. diversity train — indicative strata (question, negation, number/time, long, short, other);
  3. held-out    — per core family 1 val/test sibling (half of them val, half test), then the
                   diversity held-out slots. Chosen after all train clips, preferring sentences whose
                   words all occur in pilot train (a new combination of seen words) when
                   `heldout_prefer_in_vocab` is on (owner, 2026-10-22); otherwise the unseen words are
                   recorded. `heldout_fallback_pool` (off by default) lets a core slot take a
                   non-sibling val/test sentence made only of seen words.
  quotas — landscape and low-res minimums and every duration quartile; candidates that fill an unmet
           quota are preferred; an unmet quota is reported as a failure, never relaxed.

Copying writes to a temp name and renames, then checks each copy's SHA-256 against the manifest.
"""

from __future__ import annotations

import hashlib
import os
import shutil
from collections import defaultdict
from pathlib import Path

import pandas as pd

from ..io import sha256_file
from ..text.normalize import tokens
from ..text.tags import stratum


def hkey(*parts) -> str:
    return hashlib.sha256("|".join(str(p) for p in parts).encode("utf-8")).hexdigest()


def candidate_pool(manifest: pd.DataFrame, split_df: pd.DataFrame, pcfg: dict) -> pd.DataFrame:
    """One clip per normalised sentence: representative, decodable, no label conflict, in a split."""
    m = manifest.merge(split_df[["index", "split"]], on="index")
    m = m[m["is_representative"] & m["decode_ok"] & ~m["label_conflict"] & m["split"].isin(["train", "val", "test"])]
    m = m.assign(_order=[hkey(pcfg["seed"], "clip", i) for i in m["index"]]).sort_values("_order")
    m = m.drop_duplicates("sentence_norm", keep="first").copy()
    m["tokens"] = m["sentence_norm"].map(tokens)
    m["n_tokens"] = m["tokens"].map(len)
    m["stratum"] = m["tokens"].map(lambda t: stratum(t, pcfg["long_min_tokens"], pcfg["short_max_tokens"]))
    m["low_res"] = m[["display_w", "display_h"]].min(axis=1) < pcfg["low_res_short_side"]
    m["duration_quartile"] = pd.qcut(m["duration_s"], 4, labels=["q1", "q2", "q3", "q4"]).astype(str)
    return m.drop(columns="_order").set_index("index", drop=False)


def minimal_pair_families(pool: pd.DataFrame) -> dict[str, list[int]]:
    """Family key ("<length>|<pattern with _ at the differing slot>") → clip indices (≥ 2 members)."""
    fam = defaultdict(list)
    for i, toks in zip(pool["index"], pool["tokens"]):
        for pos in range(len(toks)):
            pattern = " ".join(toks[:pos] + ["_"] + toks[pos + 1:])
            fam[f"{len(toks)}|{pattern}"].append(int(i))
    return {k: v for k, v in fam.items() if len(v) >= 2}


class _Quotas:
    def __init__(self, q: dict, pool: pd.DataFrame):
        self.landscape_min = int(q["landscape_min"])
        self.low_res_min = int(q["low_res_min"])
        self.quartiles = set(pool["duration_quartile"]) if q.get("all_duration_quartiles") else set()
        self.landscape = self.low_res = 0
        self.seen_quartiles: set = set()

    def add(self, row):
        self.landscape += row["orientation"] == "landscape"
        self.low_res += bool(row["low_res"])
        self.seen_quartiles.add(row["duration_quartile"])

    def fills_unmet(self, row) -> bool:
        return bool((row["orientation"] == "landscape" and self.landscape < self.landscape_min)
                    or (row["low_res"] and self.low_res < self.low_res_min)
                    or (row["duration_quartile"] in self.quartiles - self.seen_quartiles))

    def unmet(self) -> list[str]:
        out = []
        if self.landscape < self.landscape_min:
            out.append(f"landscape {self.landscape} < {self.landscape_min}")
        if self.low_res < self.low_res_min:
            out.append(f"low_res {self.low_res} < {self.low_res_min}")
        missing = self.quartiles - self.seen_quartiles
        if missing:
            out.append(f"duration quartiles missing: {sorted(missing)}")
        return out


def select_pilot(manifest: pd.DataFrame, split_df: pd.DataFrame, pcfg: dict) -> tuple[pd.DataFrame, dict]:
    pool = candidate_pool(manifest, split_df, pcfg)
    seed = pcfg["seed"]
    prefer_iv = bool(pcfg.get("heldout_prefer_in_vocab", False))
    quotas = _Quotas(pcfg["quotas"], pool)
    chosen: dict[int, dict] = {}
    used_sentences: set = set()

    def take(i: int, part: str, reason: str, family: str = ""):
        row = pool.loc[i]
        chosen[i] = {"index": i, "part": part, "family": family, "reason": reason}
        used_sentences.add(row["sentence_norm"])
        quotas.add(row)

    def free(i: int) -> bool:
        return i not in chosen and pool.loc[i, "sentence_norm"] not in used_sentences

    # 1. Core train: 4 train members per family; the family must also have a free val or test sibling.
    families = minimal_pair_families(pool)
    ranked = sorted(families, key=lambda k: hkey(seed, "family", k))
    n_fam, per_fam = int(pcfg["core"]["families"]), int(pcfg["core"]["train_per_family"])
    core_slots = []  # (family id, family key)
    for slot in range(n_fam):
        for key in ranked:
            if key in (k for _, k in core_slots):
                continue
            members = sorted((i for i in families[key] if free(i)), key=lambda i: hkey(seed, "member", key, i))
            train = [i for i in members if pool.loc[i, "split"] == "train"][:per_fam]
            if len(train) == per_fam and any(pool.loc[i, "split"] in ("val", "test") for i in members):
                fid = f"F{slot + 1}"
                for i in train:
                    take(i, "core", f"{fid} train member of minimal-pair family '{key}'", fid)
                core_slots.append((fid, key))
                break
        else:
            raise RuntimeError(f"No eligible minimal-pair family for core slot {slot + 1} (needs {per_fam} train + 1 val/test)")

    # 2. Diversity train slots; quota-filling candidates are preferred.
    for stratum_name, n in pcfg["diversity_train"].items():
        for _ in range(int(n)):
            cands = [int(i) for i in pool.index[(pool["split"] == "train") & (pool["stratum"] == stratum_name)] if free(int(i))]
            if not cands:
                raise RuntimeError(f"No candidate left for diversity slot (train, {stratum_name})")
            best = min(cands, key=lambda i: (not quotas.fills_unmet(pool.loc[i]), hkey(seed, "div", i)))
            filled = " (fills an unmet quota)" if quotas.fills_unmet(pool.loc[best]) else ""
            take(best, "diversity", f"{stratum_name} (train){filled}")

    # 3. Held-out slots, chosen after all train clips so the pilot-train vocabulary is known.
    train_vocab = {t for i, c in chosen.items() for t in pool.loc[i, "tokens"]}

    def unseen(i: int) -> list[str]:
        return [t for t in pool.loc[i, "tokens"] if t not in train_vocab]

    def heldout_key(i: int, salt: str):
        return (prefer_iv and bool(unseen(i)), not quotas.fills_unmet(pool.loc[i]), hkey(seed, salt, i))

    def vocab_note(i: int) -> str:
        words = unseen(i)
        return "all words seen in pilot train" if not words else f"words unseen in pilot train: {' '.join(words)}"

    # Core held-out: one val/test sibling per family, split chosen per family so that the core gives
    # half of its held-out clips to val and half to test. Optional fallback (heldout_fallback_pool):
    # if a family has no sibling made only of seen words, take any free val/test sentence that is.
    fallback_pool = prefer_iv and bool(pcfg.get("heldout_fallback_pool", False))
    core_quota = {"val": n_fam // 2, "test": n_fam - n_fam // 2}

    def sibling_splits(key: str) -> set:
        return {pool.loc[i, "split"] for i in families[key] if pool.loc[i, "split"] in ("val", "test") and free(i)}

    # Families whose siblings sit in only one held-out split choose first, so they are not starved.
    for fid, key in sorted(core_slots, key=lambda s: (len(sibling_splits(s[1])), s[0])):
        allowed = [s for s, n in core_quota.items() if n > 0]
        cands = [i for i in families[key] if pool.loc[i, "split"] in allowed and free(i)]
        if not cands:
            raise RuntimeError(f"{fid}: no free {'/'.join(allowed)} sibling left in family '{key}'")
        best = min(cands, key=lambda i: heldout_key(i, f"member|{key}"))
        sp = pool.loc[best, "split"]
        take(best, "core", f"{fid} held-out ({sp}): differs from its train siblings by one word; {vocab_note(best)}", fid)
        core_quota[sp] -= 1
    if fallback_pool:
        # Swap a core held-out sibling that has unseen words for a free sentence of the SAME split made
        # only of pilot-train words (keeps the val/test balance); counts are rebuilt below.
        for i in [i for i, c in list(chosen.items()) if c["part"] == "core" and pool.loc[i, "split"] != "train" and unseen(i)]:
            sp, fid = pool.loc[i, "split"], chosen[i]["family"]
            alts = [int(j) for j in pool.index[pool["split"] == sp] if free(int(j)) and not unseen(int(j))]
            if alts:
                alt = min(alts, key=lambda j: heldout_key(j, f"pool|{fid}"))
                del chosen[i]
                used_sentences.discard(pool.loc[i, "sentence_norm"])
                take(alt, "core", f"{fid} held-out ({sp}): replaces a family sibling with unseen words; "
                                  f"not a family sibling, a new combination of pilot-train words", fid)
    for split_name, stratum_name in pcfg["diversity_heldout"]:
        cands = [int(i) for i in pool.index[(pool["split"] == split_name) & (pool["stratum"] == stratum_name)] if free(int(i))]
        if not cands:
            raise RuntimeError(f"No candidate left for diversity slot ({split_name}, {stratum_name})")
        best = min(cands, key=lambda i: heldout_key(i, "div"))
        take(best, "diversity", f"{stratum_name} ({split_name}); {vocab_note(best)}")

    quotas = _Quotas(pcfg["quotas"], pool)  # recount from the final choice (swaps may have changed it)
    for i in chosen:
        quotas.add(pool.loc[i])
    sel = pd.DataFrame(chosen.values()).merge(
        pool.reset_index(drop=True)[["index", "split", "stratum", "sentence_norm", "sentence_raw", "n_tokens", "orientation",
                                     "display_w", "display_h", "low_res", "duration_s", "duration_quartile", "fps_avg",
                                     "sha256", "relpath"]],
        on="index")
    sel["hard"] = sel["low_res"] | (sel["orientation"] == "landscape")
    sel["unseen_in_pilot_train"] = [" ".join(unseen(int(i))) if sp != "train" else "" for i, sp in zip(sel["index"], sel["split"])]
    order = {"train": 0, "val": 1, "test": 2}
    sel = sel.sort_values(["split", "part", "family", "index"], key=lambda c: c.map(order) if c.name == "split" else c)
    sel = sel.reset_index(drop=True)

    expected = {k: int(v) for k, v in pcfg["counts"].items()}
    got = sel["split"].value_counts().to_dict()
    heldout = sel[sel["split"] != "train"]
    report = {
        "counts": got,
        "counts_ok": all(got.get(k, 0) == v for k, v in expected.items()) and len(sel) == sum(expected.values()),
        "unique_index": bool(sel["index"].is_unique),
        "unique_sentence": bool(sel["sentence_norm"].is_unique),
        "quotas_unmet": quotas.unmet(),
        "landscape": int((sel["orientation"] == "landscape").sum()),
        "low_res": int(sel["low_res"].sum()),
        "hard_share": round(float(sel["hard"].mean()), 3),
        "duration_quartiles": sel["duration_quartile"].value_counts().sort_index().to_dict(),
        "heldout_prefer_in_vocab": prefer_iv,
        "heldout_all_words_seen": int((heldout["unseen_in_pilot_train"] == "").sum()),
        "heldout_total": int(len(heldout)),
        "strata": sel.groupby(["split", "stratum"]).size().rename("n").reset_index().to_dict("records"),
        "heldout_fallback_pool": fallback_pool,
        "families": [k for _, k in core_slots],
        "pool_size": int(len(pool)),
    }
    report["ok"] = report["counts_ok"] and report["unique_index"] and report["unique_sentence"] and not report["quotas_unmet"]
    return sel, report


def copy_pilot(selection: pd.DataFrame, data_root: Path, dest_videos: Path, log=print) -> list[dict]:
    """Copy selected clips (temp file + rename) and verify SHA-256 against the manifest value."""
    dest_videos.mkdir(parents=True, exist_ok=True)
    results = []
    for row in selection.to_dict("records"):
        i, expected = int(row["index"]), row["sha256"]
        src = data_root / row["relpath"]
        dst = dest_videos / f"{i}.mp4"
        if dst.exists() and sha256_file(dst) == expected:
            results.append({"index": i, "copied": False, "sha256_ok": True})
            continue
        tmp = dst.with_name(f".{dst.name}.{os.getpid()}.tmp")
        try:
            shutil.copy2(src, tmp)
            os.replace(tmp, dst)
        finally:
            if tmp.exists():
                tmp.unlink()
        ok = sha256_file(dst) == expected == sha256_file(src)
        results.append({"index": i, "copied": True, "sha256_ok": ok})
        if not ok:
            log(f"SHA-256 mismatch for {i}")
    return results
