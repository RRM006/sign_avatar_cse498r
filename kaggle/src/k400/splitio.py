"""Write the kaggle400 split: manifests, README_DATA.md, SPLIT_REPORT.md, SPLIT_SUMMARY.png, SELECTION_META.json."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from bdsl.io import atomic_write_json, atomic_write_text, sha256_file

from .select import MANIFEST_COLUMNS, SPLITS, oov_stats
from .verify import format_results, run_checks

USAGE_TABLE = """| Split | Used for | Never used for |
|---|---|---|
| **TRAIN** | the model learns from it: fitting weights, building vocabularies, feature standardisation (mean/sd), the sources of baselines B0 and B1 | — |
| **VAL** | development: early stopping, choosing epochs / learning rate / ablations, error analysis | fitting weights |
| **TEST** | locked. Used **once**, at the very end, after the final configuration is frozen (`evaluate --final`) | any decision: no tuning, no model choice, no threshold choice |

Enforced in code: training commands read only train and val rows (`bdsl.data.kaggle400`: reading test
raises `TestSplitLocked`); `python -m bdsl.cli evaluate --final` reads test, needs a frozen configuration,
writes `outputs/FINAL_TEST_LOCK.json` and refuses a second run unless the owner gives a written reason.
"""

KNOWN_LIMITS = """1. **Small-scale, signer-dependent.** 40 val and 40 test clips; the number of signers is unknown
   (owner estimate 4–6, unverified, ADR-0018) and which signer recorded which clip is unknown, so the
   same signers appear in train, val and test. Results do not show generalisation to new signers.
2. **Split S1 v0 is provisional.** Groups join clips with the same normalised sentence, the same
   SHA-256, or a *known* shared-segment link. Only one link is known (colour cluster 3456/3457/3458).
   The full shared-segment scan (open question G2) has not been run, so different sentences that reuse
   the same recorded footage could still sit in different splits. These leakage tests cannot detect that.
3. **Minimal-pair siblings are the most likely place for shared footage.** A val/test minimal-pair clip
   and its train sibling were often recorded as a template; if footage was edited and reused (as in the
   colour cluster), motion error on those items may be optimistic. Report the minimal-pair subset
   separately (error analysis stratum `minimal_pair_sibling_in_train`).
4. **Indicative tags.** "question" and "negation" come from small word lists (`src/bdsl/text/tags.py`),
   not from linguistic annotation; the sheet contains no `?`.
5. **Vocabulary.** The train vocabulary is small (see the OOV table); words never seen in train become
   `<unk>` for every model, so OOV items are expected to be harder.
6. **Glosses are G0 pseudo-glosses** (auto_draft, rule-based, no human review): not BdSL annotation.
7. **Hand-side labels** are MediaPipe's as given; whether some recordings are mirrored is unknown (G8).
"""


def _csv(df: pd.DataFrame) -> str:
    return "\ufeff" + df.to_csv(index=False, lineterminator="\n")


def _table(sel: pd.DataFrame, pool: pd.DataFrame, col: str) -> str:
    ct = pd.crosstab(sel[col].astype(str), sel["split"]).reindex(columns=list(SPLITS), fill_value=0)
    share = pool[col].astype(str).value_counts(normalize=True)
    lines = [f"| {col} | train | val | test | pool share |", "|---|---:|---:|---:|---:|"]
    for k in sorted(set(ct.index) | set(share.index)):
        row = ct.loc[k] if k in ct.index else pd.Series(0, index=list(SPLITS))
        n = {sp: int(row[sp]) for sp in SPLITS}
        tot = {sp: max(int((sel["split"] == sp).sum()), 1) for sp in SPLITS}
        cells = " | ".join(f"{n[sp]} ({100 * n[sp] / tot[sp]:.1f}%)" for sp in SPLITS)
        lines.append(f"| {k} | {cells} | {100 * share.get(k, 0):.1f}% |")
    return "\n".join(lines)


def summary_figure(sel: pd.DataFrame, pool: pd.DataFrame, cols: list[str], path: Path) -> None:
    import matplotlib.pyplot as plt
    import numpy as np

    from . import figstyle as fs

    fs.apply()
    fig, axes = plt.subplots(2, 3, figsize=(11, 6.2))
    groups = [("pool", pool)] + [(sp, sel[sel["split"] == sp]) for sp in SPLITS]
    for ax, col in zip(axes.ravel(), cols):
        cats = sorted(set(pool[col].astype(str)))
        x = np.arange(len(cats))
        w = 0.8 / len(groups)
        for n, (name, df) in enumerate(groups):
            share = df[col].astype(str).value_counts(normalize=True).reindex(cats, fill_value=0) * 100
            ax.bar(x + (n - (len(groups) - 1) / 2) * w, share.values, width=w * 0.85, color=fs.SPLIT_COLOURS[name],
                   label=f"{name} (n={len(df)})", edgecolor=fs.SURFACE, linewidth=0.6)
        ax.set_xticks(x, cats, rotation=0)
        ax.set_title(col.replace("_", " "))
        ax.set_ylabel("% of clips")
    axes[0, 0].legend(loc="upper right")
    fig.suptitle("kaggle400 split: train / val / test compared with the whole candidate pool (S1 v0 representatives)",
                 fontsize=11, color=fs.INK)
    fs.footer(fig, "question/negation = indicative word lists, not linguistic labels. Pool = one clip per sentence, "
                   "S1 v0 train+val+test. Measured from manifest_v1.")
    fig.tight_layout(rect=(0, 0.03, 1, 0.95))
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path)
    plt.close(fig)


def readme_data(counts: dict) -> str:
    return f"""# kaggle/data — the 400 videos of the kaggle400 experiment

**This folder is gitignored** (videos never go to Git; the repository is public). The small files
(manifests, reports, lock) are added to Git explicitly by `kaggle/tools/run_local_steps.ps1`.

| Folder / file | What it is | Rule |
|---|---|---|
| `train/videos/` ({counts.get('train', 0)} clips) + `train/train_manifest.csv` | TRAIN: the models learn from these | may be used for fitting, vocabularies, standardisation, B0/B1 sources |
| `val/videos/` ({counts.get('val', 0)} clips) + `val/val_manifest.csv` | VAL: development set | early stopping, choosing settings, error analysis |
| `test/videos/` ({counts.get('test', 0)} clips) + `test/test_manifest.csv` | TEST: locked | read **once**, by `evaluate --final`, after freezing the configuration |
| `subset_manifest.csv` | all 400 rows, with `split`, `sha256_source` and `sha256_copy` | the SHA-256 of every copy, filled by the copy step |
| `COPY_VERIFICATION.csv` | per clip: source path, SHA-256 of source and copy, size, source unchanged | written by the copy step |
| `SPLIT_REPORT.md`, `SPLIT_SUMMARY.png` | how the clips were chosen, tables per split, OOV, leakage tests, known limits | read before using any result |
| `SPLIT_LOCK.json` | line-ending-independent hashes of the 4 manifests | training refuses to run if one changes |
| `SELECTION_META.json` | inputs (hashes of manifest_v1 and S1 v0), seed, selection report | provenance |

Rules:
- Every video is a byte-identical **copy** of `dataset/initial_dataset/SIGN_LANGUAGE_DATA/<Index>.mp4`
  (SHA-256 checked). The originals are never moved or changed.
- A clip is in exactly one folder. Never move a file between folders and never edit a manifest:
  the lock would fail, and if it did not, the experiment would be invalid.
- These videos may go only to the owner's **private** Kaggle dataset (owner permission 2026-10-23,
  this experiment only). Never make that dataset public.
- Run `python kaggle/src/verify_split.py --require-videos` to re-check everything.
"""


def write_selection(root: Path, cfg: dict, sel: pd.DataFrame, report: dict, pool: pd.DataFrame,
                    inputs: dict) -> dict:
    """root = the folder that will contain data/ (kaggle/). Writes everything except the lock."""
    data = root / "data"
    kcfg = cfg["kaggle400"]
    for sp in SPLITS:
        part = sel[sel["split"] == sp][MANIFEST_COLUMNS]
        atomic_write_text(data / sp / f"{sp}_manifest.csv", _csv(part))
        (data / sp / "videos").mkdir(parents=True, exist_ok=True)
    sub = sel[MANIFEST_COLUMNS].copy()
    sub.insert(MANIFEST_COLUMNS.index("sha256") + 1, "sha256_source", sub["sha256"])
    sub.insert(MANIFEST_COLUMNS.index("sha256") + 2, "sha256_copy", "")
    atomic_write_text(data / "subset_manifest.csv", _csv(sub))
    oov = oov_stats(sel)
    counts = sel["split"].value_counts().to_dict()
    meta = {"generated_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"), "selection": "kaggle400_v1",
            "code": "kaggle/src/k400/select.py", "seed": kcfg["seed"], "kaggle400_config": kcfg,
            "known_shared_segment_links": cfg["split"]["known_shared_segment_links"], "inputs": inputs,
            "counts": counts, "report": report, "oov": oov,
            "manifest_sha256": {f"{sp}_manifest.csv": sha256_file(data / sp / f"{sp}_manifest.csv") for sp in SPLITS}}
    atomic_write_json(data / "SELECTION_META.json", meta)
    atomic_write_text(data / "README_DATA.md", readme_data(counts))
    summary_figure(sel, pool, list(kcfg["strata"]), data / "SPLIT_SUMMARY.png")
    checks = run_checks(root, cfg["split"]["known_shared_segment_links"], inputs.get("s1_csv_path"))
    atomic_write_text(data / "SPLIT_REPORT.md", split_report(cfg, sel, report, pool, oov, inputs, checks))
    return {"counts": counts, "oov": oov, "checks": checks}


def split_report(cfg, sel, report, pool, oov, inputs, checks) -> str:
    kcfg = cfg["kaggle400"]
    counts = {sp: int((sel["split"] == sp).sum()) for sp in SPLITS}
    groups = {sp: int(sel.loc[sel["split"] == sp, "group_id"].nunique()) for sp in SPLITS}
    roles = sel.groupby(["split", "mp_role"]).size().to_dict()
    tables = "\n\n".join(_table(sel, pool, c) for c in kcfg["strata"])
    oov_rows = "\n".join(
        f"| {sp} | {o['tokens']} | {o['oov_tokens']} | **{100 * o['oov_token_rate']:.1f}%** | {o['types']} | {o['oov_types']} | "
        f"{o['sentences_with_oov']} / {o['sentences']} | {o['sentences_all_words_seen']} / {o['sentences']} |"
        for sp, o in ((sp, oov[sp]) for sp in ("val", "test")))
    mp_rows = "\n".join(
        f"| {sp} | {int(((sel['split'] == sp) & (sel['mp_role'] == 'heldout')).sum())} | "
        f"{int(((sel['split'] == sp) & sel['has_train_minimal_pair_sibling']).sum())} | "
        f"{int(((sel['split'] == sp) & (sel['mp_role'] == 'heldout') & sel['all_words_in_train']).sum())} |"
        for sp in ("val", "test"))
    pilot = sel[sel["in_pilot50"]].groupby("split").size().to_dict()
    long = sel.loc[sel["duration_s"].idxmax()]
    return f"""# SPLIT_REPORT — kaggle400 (400 videos for the Kaggle experiment)

Generated by `python kaggle/src/k400_run.py select` (`kaggle/src/k400/select.py`) on
{datetime.now(timezone.utc).date().isoformat()}. Everything below is **measured** from `manifest_v1` and `S1_v0`
unless marked otherwise. Results on this subset are **small-scale and signer-dependent**.

## 1. Inputs
| Input | SHA-256 |
|---|---|
| `work/manifests/manifest_v1.csv` | `{inputs['manifest_csv_sha256']}` |
| `work/splits/S1_v0.csv` | `{inputs['split_csv_sha256']}` |
| selection seed | `{kcfg['seed']}` |

Both input hashes were checked before selecting: they equal the values pinned in
`configs/data/kaggle400.yaml`, which are the values recorded in the files' `.meta.json` (2026-10-22).

## 2. Which split is used for what
{USAGE_TABLE}
## 3. Real counts
| | train | val | test | total |
|---|---:|---:|---:|---:|
| clips | {counts['train']} | {counts['val']} | {counts['test']} | {sum(counts.values())} |
| leakage groups (S1 v0) | {groups['train']} | {groups['val']} | {groups['test']} | {sum(groups.values())} |
| minimal-pair held-out clips | — | {roles.get(('val', 'heldout'), 0)} | {roles.get(('test', 'heldout'), 0)} | |
| train siblings / vocabulary-support clips | {roles.get(('train', 'train_sibling'), 0)} / {roles.get(('train', 'vocab_support'), 0)} | — | — | |
| clips also in pilot50_v1 | {pilot.get('train', 0)} | {pilot.get('val', 0)} | {pilot.get('test', 0)} | |

Candidate pool: {report['pool_size']} clips (one representative clip per normalised sentence; S1 v0
train {report['pool_per_s1'].get('train', 0)} / val {report['pool_per_s1'].get('val', 0)} / test {report['pool_per_s1'].get('test', 0)}).
Longest selected clip: {long['index']} ({long['duration_s']:.1f} s ≈ {int(round(long['duration_s'] * 15))} frames at 15 fps).
Total size of the 400 source videos: {sel['bytes'].sum() / 1e9:.2f} GB (from `manifest_v1`).

## 4. How the clips were chosen
1. **Pool**: representative clips only (no exact copies), decodable, no label conflict, assigned to
   train/val/test in S1 v0; one clip per normalised sentence. **Every clip keeps its S1 v0 partition**
   (a train clip of S1 can only be train here, etc.), so group-disjointness is inherited from S1 v0.
2. **Colour cluster** 3456/3457/3458 (one recording edited onto three endings): one unit, all three in
   train (their S1 partition). Val/test sentences of the same minimal-pair family are excluded
   (they may share that footage): {len(report['excluded_heldout_colour_family'])} such sentence(s) exist in the pool{
   (': ' + ', '.join(map(str, report['excluded_heldout_colour_family']))) if report['excluded_heldout_colour_family'] else ''}.
3. **Minimal pairs** ({kcfg['minimal_pair_heldout']['val']} val + {kcfg['minimal_pair_heldout']['test']} test): a held-out
   sentence that differs by exactly one word from a train sentence; the train sibling is added to
   train, plus a "vocabulary support" train clip when a held-out word was still unseen. One held-out
   clip per family. These items measure an **unseen combination of seen words**.
4. **Stratified fill**: val and test, then train, are filled greedily so that each split's shares of
   {', '.join(kcfg['strata'])} stay as close as possible to the pool's shares (ties broken by a seeded hash).
5. Every chosen clip has a written `reason` in the manifests. Re-running the selection gives the same
   400 clips (the PowerShell script checks this on the desktop).

## 5. Distribution per split (count and share; last column = share in the pool)
{tables}

![SPLIT_SUMMARY](SPLIT_SUMMARY.png)

## 6. Out-of-vocabulary rate of val and test against the TRAIN vocabulary
Train vocabulary: **{oov['train_vocabulary_size']}** word types (normalised Bangla words of the 320 train sentences).

| split | word tokens | OOV tokens | OOV token rate | word types | OOV types | sentences with ≥ 1 OOV word | sentences with all words seen |
|---|---:|---:|---:|---:|---:|---:|---:|
{oov_rows}

Minimal pairs on the final selection:

| split | designated minimal-pair clips | clips with a one-word-different sibling in train | designated clips with all words seen in train |
|---|---:|---:|---:|
{mp_rows}

## 7. Leakage tests (at selection time, without videos)
```
{format_results(checks)}
```
Checks 8–10 need the copied videos and the lock; they run on the desktop after copying (section 9).

## 8. Known limits (read before using any number)
{KNOWN_LIMITS}
## 9. Copy verification and full leakage test
(Appended by the copy step on the desktop.)
"""
