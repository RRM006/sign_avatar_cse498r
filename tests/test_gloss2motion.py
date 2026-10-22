"""Model B (Day 4): motion features, masks, masked loss, metrics, baselines, training run and resume."""

import copy
import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
import torch

from bdsl.eval.motion_metrics import dtw_cost, item_metrics, mpjpe, resample
from bdsl.features.normalize import N_FEAT, PARTS, Standardizer, clip_motion, expand_mask, interpolate_gaps
from bdsl.models.baselines import b0_mean_motion, b1_retrieve
from bdsl.models.gloss2motion import Gloss2Motion, masked_loss, time_code, value_weights
from bdsl.models.train_gloss2motion import ResumeMismatch, input_tokens, run


def test_interpolate_only_short_interior_gaps():
    x = np.arange(10, dtype=float)[:, None].repeat(2, 1)
    present = np.array([1, 0, 0, 1, 0, 0, 0, 0, 0, 1], dtype=bool)
    y, p, interp = interpolate_gaps(np.where(present[:, None], x, np.nan), present, max_gap=2)
    assert np.allclose(y[1:3, 0], [1, 2]) and interp[1:3].all() and p[:4].all()
    assert not p[4:9].any() and not interp[4:9].any()         # a 5-frame gap stays missing


def _fake_npz(path, t=20, missing_right=(5, 15), seed=0):
    rng = np.random.default_rng(seed)
    pose = rng.normal(0, 0.1, (t, 33, 3))
    pose[:, 11] = [0.15, 0, 0]
    pose[:, 12] = [-0.15, 0, 0]                                 # shoulder width 0.3 m
    lh, rh = rng.normal(0, 0.05, (t, 21, 3)), rng.normal(0, 0.05, (t, 21, 3))
    mask = np.ones((t, 4), dtype=np.uint8)
    a, b = missing_right
    rh[a:b] = np.nan
    mask[a:b, 2] = 0
    np.savez(path, pose_world=pose, lhand_world=lh, rhand_world=rh, blendshapes=rng.uniform(0, 1, (t, 52)),
             head_rot=rng.normal(0, 5, (t, 3)), mask=mask)
    return path


def test_clip_motion_layout_and_masks(tmp_path):
    c = clip_motion(_fake_npz(tmp_path / "1.npz"), max_gap=5)
    assert c["x"].shape == (20, N_FEAT) and c["mask"].shape == (20, 4)
    assert c["shoulder_width_m"] == pytest.approx(0.3)
    body = c["x"][:, PARTS["body"]].reshape(20, 9, 3)
    assert np.allclose(body[:, 1], [0.5, 0, 0]) and np.allclose(body[:, 2], [-0.5, 0, 0])
    assert not c["mask"][5:15, 2].any() and (c["x"][5:15, PARTS["rhand"]] == 0).all()
    lh = c["x"][:, PARTS["lhand"]].reshape(20, 21, 3)
    assert np.allclose(lh[:, 0], 0) and not np.allclose(lh[:, 1], 0)   # wrist-relative hand shape
    assert not np.isnan(c["x"]).any()


def test_masked_loss_ignores_missing_values():
    torch.manual_seed(0)
    pred = torch.randn(2, 6, N_FEAT, requires_grad=True)
    target = torch.randn(2, 6, N_FEAT)
    vm = torch.ones(2, 6, N_FEAT, dtype=torch.bool)
    vm[0, :, PARTS["rhand"]] = False                            # right hand missing in item 0
    vm[1, 4:] = False                                           # padding after 4 frames in item 1
    n, log_len, w = torch.tensor([6, 4]), torch.zeros(2), value_weights(2.0)
    loss, _ = masked_loss(pred, target, vm, n, log_len, w, 0.5, 0.1)
    loss.backward()
    assert (pred.grad[0, :, PARTS["rhand"]] == 0).all() and (pred.grad[1, 4:] == 0).all()
    changed = target.clone()
    changed[~vm] = 1e6                                          # garbage where nothing is present
    assert masked_loss(pred, changed, vm, n, log_len, w, 0.5, 0.1)[0].item() == pytest.approx(loss.item())
    assert masked_loss(pred, target, vm, n, log_len, w, 0.5, 0.1)[1]["len"] == pytest.approx(
        float((torch.log(torch.tensor(6.0)) + torch.log(torch.tensor(4.0))) / 2))


def test_model_shapes_and_time_code():
    m = Gloss2Motion(10, d=32, heads=4, enc_layers=1, dec_layers=1, ff=64, dropout=0.0)
    out, log_len = m(torch.tensor([[4, 5, 0], [6, 7, 8]]), torch.tensor([7, 3]))
    assert out.shape == (2, 7, N_FEAT) and log_len.shape == (2,)
    gen = m.generate(torch.tensor([[4, 5, 0]]), max_frames=50)
    assert 2 <= len(gen[0]) <= 50
    code = time_code(torch.tensor([10]), 10, 16)
    assert not torch.allclose(code[0, 4], code[0, 5])


def test_metrics_and_baselines():
    t = np.linspace(0, 1, 30)[:, None]
    gt = np.sin(2 * np.pi * t) * np.ones((1, N_FEAT))
    mask = np.ones((30, 4), dtype=bool)
    assert mpjpe(gt, gt, mask)["body"] == pytest.approx(0)
    assert mpjpe(resample(gt, 45), gt, mask)["body"] < 1e-2  # same motion, other length
    assert dtw_cost(np.zeros((5, 7))) == 0
    m = item_metrics(gt, gt, mask, fps=15, dtw=True)
    assert m["dtw_body"] == pytest.approx(0) and m["velocity_ratio"] == pytest.approx(1)
    zs = [np.ones((10, N_FEAT)), 3 * np.ones((20, N_FEAT))]
    b0 = b0_mean_motion(zs, [np.ones_like(z, dtype=bool) for z in zs])
    assert b0.shape == (15, N_FEAT) and np.allclose(b0, 2)
    assert b1_retrieve(["a", "b"], [["c"], ["a", "x"], ["a", "b"]], [5, 6, 7]) == 2
    assert b1_retrieve(["a"], [["a", "b"], ["a", "c"]], [9, 3]) == 1  # tie → lower Index


def test_standardizer_uses_present_values_only():
    clips = [{"x": np.full((4, N_FEAT), 2.0, dtype=np.float32), "mask": np.ones((4, 4), dtype=bool)}]
    clips[0]["mask"][:2, 2] = False
    clips[0]["x"][:2, PARTS["rhand"]] = 100.0
    s = Standardizer.fit(clips)
    assert np.allclose(s.mean, 2.0)
    z = s.apply(clips[0]["x"], clips[0]["mask"])
    assert (z[:2, PARTS["rhand"]] == 0).all()


def test_input_tokens():
    row = {"gloss_auto": "আমি স্কুল? যাব? NOT", "tags_auto": "neg", "sentence_norm": "আমি স্কুলে যাব না"}
    assert input_tokens(row, "gloss") == ["<neg>", "আমি", "স্কুল", "যাব", "NOT"]
    assert input_tokens(row, "text") == ["আমি", "স্কুলে", "যাব", "না"]


TINY = {"feat_ver": "x", "max_gap": 5, "model": {"d": 32, "heads": 4, "enc_layers": 1, "dec_layers": 1, "ff": 64,
                                                 "dropout": 0.0},
        "loss": {"hand_weight": 2.0, "lambda_vel": 0.5, "lambda_len": 0.1},
        "train": {"lr": 0.003, "weight_decay": 0.0, "batch_size": 4, "max_epochs": 8, "patience": 50, "clip": 1.0,
                  "overfit_epochs": 150},
        "max_frames": 40, "seeds": [1]}


def _setup(tmp_path):
    feats = tmp_path / "feats"
    feats.mkdir()
    splits = ["train"] * 4 + ["val", "test"]
    words = ["আমি স্কুল যাব", "আমি অফিস যাব", "তুমি স্কুল যাব", "আমি বাসা যাব", "তুমি অফিস যাব", "আমি স্কুল যাব না"]
    for i in range(6):
        _fake_npz(feats / f"{i}.npz", t=12 + 2 * i, seed=i)
    df = pd.DataFrame({"index": [str(i) for i in range(6)], "split": splits, "sentence_norm": words,
                       "gloss_auto": [w.replace(" ", "? ") + "?" for w in words], "tags_auto": [""] * 5 + ["neg"]})
    cfg = {"gloss2motion": TINY, "features": {"fps": 15}, "_meta": {"config_hash": "h", "project_root": str(tmp_path)}}
    return cfg, df, feats


def _run(tmp_path, cfg, df, feats, **kw):
    return run(cfg, df, mode=kw.pop("mode", "gloss"), features_dir=feats, pilot_manifest_sha256="m",
               inputs_sha256=kw.pop("inputs_sha256", "i"), runs_root=tmp_path / "runs", **kw)


def test_overfit_one_clip_and_outputs(tmp_path):
    cfg, df, feats = _setup(tmp_path)
    res = _run(tmp_path, cfg, df, feats, overfit=1)
    d = Path(res["run_dir"])
    curve = pd.read_csv(d / "seed1" / "curves.csv")
    assert curve["monitor_pos_l1"].iloc[-1] < 0.25 * curve["monitor_pos_l1"].iloc[0]
    assert (d / "seed1" / "predictions" / "0.npz").exists() and (d / "metrics.json").exists()
    with np.load(d / "seed1" / "predictions" / "0.npz") as z:
        assert z["body"].shape[1:] == (9, 3) and z["rhand"].shape[1:] == (21, 3)


def test_full_run_text_ablation_and_resume(tmp_path):
    cfg, df, feats = _setup(tmp_path)
    straight = _run(tmp_path / "a", cfg, df, feats, mode="text")
    m = straight["metrics"]
    assert set(m["model_b_mean_sd"]) == {"train", "val", "test"} and "dtw_body" in m["B1"]["val"]
    assert m["B0"]["val"]["n"] == 1
    stopped = _run(tmp_path / "b", cfg, df, feats, mode="text", stop_after=3)
    assert not stopped["finished"]
    resumed = _run(tmp_path / "b", cfg, df, feats, mode="text", run_dir=Path(stopped["run_dir"]))
    w = [torch.load(Path(r["run_dir"]) / "seed1" / "ckpt_last.pt", weights_only=True)["model"] for r in (straight, resumed)]
    assert all(torch.equal(w[0][k], w[1][k]) for k in w[0])
    # json compares NaN (diversity of a 1-item split) as equal text
    assert json.dumps(straight["metrics"]["model_b"], sort_keys=True) == json.dumps(resumed["metrics"]["model_b"], sort_keys=True)
    with pytest.raises(ResumeMismatch):
        _run(tmp_path / "b", cfg, df, feats, mode="text", inputs_sha256="changed", run_dir=Path(stopped["run_dir"]))


def test_cli_refuses_inputs_that_fail_checks(tmp_path, monkeypatch, capsys):
    import bdsl.cli as cli

    pilot = tmp_path / "pilot"
    pilot.mkdir()
    (pilot / "pilot50_manifest.csv").write_text("index,split\n1,train\n", encoding="utf-8")
    ann = tmp_path / "ann.csv"
    cols = cli.MODEL_B_INPUT_COLUMNS
    pd.DataFrame([["1", "val", "আমি", "আমি", "norm_v1", "G0-v0.1", "আমি", ""]], columns=cols).to_csv(ann, index=False)
    cfg = {"paths": {"pilot_dest_dir": str(pilot), "features_dir": str(tmp_path / "f"), "runs_dir": str(tmp_path / "r")},
           "annotations": {"g0_ver": "G0-v0.1"}, "gloss2motion": copy.deepcopy(TINY)}
    monkeypatch.setattr(cli, "_annotation_paths", lambda c: (ann, None))
    monkeypatch.setattr(cli, "load_config", lambda **kw: cfg)
    assert cli.main(["train-gloss2motion"]) == 2
    out = capsys.readouterr().out
    assert "split differs" in out and "no features" in out and not (tmp_path / "r").exists()
