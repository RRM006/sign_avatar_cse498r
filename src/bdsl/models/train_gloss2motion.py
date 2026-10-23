"""Day 4: Model B pilot run — gloss → motion (or Bangla words → motion, ablation T) vs B0/B1.

Called by `uv run python -m bdsl.cli train-gloss2motion`. Inputs are G0 pseudo-glosses (`gloss_auto`,
markers removed, plus G0 tag tokens; ADR-0014) or the normalised Bangla words; targets are the
pilot MediaPipe features (feat_ver from config, ADR-0023). No reviewed glosses are used.

A run folder `<prefix>gloss2motion_<input>_<data>_<UTC time>/` holds run.json, train.log, metrics.json,
per_item.csv, standardizer.npz and seed<N>/ (curves.csv, ckpt_last.pt, ckpt_best.pt). The first seed
also writes predictions/<Index>.npz (raw units) for every item, for the Day 5 avatar.

kaggle400 (2026-10-23): the caller passes only train + val rows (`splits`), each row's feature file in a
`feature_path` column, and `sha256` / `link_group` columns so that B1 never retrieves an exact copy or a
shared-segment partner of the query. Training runs on `device` (CUDA when available); `max_steps`
stops a dry run after that many optimiser steps (no checkpoint is written, the run is not resumable).
"""

from __future__ import annotations

import hashlib
import io
import json
import logging
import math
import statistics
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
import torch

from ..device import rng_state, set_rng_state
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


def load_items(df: pd.DataFrame, features_dir: Path | None, mode: str, max_gap: int) -> list[dict]:
    """One item per row. The feature file is `feature_path` when the frame has that column (kaggle400:
    one folder per split), otherwise `<features_dir>/<Index>.npz` (pilot)."""
    items = []
    for r in df.sort_values("index", key=lambda s: s.astype(int)).to_dict("records"):
        path = Path(r["feature_path"]) if r.get("feature_path") else features_dir / f"{int(r['index'])}.npz"
        mot = clip_motion(path, max_gap)
        items.append({"index": int(r["index"]), "split": r["split"], "tokens": input_tokens(r, mode),
                      "gloss": g0_gloss(r["gloss_auto"]), "sha256": r.get("sha256"),
                      "link_group": int(r["link_group"]) if r.get("link_group") not in (None, "") else -1, **mot})
    return items


def b1_pool(query: dict, train: list[dict]) -> list[dict]:
    """Training items B1 may retrieve for `query`: never the item itself, an exact copy (same SHA-256)
    or a known shared-segment partner (same link group)."""
    def related(t):
        return (t["index"] == query["index"]
                or (query.get("sha256") and t.get("sha256") == query.get("sha256"))
                or (query.get("link_group", -1) >= 0 and t.get("link_group", -1) == query.get("link_group")))
    return [t for t in train if not related(t)] or [t for t in train if t["index"] != query["index"]] or train


def _sha_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def _batch(items, vocab: Vocab, device: torch.device | None = None):
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
    if device is not None and device.type != "cpu":
        return tokens.to(device), n.to(device), z.to(device), vm.to(device)
    return tokens, n, z, vm


def _save(path: Path, obj: dict) -> None:
    buf = io.BytesIO()
    torch.save(obj, buf)
    atomic_write_bytes(path, buf.getvalue())


def _make_model(gcfg, vocab):
    return Gloss2Motion(len(vocab), **gcfg["model"])


def _val_loss(model, items, vocab, gcfg, weights, device=None, batch_size: int = 32) -> float:
    """Masked position L1 of `items` (monitor split), weighted by present values like the training loss."""
    model.eval()
    lc = gcfg["loss"]
    num = den = 0.0
    with torch.no_grad():
        for b in range(0, len(items), batch_size):
            chunk = items[b:b + batch_size]
            tokens, n, z, vm = _batch(chunk, vocab, device)
            pred, log_len = model(tokens, n)
            _, parts = masked_loss(pred, z, vm, n, log_len, weights, lc["lambda_vel"], lc["lambda_len"])
            w = float((vm.float() * weights).sum())
            num, den = num + parts["pos"] * w, den + w
    return num / den if den else float("nan")


def train_seed(train, monitor, vocab, gcfg, seed, seed_dir, meta, log, stop_after=None, overfit=False,
               device: torch.device | None = None, max_steps: int | None = None) -> dict:
    device = device or torch.device("cpu")
    tc, lc = gcfg["train"], gcfg["loss"]
    last, best = seed_dir / "ckpt_last.pt", seed_dir / "ckpt_best.pt"
    max_epochs = tc["overfit_epochs"] if overfit else tc["max_epochs"]
    torch.manual_seed(seed)
    if device.type == "cuda":
        torch.cuda.manual_seed_all(seed)
    model = _make_model(gcfg, vocab).to(device)
    opt = torch.optim.AdamW(model.parameters(), lr=tc["lr"], weight_decay=tc["weight_decay"])
    gen = torch.Generator().manual_seed(seed)
    weights = value_weights(lc["hand_weight"]).to(device)
    state = {"epoch": 0, "best": math.inf, "best_epoch": 0, "bad_epochs": 0, "done": False, "history": [],
             "seconds": 0.0}
    ckpt_meta = {k: meta[k] for k in RESUME_KEYS} | {"label": meta["label"], "seed": seed}
    if last.exists():
        ck = torch.load(last, weights_only=True, map_location=device)
        diff = [k for k in RESUME_KEYS if ck["meta"].get(k) != ckpt_meta[k]]
        if diff or ck["meta"]["seed"] != seed:
            raise ResumeMismatch(f"{last}: inputs changed since the checkpoint ({diff or ['seed']}); start a new run")
        model.load_state_dict(ck["model"])
        opt.load_state_dict(ck["optimizer"])
        state = ck["state"]
        state.setdefault("seconds", 0.0)
        set_rng_state({k: ck[k].cpu() for k in ("rng_torch", "rng_cuda") if k in ck}, device)
        gen.set_state(ck["rng_batches"].cpu())
        log.info(f"seed {seed}: resumed after epoch {state['epoch']}")
    if state["done"]:
        return state
    epochs_this_call = steps = 0
    while state["epoch"] < max_epochs:
        t_epoch = time.perf_counter()
        model.train()
        order = torch.randperm(len(train), generator=gen).tolist()
        sums = {"total": 0.0, "pos": 0.0, "vel": 0.0, "len": 0.0}
        n_batches = 0
        for b in range(0, len(order), tc["batch_size"]):
            tokens, n, z, vm = _batch([train[i] for i in order[b:b + tc["batch_size"]]], vocab, device)
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
            steps += 1
            if max_steps and steps >= max_steps:
                break
        if max_steps and steps >= max_steps:
            score = _val_loss(model, monitor, vocab, gcfg, weights, device)
            state["dry_run"] = {"steps": steps, "train_loss": sums["total"] / n_batches, "monitor_pos_l1": score,
                                "finite": bool(math.isfinite(sums["total"]) and math.isfinite(score)),
                                "seconds": round(time.perf_counter() - t_epoch, 3)}
            log.info(f"seed {seed}: DRY RUN stopped after {steps} optimiser step(s): train loss "
                     f"{state['dry_run']['train_loss']:.4f}, monitor pos L1 {score:.4f}, device {device}")
            return state
        state["epoch"] += 1
        score = _val_loss(model, monitor, vocab, gcfg, weights, device)
        epoch_s = time.perf_counter() - t_epoch
        state["seconds"] += epoch_s
        rec = {"epoch": state["epoch"], **{f"train_{k}": v / n_batches for k, v in sums.items()},
               "monitor": "train" if overfit else "val", "monitor_pos_l1": score, "epoch_seconds": round(epoch_s, 3)}
        state["history"].append(rec)
        if score < state["best"]:
            state.update(best=score, best_epoch=state["epoch"], bad_epochs=0)
            _save(best, {"meta": ckpt_meta, "model": model.state_dict(), "epoch": state["epoch"]})
        else:
            state["bad_epochs"] += 1
        state["done"] = state["epoch"] >= max_epochs or (not overfit and state["bad_epochs"] >= tc["patience"])
        _save(last, {"meta": ckpt_meta, "model": model.state_dict(), "optimizer": opt.state_dict(), "state": state,
                     **rng_state(device), "rng_batches": gen.get_state()})
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


def predict_items(model, items: list[dict], vocab: Vocab, max_frames: int, device=None, batch_size: int = 32) -> dict:
    """Index → predicted standardised frames (numpy, CPU), in batches."""
    out = {}
    for b in range(0, len(items), batch_size):
        chunk = items[b:b + batch_size]
        toks = [vocab.encode(it["tokens"]) for it in chunk]
        tokens = torch.tensor([t + [PAD] * (max(map(len, toks)) - len(t)) for t in toks])
        tokens = tokens.to(device) if device is not None else tokens
        for it, p in zip(chunk, model.generate(tokens, max_frames)):
            out[it["index"]] = p.detach().cpu().numpy()
    return out


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


def run(cfg: dict, df: pd.DataFrame, *, mode: str, features_dir: Path | None, pilot_manifest_sha256: str,
        inputs_sha256: str, run_dir: Path | None = None, runs_root: Path | None = None,
        seeds: list[int] | None = None, overfit: int | None = None, stop_after: int | None = None,
        device: torch.device | None = None, splits: tuple[str, ...] = SPLITS, max_steps: int | None = None,
        data_name: str = "pilot50", name_prefix: str = "", label: str = LABEL, extra_meta: dict | None = None) -> dict:
    """Train and evaluate. `splits` are the splits present in `df` (kaggle400: train + val only; the
    test split is evaluated separately, once, by `evaluate --final`)."""
    gcfg = cfg["gloss2motion"]
    fps = float(cfg["features"]["fps"])
    device = device or torch.device("cpu")
    if set(df["split"]) - set(splits):
        raise ValueError(f"rows of splits {sorted(set(df['split']) - set(splits))} were passed but splits={splits}")
    old = None
    if run_dir is not None:
        old = json.loads((run_dir / "run.json").read_text(encoding="utf-8"))
        if seeds and seeds != old["seeds"]:
            raise ResumeMismatch(f"{run_dir.name} was started with seeds {old['seeds']}, not {seeds}")
        seeds = old["seeds"]
    items = load_items(df, features_dir, mode, gcfg["max_gap"])
    by_split = {s: [it for it in items if it["split"] == s] for s in splits}
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
        "label": label, "input": mode, "feat_ver": gcfg["feat_ver"], "inputs_sha256": inputs_sha256,
        "pilot_manifest_sha256": pilot_manifest_sha256, "overfit": overfit,
        "gloss2motion_config": gcfg, "gloss2motion_config_sha256": _sha_bytes(json.dumps(gcfg, sort_keys=True).encode()),
        "config_hash": cfg["_meta"]["config_hash"], "vocab_sha256": vocab_hash(vocab, vocab),
        "standardizer_sha256": _sha_bytes(std.mean.tobytes() + std.sd.tobytes()), "vocab_size": len(vocab),
        "params": sum(p.numel() for p in _make_model(gcfg, vocab).parameters()), "seeds": seeds,
        "counts": {s: len(v) for s, v in by_split.items()}, "fps": fps,
        "hand_coverage_train": {"lhand": float(np.mean([it["mask"][:, 1].mean() for it in train])),
                                "rhand": float(np.mean([it["mask"][:, 2].mean() for it in train]))},
        "versions": {"torch": torch.__version__, "numpy": np.__version__}, "git": _git(cfg["_meta"]["project_root"]),
        "data": data_name, "splits": list(splits), "device": str(device), "max_steps": max_steps,
        **(extra_meta or {}),
    }
    if old is None:
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        base = f"{name_prefix}gloss2motion_{mode}_{f'overfit{overfit}_' if overfit else ''}{data_name}_{stamp}"
        run_dir, k = runs_root / base, 2
        while run_dir.exists():   # two runs in the same second must never share (and silently resume) a folder
            run_dir, k = runs_root / f"{base}_{k}", k + 1
        meta["created_utc"] = stamp
        meta["devices_used"] = [str(device)]
    else:
        diff = [k for k in RESUME_KEYS if old.get(k) != meta[k]]
        if diff:
            raise ResumeMismatch(f"{run_dir.name}: inputs changed since the run started ({diff}); start a new run")
        meta["created_utc"] = old["created_utc"]
        meta["devices_used"] = list(dict.fromkeys(old.get("devices_used", []) + [str(device)]))
    run_dir.mkdir(parents=True, exist_ok=True)
    atomic_write_json(run_dir / "run.json", meta)
    atomic_write_bytes(run_dir / "standardizer.npz", std_bytes.getvalue())

    log = logging.getLogger(f"bdsl.gloss2motion.{run_dir.name}")
    log.setLevel(logging.INFO)
    log.handlers.clear()
    for h in (logging.FileHandler(run_dir / "train.log", encoding="utf-8"), logging.StreamHandler()):
        h.setFormatter(logging.Formatter("%(asctime)s %(message)s"))
        log.addHandler(h)
    log.info(f"{label} | input {mode} | run {run_dir.name} | {meta['counts']} | vocab {len(vocab)} | "
             f"{meta['params']:,} parameters | seeds {seeds} | device {device}")

    monitor = train if overfit else by_split["val"]
    states = {}
    for seed in seeds:
        seed_dir = run_dir / f"seed{seed}"
        seed_dir.mkdir(exist_ok=True)
        states[seed] = train_seed(train, monitor, vocab, gcfg, seed, seed_dir, meta, log, stop_after, bool(overfit),
                                  device=device, max_steps=max_steps)
        if "dry_run" in states[seed]:
            meta.setdefault("dry_run", {})[str(seed)] = states[seed]["dry_run"]
            atomic_write_json(run_dir / "run.json", meta)
            continue
        atomic_write_text(seed_dir / "curves.csv",
                          pd.DataFrame(states[seed]["history"]).to_csv(index=False, lineterminator="\n"))
    if max_steps:
        log.info("dry run finished (no checkpoint, not resumable, never a result)")
        for h in log.handlers:
            h.close()
        return {"run_dir": str(run_dir), "finished": False, "dry_run": meta.get("dry_run", {})}
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
        pool = b1_pool(it, train)
        b1_src[it["index"]] = pool[b1_retrieve(it["gloss"], [t["gloss"] for t in pool], [t["index"] for t in pool])]
    metrics = {"label": label, "run": run_dir.name, "input": mode, "splits": list(splits),
               "units": "body: shoulder widths; hands: mm; face: blendshape MAE"}
    metrics["B0"], b0_items = evaluate_all(by_split, {it["index"]: b0 for it in all_items}, std, fps)
    metrics["B1"], b1_items = evaluate_all(by_split, {i: s["z"] for i, s in b1_src.items()}, std, fps)
    rows = {it["index"]: {"label": label, "index": it["index"], "split": it["split"], "tokens": " ".join(it["tokens"]),
                          "gt_frames": len(it["z"]), "cov_lhand": float(it["mask"][:, 1].mean()),
                          "cov_rhand": float(it["mask"][:, 2].mean()), "b1_source": b1_src[it["index"]]["index"],
                          **{f"B0_{k}": b0_items[it["index"]].get(k) for k in PER_ITEM},
                          **{f"B1_{k}": b1_items[it["index"]].get(k) for k in PER_ITEM}}
            for it in all_items}
    metrics["model_b"] = {}
    for n_seed, seed in enumerate(seeds):
        model = _make_model(gcfg, vocab).to(device)
        model.load_state_dict(torch.load(run_dir / f"seed{seed}" / "ckpt_best.pt", weights_only=True,
                                         map_location=device)["model"])
        preds_z = predict_items(model, all_items, vocab, gcfg["max_frames"], device)
        seed_m, seed_items = evaluate_all(by_split, preds_z, std, fps)
        metrics["model_b"][str(seed)] = seed_m | {"best_epoch": states[seed]["best_epoch"], "epochs": states[seed]["epoch"]}
        for i, r in seed_items.items():
            rows[i] |= {f"seed{seed}_{k}": r.get(k) for k in PER_ITEM}
        if n_seed == 0:
            for it in all_items:
                _write_prediction(run_dir / f"seed{seed}" / "predictions" / f"{it['index']}.npz",
                                  std.invert(preds_z[it["index"]]), fps,
                                  {"label": label, "run": run_dir.name, "seed": seed, "index": it["index"],
                                   "split": it["split"], "input": mode, "tokens": it["tokens"],
                                   "layout": "body (9,3) shoulder widths, shoulder-midpoint centred; hands (21,3) m, "
                                             "wrist-relative, MediaPipe left/right labels (G8); blendshapes 52; head_rot deg"})
    # Wall-clock time stays OUTSIDE the quality metrics (never identical between runs; a resumed run must
    # reproduce the straight run's metrics exactly — desktop test run, 2026-10-23).
    metrics["train_seconds"] = {str(sd): round(states[sd].get("seconds", 0.0), 1) for sd in seeds}
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
