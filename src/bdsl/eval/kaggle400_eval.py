"""kaggle400 evaluation: freeze the configuration, evaluate on val, then evaluate ONCE on the locked test split.

    freeze      writes outputs/frozen_config.json: the chosen runs, every best checkpoint's SHA-256, the
                split-lock hash, the code commit and the bootstrap settings. Refused after the final run.
    evaluate    --split val: any time after freezing (no lock).
                --final (test): reads the test rows for the first time, inside `final_test_access`;
                writes outputs/FINAL_TEST_LOCK.json; a second final run is refused unless the owner
                gives a written reason (`--override-reason "…"`), which is recorded in the lock.

Methods compared (owner, 2026-10-23): Model B (G0 gloss input), Model B (Bangla word input, ablation T),
B0 mean motion, B1 retrieval (no exact copies, no shared-segment partners); Model A trained on G0
pseudo-glosses, reported only as "agreement with the rule glosser (G0 pseudo-gloss)".
Every interval is a percentile bootstrap over items (default 1,000 resamples, 95%).
"""

from __future__ import annotations

import io
import json
import statistics
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
import torch

from ..data import kaggle400 as k4
from ..features.normalize import PARTS, Standardizer, expand_mask
from ..io import atomic_write_bytes, atomic_write_json, atomic_write_text, sha256_file, sha256_text_canonical
from ..models.baselines import b0_mean_motion, b1_retrieve
from ..models.gloss2motion import Gloss2Motion
from ..models.text2gloss import Vocab, split_tags, vocab_hash
from ..provenance import code_provenance
from .bootstrap import bootstrap_mean, bootstrap_paired_diff, bootstrap_stat, resample_indices
from .motion_metrics import item_metrics, resample
from .text_metrics import bleu_chrf, exact_match, item_wer, tag_accuracy, wer

LABEL_B = "kaggle400: small-scale (320/40/40 clips), signer-dependent; coordinate error is not proof of correct BdSL"
LABEL_A = ("Model A: agreement with the rule glosser (G0 pseudo-gloss); not BdSL correctness "
           "(references are G0 auto_draft outputs)")
B_METRICS = ("mpjpe_body", "mpjpe_lhand", "mpjpe_rhand", "mpjpe_face", "dtw_body", "dtw_lhand", "dtw_rhand",
             "dtw_face", "duration_err_s", "velocity_ratio", "jerk_ratio", "hand_energy_ratio")
B_KEY_METRICS = ("mpjpe_body", "mpjpe_lhand", "mpjpe_rhand", "dtw_body", "dtw_lhand", "dtw_rhand", "duration_err_s")
A_METRICS = ("wer", "exact_match", "tag_accuracy", "bleu4", "chrf")
ROLES = {"model_b_gloss": "Model B (G0 gloss input)", "model_b_text": "Model B (Bangla word input, ablation T)",
         "model_a": "Model A (G0-reference A-GRU)"}


class FreezeError(RuntimeError):
    pass


class FinalLockError(RuntimeError):
    pass


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _run_json(run_dir: Path) -> dict:
    return json.loads((run_dir / "run.json").read_text(encoding="utf-8"))


def list_runs(cfg: dict) -> pd.DataFrame:
    """Every run folder under outputs/runs with what is needed to choose the frozen runs."""
    rows = []
    for d in sorted(k4.paths(cfg)["runs"].glob("*")):
        if not (d / "run.json").is_file():
            continue
        m = _run_json(d)
        rows.append({"run_id": d.name, "kind": "model_a" if "text2gloss" in d.name else "model_b",
                     "input": m.get("input") or m.get("reference"), "data": m.get("data"),
                     "finished": (d / "metrics.json").is_file(), "for_paper": m.get("for_paper", False),
                     "overfit": m.get("overfit"), "dry_run": bool(m.get("max_steps")), "seeds": m.get("seeds"),
                     "device": m.get("device"), "created_utc": m.get("created_utc"),
                     "overrides": json.dumps(m.get("overrides") or {}, ensure_ascii=False)})
    return pd.DataFrame(rows)


def latest_result_runs(cfg: dict) -> dict:
    """Newest finished, for-paper, non-overfit kaggle400 run per role (None where missing)."""
    runs = list_runs(cfg)
    out = {}
    if runs.empty:
        return dict.fromkeys(ROLES)
    ok = runs[runs["finished"] & runs["for_paper"] & runs["overfit"].isna() & ~runs["dry_run"] & (runs["data"] == "kaggle400")]
    for role, kind, inp in (("model_b_gloss", "model_b", "gloss"), ("model_b_text", "model_b", "text"),
                            ("model_a", "model_a", "g0")):
        sel = ok[(ok["kind"] == kind) & (ok["input"] == inp)].copy()
        # prefer runs with the default configuration (no --set overrides), then the newest
        sel["_default"] = sel["overrides"] == "{}"
        sel = sel.sort_values(["_default", "created_utc"])
        out[role] = sel["run_id"].iloc[-1] if len(sel) else None
    return out


def _lock_present(cfg: dict) -> Path | None:
    p = k4.paths(cfg)["final_lock"]
    return p if p.is_file() else None


def freeze(cfg: dict, runs: dict, not_for_paper: bool = False, replace: bool = False) -> dict:
    """Write frozen_config.json for the runs {role: run_id}. Refused after the final evaluation."""
    p = k4.paths(cfg)
    if _lock_present(cfg):
        raise FreezeError(f"{p['final_lock']} exists: the test split was already used; the configuration cannot change.")
    if p["frozen"].is_file() and not replace:
        raise FreezeError(f"{p['frozen']} exists; pass replace=True (--replace) to re-freeze before the final run.")
    lock = k4.check_split_lock(cfg)
    frozen = {"frozen_utc": _now(), "label": "kaggle400 frozen configuration for the single final test evaluation",
              "split_lock_sha256": lock["lock_sha256"], "config_hash": cfg["_meta"]["config_hash"],
              "code": code_provenance(cfg["_meta"]["project_root"]), "bootstrap": dict(cfg["kaggle400"]["bootstrap"]),
              "for_paper": True, "runs": {}}
    for role in ROLES:
        rid = runs.get(role)
        if not rid:
            raise FreezeError(f"no run chosen for {role} ({ROLES[role]})")
        d = p["runs"] / rid
        if not (d / "metrics.json").is_file():
            raise FreezeError(f"{rid}: not finished (no metrics.json)")
        m = _run_json(d)
        problems = []
        if m.get("data") != "kaggle400":
            problems.append("not a kaggle400 run")
        if m.get("overfit") or m.get("max_steps"):
            problems.append("an overfit check or dry run")
        if m.get("split_lock_sha256") != lock["lock_sha256"]:
            problems.append("trained with a different SPLIT_LOCK.json")
        if not m.get("for_paper", False):
            problems.append("marked NOT FOR PAPER")
        if problems and not (not_for_paper and problems == ["marked NOT FOR PAPER"]):
            raise FreezeError(f"{rid}: {', '.join(problems)}")
        if "marked NOT FOR PAPER" in problems:
            frozen["for_paper"] = False
        frozen["runs"][role] = {
            "run_id": rid, "description": ROLES[role], "seeds": m["seeds"], "run_json_sha256": sha256_file(d / "run.json"),
            "checkpoints": {str(s): {"file": f"seed{s}/ckpt_best.pt", "sha256": sha256_file(d / f"seed{s}" / "ckpt_best.pt")}
                            for s in m["seeds"]}}
    atomic_write_json(p["frozen"], frozen)
    return frozen


def _check_frozen(cfg: dict) -> dict:
    p = k4.paths(cfg)
    if not p["frozen"].is_file():
        raise FreezeError(f"{p['frozen']} is missing: run `freeze` first.")
    frozen = json.loads(p["frozen"].read_text(encoding="utf-8"))
    lock = k4.check_split_lock(cfg)
    if lock["lock_sha256"] != frozen["split_lock_sha256"]:
        raise FreezeError("SPLIT_LOCK.json changed since the configuration was frozen")
    for role, r in frozen["runs"].items():
        d = p["runs"] / r["run_id"]
        if sha256_file(d / "run.json") != r["run_json_sha256"]:
            raise FreezeError(f"{r['run_id']}: run.json changed since freezing")
        for s, c in r["checkpoints"].items():
            if sha256_file(d / c["file"]) != c["sha256"]:
                raise FreezeError(f"{r['run_id']} seed {s}: checkpoint changed since freezing")
    return frozen


# ---------------------------------------------------------------- items and strata
def _items(cfg: dict, split: str, mode: str, feat_ver: str, max_gap: int) -> tuple[list[dict], pd.DataFrame]:
    from ..models.train_gloss2motion import load_items

    df, problems, _ = k4.model_inputs(cfg, (split,), feat_ver)
    if problems:
        raise RuntimeError(f"{split} inputs failed the checks: {problems[:3]}")
    return load_items(df, None, mode, max_gap), df


def strata_table(cfg: dict, split: str, train_items: list[dict], target_items: list[dict]) -> pd.DataFrame:
    """Per item: the strata used for error analysis (indicative tags are word lists, not linguistics)."""
    from ..text.tags import is_negation, is_question, length_bucket

    man = k4.read_split_manifest(cfg, split).set_index("index")
    train_vocab = {t for it in train_items for t in it["tokens_text"]}
    cov_train = [float((it["mask"][:, 1] | it["mask"][:, 2]).mean()) for it in train_items]
    q1, q2 = np.percentile(cov_train, [100 / 3, 200 / 3])
    rows = []
    for it in target_items:
        r = man.loc[it["index"]]
        toks = it["tokens_text"]
        cov = float((it["mask"][:, 1] | it["mask"][:, 2]).mean())
        rows.append({"index": it["index"], "split": split, "sentence_norm": r["sentence_norm"],
                     "length_bucket": length_bucket(len(toks)), "question": bool(is_question(toks)),
                     "negation": bool(is_negation(toks)), "oov": any(t not in train_vocab for t in toks),
                     "oov_words": " ".join(t for t in toks if t not in train_vocab),
                     "minimal_pair_sibling_in_train": bool(r.get("has_train_minimal_pair_sibling", False)),
                     "hand_coverage": round(cov, 4),
                     "hand_coverage_tertile": "low" if cov < q1 else ("mid" if cov < q2 else "high"),
                     "orientation": r["orientation"]})
    return pd.DataFrame(rows)


STRATA = ("length_bucket", "question", "negation", "oov", "minimal_pair_sibling_in_train", "hand_coverage_tertile",
          "orientation")


# ---------------------------------------------------------------- Model B family
def _flat_body(xs: list[np.ndarray], n: int = 32) -> np.ndarray:
    return np.stack([resample(x[:, PARTS["body"]], n).ravel() for x in xs])


def _pairwise(F: np.ndarray) -> np.ndarray:
    return np.linalg.norm(F[:, None] - F[None], axis=-1)


def _diversity_stat(Dp: np.ndarray, Dg: np.ndarray):
    def stat(idx):
        m = np.triu(np.ones((len(idx), len(idx)), bool), 1) & (idx[:, None] != idx[None, :])
        if not m.any():
            return float("nan")
        g = Dg[np.ix_(idx, idx)][m].mean()
        return float(Dp[np.ix_(idx, idx)][m].mean() / g) if g else float("nan")
    return stat


def _gt(it: dict, std: Standardizer) -> np.ndarray:
    """Ground-truth frames as in training (missing parts = training mean; masked out of every error)."""
    return np.where(expand_mask(it["mask"]), it["x"], std.mean)


def _model_b(cfg, role_run: dict, split: str, items_by_mode: dict, train_by_mode: dict, device) -> dict:
    """Per-seed per-item metrics and raw predictions of one Model B run on `split`."""
    from ..models.train_gloss2motion import predict_items

    run_dir = k4.paths(cfg)["runs"] / role_run["run_id"]
    meta = _run_json(run_dir)
    mode, gcfg = meta["input"], meta["gloss2motion_config"]
    train, items = train_by_mode[mode], items_by_mode[mode]
    vocab = Vocab([t for it in train for t in it["tokens"]])
    if vocab_hash(vocab, vocab) != meta["vocab_sha256"]:
        raise RuntimeError(f"{run_dir.name}: training vocabulary differs from the run's")
    with np.load(run_dir / "standardizer.npz") as z:
        std = Standardizer(z["mean"], z["sd"])
    fps = float(cfg["features"]["fps"])
    out = {"run_id": run_dir.name, "mode": mode, "std": std, "per_seed": {}, "raw": {}}
    for s in meta["seeds"]:
        model = Gloss2Motion(len(vocab), **gcfg["model"]).to(device)
        model.load_state_dict(torch.load(run_dir / f"seed{s}" / "ckpt_best.pt", weights_only=True,
                                         map_location=device)["model"])
        model.eval()
        preds = predict_items(model, items, vocab, gcfg["max_frames"], device)
        raw = {i: std.invert(z) for i, z in preds.items()}
        out["raw"][str(s)] = raw
        out["per_seed"][str(s)] = {it["index"]: item_metrics(raw[it["index"]], _gt(it, std), it["mask"], fps, dtw=True)
                                   for it in items}
    out["unknown_tokens"] = {it["index"]: [t for t in it["tokens"] if t not in vocab.stoi] for it in items}
    return out


def _baselines(cfg, std: Standardizer, items: list[dict], train: list[dict]) -> dict:
    from ..models.train_gloss2motion import b1_pool

    fps = float(cfg["features"]["fps"])
    tz = [std.apply(t["x"], t["mask"]) for t in train]
    b0_raw = std.invert(b0_mean_motion(tz, [expand_mask(t["mask"]) for t in train]))
    out = {"B0": {"raw": {}, "items": {}}, "B1": {"raw": {}, "items": {}, "source": {}}}
    for it in items:
        out["B0"]["raw"][it["index"]] = b0_raw
        out["B0"]["items"][it["index"]] = item_metrics(b0_raw, _gt(it, std), it["mask"], fps, dtw=True)
        pool = b1_pool(it, train)
        src = pool[b1_retrieve(it["gloss"], [t["gloss"] for t in pool], [t["index"] for t in pool])]
        x = _gt(src, std)   # the real recording; its missing parts → training mean (as in training)
        out["B1"]["raw"][it["index"]] = x
        out["B1"]["items"][it["index"]] = item_metrics(x, _gt(it, std), it["mask"], fps, dtw=True)
        out["B1"]["source"][it["index"]] = src["index"]
    return out


def _summ_b(per_item: dict[int, dict], order: list[int], boot: dict, seed_offset: int) -> dict:
    out = {}
    for k in B_METRICS:
        v = [per_item[i].get(k, np.nan) for i in order]
        out[k] = {"mean": float(np.nanmean(v)) if np.isfinite(v).any() else float("nan"),
                  "ci95": bootstrap_mean(v, boot["resamples"], boot["ci"], boot["seed"] + seed_offset)}
    return out


def evaluate_motion(cfg, frozen, split: str, device) -> dict:
    gcfg, boot = cfg["gloss2motion"], frozen["bootstrap"]
    train_by_mode, items_by_mode = {}, {}
    for mode in ("gloss", "text"):
        train_by_mode[mode], _ = _items(cfg, "train", mode, gcfg["feat_ver"], gcfg["max_gap"])
        items_by_mode[mode], _ = _items(cfg, split, mode, gcfg["feat_ver"], gcfg["max_gap"])
    for mode in ("gloss", "text"):   # text tokens for strata
        for it, t in zip(items_by_mode[mode], items_by_mode["text"]):
            it["tokens_text"] = t["tokens"]
        for it, t in zip(train_by_mode[mode], train_by_mode["text"]):
            it["tokens_text"] = t["tokens"]
    order = [it["index"] for it in items_by_mode["gloss"]]
    res = {"label": LABEL_B, "split": split, "n_items": len(order), "methods": {}}
    raws, per_item_tables = {}, {}
    runs = {r: _model_b(cfg, frozen["runs"][r], split, items_by_mode, train_by_mode, device)
            for r in ("model_b_gloss", "model_b_text")}
    std_g = runs["model_b_gloss"]["std"]
    gt = {it["index"]: {"x": _gt(it, std_g)} for it in items_by_mode["gloss"]}
    for r, out in runs.items():
        seeds = list(out["per_seed"])
        seedmean = {i: {k: float(np.nanmean([out["per_seed"][s][i].get(k, np.nan) for s in seeds]))
                        if np.isfinite([out["per_seed"][s][i].get(k, np.nan) for s in seeds]).any() else float("nan")
                        for k in B_METRICS} for i in order}
        per_seed_summary = {s: {k: float(np.nanmean([out["per_seed"][s][i].get(k, np.nan) for i in order]))
                                for k in B_METRICS} for s in seeds}
        Dg = _pairwise(_flat_body([gt[i]["x"] for i in order]))
        div = {}
        for n_s, s in enumerate(seeds):
            Dp = _pairwise(_flat_body([out["raw"][s][i] for i in order]))
            div[s] = bootstrap_stat(len(order), _diversity_stat(Dp, Dg), boot["resamples"], boot["ci"], boot["seed"] + 50 + n_s)
        res["methods"][r] = {
            "description": ROLES[r], "run_id": out["run_id"], "seeds": seeds,
            "per_seed": per_seed_summary,
            "mean_sd_over_seeds": {k: {"mean": statistics.mean([per_seed_summary[s][k] for s in seeds]),
                                       "sd": statistics.stdev([per_seed_summary[s][k] for s in seeds]) if len(seeds) > 1 else 0.0}
                                   for k in B_METRICS},
            "seed_mean_items_ci95": _summ_b(seedmean, order, boot, 0),
            "diversity_ratio": {"per_seed": {s: d["estimate"] for s, d in div.items()},
                                "mean": statistics.mean([d["estimate"] for d in div.values()]),
                                "sd": statistics.stdev([d["estimate"] for d in div.values()]) if len(div) > 1 else 0.0,
                                "ci95_per_seed": div},
            "unknown_token_items": int(sum(bool(v) for v in out["unknown_tokens"].values())),
        }
        per_item_tables[r] = seedmean
        raws[r] = out["raw"][seeds[0]]
    base = _baselines(cfg, runs["model_b_gloss"]["std"], items_by_mode["gloss"], train_by_mode["gloss"])
    Dg = _pairwise(_flat_body([gt[i]["x"] for i in order]))
    for b in ("B0", "B1"):
        items = base[b]["items"]
        Dp = _pairwise(_flat_body([base[b]["raw"][i] for i in order]))
        res["methods"][b] = {
            "description": "B0 mean motion of the training clips" if b == "B0" else
                           "B1 retrieval: real motion of the most similar training sentence (no exact copies, no shared-segment partners)",
            "summary": {k: float(np.nanmean([items[i].get(k, np.nan) for i in order])) for k in B_METRICS},
            "items_ci95": _summ_b(items, order, boot, 100 if b == "B0" else 200),
            "diversity_ratio": bootstrap_stat(len(order), _diversity_stat(Dp, Dg), boot["resamples"], boot["ci"],
                                              boot["seed"] + (300 if b == "B0" else 400)),
        }
        per_item_tables[b] = items
        raws[b] = base[b]["raw"]
    comps = {}
    for a, b in (("model_b_gloss", "B0"), ("model_b_gloss", "B1"), ("model_b_gloss", "model_b_text"),
                 ("model_b_text", "B0")):
        comps[f"{a} - {b}"] = {k: bootstrap_paired_diff([per_item_tables[a][i].get(k, np.nan) for i in order],
                                                        [per_item_tables[b][i].get(k, np.nan) for i in order],
                                                        boot["resamples"], boot["ci"], boot["seed"] + 500)
                               for k in B_KEY_METRICS}
    res["paired_differences"] = comps
    res["paired_note"] = ("difference = first − second, mean over items; negative error difference = first is better; "
                          "'excludes_zero' = the 95% interval lies on one side of 0")
    strata = strata_table(cfg, split, train_by_mode["gloss"], items_by_mode["gloss"])
    per_item = strata.copy()
    for m, tab in per_item_tables.items():
        for k in B_METRICS:
            per_item[f"{m}__{k}"] = [tab[i].get(k, np.nan) for i in per_item["index"]]
    per_item["B1_source_index"] = [base["B1"]["source"][i] for i in per_item["index"]]
    per_item["gt_frames"] = [len(gt[i]["x"]) for i in per_item["index"]]
    raws["real_recording"] = {i: gt[i]["x"] for i in order}
    for r, out in runs.items():
        per_item[f"{r}__unknown_tokens"] = [" ".join(out["unknown_tokens"][i]) for i in per_item["index"]]
    return {"summary": res, "per_item": per_item, "raws": raws, "strata": strata,
            "blend_names": None, "train_by_mode": train_by_mode, "items_by_mode": items_by_mode}


# ---------------------------------------------------------------- Model A
def evaluate_text(cfg, frozen, split: str, device) -> dict:
    from ..models.train_text2gloss import build_vocabs, make_model, make_pairs, predict

    r = frozen["runs"]["model_a"]
    run_dir = k4.paths(cfg)["runs"] / r["run_id"]
    meta = _run_json(run_dir)
    tcfg = meta["text2gloss_config"]
    train_df, _, _ = k4.model_inputs(cfg, ("train",), cfg["gloss2motion"]["feat_ver"])
    split_df, _, _ = k4.model_inputs(cfg, (split,), cfg["gloss2motion"]["feat_ver"])
    train = make_pairs(train_df, tcfg["tag_prefix"], "g0")
    pairs = make_pairs(split_df, tcfg["tag_prefix"], "g0")
    src_v, tgt_v = build_vocabs(train)
    if vocab_hash(src_v, tgt_v) != meta["vocab_sha256"]:
        raise RuntimeError(f"{run_dir.name}: Model A vocabularies differ from the run's")
    boot = frozen["bootstrap"]
    outs = {}
    for s in meta["seeds"]:
        model = make_model(tcfg, src_v, tgt_v).to(device)
        model.load_state_dict(torch.load(run_dir / f"seed{s}" / "ckpt_best.pt", weights_only=True,
                                         map_location=device)["model"])
        outs[str(s)] = predict(model, pairs, src_v, tgt_v, tcfg["max_len"], tcfg["beam"])
    refs = [p["gloss"] for p in pairs]
    ref_tags = [p["tags"] for p in pairs]
    split_outs = {s: [split_tags(o) for o in v] for s, v in outs.items()}

    def corpus(idx, s):
        hyp = [split_outs[s][i][1] for i in idx]
        ref = [refs[i] for i in idx]
        bc = bleu_chrf(ref, hyp)
        return {"wer": wer(ref, hyp), "exact_match": exact_match(ref, hyp),
                "tag_accuracy": tag_accuracy([ref_tags[i] for i in idx], [split_outs[s][i][0] for i in idx]), **bc}

    n = len(pairs)
    per_seed = {s: corpus(list(range(n)), s) for s in outs}
    # One pass over the resamples: every metric of the seed-mean, then percentiles per metric.
    draws = {k: [] for k in A_METRICS}
    for idx in resample_indices(n, boot["resamples"], boot["seed"] + 700) if n else []:
        per = [corpus(list(idx), s) for s in outs]
        for k in A_METRICS:
            draws[k].append(statistics.mean(c[k] for c in per))
    a = (100.0 - boot["ci"]) / 2
    ci = {k: {"estimate": statistics.mean(per_seed[s][k] for s in outs) if n else float("nan"),
              "low": float(np.percentile(draws[k], a)) if draws[k] else float("nan"),
              "high": float(np.percentile(draws[k], 100 - a)) if draws[k] else float("nan"),
              "n": n, "resamples": boot["resamples"], "ci": boot["ci"], "seed": boot["seed"] + 700} for k in A_METRICS}
    summary = {"label": LABEL_A, "split": split, "n_items": n, "run_id": run_dir.name, "seeds": list(outs),
               "per_seed": per_seed,
               "mean_sd_over_seeds": {k: {"mean": statistics.mean([per_seed[s][k] for s in outs]),
                                          "sd": statistics.stdev([per_seed[s][k] for s in outs]) if len(outs) > 1 else 0.0}
                                      for k in A_METRICS},
               "ci95_seed_mean": ci,
               "src_oov_items": int(sum(any(t not in src_v.stoi for t in p["src"]) for p in pairs))}
    rows = []
    for i, p in enumerate(pairs):
        row = {"index": p["index"], "split": split, "sentence_norm": p["sentence_norm"],
               "reference_g0": " ".join(p["tgt"]), "src_oov_words": " ".join(t for t in p["src"] if t not in src_v.stoi)}
        for s in outs:
            row[f"seed{s}"] = " ".join(outs[s][i])
            row[f"seed{s}_wer"] = item_wer(refs[i], split_outs[s][i][1])
        rows.append(row)
    return {"summary": summary, "per_item": pd.DataFrame(rows), "refs": refs, "split_outs": split_outs, "pairs": pairs}


def error_analysis(strata: pd.DataFrame, motion: dict, text: dict) -> pd.DataFrame:
    """Long table: stratum, value, n, method, metric, value (means over items; Model A = corpus WER)."""
    per_item = motion["per_item"]
    rows = []
    idx_of = {p["index"]: i for i, p in enumerate(text["pairs"])}
    for col in STRATA:
        for val, grp in strata.groupby(col):
            sub = per_item[per_item["index"].isin(grp["index"])]
            for m in ("model_b_gloss", "model_b_text", "B0", "B1"):
                for k in ("mpjpe_body", "dtw_body", "mpjpe_lhand", "mpjpe_rhand"):
                    rows.append({"stratum": col, "value": str(val), "n": len(sub), "method": m, "metric": k,
                                 "mean": float(np.nanmean(sub[f"{m}__{k}"])) if len(sub) else np.nan})
            ids = [idx_of[i] for i in grp["index"] if i in idx_of]
            if ids:
                w = statistics.mean(wer([text["refs"][i] for i in ids], [text["split_outs"][s][i][1] for i in ids])
                                    for s in text["split_outs"])
                rows.append({"stratum": col, "value": str(val), "n": len(ids), "method": "model_a_g0ref",
                             "metric": "corpus_wer_vs_G0", "mean": w})
    return pd.DataFrame(rows)


def _write_motion_npz(path: Path, raw: np.ndarray, meta: dict) -> None:
    buf = io.BytesIO()
    np.savez(buf, x=raw.astype(np.float32), meta=json.dumps(meta, ensure_ascii=False))
    atomic_write_bytes(path, buf.getvalue())


def evaluate(cfg: dict, split: str, *, final: bool = False, override_reason: str | None = None, device=None) -> dict:
    """Evaluate the frozen runs on `split` ("val"), or — with final=True — once on "test"."""
    device = device or torch.device("cpu")
    p = k4.paths(cfg)
    if split == "test" and not final:
        raise k4.TestSplitLocked("the test split is evaluated only with --final")
    if final and split != "test":
        raise ValueError("--final evaluates the test split")
    frozen = _check_frozen(cfg)
    history = []
    if final and _lock_present(cfg):
        old = json.loads(p["final_lock"].read_text(encoding="utf-8"))
        if not override_reason:
            raise FinalLockError(
                f"The final test evaluation already ran ({old.get('created_utc')}); a second run is refused. "
                "Only the owner may override, in writing: --override-reason \"<why>\".")
        history = old.get("history", []) + [{k: old.get(k) for k in ("created_utc", "frozen_config_sha256", "results")}]
    stamp = _now()
    out_dir = p["eval"] / (f"FINAL_test_{stamp}" if final else f"{split}_{stamp}")

    def body():
        motion = evaluate_motion(cfg, frozen, split, device)
        text = evaluate_text(cfg, frozen, split, device)
        return motion, text

    if final:
        with k4.final_test_access("evaluate --final"):
            k4.check_split_lock(cfg, k4.SPLITS)          # every locked manifest, incl. test and subset
            motion, text = body()
            test_g0_sha = sha256_text_canonical(p["glosses"]["test"])
    else:
        motion, text = body()
    ea = error_analysis(motion["strata"], motion, text)
    metrics = {"label": "kaggle400 evaluation; " + LABEL_B, "split": split, "final": final, "created_utc": stamp,
               "frozen_config_sha256": sha256_file(p["frozen"]), "model_b_and_baselines": motion["summary"],
               "model_a": text["summary"], "for_paper": frozen.get("for_paper", False),
               "honesty": ["measured on " + str(motion["summary"]["n_items"]) + f" {split} clips; small-scale, signer-dependent",
                           "low coordinate error is not proof of correct sign language",
                           "Model A numbers are agreement with the rule glosser (G0 pseudo-gloss), not BdSL correctness",
                           "no human or expert evaluation exists"]}
    out_dir.mkdir(parents=True, exist_ok=True)
    atomic_write_json(out_dir / "metrics.json", metrics)
    atomic_write_text(out_dir / "per_item_modelB.csv", "\ufeff" + motion["per_item"].to_csv(index=False, lineterminator="\n"))
    atomic_write_text(out_dir / "per_item_modelA.csv", "\ufeff" + text["per_item"].to_csv(index=False, lineterminator="\n"))
    atomic_write_text(out_dir / "error_analysis.csv", ea.to_csv(index=False, lineterminator="\n"))
    pred_dir = p["predictions"]
    atomic_write_text(pred_dir / f"{split}_modelB_per_item.csv", "\ufeff" + motion["per_item"].to_csv(index=False, lineterminator="\n"))
    atomic_write_text(pred_dir / f"{split}_modelA_predictions.csv", "\ufeff" + text["per_item"].to_csv(index=False, lineterminator="\n"))
    for m, raw in motion["raws"].items():
        for i, x in raw.items():
            _write_motion_npz(pred_dir / f"{split}_motion" / m / f"{i}.npz", x,
                              {"method": m, "index": i, "split": split, "eval": out_dir.name,
                               "layout": "208 values per frame (body 27, lhand 63, rhand 63, face 55); raw units"})
    result = {"out_dir": str(out_dir), "metrics": metrics}
    if final:
        files = {f.name: sha256_file(f) for f in sorted(out_dir.glob("*")) if f.is_file()}
        lock = {"created_utc": stamp, "label": "the test split has been used once; do not tune anything after this",
                "frozen_config_sha256": metrics["frozen_config_sha256"], "results": out_dir.name, "result_files_sha256": files,
                "test_glosses_sha256": test_g0_sha, "code": code_provenance(cfg["_meta"]["project_root"]),
                "override_reason": override_reason, "history": history}
        atomic_write_json(p["final_lock"], lock)
        result["lock"] = lock
    return result
