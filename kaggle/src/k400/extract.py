"""Notebook 02: MediaPipe Holistic features for the 400 clips, one output folder per split.

Same extraction as the pilot (`bdsl.features.extract.extract_clip`: VIDEO mode, 15 fps grid, feat_layout_v1,
fresh landmarker per clip, no face mesh or image stored), so features carry the same `feat_ver` when the
MediaPipe version, model file and settings are the same.

Resume-safe: a clip whose .npz already has the current feat_ver is skipped; files are written atomically.
Time budget: no new clip is started after `max_minutes`, so a Kaggle version always finishes and saves
what it has; the next version (with this version's output added as Input) continues.
Outputs (state root = /kaggle/working/k400 on Kaggle):
    processed/features/<split>/<Index>.npz, feature_meta.json
    processed/qc/qc.csv, failures.csv, hand_coverage_summary.csv, extract_run.json
"""

from __future__ import annotations

import json
import os
import platform
import sys
import time
from concurrent.futures import FIRST_COMPLETED, ProcessPoolExecutor, wait
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

from bdsl.features.extract import _task
from bdsl.features.layout import LAYOUT, feat_ver, privacy_problems, read_meta
from bdsl.features.qc import qc_row
from bdsl.io import atomic_write_json, atomic_write_text, sha256_file

SPLITS = ("train", "val", "test")


def plan(data_dir: Path, feat_dir: Path, splits=SPLITS) -> list[dict]:
    rows = []
    for sp in splits:
        man = pd.read_csv(data_dir / sp / f"{sp}_manifest.csv", encoding="utf-8-sig")
        for r in man.sort_values("index").to_dict("records"):
            rows.append({"index": int(r["index"]), "split": sp, "video": data_dir / sp / "videos" / r["filename"],
                         "out": feat_dir / sp / f"{int(r['index'])}.npz", "display_w": int(r["display_w"]),
                         "display_h": int(r["display_h"]), "duration_s": float(r["duration_s"])})
    return rows


def run(cfg: dict, data_dir: Path, state_root: Path, model_path: Path, workers: int | None = None,
        max_minutes: float | None = None, splits=SPLITS, log=print) -> dict:
    import mediapipe as mp

    fcfg = cfg["features"]
    model_sha = sha256_file(model_path)
    if model_sha != cfg["mediapipe"]["model_sha256"]:
        raise RuntimeError(f"model SHA-256 {model_sha} differs from configs/base.yaml {cfg['mediapipe']['model_sha256']}")
    fv = feat_ver(fcfg, "video", mp.__version__, model_sha)
    feat_dir, qc_dir = state_root / "processed" / "features", state_root / "processed" / "qc"
    clips = plan(data_dir, feat_dir, splits)
    for sp in splits:
        (feat_dir / sp).mkdir(parents=True, exist_ok=True)
        for stale in (feat_dir / sp).glob(".*.tmp"):
            stale.unlink()
        atomic_write_json(feat_dir / sp / "feature_meta.json", {
            "feat_ver": fv, "layout": LAYOUT, "mode": "video", "fps": fcfg["fps"], "landmarker": fcfg["landmarker"],
            "mediapipe": mp.__version__, "model_file": model_path.name, "model_sha256": model_sha, "split": sp,
            "platform": platform.platform(), "python": sys.version.split()[0]})
    done = [c for c in clips if c["out"].exists() and (read_meta(c["out"]) or {}).get("feat_ver") == fv]
    todo = [c for c in clips if c not in done]
    workers = workers or max(1, (os.cpu_count() or 2))
    log(f"feat_ver {fv} | {len(done)} clips already done, {len(todo)} to extract | {workers} worker processes"
        + (f" | time budget {max_minutes} min" if max_minutes else ""))
    t0, failures, finished, stopped = time.perf_counter(), [], 0, False
    extra = {"platform": platform.platform(), "python": sys.version.split()[0]}
    with ProcessPoolExecutor(max_workers=workers) as pool:
        queue, running = list(todo), {}
        while queue or running:
            while queue and len(running) < workers * 2 and not stopped:
                if max_minutes and (time.perf_counter() - t0) / 60 > max_minutes:
                    stopped = True
                    log(f"time budget reached: no new clips started ({len(queue)} left for the next version)")
                    break
                c = queue.pop(0)
                args = (c["index"], str(c["video"]), str(c["out"]), "video", float(fcfg["fps"]), dict(fcfg["landmarker"]),
                        str(model_path), {"index": c["index"], "feat_ver": fv, "split": c["split"], **extra})
                running[pool.submit(_task, args)] = c
            if not running:
                break
            fin, _ = wait(list(running), return_when=FIRST_COMPLETED)
            for f in fin:
                c = running.pop(f)
                i, res, err = f.result()
                finished += 1
                if err:
                    failures.append({"index": i, "split": c["split"], "error": err})
                    log(f"  FAILED {c['split']}/{i}: {err}")
                if finished % 20 == 0 or (not queue and not running):
                    el = time.perf_counter() - t0
                    log(f"  {finished}/{len(todo)} clips ({el / 60:.1f} min, {el / max(finished, 1):.1f} s per clip)")
            if stopped and not running:
                break
    seconds = time.perf_counter() - t0
    summary = qc_and_report(clips, fv, qc_dir, failures)
    summary.update({"feat_ver": fv, "mediapipe": mp.__version__, "model_sha256": model_sha, "workers": workers,
                    "seconds_this_run": round(seconds, 1), "extracted_this_run": finished - len(failures),
                    "stopped_by_time_budget": stopped, "platform": platform.platform(), "python": sys.version.split()[0],
                    "kaggle": "KAGGLE_KERNEL_RUN_TYPE" in os.environ,
                    "finished_utc": datetime.now(timezone.utc).isoformat(timespec="seconds")})
    atomic_write_json(qc_dir / "extract_run.json", summary)
    return summary


def qc_and_report(clips: list[dict], fv: str, qc_dir: Path, failures: list[dict]) -> dict:
    """qc.csv (all splits), failures.csv, hand_coverage_summary.csv; privacy + rotation + length checks."""
    rows, problems = [], []
    fail_of = {f["index"]: f["error"] for f in failures}
    missing = []
    for c in clips:
        meta = read_meta(c["out"]) if c["out"].exists() else None
        if not meta or meta.get("feat_ver") != fv:
            missing.append({"index": c["index"], "split": c["split"], "error": fail_of.get(c["index"], "not extracted yet")})
            continue
        r = qc_row(c["out"]) | {"split": c["split"]}
        priv = privacy_problems(c["out"])
        h, w = meta.get("frame_hw") or (None, None)
        r["rotation_ok"] = (h, w) == (c["display_h"], c["display_w"])
        r["frames_vs_duration"] = int(meta["frames"]) - int(round(c["duration_s"] * 15))
        r["privacy_ok"] = not priv
        if priv:
            problems.append(f"{c['split']}/{c['index']}: privacy {priv}")
        if not r["rotation_ok"]:
            problems.append(f"{c['split']}/{c['index']}: decoded frame {h}x{w} (h x w) but manifest says "
                            f"{c['display_h']}x{c['display_w']} — rotation handling differs")
        rows.append(r)
    qc = pd.DataFrame(rows)
    qc_dir.mkdir(parents=True, exist_ok=True)
    atomic_write_text(qc_dir / "qc.csv", qc.to_csv(index=False, lineterminator="\n"))
    atomic_write_text(qc_dir / "failures.csv",
                      pd.DataFrame(missing, columns=["index", "split", "error"]).to_csv(index=False, lineterminator="\n"))
    cols = ["cov_pose", "cov_left_hand", "cov_right_hand", "cov_both_hands", "cov_any_hand", "cov_face",
            "longest_gap_left_hand_s", "longest_gap_right_hand_s"]
    if len(qc):
        hs = qc.groupby("split")[cols].agg(["mean", "median", "min"]).round(4)
        hs.columns = [f"{a}_{b}" for a, b in hs.columns]
        hs.insert(0, "clips", qc.groupby("split").size())
        hs = hs.reset_index()
        all_row = qc[cols].agg(["mean", "median", "min"]).round(4).unstack()
        all_row.index = [f"{a}_{b}" for a, b in all_row.index]
        hs = pd.concat([hs, pd.DataFrame([{"split": "all", "clips": len(qc), **all_row.to_dict()}])], ignore_index=True)
    else:
        hs = pd.DataFrame()
    atomic_write_text(qc_dir / "hand_coverage_summary.csv", hs.to_csv(index=False, lineterminator="\n"))
    by_split = {sp: {"expected": sum(c["split"] == sp for c in clips),
                     "with_features": int((qc["split"] == sp).sum()) if len(qc) else 0} for sp in SPLITS}
    return {"clips_expected": len(clips), "clips_with_features": int(len(qc)), "by_split": by_split,
            "failures_or_missing": len(missing), "problems": problems,
            "privacy_ok_all": bool(len(qc) and qc["privacy_ok"].all()),
            "rotation_ok_all": bool(len(qc) and qc["rotation_ok"].all()),
            "frames_vs_duration_abs_max": int(qc["frames_vs_duration"].abs().max()) if len(qc) else None,
            "complete": len(missing) == 0 and not problems}


def print_summary(summary: dict) -> str:
    lines = [f"feat_ver {summary.get('feat_ver')} | mediapipe {summary.get('mediapipe')} | {summary.get('platform')}",
             f"clips with features: {summary['clips_with_features']}/{summary['clips_expected']} "
             f"(train {summary['by_split']['train']['with_features']}/{summary['by_split']['train']['expected']}, "
             f"val {summary['by_split']['val']['with_features']}/{summary['by_split']['val']['expected']}, "
             f"test {summary['by_split']['test']['with_features']}/{summary['by_split']['test']['expected']})",
             f"failures or missing: {summary['failures_or_missing']} | privacy OK: {summary['privacy_ok_all']} | "
             f"rotation OK: {summary['rotation_ok_all']} | max |frames - duration x 15|: {summary['frames_vs_duration_abs_max']}",
             f"this run: {summary.get('extracted_this_run')} clips in {summary.get('seconds_this_run')} s; "
             f"stopped by time budget: {summary.get('stopped_by_time_budget')}",
             "EXTRACTION COMPLETE" if summary["complete"] else "EXTRACTION NOT COMPLETE — see problems / failures.csv"]
    if summary["problems"]:
        lines += ["problems:"] + [f"  {p}" for p in summary["problems"][:20]]
    return "\n".join(lines)


def hand_coverage_table(qc_dir: Path) -> pd.DataFrame:
    return pd.read_csv(qc_dir / "hand_coverage_summary.csv")


def as_json(d: dict) -> str:
    return json.dumps(d, indent=1, ensure_ascii=False, default=lambda o: o.item() if isinstance(o, np.generic) else str(o))
