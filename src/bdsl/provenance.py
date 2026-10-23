"""Where the code of a run came from, the full software environment, and the run registry.

Owner rules (2026-10-23): a result run must come from committed code. Locally the git working tree
must be clean; on Kaggle the code comes from a `git archive` of a clean commit, described by
`CODE_VERSION.json` (commit + SHA-256 of every file) at the code root. A run that cannot prove clean
code is refused, or — only with the explicit `--not-for-paper` option — named `NFP_…` and marked
`for_paper: false` everywhere.
"""

from __future__ import annotations

import csv
import hashlib
import io
import json
import os
import platform
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

from .io import atomic_write_json, atomic_write_text, sha256_file

CODE_VERSION_FILE = "CODE_VERSION.json"
REGISTRY_COLUMNS = ["run_id", "model", "input", "data", "seeds", "status", "for_paper", "label", "device", "gpu",
                    "split_lock_sha256", "feat_ver", "annotation_sha256", "code_source", "git_commit", "dirty",
                    "started_utc", "finished_utc", "seconds", "run_dir"]


class DirtyCodeError(RuntimeError):
    pass


def _git(root: Path, *args: str) -> str | None:
    try:
        return subprocess.run(["git", *args], cwd=root, capture_output=True, text=True, check=True).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return None


def code_provenance(root: str | os.PathLike) -> dict:
    """{"source": git|package|unknown, "commit", "dirty", ...}. Unknown code counts as dirty."""
    root = Path(root)
    if (root / ".git").exists():
        status = _git(root, "status", "--porcelain")
        return {"source": "git", "commit": _git(root, "rev-parse", "HEAD"),
                "branch": _git(root, "rev-parse", "--abbrev-ref", "HEAD"),
                "dirty": status is None or bool(status),
                "dirty_files": (status or "").splitlines()[:50]}
    cv = root / CODE_VERSION_FILE
    if cv.is_file():
        info = json.loads(cv.read_text(encoding="utf-8"))
        changed = [p for p, h in info.get("files", {}).items()
                   if not (root / p).is_file() or sha256_file(root / p) != h]
        return {"source": "package", "commit": info.get("commit"), "branch": None,
                "dirty": bool(info.get("dirty", True)) or bool(changed),
                "dirty_files": changed[:50], "package_created_utc": info.get("created_utc")}
    return {"source": "unknown", "commit": None, "branch": None, "dirty": True,
            "dirty_files": ["no .git folder and no CODE_VERSION.json"]}


def result_run_policy(prov: dict, not_for_paper: bool) -> tuple[bool, str]:
    """(for_paper, run-name prefix). `--not-for-paper` always gives an NFP_ run (engineering checks such as
    the resume test use it too); without it, uncommitted code raises DirtyCodeError."""
    if not_for_paper:
        return False, "NFP_"
    if not prov["dirty"]:
        return True, ""
    raise DirtyCodeError(
        "Refusing a result run: the code is not a clean commit "
        f"(source {prov['source']}, changed: {prov['dirty_files'][:5]}). Commit first, or add "
        "--not-for-paper to run anyway; such a run is named NFP_… and is never used in the paper.")


def installed_packages() -> list[str]:
    """`pip freeze`-style list from the running interpreter's metadata."""
    from importlib import metadata

    out = set()
    for d in metadata.distributions():
        name = d.metadata.get("Name")
        if name:
            out.add(f"{name}=={d.version}")
    return sorted(out, key=str.lower)


def env_record(device_info: dict, prov: dict, extra: dict | None = None) -> dict:
    """Everything needed to say what software and hardware produced a run."""
    return {
        "created_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "python": sys.version, "platform": platform.platform(), "machine": platform.machine(),
        "cpu_count": os.cpu_count(), "kaggle": "KAGGLE_KERNEL_RUN_TYPE" in os.environ,
        "kaggle_run_type": os.environ.get("KAGGLE_KERNEL_RUN_TYPE"),
        "device": device_info, "code": prov, "packages": installed_packages(), **(extra or {}),
    }


def write_env_json(run_dir: Path, record: dict) -> Path:
    return atomic_write_json(run_dir / "env.json", record)


def append_registry(path: Path, row: dict) -> Path:
    """Add one line per run (re-writes the file atomically; an existing run_id line is replaced)."""
    rows = []
    if path.exists():
        with open(path, encoding="utf-8-sig", newline="") as f:
            rows = [r for r in csv.DictReader(f) if r.get("run_id") != row.get("run_id")]
    rows.append({k: row.get(k, "") for k in REGISTRY_COLUMNS})
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=REGISTRY_COLUMNS, lineterminator="\n")
    w.writeheader()
    for r in rows:
        w.writerow({k: ("" if r.get(k) is None else r.get(k)) for k in REGISTRY_COLUMNS})
    return atomic_write_text(path, buf.getvalue())


def sha256_json(obj) -> str:
    return hashlib.sha256(json.dumps(obj, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()
