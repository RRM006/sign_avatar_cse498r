"""Canonical version routing; synthetic metadata/videos only, never experiment execution."""

from __future__ import annotations

import ast
import json
import shutil
from pathlib import Path

import pandas as pd
import pytest

from bdsl.avatar.demo_inputs import resolve_demo_paths
from bdsl.cli import _annotation_paths
from bdsl.config import load_config
from bdsl.data.kaggle400 import paths
from bdsl.paths import find_project_root
from k400.extract import plan
from k400.verify import run_checks
from k400_helpers import full_layout


@pytest.fixture(autouse=True)
def isolated_roots(monkeypatch):
    for key in ("BDSL_ENV", "BDSL_PROJECT_ROOT", "BDSL_DATA_ROOT", "BDSL_WORK_DIR",
                "K400_DATA_ROOT", "K400_STATE_ROOT", "K400_VIDEO_ROOT",
                "KAGGLE_KERNEL_RUN_TYPE", "COLAB_RELEASE_TAG"):
        monkeypatch.delenv(key, raising=False)


def test_pilot_state_is_canonical_but_videos_and_shared_assets_stay_separate():
    cfg = load_config(env="local", data="pilot50")
    root = Path(cfg["_meta"]["project_root"])
    version = root / "versions/pilot50"
    for key in ("features_dir", "runs_dir", "reports_dir", "demo_dir", "pilot_dest_dir", "annotations_dir"):
        assert Path(cfg["paths"][key]).is_relative_to(version)
    assert Path(cfg["data"]["video_root"]) == root / "dataset/pilot50_v1/videos"
    assert Path(cfg["paths"]["vrm_file"]) == root / "shared/models/vrm/Base_Female.vrm"
    annotation, reviewers = _annotation_paths(cfg)
    assert annotation.parent == version / "annotations"
    assert reviewers == root / "annotations/REVIEWERS.csv"


def test_k400_training_and_demo_use_the_same_canonical_state():
    cfg = load_config(env="local", data="kaggle400")
    root = Path(cfg["_meta"]["project_root"])
    version = root / "versions/k400"
    p, demo = paths(cfg), resolve_demo_paths(cfg)
    assert p["runs"] == demo["runs"] == version / "outputs/runs"
    assert p["data_dir"] == demo["data_dir"] == version / "data"
    assert Path(cfg["paths"]["demo_dir"]) == version / "demo"
    assert all(f.is_relative_to(version) for f in p["features"].values())
    assert p["videos"]["train"] == root / "kaggle/data/train/videos"
    pilot = load_config(env="local", data="pilot50")
    assert not Path(pilot["paths"]["runs_dir"]).is_relative_to(version)


def test_attached_data_and_explicit_external_video_roots(monkeypatch, tmp_path):
    attached = tmp_path / "attached"
    monkeypatch.setenv("K400_DATA_ROOT", str(attached))
    cfg = load_config(env="local", data="kaggle400")
    assert paths(cfg)["videos"]["train"] == attached / "data/train/videos"
    external = tmp_path / "read-only-videos"
    monkeypatch.setenv("K400_VIDEO_ROOT", str(external))
    cfg = load_config(env="local", data="kaggle400")
    assert paths(cfg)["videos"]["val"] == external / "val/videos"


def test_extraction_plan_keeps_metadata_and_external_videos_separate(tmp_path):
    metadata, videos, features = (tmp_path / n for n in ("metadata", "videos", "features"))
    (metadata / "train").mkdir(parents=True)
    pd.DataFrame([{"index": 7, "filename": "7.mp4", "display_w": 160, "display_h": 120,
                   "duration_s": 1.0}]).to_csv(metadata / "train/train_manifest.csv", index=False)
    rows = plan(metadata, features, ("train",), videos_dir=videos)
    assert rows[0]["video"] == videos / "train/videos/7.mp4"
    assert rows[0]["out"] == features / "train/7.npz"
    assert not videos.exists() and not features.exists()  # planning never touches video files


def test_split_verification_uses_external_synthetic_video_root(tmp_path):
    root, videos = tmp_path / "state", tmp_path / "external-videos"
    full_layout(root, with_features=False)
    for split in ("train", "val", "test"):
        (videos / split).mkdir(parents=True)
        shutil.move(str(root / "data" / split / "videos"), str(videos / split / "videos"))
    results = run_checks(root, [], require_videos=True, videos_dir=videos)
    assert all(r["status"] == "PASS" for r in results), results


def test_relocated_notebooks_remain_valid_without_executing_any_cell():
    root = find_project_root()
    for version, expected in (("pilot50", 7), ("k400", 10)):
        notebooks = sorted((root / "versions" / version / "notebooks").glob("*.ipynb"))
        assert len(notebooks) == expected
        for notebook in notebooks:
            document = json.loads(notebook.read_text(encoding="utf-8"))
            assert find_project_root(notebook.parent) == root
            for index, cell in enumerate(document["cells"]):
                if cell["cell_type"] == "code":
                    ast.parse("".join(cell["source"]), filename=f"{notebook.name}:cell{index}")
