"""SPLIT_LOCK.json: hashes of the four split manifests, written after the videos are copied.

Hashes are line-ending independent (`bdsl.io.sha256_text_canonical`: BOM removed, CRLF/CR → LF), so a
Git checkout with `core.autocrlf=true` (open question G12) or a re-save in Excel as "CSV UTF-8" does not
break the lock, while any change of content does. Training (`bdsl.data.kaggle400.check_split_lock`)
refuses to run when a hash differs.
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from bdsl.io import atomic_write_json, sha256_text_canonical

LOCKED = ("data/train/train_manifest.csv", "data/val/val_manifest.csv", "data/test/test_manifest.csv",
          "data/subset_manifest.csv")
HASH_METHOD = "SHA-256 of the UTF-8 text with the BOM removed and CRLF/CR turned into LF"


def videos_digest(subset: pd.DataFrame, column: str = "sha256") -> str:
    """One hash over the sorted "split/Index sha256" lines: identifies the exact set of 400 videos."""
    lines = sorted(f"{s}/{int(i)} {h}" for s, i, h in zip(subset["split"], subset["index"], subset[column]))
    return hashlib.sha256("\n".join(lines).encode("utf-8")).hexdigest()


def write_lock(root: Path, extra: dict) -> dict:
    """root = the folder that contains data/."""
    subset = pd.read_csv(root / "data" / "subset_manifest.csv", dtype={"sha256": str, "sha256_copy": str},
                         encoding="utf-8-sig")
    lock = {"lock_version": 1, "created_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "hash_method": HASH_METHOD, "files": {rel: sha256_text_canonical(root / rel) for rel in LOCKED},
            "counts": subset["split"].value_counts().to_dict(), "videos_digest": videos_digest(subset),
            "rule": "training refuses to run if any of these hashes changes; never edit a locked manifest", **extra}
    atomic_write_json(root / "data" / "SPLIT_LOCK.json", lock)
    return lock


def check_lock(root: Path) -> list[str]:
    """Problems (empty = every locked file matches)."""
    f = root / "data" / "SPLIT_LOCK.json"
    if not f.is_file():
        return ["SPLIT_LOCK.json is missing"]
    lock = json.loads(f.read_text(encoding="utf-8"))
    out = []
    for rel, h in lock["files"].items():
        p = root / rel
        if not p.is_file():
            out.append(f"{rel}: missing")
        elif sha256_text_canonical(p) != h:
            out.append(f"{rel}: hash differs from SPLIT_LOCK.json")
    return out
