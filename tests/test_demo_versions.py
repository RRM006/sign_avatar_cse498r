"""Version-aware demo checks, using synthetic temporary data only (never research results)."""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path

import numpy as np
import pytest
import torch
import yaml

from bdsl import cli
from bdsl.avatar import demo
from bdsl.avatar.demo_inputs import load_demo_inputs, resolve_demo_paths
from bdsl.config import config_hash, load_config, parse_set_overrides
from bdsl.data import kaggle400 as split_data
from bdsl.features.normalize import Standardizer
from bdsl.models.gloss2motion import Gloss2Motion
from bdsl.models.text2gloss import Vocab, vocab_hash
from bdsl.models.train_gloss2motion import RESUME_KEYS, load_items
from k400.gloss import build_vocabs, write_corpus
from k400_helpers import FEAT_VER, TINY_B, full_layout


@pytest.fixture(autouse=True)
def clean_demo_env(monkeypatch):
    for key in ("BDSL_ENV", "BDSL_PROJECT_ROOT", "BDSL_DATA_ROOT", "BDSL_WORK_DIR", "K400_DATA_ROOT",
                "K400_STATE_ROOT", "K400_VIDEO_ROOT", "KAGGLE_KERNEL_RUN_TYPE", "COLAB_RELEASE_TAG"):
        monkeypatch.delenv(key, raising=False)


def _cli_stub(monkeypatch):
    seen = {}

    def run(cfg, sentence, out_root, model_run, seed):
        seen.update(cfg=cfg, sentence=sentence, out_root=out_root, model_run=model_run, seed=seed)
        return {"out_dir": str(out_root / "synthetic"), "log": {
            "g0_gloss": "synthetic", "model_b": {"predicted_frames": 2, "unknown_tokens": []},
            "b1": {"index": 1, "sentence_norm": "synthetic", "frames": 2}}}

    monkeypatch.setattr(demo, "run_demo", run)
    return seen


def test_cli_default_is_pilot50_and_uses_its_output_path(monkeypatch):
    seen = _cli_stub(monkeypatch)
    assert cli.main(["demo", "--sentence", "আমি স্কুল যাই"]) == 0
    assert seen["cfg"]["data"]["name"] == "pilot50"
    assert seen["out_root"] == Path(seen["cfg"]["paths"]["demo_dir"])
    assert seen["model_run"] == "gloss2motion_gloss_pilot50_20261022T133822Z"
    assert seen["seed"] == 42


def test_cli_selects_k400_and_honours_out_root(monkeypatch, tmp_path):
    seen = _cli_stub(monkeypatch)
    assert cli.main(["demo", "--data", "kaggle400", "--sentence", "আমার নানা অনেক ভালো",
                     "--model-run", "chosen-run", "--out-root", str(tmp_path), "--seed", "42"]) == 0
    assert seen["out_root"] == tmp_path
    assert seen["cfg"]["data"]["name"] == "kaggle400"
    root = Path(seen["cfg"]["_meta"]["project_root"])
    paths = resolve_demo_paths(seen["cfg"])
    assert paths["runs"] == root / "versions/k400/outputs/runs"
    assert paths["data_dir"] == root / "versions/k400/data"


@pytest.mark.parametrize("name", ["does_not_exist", "../pilot50"])
def test_unknown_or_invalid_version_fails_clearly(name, capsys):
    assert cli.main(["demo", "--data", name, "--sentence", "synthetic"]) == 2
    assert "Demo refused" in capsys.readouterr().err


@pytest.mark.parametrize("env", ["local", "kaggle", "colab"])
def test_demo_paths_do_not_change_the_existing_config_hash(env):
    cfg = load_config(env=env, data="kaggle400")
    without_demo = copy.deepcopy(cfg)
    without_demo["paths"].pop("demo_data_root")
    without_demo["paths"].pop("demo_state_root")
    assert config_hash(without_demo) == cfg["_meta"]["config_hash"]
    if env == "kaggle":
        # Saved by the original, non-overfit k400 training runs.
        assert config_hash(cfg) == "83e62cae0fe05fcd092bbd50ad93a3d6143b4e82b9d833b172d2d499e5f5d453"


def test_temporary_future_config_resolves_without_a_new_code_branch(tmp_path):
    config_dir = tmp_path / "configs"
    (config_dir / "data").mkdir(parents=True)
    (config_dir / "env").mkdir()
    (config_dir / "base.yaml").write_text("paths: {}\n", encoding="utf-8")
    (config_dir / "env/local.yaml").write_text("env: {name: local}\n", encoding="utf-8")
    (config_dir / "data/kaggle600.yaml").write_text(yaml.safe_dump({
        "data": {"name": "kaggle600"}, "paths": {
            "demo_data_root": "${project_root}/future-input",
            "demo_state_root": "${project_root}/future-state"}}), encoding="utf-8")
    cfg = load_config(env="local", data="kaggle600", project_root=tmp_path)
    paths = resolve_demo_paths(cfg)
    assert paths["data"] == "kaggle600"
    assert paths["runs"] == tmp_path / "future-state/outputs/runs"
    assert paths["data_dir"] == tmp_path / "future-input/data"
    assert Path(cfg["paths"]["demo_dir"]) == tmp_path / "future-state/demo"
    assert Path(cfg["paths"]["work_dir"]) == tmp_path / "future-state/work"
    assert not (tmp_path / "future-state").exists()  # resolution is read-only


@pytest.fixture
def synthetic_run(tmp_path):
    root = tmp_path / "state"
    info = full_layout(root, with_videos=False)
    write_corpus(info["subset"], root / "processed/glosses/g0_corpus_v1.txt")
    build_vocabs(root / "processed/glosses", root / "processed/vocab")
    overrides = parse_set_overrides(TINY_B + ["gloss2motion.seeds=[42]"])
    overrides["paths"] = {"demo_data_root": str(root), "demo_state_root": str(root)}
    cfg = load_config(env="local", data="kaggle400", overrides=overrides)
    paths = resolve_demo_paths(cfg)
    adapted = paths["reader_config"]
    lock = split_data.check_split_lock(adapted)
    rows, problems, inputs_sha = split_data.model_inputs(adapted, split_data.TRAINING_SPLITS, FEAT_VER)
    assert not problems
    items = load_items(rows, None, "gloss", cfg["gloss2motion"]["max_gap"])
    train = [it for it in items if it["split"] == "train"]
    vocab = Vocab([t for it in train for t in it["tokens"]])
    std = Standardizer.fit(train)
    gcfg = cfg["gloss2motion"]
    meta = {"data": "kaggle400", "input": "gloss", "seeds": [42], "overfit": None,
            "label": "synthetic test only", "feat_ver": FEAT_VER, "fps": 15,
            "counts": rows["split"].value_counts().to_dict(), "inputs_sha256": inputs_sha,
            "split_lock_sha256": lock["lock_sha256"], "pilot_manifest_sha256": lock["lock_sha256"],
            "g0_files_sha256": split_data.glosses_sha256(adapted, split_data.TRAINING_SPLITS),
            "gloss2motion_config": gcfg,
            "gloss2motion_config_sha256": hashlib.sha256(json.dumps(gcfg, sort_keys=True).encode()).hexdigest(),
            "vocab_size": len(vocab), "vocab_sha256": vocab_hash(vocab, vocab),
            "standardizer_sha256": hashlib.sha256(std.mean.tobytes() + std.sd.tobytes()).hexdigest()}
    run_dir = paths["runs"] / "synthetic_gloss_run"
    (run_dir / "seed42").mkdir(parents=True)
    (run_dir / "run.json").write_text(json.dumps(meta), encoding="utf-8")
    np.savez(run_dir / "standardizer.npz", mean=std.mean, sd=std.sd)
    model = Gloss2Motion(len(vocab), **gcfg["model"])
    ck_meta = {k: meta[k] for k in RESUME_KEYS} | {"seed": 42}
    torch.save({"model": model.state_dict(), "meta": ck_meta}, run_dir / "seed42/ckpt_best.pt")
    return cfg, run_dir, meta


def test_split_inputs_reconstruct_training_vocab_without_reading_test(synthetic_run, monkeypatch):
    cfg, run_dir, _ = synthetic_run
    seen = []
    guard = split_data._guard

    def train_or_val_only(split):
        assert split != "test"
        seen.append(split)
        guard(split)

    monkeypatch.setattr(split_data, "_guard", train_or_val_only)
    ctx = load_demo_inputs(cfg, run_dir.name, 42)
    assert set(seen) == {"train", "val"}
    assert len(ctx.train) == 12 and len(ctx.items) == 15
    assert all(ctx.checks.values())


@pytest.mark.parametrize("field", ["data", "inputs_sha256", "vocab_sha256", "standardizer_sha256",
                                  "split_lock_sha256", "gloss2motion_config_sha256"])
def test_foreign_run_or_changed_fingerprint_is_refused(synthetic_run, field):
    cfg, run_dir, meta = synthetic_run
    meta[field] = "pilot50" if field == "data" else "changed"
    (run_dir / "run.json").write_text(json.dumps(meta), encoding="utf-8")
    with pytest.raises(ValueError):
        load_demo_inputs(cfg, run_dir.name, 42)


def test_run_outside_this_versions_root_is_refused(synthetic_run, tmp_path):
    cfg, _, _ = synthetic_run
    with pytest.raises(ValueError, match="configured runs folder"):
        load_demo_inputs(cfg, str(tmp_path / "other-version/run"), 42)


def test_declared_future_version_uses_the_same_input_checks(synthetic_run):
    cfg, run_dir, meta = synthetic_run
    cfg["data"]["name"] = "kaggle600"  # synthetic fixture only; no real version folder
    meta["data"] = "kaggle600"
    (run_dir / "run.json").write_text(json.dumps(meta), encoding="utf-8")
    ctx = load_demo_inputs(cfg, run_dir.name, 42)
    assert ctx.paths["data"] == "kaggle600" and all(ctx.checks.values())


def test_missing_checkpoint_is_refused(synthetic_run):
    cfg, run_dir, meta = synthetic_run
    meta["seeds"] = [43]
    (run_dir / "run.json").write_text(json.dumps(meta), encoding="utf-8")
    with pytest.raises(FileNotFoundError, match="missing best checkpoint"):
        load_demo_inputs(cfg, run_dir.name, 43)


def test_synthetic_demo_loads_on_cpu_and_writes_only_to_out_root(synthetic_run, tmp_path, monkeypatch):
    cfg, run_dir, _ = synthetic_run
    calls = []
    real_load = torch.load

    def cpu_load(*args, **kwargs):
        calls.append(kwargs)
        return real_load(*args, **kwargs)

    monkeypatch.setattr(torch, "load", cpu_load)
    ctx = load_demo_inputs(cfg, run_dir.name, 42)
    sentence = ctx.rows.loc[ctx.rows["split"] == "val", "sentence_raw"].iloc[0]
    out_root = tmp_path / "new-demo-outputs"
    before = {p.relative_to(run_dir): p.read_bytes() for p in run_dir.rglob("*") if p.is_file()}
    result = demo.run_demo(cfg, sentence, out_root, run_dir.name, 42)
    out = Path(result["out_dir"])
    assert out.parent == out_root
    assert {p.name for p in out.iterdir()} == {"motion_modelB.json", "motion_B1.json",
        "skeleton_side_by_side.mp4", "demo_log.json", "LIMITATIONS.md"}
    assert result["log"]["data"] == "kaggle400"
    assert result["log"]["b1"]["split"] == "train"
    assert result["log"]["input_splits"] == ["train", "val"]
    assert calls == [{"weights_only": True, "map_location": "cpu"}]
    assert before == {p.relative_to(run_dir): p.read_bytes() for p in run_dir.rglob("*") if p.is_file()}


def test_new_output_folder_never_overwrites_an_existing_demo(tmp_path):
    first = demo._new_output(tmp_path, "synthetic")
    marker = first / "keep.txt"
    marker.write_text("keep", encoding="utf-8")
    second = demo._new_output(tmp_path, "synthetic")
    assert second != first and marker.read_text(encoding="utf-8") == "keep"


def test_foreign_checkpoint_metadata_is_refused_before_writing(synthetic_run, tmp_path, monkeypatch):
    cfg, run_dir, _ = synthetic_run
    real_load = torch.load

    def foreign_checkpoint(*args, **kwargs):
        ck = real_load(*args, **kwargs)
        ck["meta"]["inputs_sha256"] = "another-run"
        return ck

    monkeypatch.setattr(torch, "load", foreign_checkpoint)
    out_root = tmp_path / "must-not-be-created"
    with pytest.raises(ValueError, match="checkpoint does not belong"):
        demo.run_demo(cfg, "synthetic", out_root, run_dir.name, 42)
    assert not out_root.exists()
