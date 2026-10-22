"""Split S1 (ADR-0018): group-disjoint train/val/test assigned by a hash of the group key.

A group's bucket depends only on (salt, group_id), so the assignment is reproducible and adding new
clips never moves existing groups. Label-conflict groups are put in "excluded".
"""

from __future__ import annotations

import hashlib

import pandas as pd

from ..text.normalize import tokens
from ..text.tags import is_negation, is_question, length_bucket
from .groups import known_link_members


def bucket(salt: str, key: str) -> int:
    return int(hashlib.sha256(f"{salt}|{key}".encode("utf-8")).hexdigest(), 16) % 100


def assign_split(df: pd.DataFrame, salt: str, ratios: dict[str, int]) -> pd.DataFrame:
    if sum(ratios.values()) != 100:
        raise ValueError(f"split ratios must sum to 100, got {ratios}")
    t, v = ratios["train"], ratios["val"]

    def split_of(b: int) -> str:
        return "train" if b < t else ("val" if b < t + v else "test")

    out = df[["index", "group_id", "sha256", "sentence_norm", "label_conflict"]].copy()
    conflict_groups = set(out.loc[out["label_conflict"], "group_id"])
    out["split"] = [
        "excluded" if g in conflict_groups else split_of(bucket(salt, g)) for g in out["group_id"]
    ]
    return out


def verify_no_leakage(split_df: pd.DataFrame, links: list[list[int]] | None = None) -> list[str]:
    """Problems found (empty list = no leakage). Excluded rows are ignored."""
    s = split_df[split_df["split"] != "excluded"]
    problems = []
    for col in ("group_id", "sha256", "sentence_norm"):
        crossing = s.groupby(col)["split"].nunique()
        crossing = crossing[crossing > 1]
        if len(crossing):
            problems.append(f"{len(crossing)} {col} value(s) appear in more than one split, e.g. {crossing.index[0]!r}")
    member = known_link_members(links)
    by_link: dict[int, set] = {}
    for i, sp in zip(s["index"], s["split"]):
        if int(i) in member:
            by_link.setdefault(member[int(i)], set()).add(sp)
    for n, splits in by_link.items():
        if len(splits) > 1:
            problems.append(f"known shared-segment link {n} crosses splits {sorted(splits)}")
    return problems


def balance_report(manifest: pd.DataFrame, split_df: pd.DataFrame, low_res_short_side: int) -> dict:
    """Counts per split for several strata, over representative clips (exact copies counted once)."""
    m = manifest.merge(split_df[["index", "split"]], on="index")
    m = m[m["is_representative"]]
    toks = m["sentence_norm"].map(tokens)
    short_side = m[["display_w", "display_h"]].min(axis=1)
    strata = {
        "length_tokens": toks.map(lambda t: length_bucket(len(t))),
        "question_indicative": toks.map(is_question),
        "negation_indicative": toks.map(is_negation),
        "orientation": m["orientation"],
        "resolution": short_side.map(lambda s: f"low(<{low_res_short_side})" if s < low_res_short_side
                                     else ("720" if s < 800 else ("1080" if s < 1200 else "higher"))),
    }
    report = {"clips": m["split"].value_counts().to_dict(),
              "groups": m.groupby("split")["group_id"].nunique().to_dict()}
    for name, values in strata.items():
        table = pd.crosstab(values, m["split"])
        report[name] = {str(k): {str(c): int(v) for c, v in row.items()} for k, row in table.iterrows()}
    return report
