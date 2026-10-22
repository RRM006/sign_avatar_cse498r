"""Leakage groups (ADR-0018).

Clips end up in one group if they share a normalised sentence, a SHA-256 (exact copy), or a known
shared-segment link. A whole group always goes to one split. Exact copies with *different*
normalised sentences are label conflicts: flagged and kept out of every split until resolved.
"""

from __future__ import annotations

from collections import defaultdict

import pandas as pd


class _UnionFind:
    def __init__(self, items):
        self.parent = {i: i for i in items}

    def find(self, i):
        while self.parent[i] != i:
            self.parent[i] = self.parent[self.parent[i]]
            i = self.parent[i]
        return i

    def union(self, a, b):
        ra, rb = self.find(a), self.find(b)
        if ra != rb:
            self.parent[max(ra, rb)] = min(ra, rb)  # the smallest Index becomes the root


def assign_groups(df: pd.DataFrame, links: list[list[int]] | None = None) -> pd.DataFrame:
    """Add group_id, exact_dup_of, is_representative and label_conflict to a manifest frame.

    Needs columns: index, sha256, sentence_norm.
    """
    out = df.copy()
    idx = [int(i) for i in out["index"]]
    uf = _UnionFind(idx)
    for col in ("sentence_norm", "sha256"):
        for _, members in out.groupby(col)["index"]:
            members = [int(m) for m in members]
            for m in members[1:]:
                uf.union(members[0], m)
    present = set(idx)
    for link in links or []:
        link = [int(i) for i in link if int(i) in present]
        for m in link[1:]:
            uf.union(link[0], m)
    out["group_id"] = [f"g{uf.find(i)}" for i in idx]

    first_by_sha = out.groupby("sha256")["index"].transform("min").astype(int)
    out["exact_dup_of"] = [None if f == i else int(f) for i, f in zip(idx, first_by_sha)]
    out["exact_dup_of"] = out["exact_dup_of"].astype("Int64")
    out["is_representative"] = out["exact_dup_of"].isna()

    sentences_per_sha = out.groupby("sha256")["sentence_norm"].transform("nunique")
    out["label_conflict"] = sentences_per_sha > 1
    return out


def known_link_members(links: list[list[int]] | None) -> dict[int, int]:
    """Index → link number, for leakage checks."""
    member = {}
    for n, link in enumerate(links or []):
        for i in link:
            member[int(i)] = n
    return member


def group_sizes(df: pd.DataFrame) -> dict[int, int]:
    """How many groups have each size (size → count)."""
    counts = defaultdict(int)
    for size in df.groupby("group_id").size():
        counts[int(size)] += 1
    return dict(sorted(counts.items()))
