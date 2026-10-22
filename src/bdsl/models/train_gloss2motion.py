"""Day 4: Model B pilot run — gloss → motion (or Bangla words → motion, ablation T) vs B0/B1.

Called by `uv run python -m bdsl.cli train-gloss2motion`. Inputs are G0 pseudo-glosses (`gloss_auto`,
markers removed, plus G0 tag tokens; ADR-0014) or the normalised Bangla words; targets are the
pilot MediaPipe features (feat_ver from config, ADR-0023). No reviewed glosses are used.

A run folder `gloss2motion_<input>_pilot50_<UTC time>/` holds run.json, train.log, metrics.json,
per_item.csv, standardizer.npz and seed<N>/ (curves.csv, ckpt_last.pt, ckpt_best.pt). The first seed
also writes predictions/<Index>.npz (raw units) for every item, for the Day 5 avatar.
"""

from __future__ import annotations

import hashlib
import io
import json
import logging
import math
import statistics
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
import torch

from ..eval.motion_metrics import item_metrics, summarize
from ..features.normalize import Standardizer, clip_motion, expand_mask
from ..io import atomic_write_bytes, atomic_write_json, atomic_write_text
from .baselines import b0_mean_motion, b1_retrieve, g0_gloss, g0_tags
from .gloss2motion import Gloss2Motion, masked_loss, value_weights
from .text2gloss import PAD, Vocab, vocab_hash
from .train_text2gloss import _git

LABEL = "pipeline test (pilot50_v1, G0 pseudo-glosses); not evidence of generalisation"
SPLITS = ("train", "val", "test")
RESUME_KEYS = ("input", "feat_ver", "inputs_sha256", "pilot_manifest_sha256", "gloss2motion_config_sha256",
               "vocab_sha256", "standardizer_sha256", "overfit")
PER_ITEM = ("mpjpe_body", "mpjpe_lhand", "mpjpe_rhand", "dtw_body", "duration_err_s", "pred_frames")


class ResumeMismatch(RuntimeError):
    pass


def input_tokens(row: dict, mode: str) -> list[str]:
    if mode == "text":
        return row["sentence_norm"].split()
    return [f"<{t}>" for t in sorted(g0_tags(row["tags_auto"]))] + g0_gloss(row["gloss_auto"])


def load_items(df: pd.DataFrame, features_dir: Path, mode: str, max_gap: int) -> list[dict]:
    items = []
    for r in df.sort_values("index", key=lambda s: s.astype(int)).to_dict("records"):
        mot = clip_motion(features_dir / f"{int(r['index'])}.npz", max_gap)
        items.append({"index": int(r["index"]), "split": r["split"], "tokens": input_tokens(r, mode),
                      "gloss": g0_gloss(r["gloss_auto"]), **mot})
    return items


def _sha_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def _batch(items, vocab: Vocab):
    toks = [vocab.encode(it["tokens"]) for it in items]
    L = max(map(len, toks))
    tokens = torch.tensor([t + [PAD] * (L - len(t)) for t in toks])
    n = torch.tensor([len(it["z"]) for it in items])
    T = int(n.max())
    z = torch.zeros(len(items), T, items[0]["z"].shape[1])
    vm = torch.zeros(len(items), T, items[0]["z"].shape[1], dtype=torch.bool)
    for b, it in enumerate(items):
        z[b, :len(it["z"])] = torch.from_numpy(it["z"])
        vm[b, :len(it["z"])] = torch.from_numpy(it["vmask"])
    return tokens, n, z, vm


def _save(path: Path, obj: dict) -> None:
    buf = io.BytesIO()
    torch.save(obj, buf)
    atomic_write_bytes(path, buf.getvalue())


def _make_model(gcfg, vocab):
    return Gloss2Motion(len(vocab), **gcfg["model"])


def _val_loss(model, items, vocab, gcfg, weights) -> float:
    model.eval()
    lc = gcfg["loss"]
    with torch.no_grad():
        tokens, n, z, vm = _batch(items, vocab)
        pred, log_len = model(tokens, n)
        _, parts = masked_loss(pred, z, vm, n, log_len, weights, lc["lambda_vel"], lc["lambda_len"])
    return parts["pos"]


def train_seed(train, monitor, vocab, gcfg, seed, seed_dir, meta, log, stop_after=None, overfit=False) -> dict:
    tc, lc = gcfg["train"], gcfg["loss"]
    last, best = seed_dir / "ckpt_last.pt", seed_dir / "ckpt_best.pt"
    max_epochs = tc["overfit_epochs"] if overfit else tc["max_epochs"]
    torch.manual_seed(seed)
    model = _make_model(gcfg, vocab)
    opt = torch.optim.AdamW(model.parameters(), lr=tc["lr"], weight_decay=tc["weight_decay"])
    gen = torch.Generator().manual_seed(seed)
    weights = value_weights(lc["hand_weight"])
    state = {"epoch": 0, "best": math.inf, "best_epoch": 0, "bad_epochs": 0, "done": False, "history": []}
    ckpt_meta = {k: meta[k] for k in RESUME_KEYS} | {"label": meta["label"], "seed": seed}
    if last.exists():
        ck = torch.load(last, weights_only=True)
        diff = [k for k in RESUME_KEYS if ck["meta"].get(k) != ckpt_meta[k]]
        if diff or ck["meta"]["seed"] != seed:
            raise ResumeMismatch(f"{last}: inputs changed since the checkpoint ({diff or ['seed']}); start a new run")
        model.load_state_dict(ck["model"])
        opt.load_state_dict(ck["optimizer"])
        state = ck["state"]
        torch.set_rng_state(ck["rng_torch"])
        gen.set_state(ck["rng_batches"])
        log.info(f"seed {seed}: resumed after epoch {state['epoch']}")
    if state["done"]:
        return state
    epochs_this_call = 0
    while state["epoch"] < max_epochs:
        model.train()
        order = torch.randperm(len(train), generator=gen).tolist()
        sums = {"total": 0.0, "pos": 0.0, "vel": 0.0, "len": 0.0}
        n_batches = 0
        for b in range(0, len(order), tc["batch_size"]):
            tokens, n, z, vm = _batch([train[i] for i in order[b:b + tc["batch_size"]]], vocab)
            pred, log_len = model(tokens, n)
            loss, parts = masked_loss(pred, z, vm, n, log_len, weights, lc["lambda_vel"], lc["lambda_len"])
            opt.zero_grad()
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), tc["clip"])
            opt.step()
            sums["total"] += loss.item()
            for k, v in parts.items():
                sums[k] += v
            n_batches += 1
        state["epoch"] += 1
        score = _val_loss(model, monitor, vocab, gcfg, weights)
        rec = {"epoch": state["epoch"], **{f"train_{k}": v / n_batches for k, v in sums.items()},
               "monitor": "train" if overfit else "val", "monitor_pos_l1": score}
        state["history"].append(rec)
        if score < state["best"]:
            state.update(best=score, best_epoch=state["epoch"], bad_epochs=0)
            _save(best, {"meta": ckpt_meta, "model": model.state_dict(), "epoch": state["epoch"]})
        else:
            state["bad_epochs"] += 1
        state["done"] = state["epoch"] >= max_epochs or (not overfit and state["bad_epochs"] >= tc["patience"])
        _save(last, {"meta": ckpt_meta, "model": model.state_dict(), "optimizer": opt.state_dict(), "state": state,
                     "rng_torch": torch.get_rng_state(), "rng_batches": gen.get_state()})
        if state["epoch"] % 25 == 0 or state["done"]:
            log.info(f"seed {seed} epoch {state['epoch']}: train loss {rec['train_total']:.4f} (pos "
                     f"{rec['train_pos']:.4f}), {rec['monitor']} pos L1 {score:.4f} (best epoch {state['best_epoch']})")
        if state["done"]:
            break
        epochs_this_call += 1
        if stop_after and epochs_this_call >= stop_after:
            log.info(f"seed {seed}: stopped after {epochs_this_call} epochs this call (resume test)")
            break
    return state


def _write_prediction(path: Path, raw: np.ndarray, fps: float, meta: dict) -> None:
    buf = io.BytesIO()
    np.savez(buf, x=raw.astype(np.float32), body=raw[:, 0:27].reshape(-1, 9, 3),
             lhand=raw[:, 27:90].reshape(-1, 21, 3), rhand=raw[:, 90:153].reshape(-1, 21, 3),
             blendshapes=raw[:, 153:205], head_rot=raw[:, 205:208], fps=np.float32(fps),
             meta=json.dumps(meta, ensure_ascii=False))
    atomic_write_bytes(path, buf.getvalue())


def evaluate_all(by_split, preds_z: dict, std: Standardizer, fps: float) -> tuple[dict, dict]:
    """Metrics per split for one method; preds_z maps Index → standardised frames."""
    out, per_item = {}, {}
    for s, items in by_split.items():
        rows, preds, gts = [], [], []
        for it in items:
            raw_p = std.invert(preds_z[it["index"]])
            raw_g = std.invert(it["z"])
            rows.append(item_metrics(raw_p, raw_g, it["mask"], fps, dtw=s != "train"))
            per_item[it["index"]] = rows[-1]
            preds.append(raw_p)
            gts.append(raw_g)
        out[s] = summarize(rows, preds, gts)
    return out, per_item


def run(cfg: dict, df: pd.DataFrame, *, mode: str, features_dir: Path, pilot_manifest_sha256: str,
        inputs_sha256: str, run_dir: Path | None = None, runs_root: Path | None = None,
        seeds: list[int] | None = None, overfit: int | None = None, stop_after: int | None = None) -> dict:
    gcfg = cfg["gloss2motion"]
    fps = float(cfg["features"]["fps"])
    old = None
    if run_dir is not None:
        old = json.loads((run_dir / "run.json").read_text(encoding="utf-8"))
        if seeds and seeds != old["seeds"]:
            raise ResumeMismatch(f"{run_dir.name} was started with seeds {old['seeds']}, not {seeds}")
        seeds = old["seeds"]
    items = load_items(df, features_dir, mode, gcfg["max_gap"])
    by_split = {s: [it for it in items if it["split"] == s] for s in SPLITS}
    if overfit:
        by_split = {"train": by_split["train"][:overfit]}
        seeds = seeds or gcfg["seeds"][:1]
    seeds = seeds or gcfg["seeds"]
    train = by_split["train"]
    std = Standardizer.fit(train)
    for it in items:
        it["z"] = std.apply(it["x"], it["mask"])
        it["vmask"] = expand_mask(it["mask"])
    vocab = Vocab([t for it in train for t in it["tokens"]])
    std_bytes = io.BytesIO()
    np.savez(std_bytes, mean=std.mean, sd=std.sd)
    meta = {
        "label": LABEL, "input": mode, "feat_ver": gcfg["feat_ver"], "inputs_sha256": inputs_sha256,
        "pilot_manifest_sha256": pilot_manifest_sha256, "overfit": overfit,
        "gloss2motion_config": gcfg, "gloss2motion_config_sha256": _sha_bytes(json.dumps(gcfg, sort_keys=True).encode()),
        "config_hash": cfg["_meta"]["config_hash"], "vocab_sha256": vocab_hash(vocab, vocab),
        "standardizer_sha256": _sha_bytes(std.mean.tobytes() + std.sd.tobytes()), "vocab_size": len(vocab),
        "params": sum(p.numel() for p in _make_model(gcfg, vocab).parameters()), "seeds": seeds,
        "counts": {s: len(v) for s, v in by_split.items()}, "fps": fps,
        "hand_coverage_train": {"lhand": float(np.mean([it["mask"][:, 1].mean() for it in train])),
                                "rhand": float(np.mean([it["mask"][:, 2].mean() for it in train]))},
        "versions": {"torch": torch.__version__, "numpy": np.__version__}, "git": _git(cfg["_meta"]["project_root"]),
    }
    if old is None:
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        run_dir = runs_root / f"gloss2motion_{mode}_{f'overfit{overfit}_' if overfit else ''}pilot50_{stamp}"
        meta["created_utc"] = stamp
    else:
        diff = [k for k in RESUME_KEYS if old.get(k) != meta[k]]
        if diff:
            raise ResumeMismatch(f"{run_dir.name}: inputs changed since the run started ({diff}); start a new run")
        meta["created_utc"] = old["created_utc"]
    run_dir.mkdir(parents=True, exist_ok=True)
    atomic_write_json(run_dir / "run.json", meta)
    atomic_write_bytes(run_dir / "standardizer.npz", std_bytes.getvalue())

    log = logging.getLogger(f"bdsl.gloss2motion.{run_dir.name}")
    log.setLevel(logging.INFO)
    log.handlers.clear()
    for h in (logging.FileHandler(run_dir / "train.log", encoding="utf-8"), logging.StreamHandler()):
        h.setFormatter(logging.Formatter("%(asctime)s %(message)s"))
        log.addHandler(h)
    log.info(f"{LABEL} | input {mode} | run {run_dir.name} | {meta['counts']} | vocab {len(vocab)} | "
             f"{meta['params']:,} parameters | seeds {seeds}")

    monitor = train if overfit else by_split["val"]
    states = {}
    for seed in seeds:
        seed_dir = run_dir / f"seed{seed}"
        seed_dir.mkdir(exist_ok=True)
        states[seed] = train_seed(train, monitor, vocab, gcfg, seed, seed_dir, meta, log, stop_after, bool(overfit))
        atomic_write_text(seed_dir / "curves.csv",
                          pd.DataFrame(states[seed]["history"]).to_csv(index=False, lineterminator="\n"))
    if not all(s["done"] for s in states.values()):
        log.info("not finished (stopped for the resume test); resume with --resume")
        for h in log.handlers:
            h.close()
        return {"run_dir": str(run_dir), "finished": False}

    # Baselines (deterministic). B1 never retrieves the item itself.
    all_items = [it for v in by_split.values() for it in v]
    b0 = b0_mean_motion([it["z"] for it in train], [it["vmask"] for it in train])
    b1_src = {}
    for it in all_items:
        pool = [t for t in train if t["index"] != it["index"]] or train
        b1_src[it["index"]] = pool[b1_retrieve(it["gloss"], [t["gloss"] for t in pool], [t["index"] for t in pool])]
    metrics = {"label": LABEL, "run": run_dir.name, "input": mode, "units": "body: shoulder widths; hands: mm; face: blendshape MAE"}
    metrics["B0"], b0_items = evaluate_all(by_split, {it["index"]: b0 for it in all_items}, std, fps)
    metrics["B1"], b1_items = evaluate_all(by_split, {i: s["z"] for i, s in b1_src.items()}, std, fps)
    rows = {it["index"]: {"label": LABEL, "index": it["index"], "split": it["split"], "tokens": " ".join(it["tokens"]),
                          "gt_frames": len(it["z"]), "cov_lhand": float(it["mask"][:, 1].mean()),
                          "cov_rhand": float(it["mask"][:, 2].mean()), "b1_source": b1_src[it["index"]]["index"],
                          **{f"B0_{k}": b0_items[it["index"]].get(k) for k in PER_ITEM},
                          **{f"B1_{k}": b1_items[it["index"]].get(k) for k in PER_ITEM}}
            for it in all_items}
    metrics["model_b"] = {}
    for n_seed, seed in enumerate(seeds):
        model = _make_model(gcfg, vocab)
        model.load_state_dict(torch.load(run_dir / f"seed{seed}" / "ckpt_best.pt", weights_only=True)["model"])
        tokens, _, _, _ = _batch(all_items, vocab)
        preds = model.generate(tokens, gcfg["max_frames"])
        preds_z = {it["index"]: p.numpy() for it, p in zip(all_items, preds)}
        seed_m, seed_items = evaluate_all(by_split, preds_z, std, fps)
        metrics["model_b"][str(seed)] = seed_m | {"best_epoch": states[seed]["best_epoch"], "epochs": states[seed]["epoch"]}
        for i, r in seed_items.items():
            rows[i] |= {f"seed{seed}_{k}": r.get(k) for k in PER_ITEM}
        if n_seed == 0:
            for it in all_items:
                _write_prediction(run_dir / f"seed{seed}" / "predictions" / f"{it['index']}.npz",
                                  std.invert(preds_z[it["index"]]), fps,
                                  {"label": LABEL, "run": run_dir.name, "seed": seed, "index": it["index"],
                                   "split": it["split"], "input": mode, "tokens": it["tokens"],
                                   "layout": "body (9,3) shoulder widths, shoulder-midpoint centred; hands (21,3) m, "
                                             "wrist-relative, MediaPipe left/right labels (G8); blendshapes 52; head_rot deg"})
    metrics["model_b_mean_sd"] = {
        s: {k: {"mean": statistics.mean(v), "sd": statistics.stdev(v) if len(v) > 1 else 0.0}
            for k in metrics["B0"][s] if k != "n"
            for v in [[metrics["model_b"][str(sd)][s][k] for sd in seeds]]}
        for s in by_split}
    atomic_write_json(run_dir / "metrics.json", metrics)
    atomic_write_text(run_dir / "per_item.csv",
                      "﻿" + pd.DataFrame(list(rows.values())).to_csv(index=False, lineterminator="\n"))
    for s in by_split:
        b, b0m, b1m = metrics["model_b_mean_sd"][s], metrics["B0"][s], metrics["B1"][s]
        dtw = f" | DTW body B {b['dtw_body']['mean']:.3f} B0 {b0m['dtw_body']:.3f} B1 {b1m['dtw_body']:.3f}" if "dtw_body" in b else ""
        log.info(f"{s:5s} MPJPE body: B {b['mpjpe_body']['mean']:.3f}±{b['mpjpe_body']['sd']:.3f} B0 {b0m['mpjpe_body']:.3f} "
                 f"B1 {b1m['mpjpe_body']:.3f}{dtw} | diversity B {b['diversity_ratio']['mean']:.2f} "
                 f"B0 {b0m['diversity_ratio']:.2f} B1 {b1m['diversity_ratio']:.2f}")
    for h in log.handlers:
        h.close()
    return {"run_dir": str(run_dir), "finished": True, "metrics": metrics}
