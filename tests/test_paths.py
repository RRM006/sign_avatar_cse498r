"""Project-root discovery, and a guard against machine-specific absolute paths in configs/code."""

import re
from pathlib import Path

import pytest

from bdsl.paths import ensure_dir, find_project_root

ROOT = find_project_root()
# A Windows drive path (C:\ or D:/) or a home-folder path.
_ABSOLUTE = re.compile(r"(?<![A-Za-z])[A-Za-z]:[\\/]|\\Users\\|/home/")


def test_root_has_bdsl_pyproject():
    assert (ROOT / "pyproject.toml").is_file()
    assert (ROOT / "configs" / "base.yaml").is_file()


def test_root_found_from_a_subfolder():
    assert find_project_root(ROOT / "configs" / "env") == ROOT


def test_explicit_root_env_var(monkeypatch, tmp_path):
    monkeypatch.setenv("BDSL_PROJECT_ROOT", ROOT.as_posix())
    assert find_project_root(tmp_path) == ROOT
    monkeypatch.setenv("BDSL_PROJECT_ROOT", tmp_path.as_posix())
    with pytest.raises(FileNotFoundError):
        find_project_root()


@pytest.mark.parametrize("path", sorted((ROOT / "configs").rglob("*.yaml")) + sorted((ROOT / "src").rglob("*.py")),
                         ids=lambda p: p.relative_to(ROOT).as_posix())
def test_no_machine_specific_absolute_paths(path: Path):
    hits = [line for line in path.read_text(encoding="utf-8").splitlines()
            if _ABSOLUTE.search(line) and "https://" not in line]
    assert not hits, f"absolute machine path in {path.name}: {hits}"


def test_ensure_dir_creates_nested(tmp_path):
    target = ensure_dir(tmp_path / "a" / "b")
    assert target.is_dir()
