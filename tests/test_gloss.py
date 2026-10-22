"""G0 v0.1 rules, annotation validation and the overwrite guard."""

import unicodedata

import pandas as pd
import pytest

from bdsl.text.annotations import (COLUMNS, REVIEWER_COLUMNS, any_reviewed, build_drafts, read_csv,
                                   usable_for_training, validate, write_csv)
from bdsl.text.gloss_rules import g0, gloss_token
from bdsl.text.normalize import normalize

N = normalize


def nfc(s):
    """Expected outputs contain `?`/`~`, which norm_v1 would strip: compare in NFC only."""
    return unicodedata.normalize("NFC", s)

CORPUS = {N(w) for w in ("খালা", "মা", "ভাই", "আমি", "যাব")}


@pytest.mark.parametrize("tok, gloss, tags, rule", [
    ("আমার", "আমার", set(), "R0"),
    ("না", "NOT", {"neg"}, "R1"),
    ("নয়", "NOT.BE", {"neg"}, "R1"),
    ("নেই", "NOT.HAVE", {"neg"}, "R1"),
    ("নি", "NOT?", {"neg"}, "R1"),
    ("কোথায়", "কোথায়", {"q-wh"}, "R2"),
    ("কি", "কি", {"q?"}, "R2b"),
    ("৩টায়", "NUM(৩টায়)?", set(), "R3"),
    ("C", "FS(C)?", set(), "R4"),
    ("খালার", "খালা~", set(), "R5"),
    ("মায়ের", "মা~", set(), "R5"),
    ("ফুফুর", "ফুফুর?", set(), "R6"),      # stem not in this corpus → not stripped
    ("ভোর", "ভোর?", set(), "R6"),          # stem "ভো" not a word → not stripped
    ("অস্ট্রেলিয়া", "অস্ট্রেলিয়া?", set(), "R6"),
])
def test_gloss_token_rules(tok, gloss, tags, rule):
    assert gloss_token(N(tok), CORPUS) == (nfc(gloss), tags, rule)


def test_g0_keeps_order_and_is_deterministic():
    s = N("সব সময় ঝগড়া ভালো না")
    a = g0(s, CORPUS)
    assert a == g0(s, CORPUS)
    assert a[0] == nfc("সব? সময়? ঝগড়া? ভালো? NOT") and a[1] == "neg"
    assert g0(N("তোমার প্রিয় রং কি"), CORPUS)[1] == "q?"


def _drafts():
    pilot = pd.DataFrame({"index": [5, 3], "split": ["train", "test"],
                          "sentence_raw": ["আমি যাব না।", "খালার  রান্না"]})
    df, counts = build_drafts(pilot, CORPUS, "G0-v0.1")
    return df, counts


def _reviewers(rows=()):
    return pd.DataFrame(list(rows), columns=REVIEWER_COLUMNS)


def test_drafts_are_valid_auto_drafts():
    df, counts = _drafts()
    assert list(df.columns) == COLUMNS and df["index"].tolist() == ["3", "5"]
    assert (df["status"] == "auto_draft").all() and (df["is_mock"] == "false").all()
    assert counts == {"R0": 1, "R1": 1, "R5": 1, "R6": 2}
    assert validate(df, _reviewers(), {3, 5}) == []
    assert not any_reviewed(df) and usable_for_training(df).empty


def _reviewed(df, status="team_reviewed", reviewer="T1", **kw):
    df = df.copy()
    df.loc[0, ["status", "gloss_reviewed", "reviewer_id", "review_date", "confidence"]] = \
        [status, "খালা রান্না", reviewer, "2026-10-22", "med"]
    for k, v in kw.items():
        df.loc[0, k] = v
    return df


def test_reviewed_rows_need_a_registered_reviewer():
    df, _ = _drafts()
    team = _reviewers([("T1", "team", "owner", "2026-10-22", "")])
    assert validate(_reviewed(df), team, {3, 5}) == []
    assert len(usable_for_training(_reviewed(df))) == 1
    assert any("not registered" in p for p in validate(_reviewed(df), _reviewers(), {3, 5}))
    assert any("expert" in p for p in validate(_reviewed(df, "expert_validated"), team, {3, 5}))
    assert any("gloss_reviewed" in p for p in validate(_reviewed(df, gloss_reviewed=""), team, {3, 5}))
    assert any("review_date" in p for p in validate(_reviewed(df, review_date="2999-01-01"), team, {3, 5}))
    assert any("not a valid code" in p for p in validate(df, _reviewers([("MOCK", "team", "", "", "")]), {3, 5}))


@pytest.mark.parametrize("column, value, expected", [
    ("is_mock", "true", "mock row"),
    ("sentence_norm", "বদলানো", "sentence_norm"),
    ("status", "done", "status"),
    ("reviewer_id", "T1", "must not have reviewer fields"),
    ("index", "999", "not in the pilot manifest"),
])
def test_invalid_rows_are_rejected(column, value, expected):
    df, _ = _drafts()
    df.loc[0, column] = value
    assert any(expected in p for p in validate(df, _reviewers(), {3, 5}))


def test_rejected_needs_a_note_and_guard_detects_human_work(tmp_path):
    df, _ = _drafts()
    team = _reviewers([("T1", "team", "owner", "2026-10-22", "")])
    rej = _reviewed(df, "rejected", gloss_reviewed="")
    assert any("note" in p for p in validate(rej, team, {3, 5}))
    assert any_reviewed(rej)
    only_gloss = df.copy()
    only_gloss.loc[1, "gloss_reviewed"] = "x"
    assert any_reviewed(only_gloss)
    path = write_csv(df, tmp_path / "a.csv")
    assert path.read_bytes().startswith(b"\xef\xbb\xbf")
    assert read_csv(path).equals(df)


def test_cli_refuses_to_overwrite_reviewed_file(tmp_path, monkeypatch):
    import bdsl.cli as cli

    df, _ = _drafts()
    reviewed = _reviewed(df)
    target = write_csv(reviewed, tmp_path / "pilot.csv")
    before = target.read_bytes()
    monkeypatch.setattr(cli, "_annotation_paths", lambda cfg: (target, tmp_path / "REVIEWERS.csv"))
    assert cli.main(["gloss-draft", "--data", "pilot50"]) == 2
    assert target.read_bytes() == before
