"""Leakage and consistency checks for kaggle/data (owner list, 2026-10-23). Each check prints PASS or FAIL.

    1  manifests agree        subset_manifest.csv = train + val + test manifests, split column = folder
    2  counts                 real counts per split (reported; FAIL only if a split is empty)
    3  no group crosses       a leakage group (same sentence / SHA-256 / known link, S1) is in one split
    4  no SHA-256 crosses     and no SHA-256 twice in the subset
    5  no sentence crosses    no normalised sentence in two splits (and none twice)
    6  no known link crosses  colour cluster 3456/3457/3458 (configs/base.yaml) stays in one split
    7  S1 partition kept      every clip is in the same partition as in S1 v0
    8  files match manifest   each videos/ folder holds exactly its manifest's files, SHA-256 equal
    9  no file in two folders same file name or SHA-256 in two split folders
   10  split lock             SPLIT_LOCK.json hashes match the manifests
Checks 8–10 need the copied videos / lock: they are SKIPPED without them, unless --require-videos.
"""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from bdsl.io import sha256_file

from .lock import check_lock

SPLITS = ("train", "val", "test")


def _read(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, dtype={"sha256": str, "sha256_copy": str, "sha256_source": str}, encoding="utf-8-sig",
                       keep_default_na=False)


def _crossing(df: pd.DataFrame, col: str) -> list:
    n = df.groupby(col)["split"].nunique()
    return n[n > 1].index.tolist()


def run_checks(root: Path, links: list[list[int]] | None, s1_csv: Path | None = None,
               require_videos: bool = False, hash_videos: bool = True) -> list[dict]:
    """root = folder that contains data/. Returns [{check, status, detail}]."""
    data = root / "data"
    res = []

    def add(name, ok, detail="", skip=False):
        res.append({"check": name, "status": "SKIP" if skip else ("PASS" if ok else "FAIL"), "detail": detail})

    sub = _read(data / "subset_manifest.csv")
    parts = {sp: _read(data / sp / f"{sp}_manifest.csv") for sp in SPLITS}
    union = pd.concat([p.assign(_folder=sp) for sp, p in parts.items()], ignore_index=True)
    same_rows = sorted(union["index"].astype(int)) == sorted(sub["index"].astype(int))
    folder_ok = (union["split"] == union["_folder"]).all()
    split_of = dict(zip(sub["index"].astype(int), sub["split"]))
    agree = all(split_of.get(int(i)) == s for i, s in zip(union["index"], union["split"]))
    add("1 manifests agree", same_rows and folder_ok and agree,
        f"{len(sub)} rows in subset_manifest; {len(union)} in the 3 split manifests")
    counts = sub["split"].value_counts().to_dict()
    add("2 counts", all(counts.get(sp, 0) > 0 for sp in SPLITS),
        ", ".join(f"{sp} {counts.get(sp, 0)}" for sp in SPLITS) + f" (total {len(sub)})")
    g = _crossing(sub, "group_id")
    add("3 no group crosses splits", not g, f"{sub['group_id'].nunique()} groups; crossing: {g[:5]}")
    h = _crossing(sub, "sha256")
    dup_h = sub["sha256"].duplicated().sum()
    add("4 no SHA-256 crosses splits", not h and not dup_h, f"crossing: {h[:3]}; duplicated in subset: {int(dup_h)}")
    s = _crossing(sub, "sentence_norm")
    dup_s = sub["sentence_norm"].duplicated().sum()
    add("5 no normalised sentence crosses splits", not s and not dup_s,
        f"crossing: {s[:3]}; duplicated in subset: {int(dup_s)}")
    bad_links, present = [], []
    for link in links or []:
        sps = {split_of[int(i)] for i in link if int(i) in split_of}
        if any(int(i) in split_of for i in link):
            present.append(f"{'/'.join(map(str, link))} → {sorted(sps)}")
        if len(sps) > 1:
            bad_links.append(link)
    add("6 no known shared-segment link crosses splits", not bad_links,
        "; ".join(present) or "no linked clip in the subset")
    moved = sub[sub["split"] != sub["s1_split"]]["index"].tolist()
    s1_detail = f"split == s1_split for all rows; moved: {moved[:5]}"
    if s1_csv is not None and Path(s1_csv).is_file():
        s1 = pd.read_csv(s1_csv)
        s1_of = dict(zip(s1["index"].astype(int), s1["split"]))
        moved += [int(i) for i, sp in split_of.items() if s1_of.get(int(i)) != sp]
        s1_detail = f"checked against {Path(s1_csv).name}; moved: {sorted(set(moved))[:5]}"
    add("7 S1 partition kept (no clip moved)", not moved, s1_detail)
    have_videos = all((data / sp / "videos").is_dir() and any((data / sp / "videos").glob("*.mp4")) for sp in SPLITS)
    if not have_videos and not require_videos:
        add("8 files match their manifest rows", True, "videos not present here", skip=True)
        add("9 no file in two folders", True, "videos not present here", skip=True)
    else:
        problems, seen_name, seen_hash = [], {}, {}
        for sp, man in parts.items():
            folder = data / sp / "videos"
            files = {f.name for f in folder.glob("*")} if folder.is_dir() else set()
            want = set(man["filename"])
            if files - want:
                problems.append(f"{sp}: extra files {sorted(files - want)[:3]}")
            if want - files:
                problems.append(f"{sp}: missing files {sorted(want - files)[:3]} ({len(want - files)} missing)")
            for r in man.to_dict("records"):
                f = folder / r["filename"]
                seen_name.setdefault(r["filename"], set()).add(sp)
                if not f.is_file():
                    continue
                if hash_videos:
                    hv = sha256_file(f)
                    seen_hash.setdefault(hv, set()).add(sp)
                    if hv != r["sha256"]:
                        problems.append(f"{sp}/{r['filename']}: SHA-256 differs from the manifest")
        add("8 files match their manifest rows", not problems,
            "; ".join(problems[:6]) or f"{len(union)} files, names and SHA-256 equal" + ("" if hash_videos else " (hash skipped)"))
        twice = [n for n, sps in seen_name.items() if len(sps) > 1] + [h[:12] for h, sps in seen_hash.items() if len(sps) > 1]
        on_disk = {}
        for sp in SPLITS:
            for f in (data / sp / "videos").glob("*.mp4") if (data / sp / "videos").is_dir() else []:
                on_disk.setdefault(f.name, set()).add(sp)
        twice += [n for n, sps in on_disk.items() if len(sps) > 1]
        add("9 no file in two folders", not twice, f"in two folders: {sorted(set(twice))[:5]}")
    lock_file = data / "SPLIT_LOCK.json"
    if not lock_file.is_file() and not require_videos:
        add("10 SPLIT_LOCK.json matches the manifests", True, "lock not written yet (written by the copy step)", skip=True)
    else:
        lp = check_lock(root)
        add("10 SPLIT_LOCK.json matches the manifests", not lp, "; ".join(lp) or "4 manifests match their locked hashes")
    return res


def format_results(res: list[dict]) -> str:
    w = max(len(r["check"]) for r in res)
    lines = [f"{r['status']:4s}  {r['check']:<{w}}  {r['detail']}" for r in res]
    n_fail = sum(r["status"] == "FAIL" for r in res)
    n_skip = sum(r["status"] == "SKIP" for r in res)
    lines.append(f"RESULT: {'FAIL' if n_fail else 'PASS'} ({len(res) - n_fail - n_skip} passed, {n_fail} failed, {n_skip} skipped)")
    return "\n".join(lines)


def overall(res: list[dict], require_videos: bool) -> bool:
    return not any(r["status"] == "FAIL" or (require_videos and r["status"] == "SKIP") for r in res)


def to_json(res: list[dict]) -> str:
    return json.dumps(res, indent=1, ensure_ascii=False)
