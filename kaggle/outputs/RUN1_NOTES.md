# kaggle400 — run 1 (2026-10-23): what was run, what is here, what to watch out for

Written by hand (not generated). The generated summary of every number is `RESULTS_SUMMARY.md`; the full
record of each step is `agent_docs/test_log.md` (2026-10-23 entries). All numbers below are **measured**
on the kaggle400 subset (320 train / 40 val / 40 test clips): small-scale and signer-dependent.

## Provenance
- Code: commit `933e9032ac3a…` (local, not pushed), uploaded as `code/` in the PRIVATE Kaggle dataset
  `bdsl-k400` Version 1 (535 files, 5.94 GB; upload check 532/532 identical, notebook 01). Every run records
  this commit with `dirty: false`.
- Platform: Kaggle, Python 3.13.15, PyTorch 2.11.0+cu128, GPU 2 × Tesla T4 (training used `cuda:0` only),
  MediaPipe 0.10.35 via the normal pip route (features `feat_ver fa89892d4908` = the pilot's).
- Notebooks (Save & Run All): 00 env check, 01 upload + split check (10/10), 02 extraction (400/400, 0
  failures, 56.8 min), 03 G0 glosses (identical to the committed copies), 04 Model B gloss, 05 ablation T
  (Bangla words), 06 Model A on G0 references, **07 Version 2** (freeze + VAL + the final TEST), 08 report,
  09 avatar export. A helper notebook `10_pack_outputs` only zipped the output of 09 for download.
- Frozen runs: `gloss2motion_gloss_kaggle400_20261023T135437Z` (Model B, G0 gloss input),
  `gloss2motion_text_kaggle400_20261023T141059Z` (Model B, Bangla word input),
  `G0REF_text2gloss_kaggle400_20261023T142908Z` (Model A). Test lock: `FINAL_TEST_LOCK.json`
  (created 20261023T151119Z, no override, empty history).

## The failed first attempt of notebook 07 (must be reported)
Version 1 of notebook 07 had no Internet, so `sacrebleu` could not be installed. The notebook did not stop:
it froze the same three runs, then the VAL and the final TEST evaluation crashed at the first BLEU/chrF
call. A code check showed that by then the test split had been read and the motion errors computed **in
memory**, but nothing was printed or saved and no lock was written: **no test result existed and nobody saw
one.** The owner decided (chat, 2026-10-23) to run notebook 07 once more with the same frozen runs, report
this openly, and add a safety stop (cell 2 of notebook 07 now stops before the freeze and before any test
access if `sacrebleu` is missing). Version 2 produced the only test results.

## Main TEST results (40 clips; tables T4–T6; 95% bootstrap CIs over items)
- Model B (G0 gloss input) vs B0 (average motion) and B1 (retrieval of a real clip): lower position error on
  every body and hand metric, CIs exclude 0. Example, DTW-MJE body: Model B 0.181, B0 0.199, B1 0.198
  shoulder widths; difference to B0 −0.017 [−0.025, −0.009].
- G0 gloss input vs plain Bangla word input: no difference in position error (e.g. DTW-MJE body −0.000
  [−0.005, +0.005]); the word input has slightly lower duration error (0.26 s [0.01, 0.51]).
- **Limitation that must be reported with these numbers:** Model B's motion is strongly damped — velocity
  ratio 0.14 (gloss) / 0.18 (words) of the real recording, hand-energy ratio 0.03 / 0.05, diversity 0.43 /
  0.50 (B1: 1.13, 1.61, 1.00). The learning curves (F2, F3) show strong over-fitting: train error keeps
  falling while val error stops improving early. Low coordinate error is **not** proof of correct BdSL;
  no human or expert evaluation exists.
- Model A: test WER vs G0 19.7 (val 34.5), exact match 54.2% — this is **agreement with the rule glosser
  (G0 pseudo-gloss), not BdSL correctness**.

## What is in this folder, and what is not
- Here: tables (T1–T8 as CSV/MD/LaTeX, `RESULTS_LEDGER.csv`, per-item tables), figures F1–F6, the evaluation
  folders, run summaries (`run.json`, `env.json`, `train.log`, `metrics.json`, `per_item.csv`, curves),
  `registry.csv`, `frozen_config.json`, `FINAL_TEST_LOCK.json`, `RESULTS_SUMMARY.md`, Model B's avatar motion
  (`motion_modelB.json`) with `info.json` / `demo_log.json` / `LIMITATIONS.md`, and `OUTPUT_HASHES_run1.csv`
  (SHA-256 of all 2,448 output files on Kaggle). Extraction QC: `kaggle/processed/qc/`.
- Kept only on the desktop (`kaggle/work/downloads/run1/`, gitignored): checkpoints (`.pt`), features and
  predicted motion (`.npz`), skeleton videos (`.mp4`), and `motion_real.json` / `motion_B1.json` — body
  landmarks derived from real people's recordings, which never go into the public repository (ADR-0017).
  `env/mediapipe_route.json` is also kept out of Git (it contains the owner's Kaggle username; owner's
  choice, 2026-10-23).
- Download check: 2,447 / 2,448 files matched `OUTPUT_HASHES.csv`; the one "mismatch", `STATE.json`, is
  explained and harmless (the code appends a "finished" line after hashing; removing it reproduces the
  listed hash exactly).

## Known issues found during run 1 (fix later; each needs a new commit and package — open question G18)
Silent progress log until a step ends; a failed `pip install` did not stop a notebook (fixed for notebook 07
only); the test lock is written only after success; skeleton videos use MPEG-4 Part 2 (`mp4v`), which
browsers cannot play (desktop players can); the `STATE.json` hash order; notebook 01 shows the selection-time
report section next to the live check.
