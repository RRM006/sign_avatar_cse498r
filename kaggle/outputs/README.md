# kaggle/outputs — results of kaggle400 run 1 (2026-10-23)

**Read `RUN1_NOTES.md` first** (provenance, the failed first attempt of notebook 07, main results, limits).
Only small files are kept here; checkpoints, features, `.npz` motion, videos, `motion_real.json` /
`motion_B1.json` (derived from real people's recordings) and `env/mediapipe_route.json` stay on the desktop
in `kaggle/work/downloads/run1/` (gitignored). `OUTPUT_HASHES_run1.csv` lists the SHA-256 of all 2,448 output
files of the run.

| Path | Written by | Contents |
|---|---|---|
| `runs/<run_id>/` | notebooks 04–06 | `run.json`, `env.json`, `train.log`, `metrics.json` (train + VAL), `per_item.csv`, `seed<N>/curves.csv`, checkpoints `seed<N>/ckpt_*.pt` (**gitignored**) |
| `registry.csv` | every training run | one line per run: run ID, model, seeds, status, for_paper, device, GPU, split-lock hash, feature version, gloss hash, code commit, dirty flag, times |
| `frozen_config.json` | notebook 07 | the runs and checkpoint SHA-256 frozen before the test |
| `eval/val_<time>/`, `eval/FINAL_test_<time>/` | notebook 07 | `metrics.json` (mean ± sd over seeds, bootstrap 95% CIs, paired differences), per-item tables, `error_analysis.csv` |
| `FINAL_TEST_LOCK.json` | notebook 07 | proof that the test split was used once (and any owner override) |
| `predictions/` | notebook 07 | per-item predictions for VAL and TEST (CSV); motion `.npz` (**gitignored**) |
| `tables/` | notebook 08 | T1–T8 as `.csv`, `.md`, `.tex`; `RESULTS_LEDGER.csv` |
| `figures/` | notebook 08 | F1–F6 as `.png` |
| `avatar/` | notebook 09 | motion JSON for the browser viewer, skeleton videos (**videos gitignored**) |
| `RESULTS_SUMMARY.md` | notebook 08 | every number with its run ID, source file and label (measured / estimated) |
| `env/` | notebooks 00, 02 | `env_report.json` (GPU, Python, CUDA, disk, packages), `mediapipe_route.json` |

Run-name prefixes: `DRYRUN_` (one-step dry run), `NFP_` (not for paper: engineering checks or uncommitted
code), `G0REF_` (Model A on G0 references). Only runs without `DRYRUN_`/`NFP_` and without `overfit` can be frozen.
