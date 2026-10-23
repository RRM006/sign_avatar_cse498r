"""kaggle400: the 400-video Kaggle experiment (owner-approved 2026-10-23; folder `kaggle/`).

Layout (paths from configs/data/kaggle400.yaml, overridable with K400_DATA_ROOT / K400_STATE_ROOT):

    <k400_data_root>/data/{train,val,test}/{<split>_manifest.csv, videos/}
    <k400_data_root>/data/subset_manifest.csv, SPLIT_LOCK.json
    <k400_state_root>/processed/features/<split>/<Index>.npz
    <k400_state_root>/processed/glosses/gloss_g0_<split>.csv
    <k400_state_root>/outputs/{runs,eval,predictions,tables,figures,avatar}/, registry.csv

Which split is used for what (owner rule, 2026-10-23):
    train  fit weights, build vocabularies, feature standardisation, B0/B1 sources
    val    early stopping, choosing epochs / learning rate / ablations, error analysis
    test   locked: read ONCE, by `evaluate --final`, after the configuration is frozen

The guard below makes the last rule hard to break by accident: every reader of split rows takes the
split name, and reading `test` raises `TestSplitLocked` unless the caller is inside
`final_test_access()`, which only the final evaluation enters.
"""

from __future__ import annotations

import hashlib
import json
from contextlib import contextmanager
from pathlib import Path

import pandas as pd

from ..io import sha256_text_canonical
from ..text.normalize import NORM_VER, normalize

SPLITS = ("train", "val", "test")
TRAINING_SPLITS = ("train", "val")
LOCK_FILE = "SPLIT_LOCK.json"
FINAL_LOCK_FILE = "FINAL_TEST_LOCK.json"
MODEL_INPUT_COLUMNS = ["index", "split", "sentence_raw", "sentence_norm", "norm_ver", "g0_ver", "gloss_auto",
                       "tags_auto"]
_final_access = {"on": False, "reason": None}


class TestSplitLocked(PermissionError):
    """Raised when anything except the final evaluation tries to read test rows."""


class SplitLockError(RuntimeError):
    pass


@contextmanager
def final_test_access(reason: str):
    """Only `evaluate --final` (and the post-lock avatar export) may enter this context."""
    if not reason:
        raise ValueError("final_test_access needs a reason")
    old = dict(_final_access)
    _final_access.update(on=True, reason=reason)
    try:
        yield
    finally:
        _final_access.update(old)


def _guard(split: str) -> None:
    if split not in SPLITS:
        raise ValueError(f"unknown split {split!r}")
    if split == "test" and not _final_access["on"]:
        raise TestSplitLocked("The test split is locked: only `evaluate --final` reads it (owner rule, 2026-10-23).")


def paths(cfg: dict) -> dict:
    """Every kaggle400 path, from the config (no machine-specific path in code)."""
    d = Path(cfg["paths"]["k400_data_root"]) / "data"
    s = Path(cfg["paths"]["k400_state_root"])
    out = s / "outputs"
    return {
        "data_dir": d, "lock": d / LOCK_FILE, "subset_manifest": d / "subset_manifest.csv",
        "manifest": {sp: d / sp / f"{sp}_manifest.csv" for sp in SPLITS},
        "videos": {sp: d / sp / "videos" for sp in SPLITS},
        "state_root": s, "features": {sp: s / "processed" / "features" / sp for sp in SPLITS},
        "glosses": {sp: s / "processed" / "glosses" / f"gloss_g0_{sp}.csv" for sp in SPLITS},
        "vocab_dir": s / "processed" / "vocab", "qc_dir": s / "processed" / "qc",
        "outputs": out, "runs": out / "runs", "eval": out / "eval", "predictions": out / "predictions",
        "tables": out / "tables", "figures": out / "figures", "avatar": out / "avatar",
        "registry": out / "registry.csv", "frozen": out / "frozen_config.json", "final_lock": out / FINAL_LOCK_FILE,
    }


def check_split_lock(cfg: dict, splits: tuple[str, ...] = TRAINING_SPLITS) -> dict:
    """Compare the manifests of `splits` with SPLIT_LOCK.json (line-ending independent hashes); raises
    SplitLockError. Training checks train + val only, so it never opens a file holding test rows; the lock
    file itself (whose hash every run records) covers all four manifests, and verify_split.py, notebook 01
    and `evaluate --final` check every locked file."""
    p = paths(cfg)
    if not p["lock"].is_file():
        raise SplitLockError(f"{p['lock']} is missing: run the copy step (kaggle/tools/run_local_steps.ps1) first.")
    lock = json.loads(p["lock"].read_text(encoding="utf-8"))
    if "test" in splits:
        _guard("test")
    wanted = {f"data/{sp}/{sp}_manifest.csv" for sp in splits} | ({"data/subset_manifest.csv"} if "test" in splits else set())
    missing_in_lock = wanted - set(lock["files"])
    problems = [f"{rel}: not listed in SPLIT_LOCK.json" for rel in sorted(missing_in_lock)]
    for rel, expected in lock["files"].items():
        if rel not in wanted:
            continue
        f = p["data_dir"].parent / rel
        if not f.is_file():
            problems.append(f"{rel}: missing")
        elif sha256_text_canonical(f) != expected:
            problems.append(f"{rel}: changed since SPLIT_LOCK.json was written")
    if problems:
        raise SplitLockError("Training refuses to run: " + "; ".join(problems))
    return {"lock_sha256": sha256_text_canonical(p["lock"]), "created_utc": lock.get("created_utc"),
            "counts": lock.get("counts")}


def read_split_manifest(cfg: dict, split: str) -> pd.DataFrame:
    _guard(split)
    return pd.read_csv(paths(cfg)["manifest"][split], dtype={"sha256": str, "index": int}, encoding="utf-8-sig")


def read_g0(cfg: dict, split: str) -> pd.DataFrame:
    _guard(split)
    return pd.read_csv(paths(cfg)["glosses"][split], dtype=str, keep_default_na=False, encoding="utf-8-sig")


def link_groups(cfg: dict) -> dict[int, int]:
    """Index → known shared-segment link number (colour cluster, ADR-0018)."""
    out = {}
    for n, link in enumerate(cfg["split"].get("known_shared_segment_links") or []):
        for i in link:
            out[int(i)] = n
    return out


def model_inputs(cfg: dict, splits: tuple[str, ...], feat_ver: str,
                 require_features: bool = True) -> tuple[pd.DataFrame, list[str], str]:
    """Rows for Model A / Model B from the G0 files of `splits`, joined to the split manifests and the
    feature files. Returns (rows, problems, SHA-256 of the rows). Never touches a split not asked for."""
    from ..features.layout import read_meta

    p = paths(cfg)
    links = link_groups(cfg)
    frames, problems = [], []
    for sp in splits:
        man = read_split_manifest(cfg, sp)
        g = read_g0(cfg, sp)
        if sorted(g["index"].astype(int)) != sorted(man["index"]):
            problems.append(f"{sp}: gloss_g0_{sp}.csv rows do not match {sp}_manifest.csv")
            continue
        m = g.merge(man[["index", "sha256", "group_id"]].astype({"index": str}), on="index", how="left")
        for r in m.to_dict("records"):
            where = f"{sp} row {r['index']}"
            if r["split"] != sp:
                problems.append(f"{where}: split column says {r['split']!r}")
            if r["g0_ver"] != cfg["annotations"]["g0_ver"]:
                problems.append(f"{where}: g0_ver {r['g0_ver']!r} is not {cfg['annotations']['g0_ver']!r}")
            if r["sentence_norm"] != normalize(r["sentence_raw"]) or r["norm_ver"] != NORM_VER:
                problems.append(f"{where}: sentence_norm does not match {NORM_VER}")
            if r["status"] != "auto_draft" or r.get("gloss_reviewed", "") or r.get("is_mock", "false") != "false":
                problems.append(f"{where}: G0 file rows must be untouched auto_draft rows")
            if require_features:
                meta = read_meta(p["features"][sp] / f"{r['index']}.npz")
                if not meta or meta.get("feat_ver") != feat_ver:
                    problems.append(f"{where}: no features with feat_ver {feat_ver}")
        m["feature_path"] = [str(p["features"][sp] / f"{i}.npz") for i in m["index"]]
        m["link_group"] = [links.get(int(i), -1) for i in m["index"]]
        frames.append(m)
    df = pd.concat(frames, ignore_index=True) if frames else pd.DataFrame(columns=MODEL_INPUT_COLUMNS)
    cols = MODEL_INPUT_COLUMNS + ["sha256", "group_id", "link_group"]
    text = df[[c for c in cols if c in df]].sort_values("index", key=lambda s: s.astype(int)).to_csv(
        index=False, lineterminator="\n")
    return df, problems, hashlib.sha256(text.encode("utf-8")).hexdigest()


def glosses_sha256(cfg: dict, splits: tuple[str, ...]) -> str:
    """One hash over the G0 files of `splits` (line-ending independent)."""
    p = paths(cfg)
    for sp in splits:
        _guard(sp)
    joined = "|".join(f"{sp}:{sha256_text_canonical(p['glosses'][sp])}" for sp in splits)
    return hashlib.sha256(joined.encode("utf-8")).hexdigest()
