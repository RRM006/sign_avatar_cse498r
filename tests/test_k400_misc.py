"""kaggle400 helpers: G0 reproduction, notebooks, path hygiene, setup carry-over, extraction QC, tables."""

import ast
import json
import re
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from k400_helpers import BLEND

ROOT = Path(__file__).resolve().parents[1]
K = ROOT / "kaggle"
_ABSOLUTE = re.compile(r"(?<![A-Za-z])[A-Za-z]:[\\/]|\\Users\\|/home/")


def test_g0_corpus_reproduces_the_pilot_drafts():
    from bdsl.text.annotations import read_csv
    from bdsl.text.gloss_rules import g0
    from k400.gloss import read_corpus

    corpus_file = K / "processed" / "glosses" / "g0_corpus_v1.txt"
    ann = ROOT / "annotations" / "pilot50_v1_gloss_v01.csv"
    if not corpus_file.is_file() or not ann.is_file():
        pytest.skip("corpus or pilot annotation file not present")
    corpus = read_corpus(corpus_file)
    rows = read_csv(ann).to_dict("records")
    assert len(corpus) == 1398
    assert all(g0(r["sentence_norm"], corpus)[:2] == (r["gloss_auto"], r["tags_auto"]) for r in rows)


def test_committed_glosses_match_a_fresh_run(tmp_path):
    from k400.gloss import compare, make_glosses, read_corpus

    if not (K / "data" / "train" / "train_manifest.csv").is_file():
        pytest.skip("kaggle/data manifests not present")
    make_glosses(K / "data", tmp_path, read_corpus(K / "processed" / "glosses" / "g0_corpus_v1.txt"), "G0-v0.1")
    assert compare(tmp_path, K / "processed" / "glosses") == {"train": "IDENTICAL", "val": "IDENTICAL", "test": "IDENTICAL"}


NOTEBOOKS = sorted((K / "notebooks").glob("*.ipynb"))


def test_ten_notebooks_exist():
    assert [p.stem[:2] for p in NOTEBOOKS] == [f"{i:02d}" for i in range(10)]


@pytest.mark.parametrize("path", NOTEBOOKS, ids=lambda p: p.stem)
def test_notebook_is_valid_and_documented(path):
    import nbformat

    nb = nbformat.read(path, 4)
    nbformat.validate(nb)
    head = nb.cells[0]
    assert head.cell_type == "markdown"
    for word in ("Purpose", "Inputs", "Outputs", "Expected run time", "What to check", "Kaggle settings"):
        assert word in head.source, word
    for cell in nb.cells:
        if cell.cell_type == "code":
            ast.parse(cell.source)
            assert not cell.get("outputs"), "committed notebooks are saved without outputs"
    assert "S.finish(" in nb.cells[-1].source


@pytest.mark.parametrize("path", sorted((K / "src").rglob("*.py")) + sorted((K / "tools").rglob("*.py")),
                         ids=lambda p: p.relative_to(ROOT).as_posix())
def test_no_machine_specific_paths_in_kaggle_code(path):
    hits = [ln for ln in path.read_text(encoding="utf-8").splitlines() if _ABSOLUTE.search(ln) and "https://" not in ln]
    assert not hits, hits


def test_powershell_script_is_ascii_and_never_pushes():
    ps = (K / "tools" / "run_local_steps.ps1").read_bytes()
    ps.decode("ascii")                                   # Windows PowerShell 5.1 reads BOM-less files as ANSI
    text = ps.decode("ascii")
    assert "git push" not in text.replace("NOT push", "").replace("no push", "")
    assert "--confirm" in text and "verify_split.py" in text and "pytest" in text


def test_mediapipe_probe_script_compiles():
    from k400.mp_env import PROBE

    compile(PROBE, "probe", "exec")


def test_setup_restores_earlier_outputs_without_overwriting(tmp_path):
    from k400.setup import find_previous_states, restore

    prev = tmp_path / "input" / "nb-02-output" / "k400"
    (prev / "processed" / "features" / "train").mkdir(parents=True)
    (prev / "STATE.json").write_text("{}", encoding="utf-8")
    (prev / "processed" / "features" / "train" / "1.npz").write_bytes(b"a")
    (prev / "outputs").mkdir()
    (prev / "outputs" / "x.json").write_text("old", encoding="utf-8")
    (tmp_path / "input" / "bdsl-k400" / "data" / "train" / "videos").mkdir(parents=True)
    states = find_previous_states(tmp_path / "input")
    assert states == [prev]
    work = tmp_path / "working" / "k400"
    (work / "outputs").mkdir(parents=True)
    (work / "outputs" / "x.json").write_text("new", encoding="utf-8")
    res = restore(states, work, log=lambda *a: None)
    assert (work / "processed" / "features" / "train" / "1.npz").read_bytes() == b"a"
    assert (work / "outputs" / "x.json").read_text(encoding="utf-8") == "new" and res["conflicts"] == ["outputs/x.json"]


def _qc_npz(path, index, hw):
    t = 20
    rng = np.random.default_rng(index)
    pose = rng.normal(0, 0.1, (t, 33, 3)).astype(np.float32)
    hand = rng.normal(0, 0.05, (t, 21, 3)).astype(np.float32)
    meta = {"index": index, "feat_ver": "fa89892d4908", "mode": "video", "frames": t, "src_frames": 40, "src_fps": 30.0,
            "ts_cv": 0.0, "detect_ms_per_frame": 10.0, "seconds": 1.0, "fps": 15, "frame_hw": list(hw)}
    path.parent.mkdir(parents=True, exist_ok=True)
    np.savez(path, pose_world=pose, pose_img=np.abs(pose), pose_vis=np.ones((t, 33), np.float32), lhand_world=hand,
             rhand_world=hand, lhand_img=np.abs(hand), rhand_img=np.abs(hand), blendshapes=np.zeros((t, 52), np.float32),
             blendshape_names=np.array(BLEND), head_rot=np.zeros((t, 3), np.float32), mask=np.ones((t, 4), np.uint8),
             t_ms=np.arange(t, dtype=np.float32), src_t_ms=np.arange(t, dtype=np.float32), src_frame=np.arange(t, dtype=np.int32),
             meta=np.array(json.dumps(meta)))


def test_extraction_qc_flags_rotation_and_missing_clips(tmp_path):
    from k400.extract import qc_and_report

    clips = []
    for i, (hw, disp) in enumerate([((1920, 1080), (1920, 1080)), ((1080, 1920), (1920, 1080)), (None, (1920, 1080))]):
        out = tmp_path / "features" / "train" / f"{i}.npz"
        if hw:
            _qc_npz(out, i, hw)
        clips.append({"index": i, "split": "train", "out": out, "display_h": disp[0], "display_w": disp[1], "duration_s": 1.33})
    s = qc_and_report(clips, "fa89892d4908", tmp_path / "qc", [{"index": 2, "error": "decode failed"}])
    assert s["clips_with_features"] == 2 and s["failures_or_missing"] == 1 and not s["complete"]
    assert not s["rotation_ok_all"] and s["privacy_ok_all"] and any("rotation" in p for p in s["problems"])
    assert pd.read_csv(tmp_path / "qc" / "failures.csv")["error"].tolist() == ["decode failed"]
    assert (tmp_path / "qc" / "hand_coverage_summary.csv").is_file()


@pytest.mark.skipif(not (ROOT / "work" / "models" / "holistic_landmarker.task").is_file(),
                    reason="needs the MediaPipe model file in work/models (desktop)")
def test_real_mediapipe_extraction_resume_and_feat_ver(tmp_path):
    pytest.importorskip("mediapipe")
    import cv2

    from bdsl.config import load_config
    from k400.extract import run

    data = tmp_path / "data"
    rows = []
    for sp in ("train", "val", "test"):
        (data / sp / "videos").mkdir(parents=True)
        w = cv2.VideoWriter(str(data / sp / "videos" / "7.mp4"), cv2.VideoWriter_fourcc(*"mp4v"), 30, (160, 120))
        for t in range(30):
            fr = np.full((120, 160, 3), 180, np.uint8)
            cv2.circle(fr, (20 + 3 * t, 60), 10, (30, 60, 200), -1)
            w.write(fr)
        w.release()
        pd.DataFrame([{"index": 7, "filename": "7.mp4", "display_w": 160, "display_h": 120, "duration_s": 1.0}]).to_csv(
            data / sp / f"{sp}_manifest.csv", index=False)
    cfg = load_config(env="local", data="kaggle400")
    model = ROOT / "work" / "models" / "holistic_landmarker.task"
    s = run(cfg, data, tmp_path / "state", model, workers=1, splits=("train",), log=lambda *a: None)
    assert s["complete"] and s["feat_ver"] == cfg["gloss2motion"]["feat_ver"] and s["rotation_ok_all"]
    again = run(cfg, data, tmp_path / "state", model, workers=1, splits=("train",), log=lambda *a: None)
    assert again["extracted_this_run"] == 0 and again["complete"]          # resume: nothing redone


def test_tables_markdown_and_latex(tmp_path):
    from k400.tables import fmt_ci, write_table

    df = pd.DataFrame([{"method": "B0 mean_motion", "MPJPE (sw)": "0.221 [0.19, 0.25]", "share": "5%"}])
    res = write_table(df, tmp_path, "T_x", "Test & caption")
    tex = (tmp_path / "T_x.tex").read_text(encoding="utf-8")
    assert r"B0 mean\_motion" in tex and r"5\%" in tex and r"Test \& caption" in tex and "\\toprule" in tex
    assert (tmp_path / "T_x.md").read_text(encoding="utf-8").count("|") > 6 and len(res["files"]) == 3
    assert fmt_ci({"low": 0.1, "high": 0.25}, 2) == "[0.10, 0.25]"


def test_child_pythons_never_inherit_the_jupyter_plot_backend(monkeypatch):
    """Found in the workspace smoke test (2026-10-23): the MediaPipe fallback Python crashed on Jupyter's
    MPLBACKEND (module://matplotlib_inline...), because mediapipe imports matplotlib."""
    from k400.mp_env import clean_env

    monkeypatch.setenv("MPLBACKEND", "module://matplotlib_inline.backend_inline")
    assert clean_env()["MPLBACKEND"] == "Agg"
    assert "MPLBACKEND" in (ROOT / "kaggle" / "src" / "k400_run.py").read_text(encoding="utf-8")


def test_notebook_07_stops_before_freeze_and_test_when_sacrebleu_is_missing():
    """Found on Kaggle (2026-10-23): Version 1 of notebook 07 ran without Internet, sacrebleu was missing, and the
    notebook went on to the freeze and to the final test (which crashed before any result). The install must be
    checked first, and a failure must stop the notebook before any bdsl command runs."""
    import sys

    import nbformat

    nb = nbformat.read(K / "notebooks" / "07_baselines_eval.ipynb", 4)
    code = [c.source for c in nb.cells if c.cell_type == "code"]
    guard = next(i for i, s in enumerate(code) if "assert ok" in s and "sacrebleu" in s)
    freeze = next(i for i, s in enumerate(code) if 'S.bdsl("freeze")' in s)
    final = next(i for i, s in enumerate(code) if '"--final"' in s)
    assert guard < freeze < final

    class Stub:
        def __init__(self, rc):
            self.rc, self.calls = rc, []

        def pip_install(self, *pins):
            return self.rc

        def bdsl(self, *args):
            self.calls.append(args)
            return 0

    failing = Stub(1)                                    # pip could not install (no Internet)
    with pytest.raises(AssertionError, match="test split was not touched"):
        exec(code[guard], {"S": failing, "sys": sys})
    assert failing.calls == []                           # nothing after the guard ran
    working = Stub(0)                                    # installed (sacrebleu is importable in the test env)
    pytest.importorskip("sacrebleu")
    exec(code[guard], {"S": working, "sys": sys})
    assert working.calls == [("list-runs",)]
