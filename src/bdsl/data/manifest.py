"""Manifest v1: one row per Index of FinalSheet2.xlsx, with file hash, header data and leakage groups.

Safety:
  * videos and the sheet are only read; size + mtime of every video and the sheet's SHA-256 are
    recorded before and after, and the run fails if anything changed;
  * every probed file is appended to a resume cache (`*.partial.jsonl`), so an interrupted run
    continues without re-hashing; a cached entry is reused only if size and mtime still match;
  * the CSV and its meta file are written atomically.
"""

from __future__ import annotations

import json
import os
import platform
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from ..io import atomic_write_json, atomic_write_text, sha256_file
from ..paths import cfg_path, ensure_dir
from ..text.normalize import NORM_VER, normalize
from .groups import assign_groups, group_sizes
from .video import probe_video

COLUMNS = [
    "index", "relpath", "bytes", "sha256", "codec", "stored_w", "stored_h", "rotation", "display_w",
    "display_h", "orientation", "fps_avg", "n_frames", "duration_s", "decode_ok", "sentence_raw",
    "sentence_norm", "norm_ver", "exact_dup_of", "is_representative", "group_id", "label_conflict", "flags",
]


def read_sheet(cfg: dict) -> pd.DataFrame:
    path = Path(cfg["paths"]["data_root"]) / cfg["data"]["sheet"]
    df = pd.read_excel(path, sheet_name=cfg["data"]["sheet_name"])
    if list(df.columns[:2]) != ["Names", "Index"]:
        raise ValueError(f"Unexpected sheet columns: {list(df.columns)}")
    out = pd.DataFrame({"index": df["Index"].astype(int), "sentence_raw": df["Names"].astype(str)})
    if out["index"].duplicated().any():
        raise ValueError("Duplicate Index values in the sheet")
    return out


def snapshot(video_dir: Path, indices: list[int]) -> dict[int, list[int]]:
    """Size and mtime (ns) of every video — compared before/after to prove nothing was modified."""
    snap = {}
    for i in indices:
        st = (video_dir / f"{i}.mp4").stat()
        snap[i] = [st.st_size, st.st_mtime_ns]
    return snap


def _probe_task(i: int, path: str) -> tuple[int, dict]:
    return i, probe_video(path)


def _load_cache(path: Path) -> dict[int, dict]:
    cache = {}
    if path.is_file():
        for line in path.read_text(encoding="utf-8").splitlines():
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue  # a line cut off by an interruption
            cache[int(rec["index"])] = rec
    return cache


def build_manifest(cfg: dict, workers: int | None = None, log=print) -> tuple[pd.DataFrame, dict]:
    t_start = time.perf_counter()
    started = datetime.now(timezone.utc)
    data_root = Path(cfg["paths"]["data_root"])
    video_dir = Path(cfg["data"]["video_root"])
    out_dir = ensure_dir(cfg_path(cfg, "manifests_dir"))
    version = cfg["manifest"]["version"]
    workers = workers or int(cfg["manifest"]["workers"])

    sheet_path = data_root / cfg["data"]["sheet"]
    sheet_sha_before = sha256_file(sheet_path)
    sheet = read_sheet(cfg)
    indices = sorted(sheet["index"].tolist())
    files = {int(p.stem) for p in video_dir.glob("*.mp4") if p.stem.isdigit()}
    missing, extra = sorted(set(indices) - files), sorted(files - set(indices))
    log(f"sheet rows {len(indices)} | video files {len(files)} | missing {len(missing)} | extra {len(extra)}")
    present = [i for i in indices if i in files]
    snap_before = snapshot(video_dir, present)

    cache_path = out_dir / f"manifest_{version}.partial.jsonl"
    cache = _load_cache(cache_path)
    todo = [i for i in present
            if not (i in cache and [cache[i]["bytes"], cache[i]["mtime_ns"]] == snap_before[i])]
    log(f"probing {len(todo)} files with {workers} workers ({len(present) - len(todo)} reused from cache)")
    results = {i: cache[i] for i in present if i not in todo}
    t_probe = time.perf_counter()
    with open(cache_path, "a", encoding="utf-8") as cache_f, ProcessPoolExecutor(max_workers=workers) as pool:
        futures = [pool.submit(_probe_task, i, str(video_dir / f"{i}.mp4")) for i in todo]
        for n, fut in enumerate(as_completed(futures), 1):
            i, rec = fut.result()
            rec["index"] = i
            results[i] = rec
            cache_f.write(json.dumps(rec) + "\n")
            cache_f.flush()
            if n % 500 == 0 or n == len(todo):
                log(f"  {n}/{len(todo)} probed ({time.perf_counter() - t_probe:.0f} s)")
    probe_seconds = time.perf_counter() - t_probe

    rows = []
    for _, s in sheet.iterrows():
        i = int(s["index"])
        rec = results.get(i, {})
        flags = []
        if i not in files:
            flags.append("file_missing")
        elif not rec.get("decode_ok", False):
            flags.append("decode_failed")
        rows.append({
            "index": i,
            "relpath": (video_dir / f"{i}.mp4").relative_to(data_root).as_posix(),
            **{k: rec.get(k) for k in ("bytes", "sha256", "codec", "stored_w", "stored_h", "rotation",
                                        "display_w", "display_h", "orientation", "fps_avg", "n_frames",
                                        "duration_s", "decode_ok")},
            "sentence_raw": s["sentence_raw"],
            "sentence_norm": normalize(s["sentence_raw"]),
            "norm_ver": NORM_VER,
            "flags": ";".join(flags),
        })
    df = pd.DataFrame(rows)
    df = assign_groups(df, cfg["split"].get("known_shared_segment_links"))
    df.loc[df["label_conflict"], "flags"] = df.loc[df["label_conflict"], "flags"].map(
        lambda f: ";".join(x for x in (f, "label_conflict") if x))
    df = df[COLUMNS].sort_values("index").reset_index(drop=True)

    snap_after = snapshot(video_dir, present)
    sheet_sha_after = sha256_file(sheet_path)
    changed = [i for i in present if snap_before[i] != snap_after[i]]
    if changed or sheet_sha_before != sheet_sha_after:
        raise RuntimeError(f"Source files changed during the run: videos {changed[:10]}, "
                           f"sheet changed={sheet_sha_before != sheet_sha_after}")

    csv_path = out_dir / f"manifest_{version}.csv"
    atomic_write_text(csv_path, df.to_csv(index=False, lineterminator="\n"))
    reps = df[df["is_representative"]]
    meta = {
        "manifest": f"manifest_{version}",
        "generated_at_utc": started.isoformat(timespec="seconds"),
        "csv": csv_path.name,
        "csv_sha256": sha256_file(csv_path),
        "config_hash": cfg["_meta"]["config_hash"],
        "norm_ver": NORM_VER,
        "sheet_sha256": sheet_sha_before,
        "sources_unchanged": True,
        "videos_checked_unchanged": len(present),
        "counts": {
            "sheet_rows": len(indices), "video_files": len(files), "missing_files": missing, "extra_files": extra,
            "decode_failed": int((~df["decode_ok"].fillna(False).astype(bool)).sum()),
            "unique_sha256": int(df["sha256"].nunique()),
            "representatives": int(len(reps)),
            "unique_sentence_norm": int(df["sentence_norm"].nunique()),
            "unique_sentence_norm_in_representatives": int(reps["sentence_norm"].nunique()),
            "groups": int(df["group_id"].nunique()),
            "group_size_histogram": group_sizes(df),
            "label_conflicts": int(df["label_conflict"].sum()),
            "label_conflict_indices": df.loc[df["label_conflict"], "index"].astype(int).tolist(),
            "orientation": df["orientation"].value_counts().to_dict(),
            "rotation": {str(k): int(v) for k, v in df["rotation"].value_counts().items()},
            "codec": df["codec"].value_counts().to_dict(),
            "total_bytes": int(df["bytes"].sum()),
            "total_duration_s": round(float(df["duration_s"].sum()), 1),
            "total_declared_frames": int(df["n_frames"].sum()),
        },
        "timing_seconds": {"probe": round(probe_seconds, 1), "total": round(time.perf_counter() - t_start, 1),
                           "files_probed_this_run": len(todo), "workers": workers},
        "machine": {"platform": platform.platform(), "cpu_count": os.cpu_count()},
    }
    atomic_write_json(out_dir / f"manifest_{version}.meta.json", meta)
    return df, meta


def load_manifest(cfg: dict) -> pd.DataFrame:
    path = cfg_path(cfg, "manifests_dir") / f"manifest_{cfg['manifest']['version']}.csv"
    df = pd.read_csv(path, dtype={"sha256": str, "flags": str}, keep_default_na=False,
                     na_values={"exact_dup_of": [""], "duration_s": [""]})
    df["exact_dup_of"] = df["exact_dup_of"].astype("Int64")
    for col in ("decode_ok", "is_representative", "label_conflict"):
        df[col] = df[col].astype(str).str.lower().eq("true")
    return df
