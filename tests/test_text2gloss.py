"""Model A (Day 3 Step 1): metrics, G0 baseline, A-GRU overfit, checkpoint resume and the training guard."""

import copy
import json
from pathlib import Path

import pandas as pd
import pytest
import torch

from bdsl.eval.text_metrics import edit_distance, exact_match, item_wer, score, tag_accuracy, wer
from bdsl.models.baselines import g0_gloss, g0_tags
from bdsl.models.text2gloss import Vocab, split_tags
from bdsl.models.train_text2gloss import ResumeMismatch, run
from bdsl.text.annotations import COLUMNS, REVIEWER_COLUMNS, write_csv
from bdsl.text.normalize import NORM_VER, normalize


def test_edit_distance_and_wer():
    assert edit_distance(list("abc"), list("abc")) == 0
    assert edit_distance(list("abc"), list("axc")) == 1
    assert edit_distance(list("abc"), []) == 3 and edit_distance([], list("ab")) == 2
    assert item_wer(["a", "b"], ["a"]) == 50.0
    # corpus WER = all edits / all reference tokens, not the mean of item WERs
    assert wer([["a"], ["a", "b", "c"]], [["x"], ["a", "b", "c"]]) == 25.0
    assert exact_match([["a"], ["b"]], [["a"], ["c"]]) == 50.0
    assert tag_accuracy([{"neg"}, set()], [{"neg"}, {"q-wh"}]) == 50.0


def test_score_uses_sacrebleu():
    ref = ["আমি", "মঙ্গলবার", "স্কুল", "যাওয়া"]   # BLEU-4 needs at least 4 tokens to be non-zero
    s = score([ref], [list(ref)], [set()], [set()])
    assert s["wer"] == 0 and s["exact_match"] == 100 and s["chrf"] == pytest.approx(100)
    assert s["bleu4"] == pytest.approx(100)


def test_g0_baseline_and_tag_tokens():
    assert g0_gloss("আমার খালা~ রান্না? NUM(৩টায়)?") == ["আমার", "খালা", "রান্না", "NUM(৩টায়)"]
    assert g0_tags("neg;q?") == {"neg", "q?"} and g0_tags("") == set()
    assert split_tags(["<neg>", "আমি", "NOT"]) == ({"neg"}, ["আমি", "NOT"])
    v = Vocab(["b", "a"])
    assert v.itos[4:] == ["a", "b"] and v.decode(v.encode(["a", "zz"]) + [2, 4]) == ["a", "<unk>"]


TINY = {"model": {"emb": 16, "enc_hidden": 24, "dec_hidden": 24, "attn": 16, "dropout": 0.0},
        "train": {"lr": 0.01, "batch_size": 4, "max_epochs": 150, "patience": 150, "clip": 1.0,
                  "label_smoothing": 0.0},
        "beam": 2, "max_len": 8, "seeds": [1], "tag_prefix": True}


def _df(is_mock="true"):
    sents = [("আমি স্কুলে যাই", "আমি স্কুল যাওয়া", "", "train"), ("আমি অফিসে যাই", "আমি অফিস যাওয়া", "", "train"),
             ("তুমি কি করো", "তুমি কি করা", "q-wh", "train"), ("আমি যাব না", "আমি যাওয়া NOT", "neg", "train"),
             ("আমি স্কুলে যাব", "আমি স্কুল যাওয়া", "", "val"), ("তুমি স্কুলে যাও", "তুমি স্কুল যাওয়া", "", "test")]
    rows = []
    for i, (s, g, t, sp) in enumerate(sents):
        rows.append({c: "" for c in COLUMNS} | {
            "index": str(i), "split": sp, "sentence_raw": s, "sentence_norm": normalize(s), "norm_ver": NORM_VER,
            "gloss_auto": s, "review_date": "2026-10-22", "confidence": "low",
            "gloss_reviewed": g, "tags_reviewed": t, "status": "team_reviewed", "reviewer_id": "T1",
            "is_mock": is_mock, "notes": "TEST DATA: not video-verified"})
    return pd.DataFrame(rows, columns=COLUMNS)


def _run(tmp_path, tcfg=TINY, **kw):
    cfg = {"text2gloss": tcfg, "_meta": {"config_hash": "x", "project_root": str(tmp_path)}}
    check = {"file": "a.csv", "file_sha256": "f" * 64, "problems": []}
    return run(cfg, _df(), check, allow_test_data=True, pilot_manifest_sha256="m" * 64,
               runs_root=tmp_path / "runs", **kw)


def test_overfit_one_sentence_and_test_labels(tmp_path):
    res = _run(tmp_path, overfit=1)
    assert res["finished"] and res["metrics"]["agru"]["1"]["train"]["exact_match"] == 100.0
    run_dir = Path(res["run_dir"])
    names = [p.name for p in run_dir.rglob("*") if p.is_file()]
    assert names and all(n.startswith("TEST_") for n in names)
    assert json.loads((run_dir / "TEST_run.json").read_text(encoding="utf-8"))["TEST_RUN"] is True
    assert json.loads((run_dir / "TEST_metrics.json").read_text(encoding="utf-8"))["TEST_RUN"] is True
    assert torch.load(run_dir / "seed1" / "TEST_ckpt_best.pt", weights_only=True)["meta"]["TEST_RUN"] is True
    assert "[TEST]" in (run_dir / "TEST_train.log").read_text(encoding="utf-8")


def test_stop_and_resume_gives_identical_weights(tmp_path):
    short = copy.deepcopy(TINY)
    short["train"]["max_epochs"] = 12
    straight = _run(tmp_path / "a", short)
    stopped = _run(tmp_path / "b", short, stop_after=5)
    assert not stopped["finished"]
    resumed = _run(tmp_path / "b", short, run_dir=Path(stopped["run_dir"]))
    w = [torch.load(Path(r["run_dir"]) / "seed1" / "TEST_ckpt_last.pt", weights_only=True)
         for r in (straight, resumed)]
    assert w[0]["state"]["epoch"] == w[1]["state"]["epoch"] == 12
    assert all(torch.equal(w[0]["model"][k], w[1]["model"][k]) for k in w[0]["model"])
    assert straight["metrics"]["agru"] == resumed["metrics"]["agru"]


def test_resume_keeps_the_original_seeds(tmp_path):
    two = copy.deepcopy(TINY)
    two["seeds"] = [1, 2]
    two["train"]["max_epochs"] = 3
    stopped = _run(tmp_path, two, seeds=[2], stop_after=1)
    resumed = _run(tmp_path, two, run_dir=Path(stopped["run_dir"]))
    assert list(resumed["metrics"]["agru"]) == ["2"]
    with pytest.raises(ResumeMismatch):
        _run(tmp_path, two, seeds=[1], run_dir=Path(stopped["run_dir"]))


def test_resume_refuses_changed_inputs(tmp_path):
    stopped = _run(tmp_path, stop_after=1)
    cfg = {"text2gloss": TINY, "_meta": {"config_hash": "x", "project_root": str(tmp_path)}}
    check = {"file": "a.csv", "file_sha256": "0" * 64, "problems": []}
    with pytest.raises(ResumeMismatch):
        run(cfg, _df(), check, allow_test_data=True, pilot_manifest_sha256="m" * 64,
            run_dir=Path(stopped["run_dir"]))


def test_run_refuses_a_failed_check(tmp_path):
    cfg = {"text2gloss": TINY, "_meta": {"config_hash": "x", "project_root": str(tmp_path)}}
    with pytest.raises(RuntimeError):
        run(cfg, _df(), {"file": "a", "file_sha256": "f", "problems": ["row 1: mock row"]},
            allow_test_data=False, pilot_manifest_sha256="m", runs_root=tmp_path)


def test_cli_guard_refuses_test_data_without_the_option(tmp_path, monkeypatch, capsys):
    import bdsl.cli as cli

    target = write_csv(_df(), tmp_path / "pilot.csv")
    reviewers = write_csv(pd.DataFrame([("T1", "team", "owner", "2026-10-22", "")], columns=REVIEWER_COLUMNS),
                          tmp_path / "REVIEWERS.csv")
    (tmp_path / "pilot50_manifest.csv").write_text(
        "index,split\n" + "".join(f"{i},{s}\n" for i, s in zip(range(6), ["train"] * 4 + ["val", "test"])),
        encoding="utf-8")
    cfg = {"paths": {"pilot_dest_dir": str(tmp_path), "runs_dir": str(tmp_path / "runs")},
           "text2gloss": TINY, "_meta": {"config_hash": "x", "project_root": str(tmp_path)}}
    monkeypatch.setattr(cli, "_annotation_paths", lambda c: (target, reviewers))
    monkeypatch.setattr(cli, "load_config", lambda **kw: cfg)
    assert cli.main(["train-text2gloss"]) == 2
    assert "Refusing to train" in capsys.readouterr().out
    assert not (tmp_path / "runs").exists()
    # a split that differs from the pilot manifest is refused even in test mode
    (tmp_path / "pilot50_manifest.csv").write_text("index,split\n" + "".join(f"{i},train\n" for i in range(6)),
                                                   encoding="utf-8")
    assert cli.main(["train-text2gloss", "--allow-test-data"]) == 2
    assert "split differs" in capsys.readouterr().out
