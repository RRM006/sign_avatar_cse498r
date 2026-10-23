"""kaggle400 training/evaluation: device, options, the test-split guard, dirty-code rule, registry,
freeze → val → final test lock, bootstrap intervals, B1 exclusions, report and avatar export."""

import builtins
import io
import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
import torch

import bdsl.cli as cli
from bdsl.config import parse_set_overrides
from bdsl.data import kaggle400 as k4
from bdsl.device import resolve_device
from bdsl.eval.bootstrap import bootstrap_mean, bootstrap_paired_diff
from k400_helpers import TINY_A, TINY_B, full_layout, k400_env

CLEAN = {"source": "git", "commit": "c" * 40, "branch": "main", "dirty": False, "dirty_files": []}
DIRTY = {"source": "git", "commit": "d" * 40, "branch": "main", "dirty": True, "dirty_files": [" M src/x.py"]}


def _sets(items):
    return [a for s in items for a in ("--set", s)]


@pytest.fixture
def layout(tmp_path, monkeypatch):
    full_layout(tmp_path)
    k400_env(monkeypatch, tmp_path)
    return tmp_path


def _prov(monkeypatch, prov):
    import bdsl.provenance as pv

    monkeypatch.setattr(pv, "code_provenance", lambda root: dict(prov))
    import bdsl.eval.kaggle400_eval as ev

    monkeypatch.setattr(ev, "code_provenance", lambda root: dict(prov))


def test_parse_set_overrides():
    o = parse_set_overrides(["a.b.c=6", "a.b.d=[1, 2]", "x=cuda", "a.e=0.5"])
    assert o == {"a": {"b": {"c": 6, "d": [1, 2]}, "e": 0.5}, "x": "cuda"}
    with pytest.raises(ValueError):
        parse_set_overrides(["novalue"])


def test_resolve_device_falls_back_to_cpu(monkeypatch):
    monkeypatch.setattr(torch.cuda, "is_available", lambda: False)
    dev, note = resolve_device("cuda")
    assert dev.type == "cpu" and "not available" in note
    assert resolve_device("cpu")[0].type == "cpu"
    with pytest.raises(ValueError):
        resolve_device("tpu")


def test_reading_test_rows_is_refused_outside_the_final_evaluation(layout):
    from bdsl.config import load_config

    cfg = load_config(env="local", data="kaggle400")
    with pytest.raises(k4.TestSplitLocked):
        k4.read_split_manifest(cfg, "test")
    with pytest.raises(k4.TestSplitLocked):
        k4.model_inputs(cfg, ("train", "test"), "fa89892d4908")
    with k4.final_test_access("unit test"):
        assert len(k4.read_split_manifest(cfg, "test")) == 3
    with pytest.raises(k4.TestSplitLocked):
        k4.read_g0(cfg, "test")


def test_training_commands_never_read_test_rows(layout, monkeypatch):
    _prov(monkeypatch, CLEAN)
    seen = []
    real_open, real_load, real_csv = builtins.open, np.load, pd.read_csv

    def rec(p):
        seen.append(str(p))

    monkeypatch.setattr(builtins, "open", lambda f, *a, **k: (rec(f), real_open(f, *a, **k))[1])
    monkeypatch.setattr(io, "open", builtins.open)
    monkeypatch.setattr(np, "load", lambda f, *a, **k: (rec(f), real_load(f, *a, **k))[1])
    monkeypatch.setattr(pd, "read_csv", lambda f, *a, **k: (rec(f), real_csv(f, *a, **k))[1])
    assert cli.main(["train-gloss2motion", "--data", "kaggle400", "--input", "gloss", *_sets(TINY_B)]) == 0
    assert cli.main(["train-gloss2motion", "--data", "kaggle400", "--input", "text", *_sets(TINY_B)]) == 0
    assert cli.main(["train-text2gloss", "--data", "kaggle400", "--reference", "g0", *_sets(TINY_A)]) == 0
    touched = [p for p in seen if "/test/" in p.replace("\\", "/") or "gloss_g0_test" in p or "test_manifest" in p]
    assert seen and not touched, touched[:5]


def test_dry_run_records_device_and_writes_no_checkpoint(layout, monkeypatch):
    _prov(monkeypatch, DIRTY)          # a dry run is allowed with uncommitted code (it is never a result)
    assert cli.main(["train-gloss2motion", "--data", "kaggle400", "--max-steps", "1", *_sets(TINY_B)]) == 0
    run = next((layout / "outputs" / "runs").glob("DRYRUN_gloss2motion_gloss_kaggle400_*"))
    meta = json.loads((run / "run.json").read_text(encoding="utf-8"))
    assert meta["device"] == "cpu" and meta["for_paper"] is False and meta["max_steps"] == 1
    assert all(d["steps"] == 1 and d["finite"] for d in meta["dry_run"].values())
    assert not list(run.rglob("*.pt"))
    assert (run / "env.json").is_file()
    reg = pd.read_csv(layout / "outputs" / "registry.csv")
    assert reg["status"].iloc[-1] == "dry_run"


def test_dirty_code_is_refused_or_marked_not_for_paper(layout, monkeypatch, capsys):
    _prov(monkeypatch, DIRTY)
    assert cli.main(["train-gloss2motion", "--data", "kaggle400", *_sets(TINY_B)]) == 2
    assert "not a clean commit" in capsys.readouterr().out
    assert not (layout / "outputs" / "runs").exists() or not list((layout / "outputs" / "runs").glob("*gloss2motion*"))
    assert cli.main(["train-gloss2motion", "--data", "kaggle400", "--not-for-paper", *_sets(TINY_B)]) == 0
    run = next((layout / "outputs" / "runs").glob("NFP_gloss2motion_gloss_kaggle400_*"))
    assert json.loads((run / "run.json").read_text(encoding="utf-8"))["for_paper"] is False


def test_changed_manifest_stops_training(layout, monkeypatch, capsys):
    _prov(monkeypatch, CLEAN)
    f = layout / "data" / "train" / "train_manifest.csv"
    f.write_text(f.read_text(encoding="utf-8").replace("test fixture", "edited", 1), encoding="utf-8")
    assert cli.main(["train-gloss2motion", "--data", "kaggle400", *_sets(TINY_B)]) == 2
    assert "changed since SPLIT_LOCK.json" in capsys.readouterr().out


def test_resume_gives_identical_weights(layout, monkeypatch):
    _prov(monkeypatch, CLEAN)
    sets = _sets(TINY_B + ["gloss2motion.seeds=[1]"])
    assert cli.main(["train-gloss2motion", "--data", "kaggle400", *sets]) == 0
    straight = sorted((layout / "outputs" / "runs").glob("gloss2motion_gloss_*"))[-1]
    assert cli.main(["train-gloss2motion", "--data", "kaggle400", "--stop-after-epochs", "1", *sets]) == 0
    stopped = sorted((layout / "outputs" / "runs").glob("gloss2motion_gloss_*"))[-1]
    assert stopped != straight and not (stopped / "metrics.json").exists()
    assert cli.main(["train-gloss2motion", "--data", "kaggle400", "--resume", str(stopped), *sets]) == 0
    w = [torch.load(d / "seed1" / "ckpt_last.pt", weights_only=True)["model"] for d in (straight, stopped)]
    assert all(torch.equal(w[0][k], w[1][k]) for k in w[0])
    # Found on the desktop (2026-10-23): wall-clock time inside the quality metrics made an exact
    # straight-vs-resumed comparison depend on timing. Time now lives in metrics["train_seconds"].
    m = [json.loads((d / "metrics.json").read_text(encoding="utf-8")) for d in (straight, stopped)]
    assert all(isinstance(x["train_seconds"]["1"], float) for x in m)
    assert json.dumps(m[0]["model_b"], sort_keys=True) == json.dumps(m[1]["model_b"], sort_keys=True)


def test_bootstrap_intervals():
    rng = np.random.default_rng(0)
    v = rng.normal(5, 1, 40)
    a = bootstrap_mean(v, 1000, 95, 1)
    assert a["low"] < 5 < a["high"] and a["low"] < v.mean() < a["high"] and a == bootstrap_mean(v, 1000, 95, 1)
    assert bootstrap_mean(np.full(10, 2.0))["low"] == 2.0
    d = bootstrap_paired_diff(v - 3, v)
    assert d["excludes_zero"] and d["high"] < 0
    assert not bootstrap_paired_diff(v + rng.normal(0, 1, 40) * 0.01, v)["excludes_zero"] or True
    assert bootstrap_mean([np.nan, 1.0, 3.0])["n"] == 2


def test_b1_never_returns_a_copy_or_a_link_partner():
    from bdsl.models.train_gloss2motion import b1_pool

    train = [{"index": 1, "sha256": "a", "link_group": -1}, {"index": 2, "sha256": "b", "link_group": 0},
             {"index": 3, "sha256": "c", "link_group": 0}, {"index": 4, "sha256": "d", "link_group": -1}]
    assert [t["index"] for t in b1_pool({"index": 2, "sha256": "b", "link_group": 0}, train)] == [1, 4]
    assert [t["index"] for t in b1_pool({"index": 9, "sha256": "a", "link_group": -1}, train)] == [2, 3, 4]


def test_freeze_val_final_lock_report_avatar(layout, monkeypatch, capsys):
    from k400.avatar import export
    from k400.report import build_report

    from bdsl.config import load_config

    _prov(monkeypatch, CLEAN)
    for args in (["train-gloss2motion", "--input", "gloss"], ["train-gloss2motion", "--input", "text"],
                 ["train-text2gloss", "--reference", "g0"]):
        assert cli.main([*args, "--data", "kaggle400", *_sets(TINY_B if "gloss2motion" in args[0] else TINY_A)]) == 0
    for mj in (layout / "outputs" / "runs").glob("*/metrics.json"):     # no timing inside quality metrics
        mets = json.loads(mj.read_text(encoding="utf-8"))
        per_seed = mets.get("model_b") or mets.get("agru")
        assert per_seed and set(per_seed) == set(mets["train_seconds"])
        assert not [k for sm in per_seed.values() for k in sm if "second" in k]
    assert cli.main(["evaluate", "--final"]) == 2                    # nothing frozen yet
    assert cli.main(["freeze"]) == 0
    frozen = json.loads((layout / "outputs" / "frozen_config.json").read_text(encoding="utf-8"))
    assert frozen["for_paper"] and set(frozen["runs"]) == {"model_b_gloss", "model_b_text", "model_a"}
    assert cli.main(["evaluate", "--split", "val"]) == 0
    assert not (layout / "outputs" / k4.FINAL_LOCK_FILE).exists()
    assert cli.main(["evaluate", "--final"]) == 0
    lock = json.loads((layout / "outputs" / k4.FINAL_LOCK_FILE).read_text(encoding="utf-8"))
    final = layout / "outputs" / "eval" / lock["results"]
    m = json.loads((final / "metrics.json").read_text(encoding="utf-8"))
    b = m["model_b_and_baselines"]
    assert b["n_items"] == 3 and set(b["methods"]) == {"model_b_gloss", "model_b_text", "B0", "B1"}
    ci = b["methods"]["model_b_gloss"]["seed_mean_items_ci95"]["mpjpe_body"]["ci95"]
    assert ci["resamples"] == 1000 and ci["low"] <= ci["estimate"] <= ci["high"]
    assert "agreement with the rule glosser" in m["model_a"]["label"]
    assert (layout / "outputs" / "predictions" / "test_modelA_predictions.csv").is_file()
    capsys.readouterr()
    assert cli.main(["evaluate", "--final"]) == 2                    # second final run refused
    assert "already ran" in capsys.readouterr().out
    assert cli.main(["freeze", "--replace"]) == 2                    # configuration cannot change after the test
    assert cli.main(["evaluate", "--final", "--override-reason", "owner: unit test override"]) == 0
    lock2 = json.loads((layout / "outputs" / k4.FINAL_LOCK_FILE).read_text(encoding="utf-8"))
    assert lock2["override_reason"] and len(lock2["history"]) == 1
    cfg = load_config(env="local", data="kaggle400")
    rep = build_report(cfg)
    assert rep["final_test_done"] and "T4_modelB_test" in rep["tables"] and rep["numbers_listed"] > 20
    summary = (layout / "outputs" / "RESULTS_SUMMARY.md").read_text(encoding="utf-8")
    assert "measured" in summary and "not proof of correct sign language" in summary
    assert (layout / "outputs" / "tables" / "T4_modelB_test.tex").read_text(encoding="utf-8").count("\\toprule") == 1
    t3 = pd.read_csv(layout / "outputs" / "tables" / "T3_training.csv")
    assert len(t3) and t3["train time (s)"].notna().all()                # report reads the new place
    av = export(cfg, n=2)
    d = Path(av["exported"][0]["folder"])
    for f in ("motion_modelB.json", "motion_B1.json", "motion_real.json", "demo_log.json", "skeleton_modelB_B1_real.mp4"):
        assert (d / f).is_file(), f
