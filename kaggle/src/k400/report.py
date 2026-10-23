"""Notebook 08: paper tables (CSV + Markdown + LaTeX), figures (PNG) and outputs/RESULTS_SUMMARY.md.

Every number comes from a file written by an earlier step and is listed in RESULTS_SUMMARY.md with its
run / evaluation ID, its source file and the label "measured" (nothing here is estimated). If a step has
not run yet, the report says so instead of inventing a value.
"""

from __future__ import annotations

import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

from bdsl.data import kaggle400 as k4
from bdsl.io import atomic_write_text

from .tables import fmt, fmt_ci, write_table

B_SHOW = [("mpjpe_body", "MPJPE body (sw)", 3), ("mpjpe_lhand", "MPJPE L hand (mm)", 1),
          ("mpjpe_rhand", "MPJPE R hand (mm)", 1), ("dtw_body", "DTW-MJE body (sw)", 3),
          ("dtw_lhand", "DTW-MJE L hand (mm)", 1), ("dtw_rhand", "DTW-MJE R hand (mm)", 1),
          ("duration_err_s", "duration error (s)", 2), ("velocity_ratio", "velocity ratio", 2),
          ("jerk_ratio", "jerk ratio", 2), ("hand_energy_ratio", "hand-energy ratio", 2)]
A_SHOW = [("wer", "gloss WER vs G0 (%)", 1), ("exact_match", "exact match (%)", 1), ("tag_accuracy", "tag accuracy (%)", 1),
          ("chrf", "chrF", 1), ("bleu4", "BLEU-4", 1)]
METHOD_ORDER = ["model_b_gloss", "model_b_text", "B0", "B1"]
SHORT = {"model_b_gloss": "Model B\n(gloss)", "model_b_text": "Model B\n(text)", "B0": "B0\nmean", "B1": "B1\nretrieval"}
HONESTY = """- All numbers are **measured** on the kaggle400 subset ({counts}): small-scale and
  **signer-dependent** (signers unknown; the same people appear in every split).
- The test split was evaluated **once**, after the configuration was frozen (`outputs/FINAL_TEST_LOCK.json`).
  Nothing was tuned on test.
- **Low coordinate error is not proof of correct sign language.** B0 gives every sentence the same average
  motion and can still have competitive error. Only BdSL-competent human evaluation can test correctness;
  none exists for this project (no human or expert validation is claimed).
- Model A numbers are **agreement with the rule glosser (G0 pseudo-gloss)**, not BdSL correctness: the
  references are G0 auto_draft outputs, not human annotation.
- Model B input glosses are G0 pseudo-glosses (auto_draft), not BdSL annotation.
- Baselines are reported exactly as measured. Where Model B does not beat a baseline, the tables show it.
"""


def _load(p: Path):
    return json.loads(p.read_text(encoding="utf-8")) if p.is_file() else None


def _latest(folder: Path, prefix: str) -> Path | None:
    c = sorted(d for d in folder.glob(f"{prefix}*") if (d / "metrics.json").is_file()) if folder.is_dir() else []
    return c[-1] if c else None


class _Ledger:
    """Every number that goes into RESULTS_SUMMARY.md, with where it came from."""

    def __init__(self):
        self.rows = []

    def add(self, quantity, value, source, run_id, label="measured"):
        self.rows.append({"quantity": quantity, "value": value, "label": label, "run_or_eval_id": run_id,
                          "source_file": source})


def _modelb_table(m: dict, split: str, eval_id: str, src: str, led: _Ledger) -> pd.DataFrame:
    rows = []
    meth = m["methods"]
    for key in METHOD_ORDER:
        if key not in meth:
            continue
        v = meth[key]
        row = {"method": v["description"].split(":")[0] if key.startswith("B") else v["description"],
               "seeds": len(v.get("seeds", [])) or "-"}
        for k, name, nd in B_SHOW:
            if "mean_sd_over_seeds" in v:
                ms = v["mean_sd_over_seeds"][k]
                ci = v["seed_mean_items_ci95"][k]["ci95"]
                row[name] = f"{fmt(ms['mean'], nd)} ± {fmt(ms['sd'], nd)} {fmt_ci(ci, nd)}"
                led.add(f"{split} {key} {k} (mean over seeds)", fmt(ms["mean"], nd), src, f"{eval_id} / {v['run_id']}")
            else:
                ci = v["items_ci95"][k]["ci95"]
                row[name] = f"{fmt(v['summary'][k], nd)} {fmt_ci(ci, nd)}"
                led.add(f"{split} {key} {k}", fmt(v["summary"][k], nd), src, eval_id)
        d = v["diversity_ratio"]
        if "mean" in d and "ci95_per_seed" in d:
            row["diversity ratio"] = f"{fmt(d['mean'], 2)} ± {fmt(d['sd'], 2)}"
            led.add(f"{split} {key} diversity_ratio (mean over seeds)", fmt(d["mean"], 2), src, eval_id)
        else:
            row["diversity ratio"] = f"{fmt(d['estimate'], 2)} {fmt_ci(d, 2)}"
            led.add(f"{split} {key} diversity_ratio", fmt(d["estimate"], 2), src, eval_id)
        rows.append(row)
    return pd.DataFrame(rows)


def _paired_table(m: dict, split: str, eval_id: str, src: str, led: _Ledger) -> pd.DataFrame:
    rows = []
    for comp, d in m["paired_differences"].items():
        for k, name, nd in B_SHOW:
            if k not in d:
                continue
            x = d[k]
            verdict = ("first lower (better)" if x["high"] < 0 else "first higher (worse)") if x["excludes_zero"] \
                else "not distinguishable at this sample size"
            rows.append({"comparison (first - second)": comp, "metric": name, "mean difference": fmt(x["estimate"], nd),
                         "95% CI": fmt_ci(x, nd), "CI excludes 0": "yes" if x["excludes_zero"] else "no", "reading": verdict,
                         "n items": x["n"]})
            led.add(f"{split} paired diff {comp} {k}", f"{fmt(x['estimate'], nd)} {fmt_ci(x, nd)}", src, eval_id)
    return pd.DataFrame(rows)


def _modela_table(a: dict, split: str, eval_id: str, src: str, led: _Ledger) -> pd.DataFrame:
    row = {"model": "A-GRU trained on G0 pseudo-glosses", "split": split, "seeds": len(a["seeds"]), "items": a["n_items"]}
    for k, name, nd in A_SHOW:
        ms, ci = a["mean_sd_over_seeds"][k], a["ci95_seed_mean"][k]
        row[name] = f"{fmt(ms['mean'], nd)} ± {fmt(ms['sd'], nd)} {fmt_ci(ci, nd)}"
        led.add(f"{split} Model A {k} (agreement with G0)", fmt(ms["mean"], nd), src, f"{eval_id} / {a['run_id']}")
    row["items with source OOV"] = a["src_oov_items"]
    return pd.DataFrame([row])


def _curves(run_dir: Path, kind: str) -> dict[str, pd.DataFrame]:
    return {d.name: pd.read_csv(d / "curves.csv") for d in sorted(run_dir.glob("seed*")) if (d / "curves.csv").is_file()}


def _fig_curves(cfg_run: dict, runs_dir: Path, path: Path, title: str, kind: str) -> list[str]:
    import matplotlib.pyplot as plt

    from . import figstyle as fs

    fs.apply()
    curves = _curves(runs_dir / cfg_run["run_id"], kind)
    if not curves:
        return []
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.6))
    shades = [fs.SLOT[1], fs.SLOT[2], fs.SLOT[3]]
    for n, (seed, c) in enumerate(curves.items()):
        col = shades[n % 3]
        if kind == "b":
            axes[0].plot(c["epoch"], c["train_pos"], color=col, label=f"{seed} train")
            axes[0].plot(c["epoch"], c["monitor_pos_l1"], color=col, linestyle="--", label=f"{seed} val")
            best = c.loc[c["monitor_pos_l1"].idxmin()]
            axes[0].scatter([best["epoch"]], [best["monitor_pos_l1"]], color=col, s=30, zorder=3)
            axes[1].plot(c["epoch"], c["train_total"], color=col, label=seed)
        else:
            axes[0].plot(c["epoch"], c["train_loss"], color=col, label=f"{seed} train loss")
            axes[1].plot(c["epoch"], c["monitor_wer"], color=col, label=f"{seed} val WER vs G0")
            best = c.loc[c["monitor_wer"].idxmin()]
            axes[1].scatter([best["epoch"]], [best["monitor_wer"]], color=col, s=30, zorder=3)
    if kind == "b":
        axes[0].set_title("masked position L1 (standardised): train (solid) vs val (dashed); dot = best epoch")
        axes[1].set_title("total training loss")
        axes[0].set_ylabel("L1")
    else:
        axes[0].set_title("training loss (cross-entropy)")
        axes[1].set_title("val gloss WER vs G0 references (%); dot = best epoch")
    for ax in axes:
        ax.set_xlabel("epoch")
        ax.legend(fontsize=7)
    fig.suptitle(title, fontsize=10)
    fs.footer(fig, f"run {cfg_run['run_id']} - measured. Train/val gap shows over-fitting honestly.")
    fig.tight_layout(rect=(0, 0.04, 1, 0.94))
    fig.savefig(path)
    plt.close(fig)
    return [path.name]


def _fig_methods(m: dict, path: Path, split: str) -> None:
    import matplotlib.pyplot as plt

    from . import figstyle as fs

    fs.apply()
    meth = m["methods"]
    show = [("mpjpe_body", "MPJPE body (shoulder widths)"), ("dtw_body", "DTW-MJE body (shoulder widths)"),
            ("mpjpe_lhand", "MPJPE left hand (mm)"), ("mpjpe_rhand", "MPJPE right hand (mm)")]
    fig, axes = plt.subplots(1, 4, figsize=(12, 3.4))
    keys = [k for k in METHOD_ORDER if k in meth]
    for ax, (k, title) in zip(axes, show):
        for n, key in enumerate(keys):
            v = meth[key]
            ci = (v["seed_mean_items_ci95"] if "seed_mean_items_ci95" in v else v["items_ci95"])[k]["ci95"]
            est = ci["estimate"]
            ax.bar(n, est, color=fs.METHOD_COLOURS[key], width=0.7, edgecolor=fs.SURFACE)
            ax.errorbar(n, est, yerr=[[est - ci["low"]], [ci["high"] - est]], color=fs.INK, capsize=3, linewidth=1)
        ax.set_xticks(range(len(keys)), [SHORT[k] for k in keys], fontsize=7)
        ax.set_title(title, fontsize=9)
    fig.suptitle(f"{split.upper()}: Model B vs baselines (lower is better); error bars = 95% bootstrap CI over items",
                 fontsize=10)
    fs.footer(fig, "Measured. Low coordinate error is not proof of correct sign language. Small-scale, signer-dependent.")
    fig.tight_layout(rect=(0, 0.05, 1, 0.92))
    fig.savefig(path)
    plt.close(fig)


def _fig_error(ea: pd.DataFrame, path: Path, split: str) -> None:
    import matplotlib.pyplot as plt

    from . import figstyle as fs

    fs.apply()
    d = ea[(ea["metric"] == "dtw_body") & ea["method"].isin(["model_b_gloss", "B0", "B1"])]
    strata = list(dict.fromkeys(d["stratum"]))
    fig, axes = plt.subplots(1, len(strata), figsize=(2.2 * len(strata) + 1, 3.4), sharey=True)
    for ax, s in zip(np.atleast_1d(axes), strata):
        sub = d[d["stratum"] == s]
        vals = list(dict.fromkeys(sub["value"]))
        for n, key in enumerate(["model_b_gloss", "B0", "B1"]):
            y = [sub[(sub["value"] == v) & (sub["method"] == key)]["mean"].mean() for v in vals]
            ax.bar(np.arange(len(vals)) + (n - 1) * 0.27, y, width=0.25, color=fs.METHOD_COLOURS[key],
                   label=fs.METHOD_NAMES[key] if s == strata[0] else None)
        ns = [int(sub[sub["value"] == v]["n"].iloc[0]) for v in vals]
        ax.set_xticks(range(len(vals)), [f"{v}\n(n={n})" for v, n in zip(vals, ns)], fontsize=7)
        ax.set_title(s.replace("_", " "), fontsize=8)
    np.atleast_1d(axes)[0].set_ylabel("DTW-MJE body (sw)")
    fig.legend(loc="upper right", fontsize=7)
    fig.suptitle(f"{split.upper()} error analysis: body DTW-MJE by stratum (means over items; small n per bar)", fontsize=10)
    fs.footer(fig, "Measured. Strata with few items are noisy; question/negation are indicative word lists.")
    fig.tight_layout(rect=(0, 0.05, 1, 0.9))
    fig.savefig(path)
    plt.close(fig)


def build_report(cfg: dict) -> dict:
    p = k4.paths(cfg)
    tdir, fdir = p["tables"], p["figures"]
    tdir.mkdir(parents=True, exist_ok=True)
    fdir.mkdir(parents=True, exist_ok=True)
    led, made, missing = _Ledger(), {"tables": [], "figures": []}, []
    state = p["state_root"]
    data_dir = p["data_dir"]
    # T1 split
    sel_meta = _load(data_dir / "SELECTION_META.json")
    if sel_meta:
        oov = sel_meta["oov"]
        sub = pd.read_csv(p["subset_manifest"], encoding="utf-8-sig")
        rows = []
        for sp in ("train", "val", "test"):
            s = sub[sub["split"] == sp]
            r = {"split": sp, "clips": len(s), "groups": s["group_id"].nunique(),
                 "minimal-pair held-out": int((s["mp_role"] == "heldout").sum()),
                 "with train minimal-pair sibling": int(s["has_train_minimal_pair_sibling"].sum()) if sp != "train" else "-",
                 "OOV token rate vs train": f"{100 * oov[sp]['oov_token_rate']:.1f}%" if sp != "train" else "-",
                 "sentences with OOV": f"{oov[sp]['sentences_with_oov']}/{oov[sp]['sentences']}" if sp != "train" else "-",
                 "mean duration (s)": fmt(s["duration_s"].mean(), 2)}
            rows.append(r)
            led.add(f"{sp} clips", len(s), "data/subset_manifest.csv", "kaggle400_v1 split")
            if sp != "train":
                led.add(f"{sp} OOV token rate vs train vocabulary", r["OOV token rate vs train"], "data/SELECTION_META.json",
                        "kaggle400_v1 split")
        made["tables"].append(write_table(pd.DataFrame(rows), tdir, "T1_split", "kaggle400 split (measured)",
                                          f"Train vocabulary: {oov['train_vocabulary_size']} word types."))
        shutil.copy2(data_dir / "SPLIT_SUMMARY.png", fdir / "F1_split_summary.png")
        made["figures"].append("F1_split_summary.png")
    else:
        missing.append("data/SELECTION_META.json")
    # T2 feature QC
    hc = p["qc_dir"] / "hand_coverage_summary.csv"
    ex = _load(p["qc_dir"] / "extract_run.json")
    if hc.is_file() and ex:
        h = pd.read_csv(hc)
        keep = ["split", "clips", "cov_pose_mean", "cov_left_hand_mean", "cov_right_hand_mean", "cov_both_hands_mean",
                "cov_any_hand_mean", "cov_face_mean"]
        t2 = h[[c for c in keep if c in h]].copy()
        for c in t2.columns[2:]:
            t2[c] = (100 * t2[c]).map(lambda v: f"{v:.1f}%")
        made["tables"].append(write_table(t2, tdir, "T2_feature_coverage",
                                          f"MediaPipe Holistic coverage per split (feat_ver {ex['feat_ver']}, measured)",
                                          f"Extraction platform: {ex['platform']}; mediapipe {ex['mediapipe']}."))
        for r in t2.to_dict("records"):
            led.add(f"{r['split']} left/right hand coverage", f"{r.get('cov_left_hand_mean')} / {r.get('cov_right_hand_mean')}",
                    "processed/qc/hand_coverage_summary.csv", f"feat_ver {ex['feat_ver']}")
    else:
        missing.append("processed/qc (notebook 02)")
    # frozen runs, training table, curves
    frozen = _load(p["frozen"])
    if frozen:
        rows = []
        for role, r in frozen["runs"].items():
            run_dir = p["runs"] / r["run_id"]
            meta = _load(run_dir / "run.json") or {}
            mets = _load(run_dir / "metrics.json") or {}
            env = _load(run_dir / "env.json") or {}
            per = mets.get("model_b") or mets.get("agru") or {}
            for seed in r["seeds"]:
                sm = per.get(str(seed), {})
                secs = (mets.get("train_seconds") or {}).get(str(seed))
                c = run_dir / f"seed{seed}" / "curves.csv"
                cv = pd.read_csv(c) if c.is_file() else None
                be = sm.get("best_epoch")
                if cv is not None and be:
                    b = cv[cv["epoch"] == be].iloc[0]
                    tr = b["train_pos"] if "train_pos" in b else b["train_loss"]
                    va = b["monitor_pos_l1"] if "monitor_pos_l1" in b else b["monitor_wer"]
                else:
                    tr = va = np.nan
                rows.append({"role": role, "run": r["run_id"], "seed": seed, "best epoch": be, "epochs run": sm.get("epochs"),
                             "train time (s)": secs, "device": meta.get("device"),
                             "GPU": "; ".join((env.get("device") or {}).get("gpu_names", [])) or "none",
                             "train loss at best": fmt(tr, 4), "val monitor at best": fmt(va, 4),
                             "monitor": "masked pos L1 (std.)" if role != "model_a" else "val WER vs G0 (%)"})
                led.add(f"{role} seed {seed} best epoch", be, f"outputs/runs/{r['run_id']}/metrics.json", r["run_id"])
                led.add(f"{role} seed {seed} training time (s)", secs, f"outputs/runs/{r['run_id']}/metrics.json",
                        r["run_id"])
        made["tables"].append(write_table(pd.DataFrame(rows), tdir, "T3_training",
                                          "Training runs used for the paper (frozen configuration; measured)",
                                          "Early stopping on VAL only. Train loss vs val monitor at the best epoch shows over-fitting."))
        for role, fname, title, kind in (("model_b_gloss", "F2_curves_modelB_gloss.png", "Model B (G0 gloss input) learning curves", "b"),
                                         ("model_b_text", "F3_curves_modelB_text.png", "Model B (Bangla word input, ablation T) learning curves", "b"),
                                         ("model_a", "F4_curves_modelA.png", "Model A (A-GRU on G0 references) learning curves", "a")):
            made["figures"] += _fig_curves(frozen["runs"][role], p["runs"], fdir / fname, title, kind)
        # T8 train vs val (training metrics) — over-fitting table
        rows = []
        for role in ("model_b_gloss", "model_b_text"):
            r = frozen["runs"][role]
            mets = _load(p["runs"] / r["run_id"] / "metrics.json") or {}
            ms = mets.get("model_b_mean_sd", {})
            for sp in ("train", "val"):
                if sp in ms:
                    rows.append({"method": role, "split": sp, "MPJPE body (sw)": fmt(ms[sp]["mpjpe_body"]["mean"]),
                                 "MPJPE L hand (mm)": fmt(ms[sp]["mpjpe_lhand"]["mean"], 1),
                                 "MPJPE R hand (mm)": fmt(ms[sp]["mpjpe_rhand"]["mean"], 1),
                                 "source": f"runs/{r['run_id']}/metrics.json"})
                    led.add(f"{role} {sp} MPJPE body (training-run evaluation)", fmt(ms[sp]["mpjpe_body"]["mean"]),
                            f"outputs/runs/{r['run_id']}/metrics.json", r["run_id"])
            for b in ("B0", "B1"):
                for sp in ("train", "val"):
                    if sp in mets.get(b, {}):
                        rows.append({"method": f"{b} ({role} run)", "split": sp, "MPJPE body (sw)": fmt(mets[b][sp]["mpjpe_body"]),
                                     "MPJPE L hand (mm)": fmt(mets[b][sp]["mpjpe_lhand"], 1),
                                     "MPJPE R hand (mm)": fmt(mets[b][sp]["mpjpe_rhand"], 1), "source": f"runs/{r['run_id']}/metrics.json"})
        test_dir = _latest(p["eval"], "FINAL_test_")
        if test_dir:
            tm = _load(test_dir / "metrics.json")["model_b_and_baselines"]["methods"]
            for key in ("model_b_gloss", "model_b_text", "B0", "B1"):
                v = tm[key]
                val = v["mean_sd_over_seeds"]["mpjpe_body"]["mean"] if "mean_sd_over_seeds" in v else v["summary"]["mpjpe_body"]
                rows.append({"method": key, "split": "test", "MPJPE body (sw)": fmt(val), "MPJPE L hand (mm)": "see T4",
                             "MPJPE R hand (mm)": "see T4", "source": f"eval/{test_dir.name}/metrics.json"})
        made["tables"].append(write_table(pd.DataFrame(rows), tdir, "T8_train_val_test",
                                          "Training-time vs held-out error (over-fitting check; measured)",
                                          "Train numbers use the best (val-selected) checkpoint on clips the model was trained on."))
    else:
        missing.append("outputs/frozen_config.json (notebook 07)")
    # evaluations
    for split, prefix in (("val", "val_"), ("test", "FINAL_test_")):
        d = _latest(p["eval"], prefix)
        if not d:
            missing.append(f"{split} evaluation (notebook 07)")
            continue
        m = _load(d / "metrics.json")
        src = f"outputs/eval/{d.name}/metrics.json"
        tb = _modelb_table(m["model_b_and_baselines"], split, d.name, src, led)
        made["tables"].append(write_table(tb, tdir, f"T4_modelB_{split}",
                                          f"{split.upper()}: Model B vs baselines (mean ± sd over 3 seeds, [95% bootstrap CI over items]; measured)",
                                          "Lower is better for errors; ratios: 1.0 = as much motion as the real recording. "
                                          "Low coordinate error is not proof of correct sign language."))
        made["tables"].append(write_table(_paired_table(m["model_b_and_baselines"], split, d.name, src, led), tdir,
                                          f"T5_paired_{split}", f"{split.upper()}: paired differences per item (95% bootstrap CI; measured)"))
        made["tables"].append(write_table(_modela_table(m["model_a"], split, d.name, src, led), tdir, f"T6_modelA_{split}",
                                          f"{split.upper()}: Model A — agreement with the rule glosser (G0 pseudo-gloss); NOT BdSL correctness",
                                          "References are G0 auto_draft outputs. Mean ± sd over 3 seeds [95% bootstrap CI]."))
        ea = pd.read_csv(d / "error_analysis.csv")
        piv = ea.pivot_table(index=["stratum", "value", "n"], columns=["method", "metric"], values="mean").round(3)
        piv.columns = [f"{a} {b}" for a, b in piv.columns]
        made["tables"].append(write_table(piv.reset_index(), tdir, f"T7_error_analysis_{split}",
                                          f"{split.upper()}: error analysis by stratum (means over items; measured)",
                                          "Small n per stratum: read as descriptive only."))
        _fig_methods(m["model_b_and_baselines"], fdir / f"F5_methods_{split}.png", split)
        _fig_error(ea, fdir / f"F6_error_analysis_{split}.png", split)
        made["figures"] += [f"F5_methods_{split}.png", f"F6_error_analysis_{split}.png"]
        shutil.copy2(d / "per_item_modelB.csv", tdir / f"per_item_modelB_{split}.csv")
        shutil.copy2(d / "per_item_modelA.csv", tdir / f"per_item_modelA_{split}.csv")
    lock = _load(p["final_lock"])
    made["lock_path"] = str(p["lock"])
    led_df = pd.DataFrame(led.rows)
    atomic_write_text(tdir / "RESULTS_LEDGER.csv", "\ufeff" + led_df.to_csv(index=False, lineterminator="\n"))
    atomic_write_text(p["outputs"] / "RESULTS_SUMMARY.md", results_summary(led_df, made, missing, lock, frozen))
    return {"tables": [t["name"] for t in made["tables"]], "figures": made["figures"], "missing": missing,
            "numbers_listed": len(led_df), "final_test_done": bool(lock)}


def results_summary(led: pd.DataFrame, made: dict, missing: list[str], lock: dict | None, frozen: dict | None) -> str:
    from .tables import to_markdown

    counts = "split counts unknown"
    try:
        c = json.loads(Path(made["lock_path"]).read_text(encoding="utf-8")).get("counts") or {}
        counts = f"{c.get('train', '?')} train / {c.get('val', '?')} val / {c.get('test', '?')} test clips"
    except (OSError, ValueError, KeyError):
        pass
    status = ("The single final test evaluation **has run** "
              f"(`outputs/FINAL_TEST_LOCK.json`, {lock['created_utc']}, results `{lock['results']}`)." if lock else
              "**The test split has NOT been evaluated yet** (no `FINAL_TEST_LOCK.json`). No test number exists.")
    fp = "" if not frozen else ("" if frozen.get("for_paper") else "\n> **NOT FOR PAPER**: the frozen configuration contains a run made from uncommitted code.\n")
    tables = "\n".join(f"- `tables/{t['name']}` (.csv / .md / .tex)" for t in made["tables"])
    figs = "\n".join(f"- `figures/{f}`" for f in made["figures"])
    miss = "\n".join(f"- {m}" for m in missing) or "- nothing"
    return f"""# RESULTS_SUMMARY — kaggle400 experiment

Generated {datetime.now(timezone.utc).isoformat(timespec='seconds')} by `kaggle/src/k400/report.py` (notebook 08)
from the files listed below. **Every number is labelled; all are "measured" (none estimated).**
{fp}
## Status
{status}

## Honesty rules for using these numbers
{HONESTY.format(counts=counts)}
## Every number, with its source
{to_markdown(led) if len(led) else 'No numbers yet.'}

## Tables (CSV for data, Markdown for reading, LaTeX for the paper)
{tables or '- none yet'}

## Figures
{figs or '- none yet'}

## Not available yet
{miss}
"""
