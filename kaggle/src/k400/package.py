"""Build the upload package for the PRIVATE Kaggle dataset (owner permission, 2026-10-23).

    bdsl-k400-<commit>.zip
      data/            the 400 videos in train/val/test folders + manifests, report, lock (from kaggle/data)
      code/            `git archive` of a CLEAN commit: src, configs, kaggle (without kaggle/data), tests,
                       pyproject.toml, uv.lock, README.md; plus code/CODE_VERSION.json (commit + file hashes)
      UPLOAD_MANIFEST.csv   path, bytes, SHA-256 of every other file in the zip
      PACKAGE_INFO.json     commit, counts, lock hash, the permission it relies on
      README_UPLOAD.md      what this dataset is and the rules for it
Only paths on the allow-list are written; anything that looks like a credential, an environment, a
checkpoint, a feature file or a source-video folder is refused. The package is refused when the code
paths have uncommitted changes (the commit must be clean).
"""

from __future__ import annotations

import csv
import hashlib
import io
import json
import re
import subprocess
import tarfile
import zipfile
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath

import pandas as pd

CODE_PATHS = ["src", "configs", "kaggle", "tests", "pyproject.toml", "uv.lock", "README.md"]
CODE_EXCLUDE_PREFIXES = ("kaggle/data/", "kaggle/work/")
DATA_FILES = ["README_DATA.md", "subset_manifest.csv", "SPLIT_REPORT.md", "SPLIT_SUMMARY.png", "SPLIT_LOCK.json",
              "SELECTION_META.json", "COPY_VERIFICATION.csv"]
SPLITS = ("train", "val", "test")
FORBIDDEN_NAMES = {"kaggle.json", ".env", "id_rsa", "id_ed25519", ".netrc", "credentials.json"}
FORBIDDEN_SUFFIXES = {".pt", ".pth", ".ckpt", ".npz", ".pem", ".key", ".p12"}
FORBIDDEN_PARTS = {".venv", "venv", ".git", "__pycache__", ".ipynb_checkpoints", "SIGN_LANGUAGE_DATA", "work"}
STORED_SUFFIXES = {".mp4", ".png", ".zip"}
_VIDEO = re.compile(r"^data/(train|val|test)/videos/(\d+)\.mp4$")


class PackageError(RuntimeError):
    pass


def forbidden(path: str) -> str | None:
    """Why a path may not be uploaded (None = fine)."""
    p = PurePosixPath(path)
    if p.name.lower() in FORBIDDEN_NAMES:
        return "credential-like file name"
    if p.suffix.lower() in FORBIDDEN_SUFFIXES:
        return f"{p.suffix} files are not uploaded (checkpoints / features / keys)"
    bad = FORBIDDEN_PARTS & set(p.parts[:-1])
    if bad:
        return f"inside a forbidden folder {sorted(bad)}"
    return None


def allowed(path: str) -> bool:
    if path in ("UPLOAD_MANIFEST.csv", "PACKAGE_INFO.json", "README_UPLOAD.md", "code/CODE_VERSION.json"):
        return True
    if path.startswith("code/"):
        rel = path[5:]
        return any(rel == c or rel.startswith(c + "/") for c in CODE_PATHS) and not rel.startswith(CODE_EXCLUDE_PREFIXES)
    if path in {f"data/{f}" for f in DATA_FILES} or path in {f"data/{s}/{s}_manifest.csv" for s in SPLITS}:
        return True
    return bool(_VIDEO.match(path))


def _git(project_root: Path, *args: str, binary: bool = False):
    r = subprocess.run(["git", *args], cwd=project_root, capture_output=True, check=False)
    if r.returncode != 0:
        raise PackageError(f"git {' '.join(args)} failed: {r.stderr.decode(errors='replace').strip()}")
    return r.stdout if binary else r.stdout.decode("utf-8", errors="replace").strip()


def git_clean_state(project_root: Path) -> dict:
    """Commit + any uncommitted change in the code paths (tracked changes or untracked files)."""
    commit = _git(project_root, "rev-parse", "HEAD")
    status = _git(project_root, "status", "--porcelain", "--untracked-files=all", "--", *CODE_PATHS)
    changes = [ln for ln in status.splitlines() if ln.strip() and not any(
        ln[3:].strip('"').startswith(x) for x in CODE_EXCLUDE_PREFIXES)]
    return {"commit": commit, "branch": _git(project_root, "rev-parse", "--abbrev-ref", "HEAD"), "changes": changes}


def code_files(project_root: Path, commit: str) -> dict[str, bytes]:
    """{repo path: bytes} of the committed code paths (git archive), kaggle/data excluded."""
    tar_bytes = _git(project_root, "archive", "--format=tar", commit, "--", *CODE_PATHS, binary=True)
    out = {}
    with tarfile.open(fileobj=io.BytesIO(tar_bytes)) as tf:
        for m in tf.getmembers():
            if m.isfile() and not m.name.startswith(CODE_EXCLUDE_PREFIXES):
                out[m.name] = tf.extractfile(m).read()
    return out


def _sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def build(project_root: Path, k400_root: Path, out_dir: Path, log=print, allow_dirty: bool = False) -> dict:
    """k400_root = kaggle/ (contains data/). Returns a summary with sizes."""
    state = git_clean_state(project_root)
    if state["changes"] and not allow_dirty:
        raise PackageError("Refusing to package: the code is not a clean commit. Uncommitted: "
                           + "; ".join(state["changes"][:10]))
    data = k400_root / "data"
    lock = json.loads((data / "SPLIT_LOCK.json").read_text(encoding="utf-8"))
    sub = pd.read_csv(data / "subset_manifest.csv", dtype=str, encoding="utf-8-sig", keep_default_na=False)
    if (sub["sha256_copy"] == "").any():
        raise PackageError("subset_manifest.csv has empty sha256_copy values: run the copy step first")
    code = code_files(project_root, state["commit"])
    created = datetime.now(timezone.utc).isoformat(timespec="seconds")
    code_version = {"commit": state["commit"], "branch": state["branch"], "dirty": bool(state["changes"]),
                    "created_utc": created, "source": "git archive of the commit above",
                    "files": {p: _sha(b) for p, b in sorted(code.items())}}
    entries: list[tuple[str, Path | bytes]] = [(f"code/{p}", b) for p, b in sorted(code.items())]
    entries.append(("code/CODE_VERSION.json", json.dumps(code_version, indent=1, ensure_ascii=False).encode("utf-8")))
    for f in DATA_FILES:
        if not (data / f).is_file():
            raise PackageError(f"missing {data / f}")
        entries.append((f"data/{f}", data / f))
    for sp in SPLITS:
        entries.append((f"data/{sp}/{sp}_manifest.csv", data / sp / f"{sp}_manifest.csv"))
    expected = {(r["split"], r["filename"]): r["sha256_copy"] for r in sub.to_dict("records")}
    for (sp, fn) in sorted(expected):
        entries.append((f"data/{sp}/videos/{fn}", data / sp / "videos" / fn))
    for path, _ in entries:
        why = forbidden(path)
        if why or not allowed(path):
            raise PackageError(f"refusing to package {path}: {why or 'not on the allow-list'}")
    out_dir.mkdir(parents=True, exist_ok=True)
    zpath = out_dir / f"bdsl-k400-{state['commit'][:8]}.zip"
    tmp = zpath.with_name(zpath.name + ".tmp")
    rows, sizes = [], {"code": [0, 0], "metadata": [0, 0], **{f"videos_{s}": [0, 0] for s in SPLITS}}
    with zipfile.ZipFile(tmp, "w", allowZip64=True) as z:
        for n, (path, src) in enumerate(entries, 1):
            b = src if isinstance(src, bytes) else Path(src).read_bytes()
            h = _sha(b)
            m = _VIDEO.match(path)
            if m and h != expected[(m.group(1), f"{m.group(2)}.mp4")]:
                raise PackageError(f"{path}: SHA-256 differs from subset_manifest.csv sha256_copy")
            comp = zipfile.ZIP_STORED if PurePosixPath(path).suffix in STORED_SUFFIXES else zipfile.ZIP_DEFLATED
            z.writestr(zipfile.ZipInfo(path, date_time=(2026, 10, 23, 0, 0, 0)), b, compress_type=comp)
            rows.append({"path": path, "bytes": len(b), "sha256": h})
            key = f"videos_{m.group(1)}" if m else ("code" if path.startswith("code/") else "metadata")
            sizes[key][0] += 1
            sizes[key][1] += len(b)
            if n % 100 == 0:
                log(f"  {n}/{len(entries)} files written")
        buf = io.StringIO()
        w = csv.DictWriter(buf, fieldnames=["path", "bytes", "sha256"], lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
        manifest = buf.getvalue().encode("utf-8")
        info = {"package": "bdsl-k400", "created_utc": created, "commit": state["commit"], "branch": state["branch"],
                "code_dirty": bool(state["changes"]), "n_files": len(rows), "total_bytes": sum(r["bytes"] for r in rows),
                "counts": lock.get("counts"), "videos_digest": lock.get("videos_digest"),
                "split_lock_files": lock.get("files"), "upload_manifest_sha256": _sha(manifest),
                "permission": "owner, 2026-10-23: 400 videos + features + metadata + code to a PRIVATE Kaggle dataset "
                              "(team collaborators only), this experiment only",
                "never_included": sorted(FORBIDDEN_NAMES) + sorted(FORBIDDEN_SUFFIXES) + sorted(FORBIDDEN_PARTS)}
        readme = README_UPLOAD.format(commit=state["commit"], created=created, counts=lock.get("counts")).encode("utf-8")
        for path, b in (("UPLOAD_MANIFEST.csv", manifest), ("README_UPLOAD.md", readme),
                        ("PACKAGE_INFO.json", json.dumps(info, indent=1, ensure_ascii=False).encode("utf-8"))):
            z.writestr(zipfile.ZipInfo(path, date_time=(2026, 10, 23, 0, 0, 0)), b, compress_type=zipfile.ZIP_DEFLATED)
            sizes["metadata"][0] += 1
            sizes["metadata"][1] += len(b)
    tmp.replace(zpath)
    return {"zip": str(zpath), "zip_bytes": zpath.stat().st_size, "commit": state["commit"], "files": len(rows) + 3,
            "sizes": {k: {"files": v[0], "bytes": v[1]} for k, v in sizes.items()}, "code_dirty": bool(state["changes"])}


def verify(zpath: Path, log=print) -> list[str]:
    """Re-open the zip: CRC of every entry, every file on the allow-list, sizes and SHA-256 = UPLOAD_MANIFEST."""
    problems = []
    with zipfile.ZipFile(zpath) as z:
        bad = z.testzip()
        if bad:
            problems.append(f"CRC error in {bad}")
        names = z.namelist()
        for n in names:
            why = forbidden(n)
            if why or not allowed(n):
                problems.append(f"{n}: {why or 'not on the allow-list'}")
        rows = list(csv.DictReader(io.StringIO(z.read("UPLOAD_MANIFEST.csv").decode("utf-8"))))
        listed = {r["path"] for r in rows}
        extra = set(names) - listed - {"UPLOAD_MANIFEST.csv", "PACKAGE_INFO.json", "README_UPLOAD.md"}
        if extra:
            problems.append(f"files not in UPLOAD_MANIFEST.csv: {sorted(extra)[:5]}")
        for k, r in enumerate(rows, 1):
            if r["path"] not in names:
                problems.append(f"{r['path']}: listed but missing")
                continue
            h = hashlib.sha256()
            with z.open(r["path"]) as f:
                for block in iter(lambda: f.read(1 << 20), b""):
                    h.update(block)
            if h.hexdigest() != r["sha256"] or z.getinfo(r["path"]).file_size != int(r["bytes"]):
                problems.append(f"{r['path']}: size or SHA-256 differs from UPLOAD_MANIFEST.csv")
            if k % 200 == 0:
                log(f"  {k}/{len(rows)} files re-hashed")
        info = json.loads(z.read("PACKAGE_INFO.json"))
        videos = [n for n in names if _VIDEO.match(n)]
        if info.get("counts") and len(videos) != sum(info["counts"].values()):
            problems.append(f"{len(videos)} videos in the zip, lock counts {info['counts']}")
    return problems


README_UPLOAD = """# bdsl-k400 — PRIVATE Kaggle dataset for the kaggle400 experiment (CSE498R)

- 400 team-recorded Bangla Sign Language videos (train/val/test folders), their manifests, the split
  report and lock, and the code of commit `{commit}` (folder `code/`). Package created {created}.
- Counts: {counts}.
- Permission (owner, 2026-10-23): upload to a PRIVATE Kaggle dataset, team collaborators only, for this
  experiment only. **Never make this dataset public. Never re-share the videos.**
- The test split is locked: it is read once, by `evaluate --final`, after the configuration is frozen.
- Integrity: `UPLOAD_MANIFEST.csv` lists the SHA-256 of every file; notebook 01 re-checks them.
"""
