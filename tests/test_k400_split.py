"""kaggle400 split: selection rules, leakage tests, line-ending-independent lock, copying, packaging."""

import hashlib
import json
import os
import shutil
import subprocess
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from k400_helpers import full_layout, make_layout
from k400.lock import check_lock, write_lock
from k400.select import build_pool, minimal_pair_families, select_subset
from k400.verify import overall, run_checks

ROOT = Path(__file__).resolve().parents[1]
LINKS = [[3456, 3457, 3458]]
KCFG = {"seed": 7, "targets": {"train": 30, "val": 6, "test": 6}, "minimal_pair_heldout": {"val": 2, "test": 2},
        "strata": ["length_bucket", "question", "negation", "orientation", "resolution_bucket", "duration_quartile"],
        "low_res_short_side": 500}


def _synthetic_manifest(n=240, seed=0):
    rng = np.random.default_rng(seed)
    words = ["আমি", "তুমি", "সে", "স্কুল", "অফিস", "বাসা", "যাব", "খাব", "ভাত", "রুটি", "না", "কেন", "লাল", "নীল", "আজ"]
    rows, seen = [], set()
    i = 0
    while len(rows) < n:
        toks = list(rng.choice(words, size=int(rng.integers(2, 6)), replace=False))
        s = " ".join(toks)
        if s in seen:
            continue
        seen.add(s)
        rows.append({"index": i, "relpath": f"SIGN_LANGUAGE_DATA/{i}.mp4", "bytes": 1000 + i,
                     "sha256": hashlib.sha256(str(i).encode()).hexdigest(), "codec": "h264",
                     "display_w": int(rng.choice([1080, 1920, 480])), "display_h": 1920,
                     "orientation": str(rng.choice(["portrait", "landscape"], p=[0.85, 0.15])), "fps_avg": 30.0,
                     "duration_s": float(rng.uniform(2, 12)), "decode_ok": True, "sentence_raw": s, "sentence_norm": s,
                     "is_representative": True, "group_id": f"g{i}", "label_conflict": False})
        i += 1
    m = pd.DataFrame(rows)
    # an exact copy (not representative) and the colour cluster as one linked group
    dup = m.iloc[0].copy()
    dup["index"], dup["is_representative"] = 9999, False
    m = pd.concat([m, dup.to_frame().T], ignore_index=True)
    for k, idx in enumerate((3456, 3457, 3458)):
        r = m.iloc[1].copy()
        r["index"], r["sentence_raw"] = idx, f"আমার পছন্দের রং {['কালো', 'লাল', 'সাদা'][k]}"
        r["sentence_norm"], r["sha256"], r["group_id"] = r["sentence_raw"], hashlib.sha256(str(idx).encode()).hexdigest(), "g3456"
        m = pd.concat([m, r.to_frame().T], ignore_index=True)
    m = m.astype({"index": int, "is_representative": bool, "decode_ok": bool, "label_conflict": bool,
                  "duration_s": float, "display_w": int, "display_h": int})
    split = pd.DataFrame({"index": m["index"], "group_id": m["group_id"]})
    rng2 = np.random.default_rng(1)
    split["split"] = [("train" if g == "g3456" else str(rng2.choice(["train", "val", "test"], p=[0.7, 0.15, 0.15])))
                      for g in m["group_id"]]
    split.loc[split["index"] == 9999, "split"] = split.loc[split["index"] == 0, "split"].iloc[0]
    return m, split


def test_selection_rules_and_determinism():
    m, s = _synthetic_manifest()
    sel, report, pool = select_subset(m, s, KCFG, LINKS, {5, 6})
    sel2, _, _ = select_subset(m, s, KCFG, LINKS, {5, 6})
    assert sel["index"].tolist() == sel2["index"].tolist()                       # same seed → same clips
    assert sel["split"].value_counts().to_dict() == {"train": 30, "val": 6, "test": 6}
    s1 = dict(zip(s["index"], s["split"]))
    assert all(s1[i] == sp for i, sp in zip(sel["index"], sel["split"]))       # S1 partition kept
    assert 9999 not in set(sel["index"])                                        # no exact copies
    assert set(sel[sel["index"].isin([3456, 3457, 3458])]["split"]) == {"train"} and sel["index"].isin([3456]).any()
    assert sel["sentence_norm"].is_unique and sel["sha256"].is_unique
    assert (sel["reason"].str.len() > 10).all()
    held = sel[sel["mp_role"] == "heldout"]
    assert len(held) == 4
    train_ids = set(sel.loc[sel["split"] == "train", "index"])
    for r in held.to_dict("records"):
        assert int(r["mp_partner"]) in train_ids
        fam = minimal_pair_families(pool)[r["mp_family"]]
        assert r["index"] in fam and int(r["mp_partner"]) in fam
    assert held["all_words_in_train"].all()
    sel3, _, _ = select_subset(m, s, {**KCFG, "seed": 8}, LINKS)
    assert sel3["index"].tolist() != sel["index"].tolist()                      # the seed matters


def test_pool_is_one_representative_per_sentence():
    m, s = _synthetic_manifest()
    pool = build_pool(m, s, KCFG)
    assert pool["sentence_norm"].is_unique and pool["is_representative"].all()
    assert set(pool["duration_quartile"]) == {"q1", "q2", "q3", "q4"}


@pytest.mark.skipif(not (ROOT / "work" / "manifests" / "manifest_v1.csv").is_file()
                    or not (ROOT / "kaggle" / "data" / "subset_manifest.csv").is_file(),
                    reason="needs work/manifests/manifest_v1.csv and the committed kaggle/data manifests (desktop)")
def test_real_selection_reproduces_committed_manifests():
    from bdsl.config import load_config

    cfg = load_config(env="local", data="kaggle400")
    m = pd.read_csv(ROOT / "work" / "manifests" / "manifest_v1.csv", dtype={"sha256": str})
    s = pd.read_csv(ROOT / "work" / "splits" / "S1_v0.csv")
    sel, _, _ = select_subset(m, s, cfg["kaggle400"], cfg["split"]["known_shared_segment_links"])
    committed = pd.read_csv(ROOT / "kaggle" / "data" / "subset_manifest.csv", encoding="utf-8-sig")
    assert sorted(zip(sel["index"], sel["split"])) == sorted(zip(committed["index"], committed["split"]))


def test_verify_passes_and_catches_each_problem(tmp_path):
    full_layout(tmp_path)
    res = run_checks(tmp_path, LINKS, require_videos=True)
    assert overall(res, True), res
    status = lambda r, n: next(x["status"] for x in r if x["check"].startswith(n))  # noqa: E731
    # a file put into a second folder
    v = sorted((tmp_path / "data" / "train" / "videos").glob("*.mp4"))[0]
    shutil.copy2(v, tmp_path / "data" / "val" / "videos" / v.name)
    r = run_checks(tmp_path, LINKS, require_videos=True)
    assert status(r, "8") == "FAIL" and status(r, "9") == "FAIL"
    (tmp_path / "data" / "val" / "videos" / v.name).unlink()
    # changed video bytes
    v.write_bytes(b"changed")
    assert status(run_checks(tmp_path, LINKS, require_videos=True), "8") == "FAIL"


def _edit_manifest(root, split, fn):
    f = root / "data" / split / f"{split}_manifest.csv"
    df = pd.read_csv(f, encoding="utf-8-sig", dtype=str, keep_default_na=False)
    df = fn(df)
    f.write_bytes(("\ufeff" + df.to_csv(index=False, lineterminator="\n")).encode("utf-8"))
    sub = pd.concat([pd.read_csv(root / "data" / s / f"{s}_manifest.csv", encoding="utf-8-sig", dtype=str,
                                 keep_default_na=False) for s in ("train", "val", "test")])
    old = pd.read_csv(root / "data" / "subset_manifest.csv", encoding="utf-8-sig", dtype=str, keep_default_na=False)
    sub = sub.merge(old[["index", "sha256_source", "sha256_copy"]], on="index", how="left")
    (root / "data" / "subset_manifest.csv").write_bytes(("\ufeff" + sub.to_csv(index=False, lineterminator="\n")).encode("utf-8"))


@pytest.mark.parametrize("problem,check", [("sentence", "5"), ("sha", "4"), ("group", "3"), ("link", "6"), ("s1", "7")])
def test_leakage_checks_fail_on_crossing(tmp_path, problem, check):
    info = full_layout(tmp_path, with_videos=False)
    sub = info["subset"]
    t0 = sub[sub["split"] == "train"].iloc[0]
    v0 = sub[sub["split"] == "val"].iloc[0]

    def fn(df):
        k = df["index"] == str(v0["index"])
        if problem == "sentence":
            df.loc[k, "sentence_norm"] = t0["sentence_norm"]
        if problem == "sha":
            df.loc[k, "sha256"] = t0["sha256"]
        if problem == "group":
            df.loc[k, "group_id"] = t0["group_id"]
        if problem == "s1":
            df.loc[k, "s1_split"] = "train"
        return df
    _edit_manifest(tmp_path, "val", fn)
    links = [[int(t0["index"]), int(v0["index"])]] if problem == "link" else LINKS
    res = run_checks(tmp_path, links)
    assert next(x["status"] for x in res if x["check"].startswith(check)) == "FAIL"
    assert next(x["status"] for x in res if x["check"].startswith("10")) in ("FAIL", "PASS")
    if problem != "link":
        assert check_lock(tmp_path)          # any manifest edit breaks the lock


def test_lock_ignores_line_endings_and_bom_but_not_content(tmp_path):
    make_layout(tmp_path, with_videos=False, with_features=False)
    write_lock(tmp_path, {})
    f = tmp_path / "data" / "val" / "val_manifest.csv"
    text = f.read_bytes().replace(b"\r\n", b"\n")
    f.write_bytes(text.replace(b"\n", b"\r\n"))                              # Git autocrlf / Excel
    assert check_lock(tmp_path) == []
    f.write_bytes(text.lstrip(b"\xef\xbb\xbf"))                              # BOM removed
    assert check_lock(tmp_path) == []
    f.write_bytes(text.replace(b"test fixture", b"test fixturX", 1))
    assert check_lock(tmp_path) and "val_manifest" in check_lock(tmp_path)[0]


def test_copy_videos_verifies_and_never_overwrites(tmp_path):
    from k400 import copyvid

    root = tmp_path / "kaggle"
    info = make_layout(root, with_videos=False, with_features=False)
    src_root = tmp_path / "initial_dataset"
    for rel, b in info["source_videos"].items():
        (src_root / rel).parent.mkdir(parents=True, exist_ok=True)
        (src_root / rel).write_bytes(b)
    sub = pd.read_csv(root / "data" / "subset_manifest.csv", encoding="utf-8-sig", dtype=str, keep_default_na=False)
    sub["sha256_copy"] = ""
    (root / "data" / "subset_manifest.csv").write_bytes(("\ufeff" + sub.to_csv(index=False, lineterminator="\n")).encode("utf-8"))
    first = src_root / info["subset"]["source_relpath"].iloc[0]
    mtime = os.stat(first).st_mtime_ns
    proj = tmp_path / "proj"
    (proj / "dataset" / "initial_dataset").mkdir(parents=True)
    (proj / "dataset" / "initial_dataset" / "DATASET_WORK_LOG.md").write_text("# Dataset Work Log\n\n## old entry\n- x\n", encoding="utf-8")
    (root / "data" / "SPLIT_REPORT.md").write_text("# r\n", encoding="utf-8")
    assert copyvid.run(root, src_root, proj, LINKS, None, log=lambda *a: None) == 0
    assert os.stat(first).st_mtime_ns == mtime                                 # source untouched
    cv = pd.read_csv(root / "data" / "COPY_VERIFICATION.csv", encoding="utf-8-sig")
    assert cv["ok"].all() and (cv["action"] == "copied").all()
    assert check_lock(root) == [] and "Desktop run" in (root / "data" / "SPLIT_REPORT.md").read_text(encoding="utf-8")
    sub = pd.read_csv(root / "data" / "subset_manifest.csv", encoding="utf-8-sig", dtype=str)
    assert (sub["sha256_copy"] == sub["sha256"]).all()
    # second run (found on the desktop, 2026-10-23: the script is re-run after a fix): already present,
    # one log entry that keeps the first run and gains a re-check line, one report section only
    assert copyvid.run(root, src_root, proj, LINKS, None, log=lambda *a: None) == 0
    log = (proj / "dataset" / "initial_dataset" / "DATASET_WORK_LOG.md").read_text(encoding="utf-8")
    assert log.count("k400-copy-log") == 1 and "## old entry" in log
    k = len(sub)
    assert f"(copied {k}, already present 0)" in log and log.count("- Re-check ") == 1
    assert f"copied in this run 0, already present {k}" in log
    report = (root / "data" / "SPLIT_REPORT.md").read_text(encoding="utf-8")
    assert report.count("### Desktop run") == 1 and report.startswith("# r\n")
    assert f"copied in this run: 0; already present from an earlier run (re-hashed now): {k}" in report
    # a different file at the destination is never overwritten
    dst = next((root / "data" / "train" / "videos").glob("*.mp4"))
    dst.write_bytes(b"something else")
    assert copyvid.run(root, src_root, proj, LINKS, None, log=lambda *a: None) == 1
    assert dst.read_bytes() == b"something else"


def _git(cwd, *args):
    subprocess.run(["git", "-c", "user.email=t@t", "-c", "user.name=t", "-c", "core.autocrlf=false", *args], cwd=cwd,
                   check=True, capture_output=True)


@pytest.mark.skipif(shutil.which("git") is None, reason="git not installed")
def test_package_allow_list_clean_commit_and_verify(tmp_path):
    from k400.package import PackageError, build, forbidden, verify

    proj = tmp_path / "proj"
    for rel, text in {"src/bdsl/x.py": "x = 1\n", "configs/base.yaml": "a: 1\n", "kaggle/src/k400/y.py": "y = 2\n",
                      "kaggle/README.md": "# k\n", "tests/test_x.py": "def test(): pass\n", "pyproject.toml": "[project]\n",
                      "uv.lock": "lock\n", "README.md": "# p\n", "research/papers/a.pdf": "pdf",
                      "dataset/initial_dataset/videos/0.mp4": "video", ".gitignore": "kaggle/data/\nkaggle/work/\n"}.items():
        (proj / rel).parent.mkdir(parents=True, exist_ok=True)
        (proj / rel).write_text(text, encoding="utf-8")
    full_layout(proj / "kaggle", with_features=False)
    for f in ("README_DATA.md", "SPLIT_REPORT.md", "SELECTION_META.json", "COPY_VERIFICATION.csv"):
        (proj / "kaggle" / "data" / f).write_text("x\n", encoding="utf-8")
    (proj / "kaggle" / "data" / "SPLIT_SUMMARY.png").write_bytes(b"\x89PNG")
    _git(proj, "init", "-q")
    _git(proj, "add", "-A")
    _git(proj, "add", "-f", "kaggle/data/SPLIT_REPORT.md")
    _git(proj, "commit", "-qm", "init")
    (proj / "src" / "bdsl" / "x.py").write_text("x = 2\n", encoding="utf-8")
    with pytest.raises(PackageError, match="not a clean commit"):
        build(proj, proj / "kaggle", tmp_path / "out")
    _git(proj, "commit", "-qam", "change")
    res = build(proj, proj / "kaggle", tmp_path / "out", log=lambda *a: None)
    assert verify(Path(res["zip"]), log=lambda *a: None) == []
    names = zipfile.ZipFile(res["zip"]).namelist()
    assert "code/src/bdsl/x.py" in names and "code/CODE_VERSION.json" in names and "PACKAGE_INFO.json" in names
    assert not any(n.startswith(("code/research", "code/dataset", "code/kaggle/data")) for n in names)
    assert sum(n.startswith("data/") and n.endswith(".mp4") for n in names) == 18
    info = json.loads(zipfile.ZipFile(res["zip"]).read("PACKAGE_INFO.json"))
    assert info["code_dirty"] is False and len(info["commit"]) == 40
    for bad in ("code/kaggle/kaggle.json", "code/.venv/lib/x.py", "code/kaggle/work/a.txt", "data/x.npz", "code/a/b.pt"):
        assert forbidden(bad), bad


def test_package_verify_detects_tampering(tmp_path):
    from k400.package import verify

    z = tmp_path / "p.zip"
    with zipfile.ZipFile(z, "w") as f:
        f.writestr("data/train/train_manifest.csv", "a\n")
        f.writestr("UPLOAD_MANIFEST.csv", "path,bytes,sha256\ndata/train/train_manifest.csv,2,"
                   + hashlib.sha256(b"b\n").hexdigest() + "\n")
        f.writestr("PACKAGE_INFO.json", "{}")
        f.writestr("kaggle.json", "{}")
    probs = verify(z, log=lambda *a: None)
    assert any("SHA-256" in p for p in probs) and any("kaggle.json" in p for p in probs)
