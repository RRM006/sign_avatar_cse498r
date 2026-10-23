"""Copy the 400 chosen videos into kaggle/data/<split>/videos/ (owner permission, 2026-10-23).

Safety rules:
  - the originals are only opened for reading; their size and modification time are compared before
    and after, and their SHA-256 is measured and compared with manifest_v1;
  - each copy is written to a temporary name and renamed, then hashed: copy SHA-256 = source SHA-256 =
    manifest SHA-256, or the clip is reported as a failure;
  - an existing copy with the right hash is kept (resume-safe); an existing file with a different
    hash is NOT overwritten (stop and ask the owner);
  - nothing runs without --confirm.
Afterwards: COPY_VERIFICATION.csv, the `sha256_copy` column of subset_manifest.csv, SPLIT_LOCK.json,
the full leakage test appended to SPLIT_REPORT.md, and an entry in DATASET_WORK_LOG.md.
"""

from __future__ import annotations

import os
import platform
import shutil
import time
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from bdsl.io import atomic_write_text, sha256_file

from .lock import write_lock
from .verify import format_results, overall, run_checks

LOG_MARKER = "<!-- k400-copy-log -->"
REPORT_SECTION = "\n### Desktop run, "


def copy_all(root: Path, source_root: Path, log=print) -> pd.DataFrame:
    """root = kaggle/ (contains data/); source_root = dataset/initial_dataset (contains SIGN_LANGUAGE_DATA/)."""
    data = root / "data"
    sub = pd.read_csv(data / "subset_manifest.csv", dtype={"sha256": str, "sha256_source": str, "sha256_copy": str},
                      encoding="utf-8-sig", keep_default_na=False)
    rows = []
    t0 = time.perf_counter()
    for n, r in enumerate(sub.to_dict("records"), 1):
        i, sp = int(r["index"]), r["split"]
        src = source_root / r["source_relpath"]
        dst = data / sp / "videos" / r["filename"]
        row = {"index": i, "split": sp, "source": r["source_relpath"], "copy": f"data/{sp}/videos/{r['filename']}",
               "sha256_manifest_v1": r["sha256"], "sha256_source": "", "sha256_copy": "", "bytes": "",
               "source_unchanged": False, "action": "", "ok": False, "error": ""}
        try:
            st0 = os.stat(src)
            row["sha256_source"] = sha256_file(src)
            if dst.exists():
                h = sha256_file(dst)
                if h != row["sha256_source"]:
                    raise RuntimeError(f"{dst} exists with a different SHA-256; not overwritten (ask the owner)")
                row["action"] = "already present"
            else:
                dst.parent.mkdir(parents=True, exist_ok=True)
                tmp = dst.with_name(f".{dst.name}.{os.getpid()}.tmp")
                try:
                    shutil.copy2(src, tmp)
                    os.replace(tmp, dst)
                finally:
                    if tmp.exists():
                        tmp.unlink()
                row["action"] = "copied"
            row["sha256_copy"] = sha256_file(dst)
            st1 = os.stat(src)
            row["source_unchanged"] = (st0.st_size, st0.st_mtime_ns) == (st1.st_size, st1.st_mtime_ns)
            row["bytes"] = dst.stat().st_size
            row["ok"] = bool(row["source_unchanged"] and row["sha256_copy"] == row["sha256_source"] == r["sha256"])
            if not row["ok"]:
                row["error"] = "hash or source check failed"
        except Exception as exc:  # noqa: BLE001 — every failure is reported, never skipped
            row["error"] = f"{type(exc).__name__}: {exc}"
        rows.append(row)
        if n % 50 == 0 or n == len(sub):
            log(f"  {n}/{len(sub)} clips checked ({time.perf_counter() - t0:.0f} s)")
    return pd.DataFrame(rows)


def run(root: Path, source_root: Path, project_root: Path, links, s1_csv: Path | None, log=print) -> int:
    data = root / "data"
    res = copy_all(root, source_root, log)
    atomic_write_text(data / "COPY_VERIFICATION.csv", "\ufeff" + res.to_csv(index=False, lineterminator="\n"))
    n_ok, n = int(res["ok"].sum()), len(res)
    log(f"copies verified: {n_ok}/{n}; copied now: {int((res['action'] == 'copied').sum())}; "
        f"already present: {int((res['action'] == 'already present').sum())}; "
        f"source files unchanged: {int(res['source_unchanged'].sum())}/{n}; total {res['bytes'].replace('', 0).astype(int).sum() / 1e9:.2f} GB")
    if n_ok != n:
        log(res[~res["ok"]][["index", "split", "error"]].head(20).to_string(index=False))
        log("COPY FAILED: SPLIT_LOCK.json was NOT written. Fix the problem above and run again.")
        return 1
    sub_path = data / "subset_manifest.csv"
    sub = pd.read_csv(sub_path, dtype=str, encoding="utf-8-sig", keep_default_na=False)
    copy_of = dict(zip(res["index"].astype(str), res["sha256_copy"]))
    sub["sha256_copy"] = sub["index"].map(copy_of)
    atomic_write_text(sub_path, "\ufeff" + sub.to_csv(index=False, lineterminator="\n"))
    lock = write_lock(root, {"copy_verification": "data/COPY_VERIFICATION.csv", "copied_on": platform.node(),
                             "source": "dataset/initial_dataset/SIGN_LANGUAGE_DATA (read-only)"})
    checks = run_checks(root, links, s1_csv, require_videos=True)
    ok = overall(checks, require_videos=True)
    report = data / "SPLIT_REPORT.md"
    text = report.read_text(encoding="utf-8") if report.is_file() else "# SPLIT_REPORT\n"
    # The report shows the CURRENT state: a re-run replaces its own section (the history is in
    # DATASET_WORK_LOG.md and the script logs), so the section never appears twice.
    old = text.find(REPORT_SECTION)
    if old != -1:
        nxt = text.find("\n## ", old + 1)
        text = text[:old].rstrip("\n") + "\n" + (text[nxt:] if nxt != -1 else "")
    copied, present = int((res["action"] == "copied").sum()), int((res["action"] == "already present").sum())
    section = (f"{REPORT_SECTION}{datetime.now(timezone.utc).isoformat(timespec='seconds')} ({platform.node()})\n"
               f"- Copies: {n_ok}/{n} byte-identical (SHA-256 of source = copy = manifest_v1); "
               f"copied in this run: {copied}; already present from an earlier run (re-hashed now): {present}; "
               f"source files unchanged (size + modification time): {int(res['source_unchanged'].sum())}/{n}.\n"
               f"- Total size of the copies: {res['bytes'].astype(int).sum() / 1e9:.2f} GB.\n"
               f"- SPLIT_LOCK.json written; videos digest `{lock['videos_digest']}`.\n\n"
               f"```\n{format_results(checks)}\n```\n")
    atomic_write_text(report, text + section)
    _work_log(project_root, n_ok, n, res, lock, ok)
    log(format_results(checks))
    return 0 if ok else 1


def _work_log(project_root: Path, n_ok, n, res, lock, ok) -> None:
    """One entry for the copy; a later run adds a dated re-check line to it (the first run is kept)."""
    log = project_root / "dataset" / "initial_dataset" / "DATASET_WORK_LOG.md"
    if not log.is_file():
        return
    text = log.read_text(encoding="utf-8")
    copied, present = int((res["action"] == "copied").sum()), int((res["action"] == "already present").sum())
    if LOG_MARKER in text:
        m = text.index(LOG_MARKER)
        end = text.find("\n## ", m)
        end = len(text) if end == -1 else end
        line = (f"- Re-check {datetime.now(timezone.utc).isoformat(timespec='seconds')} ({platform.node()}): "
                f"copied in this run {copied}, already present {present}; {n_ok}/{n} byte-identical; sources "
                f"unchanged {int(res['source_unchanged'].sum())}/{n}; leakage tests {'PASS' if ok else 'FAIL'}.")
        text = text[:end].rstrip("\n") + "\n" + line + "\n" + text[end:]
        atomic_write_text(log, text.rstrip("\n") + "\n")
        return
    entry = f"""
## {datetime.now(timezone.utc).date().isoformat()} (kaggle400: 400-video copy for the Kaggle experiment) {LOG_MARKER}

- Computer: {platform.node()}
- Task: copy the 400 clips chosen for kaggle400 (owner permission in chat, 2026-10-23) into
  `kaggle/data/{{train,val,test}}/videos/`.
- Files/folders inspected: `SIGN_LANGUAGE_DATA/<Index>.mp4` for the 400 Index values in
  `kaggle/data/subset_manifest.csv` (read-only: SHA-256, size, modification time).
- Action performed: `kaggle/src/k400_run.py copy-videos --confirm` (temp file + rename; SHA-256 of
  source, copy and manifest_v1 compared; size and modification time of every source compared before/after).
- Files changed: `kaggle/data/` (gitignored copies, COPY_VERIFICATION.csv, subset_manifest.csv
  `sha256_copy`, SPLIT_LOCK.json, SPLIT_REPORT.md section 9); this log entry.
- Dataset files changed: None (sources unchanged: {int(res['source_unchanged'].sum())}/{n}).
- Result: {n_ok}/{n} copies byte-identical (copied {copied}, already present {present}); {res['bytes'].astype(int).sum() / 1e9:.2f} GB; videos digest
  `{lock['videos_digest'][:16]}…`; leakage tests {'PASS' if ok else 'FAIL'}.
- Errors/warnings: {'None' if ok and n_ok == n else 'see kaggle/data/COPY_VERIFICATION.csv'}.
- Next step: upload the package (private Kaggle dataset) on the owner's own action.
"""
    atomic_write_text(log, text.rstrip("\n") + "\n" + entry)
