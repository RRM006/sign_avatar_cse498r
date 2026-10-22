"""Atomic writes and hashing."""

import hashlib
import json

import pytest

from bdsl.io import atomic_write_json, atomic_write_text, sha256_file


def test_atomic_write_creates_and_replaces(tmp_path):
    target = tmp_path / "sub" / "out.txt"
    atomic_write_text(target, "first")
    atomic_write_text(target, "second")
    assert target.read_text(encoding="utf-8") == "second"
    assert [p.name for p in target.parent.iterdir()] == ["out.txt"]  # no .tmp left behind


def test_failed_json_write_keeps_the_old_file(tmp_path):
    target = tmp_path / "report.json"
    atomic_write_json(target, {"ok": 1})
    with pytest.raises(TypeError):
        atomic_write_json(target, {"bad": object()})
    assert json.loads(target.read_text(encoding="utf-8")) == {"ok": 1}
    assert [p.name for p in tmp_path.iterdir()] == ["report.json"]


def test_json_is_utf8_and_sorted(tmp_path):
    target = atomic_write_json(tmp_path / "b.json", {"z": 1, "a": "বাংলা"})
    text = target.read_text(encoding="utf-8")
    assert "বাংলা" in text and text.index('"a"') < text.index('"z"')


def test_sha256_matches_hashlib(tmp_path):
    data = b"abc" * 1000
    path = tmp_path / "f.bin"
    path.write_bytes(data)
    assert sha256_file(path, chunk_size=7) == hashlib.sha256(data).hexdigest()
