"""Day 3 Step 1: Model A pilot run — G0 baseline vs A-GRU on pilot50_v1 (a "pipeline test").

Called by `uv run python -m bdsl.cli train-text2gloss`. The caller must run the annotation check first
and refuse to train if it reports problems (cli.cmd_train_text2gloss does).

A run folder `<prefix>text2gloss_pilot50_<UTC time>/` holds:
  <prefix>run.json         inputs, hashes, versions, vocab sizes, parameter count
  <prefix>train.log        one line per epoch and seed
  <prefix>metrics.json     G0 and A-GRU per split (A-GRU per seed + mean/sd)
  <prefix>per_item.csv     reference, G0 and every seed's output per sentence
  seed<N>/<prefix>curves.csv, <prefix>ckpt_last.pt (resume), <prefix>ckpt_best.pt (lowest val WER)
With --allow-test-data the prefix is `TEST_` and every file and checkpoint says TEST_RUN = true.
"""

from __future__ import annotations

import hashlib
import io
import json
import logging
import math
import statistics
import subprocess
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import torch
from torch import nn

from ..eval.text_metrics import item_wer, score
from ..io import atomic_write_bytes, atomic_write_json, atomic_write_text
from .baselines import g0_gloss, g0_tags
from .text2gloss import (BOS, EOS, PAD, TAGS, Seq2Seq, Vocab, beam_decode, count_params, greedy_decode,
                         split_tags, tag_token, vocab_hash)

TEST_LABEL = "TEST - fake review data, not video-verified, pipeline test only"
REAL_LABEL = "pipeline test (pilot50_v1, reviewed glosses); not evidence of generalisation"
SPLITS = ("train", "val", "test")
# Inputs that must not change between a run and its resume.
RESUME_KEYS = ("TEST_RUN", "annotation_sha256", "pilot_manifest_sha256", "text2gloss_config_sha256",
               "vocab_sha256", "overfit")


class ResumeMismatch(RuntimeError):
    pass


def make_pairs(df: pd.DataFrame, tag_prefix: bool) -> list[dict]:
    pairs = []
    for r in df.to_dict("records"):
        tags = sorted(t for t in r["tags_reviewed"].split(";") if t)
        unknown = set(tags) - set(TAGS)
        if unknown:
            raise ValueError(f"row {r['index']}: unknown tags {unknown}")
        gloss = r["gloss_reviewed"].split()
        pairs.append({"index": int(r["index"]), "split": r["split"], "sentence_norm": r["sentence_norm"],
                      "src": r["sentence_norm"].split(), "gloss": gloss, "tags": set(tags),
                      "tgt": ([tag_token(t) for t in tags] if tag_prefix else []) + gloss,
                      "g0_gloss": g0_gloss(r["gloss_auto"]), "g0_tags": g0_tags(r["tags_auto"])})
    return sorted(pairs, key=lambda p: p["index"])


def build_vocabs(train: list[dict]) -> tuple[Vocab, Vocab]:
    """Vocabularies from the training pairs only: held-out words become <unk>."""
    return Vocab([t for p in train for t in p["src"]]), Vocab([t for p in train for t in p["tgt"]])


def _batch(pairs, src_v: Vocab, tgt_v: Vocab):
    src = [src_v.encode(p["src"]) for p in pairs]
    tgt = [[BOS] + tgt_v.encode(p["tgt"]) + [EOS] for p in pairs]
    s_max, t_max = max(map(len, src)), max(map(len, tgt))
    return (torch.tensor([s + [PAD] * (s_max - len(s)) for s in src]), torch.tensor([len(s) for s in src]),
            torch.tensor([t + [PAD] * (t_max - len(t)) for t in tgt]))


def predict(model, pairs, src_v, tgt_v, max_len: int, beam: int | None = None) -> list[list[str]]:
    if beam:
        return [tgt_v.decode(beam_decode(model, src_v.encode(p["src"]), beam, max_len)) for p in pairs]
    src, src_len, _ = _batch(pairs, src_v, tgt_v)
    return [tgt_v.decode(ids) for ids in greedy_decode(model, src, src_len, max_len)]


def evaluate(pairs, outputs: list[list[str]]) -> dict:
    split = [split_tags(o) for o in outputs]
    return score([p["gloss"] for p in pairs], [g for _, g in split], [p["tags"] for p in pairs],
                 [t for t, _ in split])


def make_model(tcfg: dict, src_v: Vocab, tgt_v: Vocab) -> Seq2Seq:
    return Seq2Seq(len(src_v), len(tgt_v), **tcfg["model"])


def _save(path: Path, obj: dict) -> None:
    buf = io.BytesIO()
    torch.save(obj, buf)
    atomic_write_bytes(path, buf.getvalue())


def train_seed(train, monitor, src_v, tgt_v, tcfg: dict, seed: int, seed_dir: Path, meta: dict,
               log: logging.Logger, stop_after: int | None = None, overfit: bool = False) -> dict:
    """Train one seed, resuming from <prefix>ckpt_last.pt if present. `monitor` drives early stopping
    (val, greedy decoding), or in overfit mode the training pairs themselves until beam-search exact
    match reaches 100%."""
    prefix, tc = meta["prefix"], tcfg["train"]
    last, best = seed_dir / f"{prefix}ckpt_last.pt", seed_dir / f"{prefix}ckpt_best.pt"
    torch.manual_seed(seed)
    model = make_model(tcfg, src_v, tgt_v)
    opt = torch.optim.Adam(model.parameters(), lr=tc["lr"])
    gen = torch.Generator().manual_seed(seed)
    state = {"epoch": 0, "best_wer": math.inf, "best_epoch": 0, "bad_epochs": 0, "done": False, "history": []}
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
    loss_fn = nn.CrossEntropyLoss(ignore_index=PAD, label_smoothing=tc["label_smoothing"])
    epochs_this_call = 0
    while state["epoch"] < tc["max_epochs"]:
        model.train()
        order = torch.randperm(len(train), generator=gen).tolist()
        loss_sum, n_tok = 0.0, 0
        for b in range(0, len(order), tc["batch_size"]):
            src, src_len, tgt = _batch([train[i] for i in order[b:b + tc["batch_size"]]], src_v, tgt_v)
            logits = model(src, src_len, tgt[:, :-1])
            loss = loss_fn(logits.reshape(-1, logits.size(-1)), tgt[:, 1:].reshape(-1))
            opt.zero_grad()
            loss.backward()
            nn.utils.clip_grad_norm_(model.parameters(), tc["clip"])
            opt.step()
            n = int((tgt[:, 1:] != PAD).sum())
            loss_sum, n_tok = loss_sum + loss.item() * n, n_tok + n
        state["epoch"] += 1
        # Overfit mode decodes with the final beam search: a greedy-only hit can stop a barely trained model.
        m = evaluate(monitor, predict(model, monitor, src_v, tgt_v, tcfg["max_len"], tcfg["beam"] if overfit else None))
        rec = {"epoch": state["epoch"], "train_loss": loss_sum / n_tok, "monitor": "train" if overfit else "val",
               "monitor_wer": m["wer"], "monitor_exact_match": m["exact_match"]}
        state["history"].append(rec)
        if m["wer"] < state["best_wer"]:
            state.update(best_wer=m["wer"], best_epoch=state["epoch"], bad_epochs=0)
            _save(best, {"meta": ckpt_meta, "model": model.state_dict(), "epoch": state["epoch"]})
        else:
            state["bad_epochs"] += 1
        stop = m["exact_match"] == 100.0 if overfit else state["bad_epochs"] >= tc["patience"]
        state["done"] = stop or state["epoch"] >= tc["max_epochs"]
        _save(last, {"meta": ckpt_meta, "model": model.state_dict(), "optimizer": opt.state_dict(), "state": state,
                     "rng_torch": torch.get_rng_state(), "rng_batches": gen.get_state()})
        if state["epoch"] % 10 == 0 or state["done"]:
            log.info(f"seed {seed} epoch {state['epoch']}: loss {rec['train_loss']:.3f}, {rec['monitor']} WER "
                     f"{m['wer']:.1f}, exact {m['exact_match']:.0f}% (best epoch {state['best_epoch']})")
        if state["done"]:
            break
        epochs_this_call += 1
        if stop_after and epochs_this_call >= stop_after:
            log.info(f"seed {seed}: stopped after {epochs_this_call} epochs this call (resume test)")
            break
    return state


def _sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _git(cwd: str) -> dict:
    def run(*a):
        try:
            return subprocess.run(["git", *a], cwd=cwd, capture_output=True, text=True, check=True).stdout.strip()
        except (OSError, subprocess.CalledProcessError):
            return None
    return {"branch": run("rev-parse", "--abbrev-ref", "HEAD"), "commit": run("rev-parse", "HEAD"),
            "dirty": bool(run("status", "--porcelain"))}


def run(cfg: dict, df: pd.DataFrame, check: dict, *, allow_test_data: bool, pilot_manifest_sha256: str,
        run_dir: Path | None = None, runs_root: Path | None = None, seeds: list[int] | None = None,
        overfit: int | None = None, stop_after: int | None = None) -> dict:
    """Train and evaluate. `check` is the clean report of cli.check_annotations (problems == [])."""
    if check["problems"]:
        raise RuntimeError("annotation check failed; refusing to train")
    import sacrebleu

    tcfg = cfg["text2gloss"]
    prefix = "TEST_" if allow_test_data else ""
    if run_dir is not None:
        old = json.loads((run_dir / f"{prefix}run.json").read_text(encoding="utf-8"))
        if seeds and seeds != old["seeds"]:
            raise ResumeMismatch(f"{run_dir.name} was started with seeds {old['seeds']}, not {seeds}")
        seeds = old["seeds"]
    pairs = make_pairs(df, tcfg["tag_prefix"])
    by_split = {s: [p for p in pairs if p["split"] == s] for s in SPLITS}
    if overfit:
        by_split = {"train": by_split["train"][:overfit]}
        seeds = seeds or tcfg["seeds"][:1]
    seeds = seeds or tcfg["seeds"]
    src_v, tgt_v = build_vocabs(by_split["train"])
    meta = {
        "TEST_RUN": allow_test_data, "label": TEST_LABEL if allow_test_data else REAL_LABEL, "prefix": prefix,
        "annotation_file": check["file"], "annotation_sha256": check["file_sha256"],
        "pilot_manifest_sha256": pilot_manifest_sha256, "overfit": overfit,
        "text2gloss_config": tcfg, "text2gloss_config_sha256": _sha(json.dumps(tcfg, sort_keys=True)),
        "config_hash": cfg["_meta"]["config_hash"], "vocab_sha256": vocab_hash(src_v, tgt_v),
        "vocab_sizes": {"src": len(src_v), "tgt": len(tgt_v)},
        "params": count_params(make_model(tcfg, src_v, tgt_v)), "seeds": seeds,
        "counts": {s: len(v) for s, v in by_split.items()},
        "versions": {"torch": torch.__version__, "sacrebleu": sacrebleu.__version__}, "git": _git(cfg["_meta"]["project_root"]),
    }
    if run_dir is None:
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        name = f"{prefix}text2gloss_{f'overfit{overfit}_' if overfit else ''}pilot50_{stamp}"
        run_dir = runs_root / name
        meta["created_utc"] = stamp
    else:
        diff = [k for k in RESUME_KEYS if old.get(k) != meta[k]]
        if diff:
            raise ResumeMismatch(f"{run_dir.name}: inputs changed since the run started ({diff}); start a new run")
        meta["created_utc"] = old["created_utc"]
    run_dir.mkdir(parents=True, exist_ok=True)
    atomic_write_json(run_dir / f"{prefix}run.json", meta)

    log = logging.getLogger(f"bdsl.text2gloss.{run_dir.name}")
    log.setLevel(logging.INFO)
    log.handlers.clear()
    fmt = logging.Formatter(f"%(asctime)s {'[TEST] ' if allow_test_data else ''}%(message)s")
    for h in (logging.FileHandler(run_dir / f"{prefix}train.log", encoding="utf-8"), logging.StreamHandler()):
        h.setFormatter(fmt)
        log.addHandler(h)
    log.info(f"{meta['label']} | run {run_dir.name} | {meta['counts']} | vocab {meta['vocab_sizes']} | "
             f"{meta['params']:,} parameters | seeds {seeds}")

    monitor = by_split["train"] if overfit else by_split["val"]
    states = {}
    for seed in seeds:
        seed_dir = run_dir / f"seed{seed}"
        seed_dir.mkdir(exist_ok=True)
        states[seed] = train_seed(by_split["train"], monitor, src_v, tgt_v, tcfg, seed, seed_dir, meta, log,
                                  stop_after, bool(overfit))
        atomic_write_text(seed_dir / f"{prefix}curves.csv",
                          pd.DataFrame(states[seed]["history"]).to_csv(index=False, lineterminator="\n"))
    if not all(s["done"] for s in states.values()):
        log.info("not finished (stopped for the resume test); resume with --resume")
        for h in log.handlers:
            h.close()
        return {"run_dir": str(run_dir), "finished": False}

    # Final evaluation: best checkpoint per seed, beam search, every split.
    metrics = {"TEST_RUN": allow_test_data, "label": meta["label"], "run": run_dir.name,
               "g0": {s: evaluate(v, [[tag_token(t) for t in p["g0_tags"]] + p["g0_gloss"] for p in v])
                      for s, v in by_split.items()},
               "agru": {}}
    rows = {p["index"]: {"run_label": meta["label"], "index": p["index"], "split": p["split"],
                         "sentence_norm": p["sentence_norm"], "reference": " ".join(p["tgt"]),
                         "g0": " ".join(p["g0_gloss"]), "g0_wer": item_wer(p["gloss"], p["g0_gloss"])}
            for v in by_split.values() for p in v}
    for seed in seeds:
        model = make_model(tcfg, src_v, tgt_v)
        best = torch.load(run_dir / f"seed{seed}" / f"{prefix}ckpt_best.pt", weights_only=True)
        model.load_state_dict(best["model"])
        seed_m = {"best_epoch": states[seed]["best_epoch"], "epochs": states[seed]["epoch"]}
        for s, v in by_split.items():
            outs = predict(model, v, src_v, tgt_v, tcfg["max_len"], tcfg["beam"])
            seed_m[s] = evaluate(v, outs)
            for p, o in zip(v, outs):
                rows[p["index"]][f"seed{seed}"] = " ".join(o)
                rows[p["index"]][f"seed{seed}_wer"] = item_wer(p["gloss"], split_tags(o)[1])
        metrics["agru"][str(seed)] = seed_m
    metrics["agru_mean_sd"] = {
        s: {k: {"mean": statistics.mean(vals), "sd": statistics.stdev(vals) if len(vals) > 1 else 0.0}
            for k in ("wer", "exact_match", "tag_accuracy", "bleu4", "chrf")
            for vals in [[metrics["agru"][str(sd)][s][k] for sd in seeds]]}
        for s in by_split}
    atomic_write_json(run_dir / f"{prefix}metrics.json", metrics)
    atomic_write_text(run_dir / f"{prefix}per_item.csv",
                      "﻿" + pd.DataFrame(list(rows.values())).to_csv(index=False, lineterminator="\n"))
    for s in by_split:
        g, a = metrics["g0"][s], metrics["agru_mean_sd"][s]
        log.info(f"{s:5s} G0 WER {g['wer']:.1f} exact {g['exact_match']:.0f}% | A-GRU WER {a['wer']['mean']:.1f}"
                 f"±{a['wer']['sd']:.1f} exact {a['exact_match']['mean']:.0f}% tags {a['tag_accuracy']['mean']:.0f}%"
                 f" BLEU {a['bleu4']['mean']:.1f} chrF {a['chrf']['mean']:.1f}")
    for h in log.handlers:
        h.close()
    return {"run_dir": str(run_dir), "finished": True, "metrics": metrics}
