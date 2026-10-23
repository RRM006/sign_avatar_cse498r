# kaggle/processed — derived data (made by notebooks 02 and 03)

| Folder | Made by | Contents | In Git? |
|---|---|---|---|
| `features/{train,val,test}/` | notebook 02 (Kaggle CPU) | one MediaPipe Holistic `.npz` per clip (`feat_layout_v1`, VIDEO mode, 15 fps; no raw face mesh, no image) + `feature_meta.json` | **no** (gitignored) |
| `qc/` | notebook 02 | `qc.csv` (per clip: coverage, gaps, jitter, rotation check, privacy check), `failures.csv`, `hand_coverage_summary.csv` (per split), `extract_run.json` (time, platform, versions) | yes (small) |
| `glosses/` | notebook 03 (also made on the desktop, committed for comparison) | `gloss_g0_<split>.csv`: G0 v0.1 **pseudo-glosses**, status `auto_draft`, NOT BdSL annotation; `g0_corpus_v1.txt`: the 1,398 sheet words the G0 genitive rule needs | yes |
| `vocab/` | notebook 03 | vocabularies built from **TRAIN only** (Model B gloss/text input, Model A source/target) + `vocab_report.json` (VAL out-of-vocabulary rates) | yes |

On Kaggle these folders live in `/kaggle/working/k400/processed/` and are carried from notebook to notebook
through "Add Input" (see `../GUIDE_KAGGLE_STEP_BY_STEP.md`, step 5).
