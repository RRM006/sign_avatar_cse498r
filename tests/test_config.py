"""Layered config: merging, env selection, env-var roots, interpolation and the config hash."""

from pathlib import Path

import pytest

from bdsl.config import ENV_NAMES, config_hash, deep_merge, detect_env, load_config

_ENV_VARS = ("BDSL_ENV", "BDSL_DATA_ROOT", "BDSL_WORK_DIR", "BDSL_PROJECT_ROOT",
             "KAGGLE_KERNEL_RUN_TYPE", "COLAB_RELEASE_TAG")


@pytest.fixture(autouse=True)
def clean_env(monkeypatch):
    for var in _ENV_VARS:
        monkeypatch.delenv(var, raising=False)


def test_local_defaults_resolve_inside_project():
    cfg = load_config(env="local")
    root = Path(cfg["_meta"]["project_root"])
    assert cfg["env"]["name"] == "local"
    assert Path(cfg["paths"]["work_dir"]) == root / "work"
    assert Path(cfg["paths"]["reports_dir"]) == root / "work" / "reports"
    assert Path(cfg["data"]["sample_dir"]) == root / "dataset" / "initial_dataset" / "videos"
    assert "${" not in str(cfg)


@pytest.mark.parametrize("env", ENV_NAMES)
def test_every_env_layer_loads(env):
    cfg = load_config(env=env, data="full")
    assert cfg["env"]["name"] == env
    assert cfg["_meta"]["layers"][-1] == "configs/data/full.yaml"


def test_kaggle_layer_overrides_roots_and_derived_paths_follow():
    cfg = load_config(env="kaggle")
    assert cfg["paths"]["work_dir"] == "/kaggle/working/work"
    assert cfg["paths"]["models_dir"] == "/kaggle/working/work/models"


def test_env_var_work_dir_moves_every_derived_path(monkeypatch, tmp_path):
    monkeypatch.setenv("BDSL_WORK_DIR", tmp_path.as_posix())
    cfg = load_config(env="local")
    assert Path(cfg["paths"]["work_dir"]) == tmp_path
    assert Path(cfg["paths"]["reports_dir"]) == tmp_path / "reports"
    assert cfg["_meta"]["env_var_overrides"] == ["BDSL_WORK_DIR"]


def test_data_layers_select_video_root():
    pilot = load_config(env="local", data="pilot50")
    full = load_config(env="local", data="full")
    assert pilot["data"]["video_root"].endswith("dataset/pilot50_v1/videos")
    assert full["data"]["video_root"].endswith("dataset/initial_dataset/SIGN_LANGUAGE_DATA")


def test_hash_ignores_machine_paths_but_not_settings(monkeypatch, tmp_path):
    base = load_config(env="local")
    monkeypatch.setenv("BDSL_WORK_DIR", tmp_path.as_posix())
    moved = load_config(env="local")
    assert moved["_meta"]["config_hash"] == base["_meta"]["config_hash"]
    reseeded = load_config(env="local", overrides={"project": {"seed": 7}})
    assert reseeded["_meta"]["config_hash"] != base["_meta"]["config_hash"]
    assert config_hash(base) == base["_meta"]["config_hash"]


def test_detect_env(monkeypatch):
    assert detect_env() == "local"
    monkeypatch.setenv("KAGGLE_KERNEL_RUN_TYPE", "Interactive")
    assert detect_env() == "kaggle"
    monkeypatch.setenv("BDSL_ENV", "colab")
    assert detect_env() == "colab"


def test_unknown_env_and_reference_fail_loudly():
    with pytest.raises(ValueError):
        load_config(env="laptop")
    with pytest.raises(KeyError):
        load_config(env="local", overrides={"paths": {"work_dir": "${no.such.key}"}})


def test_deep_merge_keeps_unrelated_keys():
    merged = deep_merge({"a": {"x": 1, "y": 2}, "b": 1}, {"a": {"y": 3}})
    assert merged == {"a": {"x": 1, "y": 3}, "b": 1}
