"""Safe file writing and hashing.

Every write goes to a temporary file in the same folder first and is then renamed over the target
(`os.replace` is atomic on one filesystem). A crash mid-write therefore leaves either the old file
or the new one — never a half-written file.
"""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from typing import Any


def atomic_write_bytes(path: str | os.PathLike, data: bytes) -> Path:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    tmp = target.with_name(f".{target.name}.{os.getpid()}.tmp")
    try:
        with open(tmp, "wb") as f:
            f.write(data)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, target)
    finally:
        if tmp.exists():
            tmp.unlink()
    return target


def atomic_write_text(path: str | os.PathLike, text: str) -> Path:
    return atomic_write_bytes(path, text.encode("utf-8"))


def atomic_write_json(path: str | os.PathLike, obj: Any) -> Path:
    # Serialise first: if `obj` cannot be encoded, nothing on disk is touched.
    text = json.dumps(obj, indent=2, ensure_ascii=False, sort_keys=True) + "\n"
    return atomic_write_text(path, text)


def sha256_file(path: str | os.PathLike, chunk_size: int = 1 << 20) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(chunk_size), b""):
            h.update(block)
    return h.hexdigest()
