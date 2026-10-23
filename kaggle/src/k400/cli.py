"""`python kaggle/src/k400_run.py <command>` — kaggle400 helper commands (imports are lazy per command).

Desktop (run by kaggle/tools/run_local_steps.ps1):
    select [--check]             choose the 400 clips → kaggle/data manifests, report, figure
    copy-videos --confirm        copy + SHA-256-verify the videos, write SPLIT_LOCK.json
    verify [--require-videos]    leakage / consistency tests (same as kaggle/src/verify_split.py)
    gloss [--compare-with DIR]   G0 pseudo-glosses for the 400 sentences + TRAIN-only vocabularies
    package                      build the private-dataset zip from a clean commit
    verify-package ZIP           re-check the zip (CRC, allow-list, SHA-256 of every file)
    verify-download DIR          check downloaded Kaggle outputs against their OUTPUT_HASHES.csv
Kaggle notebooks:
    verify-upload                SHA-256 of every uploaded file against UPLOAD_MANIFEST.csv
    env-report                   Python / GPU / CUDA / disk / packages → outputs/env/
    mp-setup [--video PATH]      install + probe MediaPipe 0.10.35 (main route, else the pinned fallback)
    extract [--max-minutes N]    MediaPipe features for the clips not yet done (resume-safe)
    report                       paper tables, figures and RESULTS_SUMMARY.md
    avatar                       motion JSON + skeleton videos for a few TEST sentences (after the test lock)
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def _cfg():
    from bdsl.config import load_config

    return load_config(data="kaggle400")


def _scratch(state_root: Path) -> Path:
    """Big temporary files (model download, fallback Python) that must NOT be saved as notebook Output:
    on Kaggle /tmp (not saved), on the desktop kaggle/work (gitignored)."""
    import os

    if "KAGGLE_KERNEL_RUN_TYPE" in os.environ or Path("/kaggle/working").is_dir():
        return Path("/tmp/k400_scratch")
    return state_root / "work"


def _roots(cfg) -> tuple[Path, Path, Path]:
    """(project/code root, k400 data root, k400 state root)."""
    return (Path(cfg["_meta"]["project_root"]), Path(cfg["paths"]["k400_data_root"]),
            Path(cfg["paths"]["k400_state_root"]))


def cmd_select(args) -> int:
    import tempfile

    import pandas as pd

    from bdsl.io import sha256_file, sha256_text_canonical

    from .gloss import CORPUS_FILE, write_corpus
    from .select import select_subset
    from .splitio import write_selection

    cfg = _cfg()
    proj, data_root, state_root = _roots(cfg)
    src = cfg["kaggle400"]["source"]
    man_path = Path(cfg["paths"]["manifests_dir"]) / f"{src['manifest']}.csv"
    s1_path = Path(cfg["paths"]["splits_dir"]) / f"{src['split']}.csv"
    got = {"manifest": sha256_file(man_path), "split": sha256_file(s1_path)}
    if got["manifest"] != src["manifest_csv_sha256"] or got["split"] != src["split_csv_sha256"]:
        print(f"Refusing: inputs differ from configs/data/kaggle400.yaml: {got}")
        return 2
    manifest = pd.read_csv(man_path, dtype={"sha256": str})
    split_df = pd.read_csv(s1_path)
    pilot_csv = Path(cfg["paths"]["pilot_work_dir"]) / f"{cfg['pilot']['name']}_selection.csv"
    pilot = set(pd.read_csv(pilot_csv)["index"].astype(int)) if pilot_csv.is_file() else set()
    sel, report, pool = select_subset(manifest, split_df, cfg["kaggle400"], cfg["split"]["known_shared_segment_links"], pilot)
    inputs = {"manifest_csv_sha256": got["manifest"], "split_csv_sha256": got["split"],
              "s1_csv_path": str(s1_path), "pilot50_selection_found": pilot_csv.is_file()}
    target = Path(tempfile.mkdtemp(prefix="k400_select_check_")) if args.check else data_root
    res = write_selection(target, cfg, sel, report, pool, inputs)
    corpus_path = (target if args.check else state_root) / "processed" / "glosses" / CORPUS_FILE
    n_words = write_corpus(manifest, corpus_path)
    print(json.dumps({"counts": res["counts"], "oov": res["oov"], "written_to": str(target / "data"),
                      "g0_corpus_words": n_words}, indent=1, ensure_ascii=False))
    from .verify import format_results

    print(format_results(res["checks"]))
    if not args.check:
        return 0
    same = []
    for rel in ("data/train/train_manifest.csv", "data/val/val_manifest.csv", "data/test/test_manifest.csv"):
        a, b = data_root / rel, target / rel
        same.append((rel, a.is_file() and sha256_text_canonical(a) == sha256_text_canonical(b)))
    sub_a = pd.read_csv(data_root / "data" / "subset_manifest.csv", dtype=str, encoding="utf-8-sig", keep_default_na=False)
    sub_b = pd.read_csv(target / "data" / "subset_manifest.csv", dtype=str, encoding="utf-8-sig", keep_default_na=False)
    same.append(("data/subset_manifest.csv (without sha256_copy)",
                 sub_a.drop(columns="sha256_copy").equals(sub_b.drop(columns="sha256_copy"))))
    ca = state_root / "processed" / "glosses" / CORPUS_FILE
    same.append((f"processed/glosses/{CORPUS_FILE}", ca.is_file() and sha256_text_canonical(ca) == sha256_text_canonical(corpus_path)))
    for rel, ok in same:
        print(f"{'PASS' if ok else 'FAIL'}  re-selection identical: {rel}")
    print("SELECTION CHECK:", "PASS (same 400 clips, same manifests)" if all(ok for _, ok in same) else "FAIL")
    return 0 if all(ok for _, ok in same) else 1


def cmd_copy(args) -> int:
    from .copyvid import run

    if not args.confirm:
        print("Refusing to copy without --confirm (owner permission: kaggle/tools/run_local_steps.ps1 passes it).")
        return 2
    cfg = _cfg()
    proj, data_root, _ = _roots(cfg)
    s1 = Path(cfg["paths"]["splits_dir"]) / f"{cfg['kaggle400']['source']['split']}.csv"
    return run(data_root, Path(cfg["paths"]["data_root"]), proj, cfg["split"]["known_shared_segment_links"],
               s1 if s1.is_file() else None)


def cmd_verify(args) -> int:
    from .verify import format_results, overall, run_checks, to_json

    cfg = _cfg()
    _, data_root, _ = _roots(cfg)
    s1 = Path(cfg["paths"]["splits_dir"]) / f"{cfg['kaggle400']['source']['split']}.csv"
    res = run_checks(data_root, cfg["split"]["known_shared_segment_links"], s1 if s1.is_file() else None,
                     require_videos=args.require_videos, hash_videos=not args.no_hash)
    print(to_json(res) if args.json else format_results(res))
    return 0 if overall(res, args.require_videos) else 1


def cmd_gloss(args) -> int:
    from .gloss import CORPUS_FILE, build_vocabs, compare, make_glosses, read_corpus, summary_json

    cfg = _cfg()
    proj, data_root, state_root = _roots(cfg)
    gloss_dir = state_root / "processed" / "glosses"
    corpus_file = gloss_dir / CORPUS_FILE
    if not corpus_file.is_file():
        committed = proj / "kaggle" / "processed" / "glosses" / CORPUS_FILE
        corpus_file.parent.mkdir(parents=True, exist_ok=True)
        corpus_file.write_bytes(committed.read_bytes())
    res = make_glosses(data_root / "data", gloss_dir, read_corpus(corpus_file), cfg["annotations"]["g0_ver"])
    vocab = build_vocabs(gloss_dir, state_root / "processed" / "vocab")
    out = {"label": "G0 pseudo-gloss (auto_draft, rule-based) - NOT a BdSL annotation", "glosses": res, "vocab": vocab}
    if args.compare_with:
        out["compare_with_committed"] = compare(gloss_dir, Path(args.compare_with))
    print(summary_json(out))
    bad = [k for k, v in out.get("compare_with_committed", {}).items() if v != "IDENTICAL"]
    return 1 if bad else 0


def cmd_package(args) -> int:
    from .package import PackageError, build

    cfg = _cfg()
    proj, data_root, _ = _roots(cfg)
    out = Path(args.out) if args.out else proj / "kaggle" / "work" / "upload"
    try:
        res = build(proj, data_root, out, allow_dirty=args.allow_dirty_for_tests)
    except PackageError as e:
        print(f"PACKAGE FAILED: {e}")
        return 1
    print(f"zip: {res['zip']}")
    print(f"zip size: {res['zip_bytes'] / 1e9:.3f} GB ({res['zip_bytes']:,} bytes); {res['files']} files; commit {res['commit']}")
    for k, v in res["sizes"].items():
        print(f"  {k:14s} {v['files']:5d} files  {v['bytes'] / 1e6:10.1f} MB")
    return 0


def cmd_verify_package(args) -> int:
    from .package import verify

    problems = verify(Path(args.zip))
    for p in problems[:30]:
        print("PROBLEM:", p)
    print("PACKAGE CHECK:", "PASS" if not problems else f"FAIL ({len(problems)} problems)")
    return 0 if not problems else 1


def cmd_verify_download(args) -> int:
    import csv
    import hashlib

    root = Path(args.dir)
    rows = list(csv.DictReader(open(root / "OUTPUT_HASHES.csv", encoding="utf-8")))
    bad = []
    for r in rows:
        f = root / r["path"]
        if not f.is_file() or hashlib.sha256(f.read_bytes()).hexdigest() != r["sha256"]:
            bad.append(r["path"])
    print(f"{len(rows) - len(bad)}/{len(rows)} files match OUTPUT_HASHES.csv")
    for b in bad[:20]:
        print("MISMATCH:", b)
    print("DOWNLOAD CHECK:", "PASS" if not bad else "FAIL")
    return 0 if not bad else 1


def cmd_verify_upload(args) -> int:
    """Notebook 01: SHA-256 of every uploaded file against UPLOAD_MANIFEST.csv (videos, manifests, code)."""
    import csv

    from bdsl.io import sha256_file

    cfg = _cfg()
    root = Path(args.root) if args.root else Path(cfg["paths"]["k400_data_root"])
    man = root / "UPLOAD_MANIFEST.csv"
    if not man.is_file():
        print(f"No UPLOAD_MANIFEST.csv in {root} (only the uploaded package has one).")
        return 1
    rows = list(csv.DictReader(open(man, encoding="utf-8")))
    bad, missing = [], []
    for n, r in enumerate(rows, 1):
        f = root / r["path"]
        if not f.is_file():
            missing.append(r["path"])
        elif f.stat().st_size != int(r["bytes"]) or sha256_file(f) != r["sha256"]:
            bad.append(r["path"])
        if n % 100 == 0:
            print(f"  {n}/{len(rows)} files checked", flush=True)
    kinds = {"videos": sum(r["path"].endswith(".mp4") for r in rows), "code": sum(r["path"].startswith("code/") for r in rows)}
    print(f"files listed: {len(rows)} (videos {kinds['videos']}, code files {kinds['code']}); "
          f"missing: {len(missing)}; different: {len(bad)}")
    for x in (missing + bad)[:20]:
        print("PROBLEM:", x)
    print("UPLOAD CHECK:", "PASS (every file identical to the desktop package)" if not (bad or missing) else "FAIL")
    return 0 if not (bad or missing) else 1


def cmd_env_report(args) -> int:
    import platform
    import shutil

    from bdsl.device import device_info, resolve_device
    from bdsl.io import atomic_write_json
    from bdsl.provenance import code_provenance, installed_packages

    cfg = _cfg()
    proj, _, state_root = _roots(cfg)
    dev, note = resolve_device("auto")
    du = shutil.disk_usage(state_root)
    rep = {"python": sys.version.split()[0], "platform": platform.platform(), "cpu_count": __import__("os").cpu_count(),
           "device": device_info(dev), "device_note": note, "code": code_provenance(proj),
           "disk_free_gb_working": round(du.free / 1e9, 1), "disk_total_gb_working": round(du.total / 1e9, 1),
           "packages": installed_packages()}
    try:
        import psutil  # noqa: F401  (optional)

        rep["ram_gb"] = round(__import__("psutil").virtual_memory().total / 1e9, 1)
    except ImportError:
        rep["ram_gb"] = None
    atomic_write_json(state_root / "outputs" / "env" / "env_report.json", rep)
    print(json.dumps({k: v for k, v in rep.items() if k != "packages"}, indent=1))
    return 0


def cmd_mp_setup(args) -> int:
    from bdsl.io import atomic_write_json

    from .mp_env import download_model, ensure

    cfg = _cfg()
    _, data_root, state_root = _roots(cfg)
    mp = cfg["mediapipe"]
    model_dir = Path(args.model_dir) if args.model_dir else _scratch(state_root) / "models"
    model = download_model(mp["model_url"], model_dir / mp["model_file"], mp["model_sha256"])
    print(json.dumps({"model": model}, indent=1))
    if not model["ok"]:
        print("MODEL FILE SHA-256 DIFFERS from configs/base.yaml: the URL now serves a different model. "
              "STOP and tell Claude (fallback: upload the desktop copy work/models/holistic_landmarker.task "
              "as a small private dataset).")
        return 1
    video = Path(args.video) if args.video else next(iter(sorted((data_root / "data" / "train" / "videos").glob("*.mp4"))), None)
    rep = ensure(Path(model["path"]), video, _scratch(state_root) / "py312", allow_fallback=not args.no_fallback)
    rep["model"] = model
    atomic_write_json(state_root / "outputs" / "env" / "mediapipe_route.json", rep)
    print(json.dumps({k: rep[k] for k in ("route", "python", "probe", "ok")}, indent=1))
    print("MEDIAPIPE:", f"OK via {rep['route']}" if rep["ok"] else "FAILED on both routes - STOP and paste this output to Claude")
    return 0 if rep["ok"] else 1


def cmd_extract(args) -> int:
    from .extract import as_json, print_summary, run

    cfg = _cfg()
    _, data_root, state_root = _roots(cfg)
    model = Path(args.model) if args.model else _scratch(state_root) / "models" / cfg["mediapipe"]["model_file"]
    max_min = args.max_minutes if args.max_minutes is not None else cfg["kaggle400"]["extraction"]["max_minutes"]
    summary = run(cfg, data_root / "data", state_root, model, workers=args.workers, max_minutes=max_min,
                  splits=tuple(args.splits))
    print(print_summary(summary))
    if args.json:
        print(as_json(summary))
    return 0 if summary["complete"] else 3


def cmd_report(args) -> int:
    from .report import build_report

    res = build_report(_cfg())
    print(json.dumps(res, indent=1, ensure_ascii=False))
    return 0


def cmd_avatar(args) -> int:
    from .avatar import export

    res = export(_cfg(), n=args.n)
    print(json.dumps(res, indent=1, ensure_ascii=False))
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="k400_run.py", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("select")
    s.add_argument("--check", action="store_true", help="re-select into a temp folder and compare with kaggle/data")
    s.set_defaults(func=cmd_select)
    c = sub.add_parser("copy-videos")
    c.add_argument("--confirm", action="store_true")
    c.set_defaults(func=cmd_copy)
    v = sub.add_parser("verify")
    v.add_argument("--require-videos", action="store_true")
    v.add_argument("--no-hash", action="store_true", help="skip SHA-256 of the videos (quick check)")
    v.add_argument("--json", action="store_true")
    v.set_defaults(func=cmd_verify)
    g = sub.add_parser("gloss")
    g.add_argument("--compare-with", default=None, help="folder with the committed gloss_g0_<split>.csv files")
    g.set_defaults(func=cmd_gloss)
    p = sub.add_parser("package")
    p.add_argument("--out", default=None)
    p.add_argument("--allow-dirty-for-tests", action="store_true", help=argparse.SUPPRESS)
    p.set_defaults(func=cmd_package)
    vp = sub.add_parser("verify-package")
    vp.add_argument("zip")
    vp.set_defaults(func=cmd_verify_package)
    vd = sub.add_parser("verify-download")
    vd.add_argument("dir", help="folder that contains OUTPUT_HASHES.csv (the downloaded k400 folder)")
    vd.set_defaults(func=cmd_verify_download)
    vu = sub.add_parser("verify-upload")
    vu.add_argument("--root", default=None, help="dataset root with UPLOAD_MANIFEST.csv (default: K400 data root)")
    vu.set_defaults(func=cmd_verify_upload)
    sub.add_parser("env-report").set_defaults(func=cmd_env_report)
    m = sub.add_parser("mp-setup")
    m.add_argument("--video", default=None)
    m.add_argument("--model-dir", default=None)
    m.add_argument("--no-fallback", action="store_true")
    m.set_defaults(func=cmd_mp_setup)
    e = sub.add_parser("extract")
    e.add_argument("--splits", nargs="+", default=["train", "val", "test"], choices=["train", "val", "test"])
    e.add_argument("--max-minutes", type=float, default=None)
    e.add_argument("--workers", type=int, default=None)
    e.add_argument("--model", default=None)
    e.add_argument("--json", action="store_true")
    e.set_defaults(func=cmd_extract)
    sub.add_parser("report").set_defaults(func=cmd_report)
    a = sub.add_parser("avatar")
    a.add_argument("--n", type=int, default=None)
    a.set_defaults(func=cmd_avatar)
    args = ap.parse_args(argv)
    return args.func(args)
