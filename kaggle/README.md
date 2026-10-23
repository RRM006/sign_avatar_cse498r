# kaggle/ — the kaggle400 experiment (400 videos, real training on Kaggle)

A self-contained folder for one experiment of the CSE498R project *Bangla Text → BdSL with a 3D avatar*:
**400 videos**, split into **TRAIN / VAL / TEST** folders, trained for real on a Kaggle GPU, with every
metric, figure, prediction and notebook output saved for the paper. Owner approval: chat, 2026-10-23.

> **Status (2026-10-23):** the folder, code, notebooks and tests are ready. The 400 videos are copied and
> the upload package is built on the desktop by `tools/run_local_steps.ps1`. **No Kaggle run has happened
> yet**, so no result exists. `outputs/` stays empty until the notebooks run.

## How the folder is organised

| Folder / file | What it holds | In Git? |
|---|---|---|
| `GUIDE_KAGGLE_STEP_BY_STEP.md` | every click on Kaggle, for a first-time user | yes |
| `requirements_kaggle.txt` | the pinned packages the notebooks install on Kaggle | yes |
| `data/` | `train/ val/ test/` (each `videos/` + `<split>_manifest.csv`), `subset_manifest.csv`, `SPLIT_REPORT.md`, `SPLIT_SUMMARY.png`, `SPLIT_LOCK.json` — see `data/README_DATA.md` | videos **never**; the small files yes (added explicitly) |
| `processed/` | `features/<split>/` (MediaPipe, made on Kaggle), `qc/`, `glosses/` (G0 pseudo-glosses), `vocab/` (TRAIN only) | features **never**; the rest yes |
| `notebooks/` | `00`–`09`, run on Kaggle top to bottom; their outputs are saved inside the `.ipynb` | yes |
| `src/` | `k400/` helper package, `k400_run.py` (commands), `verify_split.py` | yes |
| `tools/` | `run_local_steps.ps1` (desktop steps), `build_notebooks.py`, `commit_message.txt` | yes |
| `outputs/` | `runs/<run_id>/`, `eval/`, `predictions/`, `tables/`, `figures/`, `avatar/`, `registry.csv`, `RESULTS_SUMMARY.md` | small CSV/JSON/PNG/MD yes; checkpoints, `.npz`, videos **never** |
| `work/` | upload zip, logs, scratch | **never** |

## Which split is used for what

| Split | Used for | Never used for |
|---|---|---|
| **TRAIN** (320) | the model learns from it: fitting weights, building vocabularies, feature standardisation (mean/sd), the sources of baselines B0 and B1 | — |
| **VAL** (40) | development: early stopping, choosing epochs / learning rate / ablations, error analysis | fitting weights |
| **TEST** (40) | locked: used **once**, at the very end, after the final configuration is frozen | any decision — no tuning, no model choice |

Enforced in code (`src/bdsl/data/kaggle400.py`, `src/bdsl/eval/kaggle400_eval.py`):
- training commands read only train and val rows; reading test raises `TestSplitLocked`
  (unit test `tests/test_k400_training.py::test_training_commands_never_read_test_rows` records every
  file the training commands open and checks that no test file is among them);
- `python -m bdsl.cli evaluate --final` reads test, needs `outputs/frozen_config.json` (checkpoint hashes),
  writes `outputs/FINAL_TEST_LOCK.json`, and refuses a second run unless the owner gives a written reason
  (`--override-reason "…"`, recorded in the lock);
- training refuses to run if a manifest no longer matches `data/SPLIT_LOCK.json`.

## The pipeline, notebook by notebook

| # | Notebook | What it does | Kaggle accelerator |
|---|---|---|---|
| 00 | `00_env_check_kaggle` | GPU / Python / CUDA / disk; MediaPipe 0.10.35 install + test on a real frame (pinned fallback if needed) | GPU |
| 01 | `01_data_split_check` | SHA-256 of every uploaded file; 10 leakage / file checks; tables and chart per split | none |
| 02 | `02_extract_features` | MediaPipe Holistic features (VIDEO mode, 15 fps, `feat_layout_v1`), per split, QC, resume-safe | none (CPU) |
| 03 | `03_gloss_g0` | G0 **pseudo**-glosses for all 400 (auto_draft, NOT BdSL annotation); TRAIN-only vocabularies | none |
| 04 | `04_train_model_b` | Model B gloss → motion, 3 seeds (42/43/44), early stopping on VAL; dry run + resume test | GPU |
| 05 | `05_train_ablation_text` | the same model with Bangla words as input (ablation T) | GPU |
| 06 | `06_train_model_a` | text → gloss on G0 references = **agreement with the rule glosser**, not BdSL correctness | GPU |
| 07 | `07_baselines_eval` | freeze; B0 / B1 / Model B / ablation / Model A on VAL with bootstrap CIs; **then ONCE on TEST** | none or GPU |
| 08 | `08_report_figures` | paper tables (CSV + Markdown + LaTeX), figures (PNG), `outputs/RESULTS_SUMMARY.md` | none |
| 09 | `09_avatar_export` | motion JSON + skeleton videos for 5 TEST sentences (only after the test lock) | none |

Each notebook starts with: purpose, Kaggle settings, inputs, outputs, expected run time, what to check,
and ends with a PASS/FAIL list. Notebook *N* takes the Output of notebook *N−1* as an extra Input, so the
results accumulate in `/kaggle/working/k400/` (= this folder's `processed/` + `outputs/`).

## Commands (all real steps are commands; notebooks only call them)

```text
# desktop (PowerShell, project root) — normally via tools\run_local_steps.ps1
uv run python kaggle/src/k400_run.py select [--check]     # choose the 400 clips (deterministic, seed 20261023)
uv run python kaggle/src/k400_run.py copy-videos --confirm
uv run python kaggle/src/verify_split.py --require-videos # anyone can re-check the split
uv run python kaggle/src/k400_run.py package              # private-dataset zip from a clean commit
# Kaggle notebooks
python kaggle/src/k400_run.py env-report | mp-setup | extract | gloss | report | avatar | verify-upload
python -m bdsl.cli train-gloss2motion --data kaggle400 [--input text] [--max-steps 1] [--set key=value]
python -m bdsl.cli train-text2gloss  --data kaggle400 --reference g0
python -m bdsl.cli list-runs | freeze | evaluate --split val | evaluate --final
```

Options added for kaggle400 (owner-approved): `--device cuda|cpu|auto` (default from the config: CUDA on
Kaggle, with a recorded CPU fallback), `--max-steps N` (dry run, never a result), `--stop-after-epochs N`
and `--resume <run>`, `--set key=value` (recorded in `run.json`), `--not-for-paper`.

## What every run saves (for the paper)
`outputs/runs/<run_id>/`: `run.json` (inputs, hashes, config, device, seeds, split-lock hash, code commit),
`env.json` (all installed packages, Python, GPU, CUDA, cuDNN, code provenance), `train.log`,
`seed<N>/curves.csv` (train and VAL loss per epoch, seconds per epoch), `metrics.json`, `per_item.csv`,
checkpoints `ckpt_last.pt` / `ckpt_best.pt` (gitignored). One line per run in `outputs/registry.csv`.

**Clean code rule.** A result run must come from committed code: locally a clean Git tree, on Kaggle the
`code/` folder of the upload (a `git archive` of a clean commit, every file hashed in `CODE_VERSION.json`).
Otherwise the run is refused, or — only with `--not-for-paper` — named `NFP_…` and never frozen.

## Honesty rules (they protect the paper)
- Every number is labelled **measured** or **estimated** (`outputs/RESULTS_SUMMARY.md` lists each with its
  run ID and source file). Time estimates in the notebooks are marked [ESTIMATE].
- 320 / 40 / 40 clips, unknown signers: **small-scale, signer-dependent**.
- The test split is evaluated **once**, after freezing. No tuning on test.
- **Low coordinate error is not proof of correct sign language.**
- G0 glosses are pseudo-glosses; Model A results are "agreement with the rule glosser (G0 pseudo-gloss)".
- If Model B does not beat a baseline, the tables say so. Nothing is hidden.
- No human or expert validation exists; none is claimed.

## Local extraction (backup only)
If MediaPipe cannot run on Kaggle at all, features can be made on the desktop instead:
`uv run python kaggle/src/k400_run.py extract --model work/models/holistic_landmarker.task`
(writes `kaggle/processed/features/`; about 20–30 minutes [ESTIMATE from the pilot rate]). They would then
be uploaded as a new version of the private dataset — ask before doing this; it is not the main route.

## Data permissions
The 400 videos go only to the owner's **private** Kaggle dataset, team collaborators only, for this
experiment only (owner, 2026-10-23; ADR-0017 otherwise unchanged). Never make the dataset public, never put
`kaggle.json` (API token) in the repository, never push this repository without the owner's decision.
