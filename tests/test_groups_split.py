"""Leakage groups and split S1 on synthetic data."""

import pandas as pd

from bdsl.data.groups import assign_groups
from bdsl.data.split import assign_split, bucket, verify_no_leakage


def _frame(rows):
    return pd.DataFrame(rows, columns=["index", "sha256", "sentence_norm"])


def test_groups_join_sentence_sha_and_links():
    df = assign_groups(_frame([
        (1, "a", "s1"), (2, "b", "s1"),      # same sentence
        (3, "c", "s2"), (4, "c", "s2"),      # exact copy
        (5, "d", "s3"), (6, "e", "s4"),      # joined by a known link
        (7, "f", "s5"),
    ]), links=[[5, 6], [99]])               # 99 is absent and ignored
    g = dict(zip(df["index"], df["group_id"]))
    assert g[1] == g[2] == "g1" and g[3] == g[4] == "g3" and g[5] == g[6] == "g5" and g[7] == "g7"
    assert df.set_index("index").loc[4, "exact_dup_of"] == 3
    assert df["is_representative"].tolist() == [True, True, True, False, True, True, True]
    assert not df["label_conflict"].any()


def test_exact_copy_with_different_sentences_is_a_conflict():
    df = assign_groups(_frame([(1, "x", "s1"), (2, "x", "s2"), (3, "y", "s3")]))
    assert df["label_conflict"].tolist() == [True, True, False]
    split = assign_split(df, "salt", {"train": 80, "val": 10, "test": 10})
    assert split.loc[split["index"].isin([1, 2]), "split"].eq("excluded").all()


def test_split_is_deterministic_group_disjoint_and_close_to_ratios():
    rows = [(i, f"h{i}", f"s{i // 2}") for i in range(4000)]  # pairs share a sentence
    df = assign_groups(_frame(rows))
    a = assign_split(df, "S1-v0", {"train": 80, "val": 10, "test": 10})
    b = assign_split(df, "S1-v0", {"train": 80, "val": 10, "test": 10})
    assert a["split"].tolist() == b["split"].tolist()
    assert verify_no_leakage(a) == []
    share = a.groupby("group_id")["split"].first().value_counts(normalize=True)
    assert abs(share["train"] - 0.8) < 0.04 and abs(share["val"] - 0.1) < 0.03 and abs(share["test"] - 0.1) < 0.03
    assert bucket("S1-v0", "g0") == bucket("S1-v0", "g0") and 0 <= bucket("x", "y") < 100


def test_leakage_checker_catches_crossings():
    df = assign_groups(_frame([(1, "a", "s1"), (2, "b", "s1"), (3, "c", "s2"), (4, "d", "s3")]))
    split = assign_split(df, "salt", {"train": 80, "val": 10, "test": 10})
    split.loc[split["index"] == 2, "split"] = "test" if split.loc[0, "split"] != "test" else "train"
    problems = verify_no_leakage(split)
    assert any("group_id" in p for p in problems) and any("sentence_norm" in p for p in problems)
    split2 = assign_split(df, "salt", {"train": 80, "val": 10, "test": 10})
    split2["split"] = ["train", "train", "train", "test"]
    assert any("link" in p for p in verify_no_leakage(split2, links=[[3, 4]]))
