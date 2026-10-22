"""Gloss annotation files: schema, validation, and the guard that protects human reviews (ADR-0015).

Statuses: auto_draft (G0 output, nobody checked it) → team_reviewed (a registered team reviewer
checked it against the clip) → expert_validated (a registered BdSL-competent reviewer) or rejected.
Reviewers appear only as codes registered by the owner in REVIEWERS.csv; the AI never registers a
reviewer and never sets a reviewed status. Mock rows (is_mock=true) are refused in real files.
CSV files are UTF-8 with a BOM so spreadsheet programs show Bangla correctly.
"""

from __future__ import annotations

import re
from datetime import date
from pathlib import Path

import pandas as pd

from ..io import atomic_write_bytes
from .gloss_rules import g0
from .normalize import NORM_VER, normalize

COLUMNS = [
    "index", "split", "sentence_raw", "sentence_norm", "norm_ver", "g0_ver", "gloss_auto", "tags_auto",
    "gloss_reviewed", "tags_reviewed", "tense_note", "status", "annotator_id", "reviewer_id", "review_date",
    "confidence", "notes", "is_mock",
]
STATUSES = ("auto_draft", "team_reviewed", "expert_validated", "rejected")
REVIEWED = ("team_reviewed", "expert_validated")
REVIEWER_COLUMNS = ["reviewer_id", "role", "assigned_by", "assigned_date", "notes"]
ROLES = ("team", "expert")
CONFIDENCE = ("low", "med", "high")
_CODE = re.compile(r"^[A-Za-z0-9-]{1,12}$")
# Notes that say a reviewed row was not checked against its clip. Such rows are test data.
_UNVERIFIED = re.compile(r"not video-verified|video not checked|test data", re.IGNORECASE)


def read_csv(path: str | Path) -> pd.DataFrame:
    return pd.read_csv(path, dtype=str, keep_default_na=False, encoding="utf-8-sig")


def write_csv(df: pd.DataFrame, path: str | Path) -> Path:
    text = df.to_csv(index=False, lineterminator="\n")
    return atomic_write_bytes(path, ("﻿" + text).encode("utf-8"))


def any_reviewed(df: pd.DataFrame) -> bool:
    """True if any row carries human work (a non-draft status or a reviewed gloss)."""
    return bool((df["status"] != "auto_draft").any() or (df["gloss_reviewed"].str.strip() != "").any())


def build_drafts(pilot: pd.DataFrame, corpus: set[str], g0_ver: str) -> tuple[pd.DataFrame, dict]:
    """One auto_draft row per pilot clip, plus a count of tokens per G0 rule."""
    rows, rule_counts = [], {}
    for r in pilot.sort_values("index").to_dict("records"):
        norm = normalize(r["sentence_raw"])
        gloss, tags, rules = g0(norm, corpus)
        for rule in rules:
            rule_counts[rule] = rule_counts.get(rule, 0) + 1
        rows.append({
            "index": str(int(r["index"])), "split": r["split"], "sentence_raw": r["sentence_raw"], "sentence_norm": norm,
            "norm_ver": NORM_VER, "g0_ver": g0_ver, "gloss_auto": gloss, "tags_auto": tags, "gloss_reviewed": "",
            "tags_reviewed": "", "tense_note": "", "status": "auto_draft", "annotator_id": f"auto:{g0_ver}",
            "reviewer_id": "", "review_date": "", "confidence": "", "notes": "", "is_mock": "false",
        })
    return pd.DataFrame(rows, columns=COLUMNS), dict(sorted(rule_counts.items()))


def validate_reviewers(rev: pd.DataFrame) -> list[str]:
    problems = []
    if list(rev.columns) != REVIEWER_COLUMNS:
        return [f"REVIEWERS.csv columns must be {REVIEWER_COLUMNS}, got {list(rev.columns)}"]
    if rev["reviewer_id"].duplicated().any():
        problems.append("duplicate reviewer_id in REVIEWERS.csv")
    for r in rev.to_dict("records"):
        if not _CODE.match(r["reviewer_id"]) or r["reviewer_id"].upper() == "MOCK":
            problems.append(f"reviewer code {r['reviewer_id']!r} is not a valid code")
        if r["role"] not in ROLES:
            problems.append(f"reviewer {r['reviewer_id']!r}: role must be one of {ROLES}")
    return problems


def _valid_date(s: str) -> bool:
    try:
        return date.fromisoformat(s) <= date.today()
    except ValueError:
        return False


def is_test_data(df: pd.DataFrame) -> pd.Series:
    """True for a mock row, or a reviewed row whose notes say the clip was not checked."""
    unverified = df["notes"].str.contains(_UNVERIFIED, regex=True)
    return (df["is_mock"] == "true") | (df["status"].isin(REVIEWED) & unverified)


def validate(df: pd.DataFrame, reviewers: pd.DataFrame, allowed_indices: set[int] | None = None,
             allow_test_data: bool = False) -> list[str]:
    """All problems found (empty list = valid). Real annotation files only: mock rows and reviewed rows
    whose notes say "not video-verified" are refused. allow_test_data=True accepts them for a TEST run
    only; never use it for real results."""
    if list(df.columns) != COLUMNS:
        return [f"columns must be {COLUMNS}, got {list(df.columns)}"]
    problems = validate_reviewers(reviewers)
    roles = dict(zip(reviewers["reviewer_id"], reviewers["role"])) if not problems else {}
    if df["index"].duplicated().any():
        problems.append("duplicate index values")
    for r in df.to_dict("records"):
        i = r["index"]
        where = f"row {i}"
        if not i.isdigit() or (allowed_indices is not None and int(i) not in allowed_indices):
            problems.append(f"{where}: index not in the pilot manifest")
        if r["sentence_norm"] != normalize(r["sentence_raw"]) or r["norm_ver"] != NORM_VER:
            problems.append(f"{where}: sentence_norm/norm_ver does not match {NORM_VER}(sentence_raw)")
        if r["status"] not in STATUSES:
            problems.append(f"{where}: status {r['status']!r} not in {STATUSES}")
        if r["is_mock"] not in ("true", "false"):
            problems.append(f"{where}: is_mock must be true or false")
        elif r["is_mock"] == "true" and not allow_test_data:
            problems.append(f"{where}: mock row in a real annotation file")
        if r["status"] in REVIEWED and _UNVERIFIED.search(r["notes"]) and not allow_test_data:
            problems.append(f"{where}: notes say the row is test data / not video-verified")
        if r["status"] == "auto_draft":
            if r["reviewer_id"] or r["review_date"] or r["confidence"]:
                problems.append(f"{where}: auto_draft row must not have reviewer fields")
            continue
        role = roles.get(r["reviewer_id"])
        if role is None:
            problems.append(f"{where}: reviewer {r['reviewer_id']!r} is not registered in REVIEWERS.csv")
        elif r["status"] == "expert_validated" and role != "expert":
            problems.append(f"{where}: expert_validated needs a reviewer registered with role 'expert'")
        if not _valid_date(r["review_date"]):
            problems.append(f"{where}: review_date must be a past or present YYYY-MM-DD date")
        if r["status"] in REVIEWED:
            if not r["gloss_reviewed"].strip():
                problems.append(f"{where}: {r['status']} row needs gloss_reviewed")
            if r["confidence"] not in CONFIDENCE:
                problems.append(f"{where}: confidence must be one of {CONFIDENCE}")
        if r["status"] == "rejected" and not r["notes"].strip():
            problems.append(f"{where}: rejected row needs a note saying why")
    return problems


def usable_for_training(df: pd.DataFrame, allow_test_data: bool = False) -> pd.DataFrame:
    """Rows a model may learn from: reviewed by a person and not test data (design doc 04 §F-10).
    allow_test_data=True also returns test rows, for a TEST run only."""
    keep = df["status"].isin(REVIEWED)
    if not allow_test_data:
        keep &= ~is_test_data(df)
    return df[keep]
