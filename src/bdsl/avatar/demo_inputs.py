"""Read-only demo inputs: legacy pilot layout or config-selected split/G0 layout.

Split-layout versions declare paths.demo_data_root (data/) and paths.demo_state_root
(processed/ + outputs/). The existing split/G0 reader is reused with an adapted config;
training paths and the caller's config are never changed. No video is opened here.
"""

from __future__ import annotations

import copy
import hashlib
import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

from ..data import kaggle400 as split_data
from ..io import sha256_file
from ..models.text2gloss import Vocab, vocab_hash
from ..models.train_gloss2motion import load_items


def resolve_demo_paths(cfg: dict) -> dict:
    """Resolve a configured layout, without probing files or creating directories."""
    name, paths = cfg["data"]["name"], cfg["paths"]
    if name == "pilot50":
        return {"data": name, "layout": "pilot", "runs": Path(paths["runs_dir"]),
                "features": Path(paths["features_dir"]) / cfg["gloss2motion"]["feat_ver"]}
    if not all(paths.get(k) for k in ("demo_data_root", "demo_state_root")):
        raise ValueError(f"Version {name!r} needs paths.demo_data_root and paths.demo_state_root")
    adapted = copy.deepcopy(cfg)
    adapted["paths"].update(k400_data_root=paths["demo_data_root"], k400_state_root=paths["demo_state_root"])
    resolved = split_data.paths(adapted)
    return {**resolved, "data": name, "layout": "split", "features": None, "reader_config": adapted,
            "corpus": Path(paths["demo_state_root"]) / "processed/glosses/g0_corpus_v1.txt"}


@dataclass
class DemoInputs:
    paths: dict
    run_dir: Path
    meta: dict
    rows: pd.DataFrame
    items: list[dict]
    train: list[dict]
    vocab: Vocab
    mean: np.ndarray
    sd: np.ndarray
    corpus: set[str]
    blend_names: list[str]
    checks: dict


def load_demo_inputs(cfg: dict, model_run: str, seed: int) -> DemoInputs:
    """Validate the version, run and training fingerprints before inference or writing."""
    p = resolve_demo_paths(cfg)
    root = p["runs"].resolve()
    run_dir = (root / model_run).resolve()
    if run_dir.parent != root:
        raise ValueError("the run must be a direct child of this version's configured runs folder")
    meta = json.loads((run_dir / "run.json").read_text(encoding="utf-8"))
    # Old pilot run.json files predate the explicit data field; their manifest/input
    # fingerprints below still have to match. Split-layout runs must identify the version.
    if meta.get("data", "pilot50") != p["data"]:
        raise ValueError(f"run version {meta.get('data', 'pilot50')!r} does not match {p['data']!r}")
    if meta.get("input") != "gloss":
        raise ValueError("the demo requires a gloss-input Model B run")
    if meta.get("overfit") or meta.get("max_steps") or run_dir.name.startswith(("TEST_", "DRYRUN_", "NFP_")):
        raise ValueError("engineering checks are not supported as result demos")
    if seed not in meta["seeds"]:
        raise ValueError(f"seed {seed} is not in this run's seeds {meta['seeds']}")
    if not (run_dir / f"seed{seed}/ckpt_best.pt").is_file():
        raise FileNotFoundError(f"missing best checkpoint for seed {seed} in {run_dir}")
    gcfg = cfg["gloss2motion"]
    gcfg_sha = hashlib.sha256(json.dumps(gcfg, sort_keys=True).encode()).hexdigest()
    checks = {"model_config_sha256": gcfg_sha == meta["gloss2motion_config_sha256"],
              "feat_ver": gcfg["feat_ver"] == meta["feat_ver"], "fps": cfg["features"]["fps"] == meta["fps"]}
    if not all(checks.values()):
        raise ValueError(f"the version's motion settings differ from the run: {checks}")

    if p["layout"] == "pilot":
        from ..cli import check_model_b_inputs
        from ..data.manifest import read_sheet
        from ..text.normalize import tokens

        rows, problems, inputs_sha = check_model_b_inputs(cfg)
        manifest = Path(cfg["paths"]["pilot_dest_dir"]) / "pilot50_manifest.csv"
        checks["manifest_sha256"] = sha256_file(manifest) == meta["pilot_manifest_sha256"]
        corpus = {t for s in read_sheet(cfg)["sentence_raw"] for t in tokens(s)}
    else:
        adapted = p["reader_config"]
        lock = split_data.check_split_lock(adapted)
        rows, problems, inputs_sha = split_data.model_inputs(adapted, split_data.TRAINING_SPLITS, meta["feat_ver"])
        checks["split_lock_sha256"] = lock["lock_sha256"] == meta["split_lock_sha256"] == meta["pilot_manifest_sha256"]
        g0_sha = split_data.glosses_sha256(adapted, split_data.TRAINING_SPLITS)
        checks["g0_files_sha256"] = g0_sha == meta["g0_files_sha256"]
        corpus = {line.strip() for line in p["corpus"].read_text(encoding="utf-8").splitlines() if line.strip()}
    if problems:
        raise ValueError(f"Model B inputs failed the checks: {problems[:3]}")
    checks["inputs_sha256"] = inputs_sha == meta["inputs_sha256"]
    checks["split_counts"] = rows["split"].value_counts().to_dict() == meta["counts"]
    if not all(checks.values()):
        raise ValueError(f"the run's inputs changed since training: {checks}")

    items = load_items(rows, p["features"], "gloss", gcfg["max_gap"])
    train = [it for it in items if it["split"] == "train"]
    if not train:
        raise ValueError("the configured version has no training items for vocabulary/B1")
    vocab = Vocab([t for it in train for t in it["tokens"]])
    checks["vocab_sha256"] = (vocab_hash(vocab, vocab) == meta["vocab_sha256"]
                              and len(vocab) == meta["vocab_size"])
    if p["layout"] == "split":
        saved = json.loads((p["vocab_dir"] / "vocab_modelB_gloss_input.json").read_text(encoding="utf-8"))
        checks["saved_train_vocab"] = (saved["itos"] == vocab.itos and saved["size"] == len(vocab)
                                       and saved["built_from"] == "train")
    with np.load(run_dir / "standardizer.npz", allow_pickle=False) as z:
        mean, sd = z["mean"], z["sd"]
    std_sha = hashlib.sha256(mean.tobytes() + sd.tobytes()).hexdigest()
    checks["standardizer_sha256"] = std_sha == meta["standardizer_sha256"]
    checks["standardizer_valid"] = (mean.shape == sd.shape == (208,)
                                    and bool(np.isfinite(mean).all() and np.isfinite(sd).all() and (sd > 0).all()))
    if not all(checks.values()):
        raise ValueError(f"the run's vocabulary or standardizer changed: {checks}")
    sample = next(p["features"].glob("*.npz")) if p["layout"] == "pilot" else Path(rows.iloc[0]["feature_path"])
    with np.load(sample, allow_pickle=False) as z:
        blend_names = [str(n) for n in z["blendshape_names"]]
    return DemoInputs(p, run_dir, meta, rows, items, train, vocab, mean, sd, corpus, blend_names, checks)
