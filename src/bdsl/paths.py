"""Find the project root and turn configured path strings into Path objects.

No absolute machine path is written in code: the root is found at run time, and every other path
comes from the config (configs/*.yaml) or from the BDSL_* environment variables.
"""

from __future__ import annotations

import os
from pathlib import Path

PROJECT_NAME = "bdsl"
_MARKER = "pyproject.toml"


def _is_project_root(path: Path) -> bool:
    marker = path / _MARKER
    if not marker.is_file():
        return False
    return f'name = "{PROJECT_NAME}"' in marker.read_text(encoding="utf-8")


def find_project_root(start: str | os.PathLike | None = None) -> Path:
    """Return the folder that holds this project's pyproject.toml.

    Search order: the BDSL_PROJECT_ROOT env var, then upwards from `start` (if given), from this
    file (works for the editable install) and from the current working directory.
    """
    explicit = os.environ.get("BDSL_PROJECT_ROOT")
    if explicit:
        root = Path(explicit).resolve()
        if not _is_project_root(root):
            raise FileNotFoundError(f"BDSL_PROJECT_ROOT={explicit} has no bdsl {_MARKER}")
        return root
    starts = [Path(start)] if start else []
    starts += [Path(__file__).resolve().parent, Path.cwd()]
    for s in starts:
        for candidate in [s.resolve(), *s.resolve().parents]:
            if _is_project_root(candidate):
                return candidate
    raise FileNotFoundError(
        f"Could not find the bdsl project root ({_MARKER}). Set BDSL_PROJECT_ROOT or run from inside the project."
    )


def cfg_path(cfg: dict, key: str) -> Path:
    """Path for a key in the `paths` section, e.g. cfg_path(cfg, "work_dir")."""
    return Path(cfg["paths"][key])


def ensure_dir(path: str | os.PathLike) -> Path:
    """Create a folder (and parents) if needed and return it as a Path."""
    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)
    return p
