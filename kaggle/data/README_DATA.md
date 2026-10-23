# kaggle/data — the 400 videos of the kaggle400 experiment

**This folder is gitignored** (videos never go to Git; the repository is public). The small files
(manifests, reports, lock) are added to Git explicitly by `kaggle/tools/run_local_steps.ps1`.

| Folder / file | What it is | Rule |
|---|---|---|
| `train/videos/` (320 clips) + `train/train_manifest.csv` | TRAIN: the models learn from these | may be used for fitting, vocabularies, standardisation, B0/B1 sources |
| `val/videos/` (40 clips) + `val/val_manifest.csv` | VAL: development set | early stopping, choosing settings, error analysis |
| `test/videos/` (40 clips) + `test/test_manifest.csv` | TEST: locked | read **once**, by `evaluate --final`, after freezing the configuration |
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
