# test_log.md — What Was Tested + Results

> Records what we tested or verified, how, and the result, including failures. This makes progress
> verifiable.
>
> Template for each entry:
> ```
> ## YYYY-MM-DD — <area/module> — <what was tested>
> - Setup: <how it was tested; tools/versions; environment; data used>
> - Metric(s) / checks: <what was measured or verified>
> - Result: <the numbers / pass-fail / observations>
> - Notes: <what helped or hurt; errors; next idea>
> ```

---

## What we care about (per area)
Evaluation protocol: ADR-0020 (metric set accepted in principle). Pilot results are "pipeline tests";
reported numbers need the S1 test set, 3 seeds and confidence intervals.

## Planned test cases
Acceptance tests per step are listed in `milestone_log.md` (milestones 5–10) and `current_task.md`.
Results are logged here only after they are actually run.

---

## 2026-10-23 — kaggle400 run-1 small results copied into the project + privacy scan (measured)
- robocopy `…/run1/k400/outputs` → `kaggle/outputs` excluding `*.pt *.npz *.mp4 motion_real.json motion_B1.json`:
  2,031 files seen, **144 copied (4.25 MB)**, 1,887 skipped, 0 failed (6 "extras" = existing README/.gitkeep);
  `…/processed/qc` → `kaggle/processed/qc`: 4 files (139.8 kB); `OUTPUT_HASHES.csv` → `OUTPUT_HASHES_run1.csv`.
- AI check of every copied file (listing + content scan of all 141 text files in the workspace): no `.pt`,
  `.npz`, `.mp4`, `motion_real.json` or `motion_B1.json`; largest file 0.35 MB. Personal markers: only
  `kaggle/outputs/env/mediapipe_route.json` contains the owner's Kaggle username (one path) → kept out of
  Git (owner). No e-mail, Windows user path, PC name, API key or password; "token" hits are package names
  (`tokenizers`, `tiktoken`); `registry.csv` has generic `/kaggle/working/k400/...` paths only.
- Added by hand: `kaggle/outputs/RUN1_NOTES.md` (provenance, failed first attempt of 07, main results,
  limitations, what is and is not in Git); `kaggle/outputs/README.md` header updated.

## 2026-10-23 — kaggle400 outputs downloaded to the desktop and checked (measured)
- Download: Kaggle offers no "download all outputs" button (only Kaggle CLI with an API key, or the .ipynb).
  A helper notebook `10_pack_outputs` (input = output of 09; copies files into one zip, computes nothing)
  packed `/kaggle/input/notebooks/<owner>/09-avatar-export/k400`: **2,449 files, 874.6 MB**
  (`k400_outputs_run1.zip`). The owner downloaded it and extracted it to
  `kaggle/work/downloads/run1/k400/` (gitignored).
- `k400_run.py verify-download`: **2,447/2,448 files match `OUTPUT_HASHES.csv`**, MISMATCH `STATE.json` →
  "DOWNLOAD CHECK: FAIL". Cause (code + file check in the workspace): `Setup.finish()` writes
  `OUTPUT_HASHES.csv` and then appends a "finished" entry to `STATE.json`. Removing only that last entry
  ("09_avatar_export finished", 15:33:49 UTC) and writing the JSON the same way reproduces the listed hash
  exactly (`759f3cbf…`, 2,869 bytes). → **All 2,448 files arrived byte-identical**; the check fails by design
  flaw for STATE.json in every run (G18 item 8).
- Owner: the files are there and the skeleton videos play on the desktop. (The AI could not fetch the videos:
  8 folders deep, the desktop link allows 7.)
- AI check of the report files (read in the workspace): FINAL_TEST_LOCK created 20261023T151119Z, results
  `FINAL_test_20261023T151119Z`, override none, history empty, code = package `933e903…`, dirty False;
  frozen runs = the three runs of notebooks 04/05/06, for_paper true. Figures F2, F4, F5 (test), F6 (test)
  viewed: rendered correctly, labels and CIs present.
- TEST numbers not printed by notebook 07 (from T4_modelB_test, mean ± sd over 3 seeds [95% CI]): Model B
  gloss velocity ratio **0.14** [0.12, 0.16], jerk ratio 0.11, **hand-energy ratio 0.03** [0.02, 0.05],
  diversity 0.43; Model B text velocity 0.18 [0.16, 0.21], jerk 0.15, hand energy 0.05 [0.04, 0.06],
  diversity 0.50; B0 velocity 0.11, hand energy 0.02, diversity 0.00; B1 velocity 1.13, hand energy 1.61,
  diversity 1.00. Duration error (s): gloss 1.92, text 1.66, B0 2.05, B1 1.97.
- T5 paired (test): Model B (gloss and text) lower than B0 and than B1 on every MPJPE and DTW-MJE metric
  (body, left hand, right hand; CIs exclude 0; e.g. gloss − B0 MPJPE body −0.013 [−0.019, −0.006]);
  duration error vs B0/B1 not distinguishable; gloss − text: no position/DTW difference, duration error
  gloss higher by 0.26 s [0.01, 0.51].
- T3: Model A best epochs 62 / 92 / 57 (seeds 42 / 43 / 44), val WER at best 31.4 / 32.0 / 31.4.
  F2 (Model B gloss): train position L1 falls 0.70 → 0.33 while val L1 stays ≈ 0.63–0.66 after
  ~15–40 epochs → strong over-fitting; little generalisation beyond an average pose per sentence.
- Hand coverage (MediaPipe detections, all 400 clips): left 63.3%, right 25.3% of frames (RESULTS_SUMMARY).

## 2026-10-23 — kaggle400 Step D, notebook 09 (avatar export, 5 TEST sentences) on Kaggle — PASS, videos not browser-playable
- Setup: `09_avatar_export` (Save & Run All), inputs = dataset `bdsl-k400` + output of `08_report_figures`
  ("carried over: 2413 files"), Accelerator None, Internet On; reported by the owner 21:43 UTC+6.
- Exported (index → B1 source clip): 1255 → 787 ("তুমি কি সি পি কিভাবে"), 2513 → 2492, 1863 → 1663, 3061 → 3062,
  3232 → 3098; each folder has motion_modelB/B1/real.json, demo_log.json, info.json, LIMITATIONS.md and
  `skeleton_modelB_B1_real.mp4` (about 1.6 MB). Nothing re-scored.
- Output: 2,448 files (873.7 MB) with `OUTPUT_HASHES.csv`. Final list: PASS avatar export done · PASS 5 skeleton
  videos → **NOTEBOOK RESULT: PASS**.
- Problem (owner): the skeleton video does not play in Kaggle's browser player (stays at 0:00). Cause
  (workspace check): `src/bdsl/avatar/export.py` writes with OpenCV fourcc `mp4v` = MPEG-4 Part 2 (smoke-test
  file: codec mpeg4, 1440 × 570, 15 fps, 180 frames), which browsers do not decode. The files are expected to
  play in a desktop player (e.g. VLC) — to be checked after download → G18 item (7).
- **Step D complete: notebooks 00–09 all PASS** (07 on its second attempt, see below).

## 2026-10-23 — kaggle400 Step D, notebook 08 (tables, figures, RESULTS_SUMMARY.md) on Kaggle — PASS (measured)
- Setup: `08_report_figures` (Save & Run All), inputs = dataset `bdsl-k400` + output of `07_baselines_eval`
  Version 2 ("carried over: 2363 files"), Accelerator None; reported by the owner 21:27 UTC+6.
- `k400_run.py report`: tables T1_split, T2_feature_coverage, T3_training, T8_train_val_test,
  T4_modelB_{val,test}, T5_paired_{val,test}, T6_modelA_{val,test}, T7_error_analysis_{val,test} (12);
  figures F1_split_summary, F2_curves_modelB_gloss, F3_curves_modelB_text, F4_curves_modelA,
  F5_methods_{val,test}, F6_error_analysis_{val,test} (8); **missing: none**; **185 numbers** in the results
  ledger; `final_test_done: true`.
- Output: 2,412 files (863.1 MB) with `OUTPUT_HASHES.csv`. Final list: PASS report built · PASS final test
  results present → **NOTEBOOK RESULT: PASS**.
- Not yet checked: the tables' contents (incl. TEST velocity/diversity) and the figures by eye — after the
  outputs are downloaded to the desktop. `RESULTS_SUMMARY.md` is generated from saved files and does not
  mention the crashed Version 1 of notebook 07; that note must be added in the write-up.

## 2026-10-23 — kaggle400 Step D, notebook 07 Version 2 (freeze + VAL + the final TEST) — PASS (measured)
- Setup: `07_baselines_eval` Version 2 ("run 2", Save & Run All) with the updated notebook (cell 2 safety stop),
  inputs = dataset `bdsl-k400` + output of `06_train_model_a`, Accelerator None (evaluation on CPU), Internet
  On; reported by the owner 21:15 UTC+6. This is the second attempt; Version 1 crashed before producing any
  result (entry below) — to be reported openly (owner decision, option a).
- `pip install sacrebleu==2.6.0`: exit 0 → "sacrebleu OK". `list-runs` → `freeze`: the same three runs as in
  Version 1 — model_b_gloss `gloss2motion_gloss_kaggle400_20261023T135437Z`, model_b_text
  `gloss2motion_text_kaggle400_20261023T141059Z`, model_a `G0REF_text2gloss_kaggle400_20261023T142908Z`;
  for_paper true; split lock sha256 `529d82c2…`. `evaluate --split val`: done (output not copied here).
- `evaluate --final` (test split, read for the first time to produce a result): results
  `outputs/eval/FINAL_test_20261023T151119Z/`; **`FINAL_TEST_LOCK.json` written** (created 20261023T151119Z).
- **TEST results** (40 clips; measured; small-scale, signer-dependent; body in shoulder widths, hands in mm;
  Model B = mean over seeds 42/43/44):
  | method | MPJPE body | DTW body | MPJPE left hand | MPJPE right hand |
  |---|---|---|---|---|
  | Model B, G0 gloss input | 0.199 | 0.181 | 49.5 | 57.3 |
  | Model B, Bangla word input (ablation T) | 0.198 | 0.181 | 48.5 | 56.5 |
  | B0 mean motion | 0.212 | 0.199 | 53.3 | 63.2 |
  | B1 retrieval | 0.249 | 0.198 | 61.6 | 64.9 |
  (unrounded body MPJPE: gloss 0.19944, text 0.19817, B0 0.21237, B1 0.24880)
- Paired differences, DTW body, bootstrap 95% CI over test items (1,000 resamples): gloss − B0 **−0.017
  [−0.025, −0.009]** (excludes 0); gloss − B1 **−0.017 [−0.032, −0.004]** (excludes 0); text − B0 **−0.017
  [−0.025, −0.009]** (excludes 0); gloss − text **−0.000 [−0.005, +0.005]** (does not exclude 0).
- Model A on TEST (agreement with the rule glosser, G0 pseudo-gloss — not BdSL correctness), mean of 3 seeds:
  WER **19.7** (sd 1.0), exact match 54.2%, tag accuracy 94.2%, BLEU 68.7, chrF 76.8. (Test OOV 12.1% vs
  val 20.7% of word tokens — notebook 03 / SPLIT_REPORT.)
- Reading (AI, evidence only): on these 40 test clips both Model B variants have a small but CI-supported
  lower DTW body error than B0 and B1 (≈ 8% vs B0); gloss input and word input do not differ. Velocity and
  diversity on TEST are not in this printout (notebook 08 tables); on VAL Model B moved at 13–18% of real
  speed, which must be reported next to the error numbers. Low coordinate error is not proof of correct BdSL.
- Output: 2,362 files (861.8 MB) with `OUTPUT_HASHES.csv`. Final list: PASS configuration frozen before the
  test · PASS VAL evaluation done · PASS final TEST evaluation done once, lock written → **NOTEBOOK RESULT: PASS**.
- Never re-run notebook 07 (G15).

## 2026-10-23 — kaggle400 Step D, notebook 07 Version 1 (freeze + VAL + final TEST) — ERROR, no result produced
- Setup: `07_baselines_eval` Version 1 (Save & Run All), inputs = dataset `bdsl-k400` + output of
  `06_train_model_a` ("carried over: 1949 files"), Accelerator None; full log from the owner, 20:52 UTC+6.
- `pip install sacrebleu==2.6.0` failed: 5 retries, "Failed to resolve 'pypi.org' (Temporary failure in name
  resolution)" → no Internet in this version (cause of the missing Internet not yet confirmed). The notebook did
  not stop there (the pip exit code was not checked — design flaw, G18 item 5).
- `list-runs` + `freeze`: OK. Frozen (for_paper true; split lock sha256 `529d82c2…`): model_b_gloss
  `gloss2motion_gloss_kaggle400_20261023T135437Z` (notebook 04), model_b_text
  `gloss2motion_text_kaggle400_20261023T141059Z` (05), model_a `G0REF_text2gloss_kaggle400_20261023T142908Z` (06).
  No NFP_, DRYRUN_ or overfit run was frozen.
- `evaluate --split val`: crashed in `evaluate_text` (`ModuleNotFoundError: sacrebleu`); nothing written.
- `evaluate --final`: crashed at the same place. **Code check (workspace, `kaggle400_eval.evaluate`):** inside
  the test-access block the code had already loaded the test split and computed the Model B / B0 / B1 test
  errors in memory (`evaluate_motion`) and Model A test outputs, then crashed at the first BLEU/chrF call.
  Nothing is printed or written before that point: **no test number was produced, saved or seen**, and
  `FINAL_TEST_LOCK.json` was not written. The next cell failed with FileNotFoundError (no lock) → version Error.
- Owner decision (chat, 20:57 UTC+6): option (a) — run notebook 07 once more with the same frozen runs and
  report this failed first attempt openly (test log and paper). Safety stop added before the re-run: cell 2 of
  `kaggle/notebooks/07_baselines_eval.ipynb` (and `kaggle/tools/build_notebooks.py`) now asserts that
  `sacrebleu` is installed and importable before the freeze and before any test access; new test
  `test_notebook_07_stops_before_freeze_and_test_when_sacrebleu_is_missing`; workspace suite **210 passed**.
  The uploaded `code/` (commit `933e903`) is unchanged, so the runs keep their clean-code status.

## 2026-10-23 — kaggle400 Step D, notebook 06 (Model A on G0 references) on Kaggle — PASS (measured)
- Label (printed by the run): "agreement with the rule glosser (G0 pseudo-gloss); references are G0 auto_draft
  outputs, not BdSL annotation; says nothing about BdSL correctness".
- Setup: notebook `06_train_model_a` Version 1 (Save & Run All, GPU T4 x2; `cuda:0`), inputs = dataset
  `bdsl-k400` + output of `05_train_ablation_text`, Internet On (sacrebleu 2.6.0); reported by the owner
  20:37 UTC+6. A-GRU 2,082,968 parameters; vocab src 420 / tgt 408; train 320 / val 40.
- Dry run (`DRYRUN_G0REF_…`): 1 step per seed on `cuda:0`, train loss 6.043 / 6.038 / 6.136, finite.
- Overfit checks (engineering, never results): 1 sentence → WER 0.0, exact 100% at epoch 2; 40 sentences →
  WER 0.0, exact 100% at epoch 13 (tags 100%, BLEU 100, chrF 100). The code can learn.
- Real run (for the paper, clean code; 3 seeds, early stopping on VAL WER vs G0), mean of 3 seeds:
  train WER 0.0, exact 99.9%, tags 100%, BLEU 100.0, chrF 100.0; **val WER 34.5%, exact match 30.0%,
  tag accuracy 97.5%, BLEU 47.0, chrF 60.6**. (Per-seed best epochs not copied into this log.)
- Reading (AI, evidence only): the train/val gap fits the vocabulary limit — 20.7% of val word tokens are
  unseen in train and become `<unk>` (notebook 03). These scores measure agreement with the G0 rule only.
- Output: 1,948 files (824.4 MB) with `OUTPUT_HASHES.csv`. Final list: PASS 3 seeds finished · PASS marked
  for the paper · PASS labelled as agreement with G0, not BdSL → **NOTEBOOK RESULT: PASS**.

## 2026-10-23 — kaggle400 Step D, notebook 05 (ablation T, Bangla words → motion) on Kaggle — PASS (measured)
- Setup: notebook `05_train_ablation_text` Version 1 (Save & Run All, GPU T4 x2; `cuda:0`), inputs = dataset
  `bdsl-k400` + output of `04_train_model_b`; reported by the owner 20:21 UTC+6. Same model and settings as
  notebook 04, input = normalised Bangla words (vocab 420; 2,724,881 parameters).
- Dry run (`DRYRUN_…`): 1 step per seed on `cuda:0`, train loss 1.589 / 1.484 / 1.508, val pos L1 0.816 /
  0.822 / 0.819; all finite.
- Real run (for the paper, clean code): seeds 42 / 43 / 44 → best epoch **66 / 34 / 38**, epochs run 126 / 94 / 98,
  training time 130.5 / 96.9 / 101.3 s.
- Measured on **VAL** (40 clips; no CIs here): Model B (text, mean of 3 seeds) MPJPE body **0.216**, left hand
  **52.4 mm**, right hand **62.3 mm**, velocity ratio **0.177**, diversity ratio **0.464** (B0 and B1 as in
  notebook 04: 0.229 / 56.8 / 63.4 and 0.265 / 66.2 / 67.4). Train: 0.168 / 34.8 / 39.6 mm, velocity 0.173,
  diversity 0.554.
- Reading (AI, evidence only): on VAL, word input ≈ G0-gloss input (notebook 04: 0.218 / 52.1 / 61.6 mm) in
  position error, with somewhat more motion (velocity 0.18 vs 0.13); G0 glosses show no measurable advantage
  here. The TEST comparison with 95% CIs and paired differences comes from notebook 07.
- Output: 1,915 files (670.6 MB) with `OUTPUT_HASHES.csv`. Final list: PASS dry run on cuda · PASS loss
  finite · PASS 3 seeds finished · PASS marked for the paper → **NOTEBOOK RESULT: PASS**.

## 2026-10-23 — kaggle400 Step D, notebook 04 (Model B, G0 gloss → motion) on Kaggle — PASS (measured)
- Setup: notebook `04_train_model_b` Version 1 (Save & Run All, GPU T4 x2; training on `cuda:0`), inputs =
  dataset `bdsl-k400` + output of `03_gloss_g0`; Python 3.13.15; reported by the owner 20:04 UTC+6.
  Model B 2,722,577 parameters, vocab 408, train 320 / val 40 clips; config = ADR-0026 + `max_frames` 360
  (proposed ADR-0028).
- Dry run (`DRYRUN_…`, never a result): 1 optimiser step per seed on `cuda:0`; train loss 1.588 / 1.462 /
  1.548, val pos L1 0.834 / 0.809 / 0.826 (seeds 42 / 43 / 44); all finite.
- Resume test (`NFP_…`, not for the paper; seed 42, 4 epochs straight vs 2 + resume 2): identical epoch-4 losses
  (train 0.8315, val pos L1 0.6855) and **max |weight difference| 0.0** on the GPU.
- Real run (for the paper, clean code `933e903`): seeds 42 / 43 / 44 → best epoch **38 / 27 / 18**, epochs run
  98 / 87 / 78 (early stopping on VAL masked position L1, patience 60), training time 98.7 / 87.3 / 77.9 s.
- Measured on **VAL** (40 clips; model checking only, not the paper's test result; no CIs here):
  Model B (mean of 3 seeds) MPJPE body **0.218** shoulder widths, left hand **52.1 mm**, right hand **61.6 mm**,
  velocity ratio **0.130**, diversity ratio **0.376**; B0 (mean motion) 0.229 / 56.8 / 63.4 mm, velocity 0.105,
  diversity 0.000; B1 (retrieval) 0.265 / 66.2 / 67.4 mm, velocity 0.981, diversity 0.941.
  Train (same metrics): Model B 0.187 / 42.3 / 47.7 mm, velocity 0.125, diversity 0.443; B0 0.218 / 53.7 / 62.5;
  B1 0.257 / 61.7 / 67.7.
- Reading (AI, evidence only): on val Model B has slightly lower position error than B0 and B1, but its motion
  is strongly damped (13% of the real velocity; diversity 0.38) — the same pattern as the pilot (G11). Whether
  the difference to B0 holds on TEST, with 95% CIs, is decided in notebook 07.
- Output: 1,536 files (470.3 MB) with `OUTPUT_HASHES.csv`. Final list: PASS dry run on cuda · PASS dry-run loss
  finite · PASS 3 seeds finished · PASS marked for the paper (clean code) · PASS resume reproduces the weights →
  **NOTEBOOK RESULT: PASS**.

## 2026-10-23 — kaggle400 Step D, notebook 03 (G0 pseudo-glosses + vocabularies) on Kaggle — PASS (measured)
- Setup: notebook `03_gloss_g0` (Save & Run All), inputs = dataset `bdsl-k400` + output of `02_extract_features`
  Version 1 ("carried over: 410 files from earlier notebooks (1 attached output)"), Accelerator None,
  Python 3.13.15; reported by the owner 19:45 UTC+6.
- G0 v0.1 drafts (rule-based pseudo-glosses, status auto_draft — NOT BdSL annotation): train 320 rows
  (tokens per rule R0 267, R1 20, R2 9, R2b 9, R3 5, R4 2, R5 26, R6 1,026), val 40 (R0 36, R1 2, R2b 2,
  R3 1, R5 1, R6 127), test 40 (R0 38, R1 2, R2 1, R2b 2, R5 5, R6 125); all `auto_draft`.
- `compare_with_committed`: **IDENTICAL** for train, val and test. Canonical SHA-256 on Kaggle = the committed
  desktop files (checked in the workspace): train `aa36b9a4…`, val `a77cf8bd…`, test `9960a5b8…`.
- Vocabularies (TRAIN only; = the committed `vocab_report.json`): Model B gloss input / Model A target G0
  408 types, val OOV 34/173 tokens = **19.65%**; Model B text input / Model A source 420 types, val OOV
  35/169 = **20.71%**.
- Output: 418 files (65.7 MB) with `OUTPUT_HASHES.csv`. Final list: PASS G0 files identical · PASS
  320 + 40 + 40 rows, all auto_draft → **NOTEBOOK RESULT: PASS**.

## 2026-10-23 — kaggle400 Step D, notebook 02 (MediaPipe extraction) on Kaggle — PASS (measured)
- Setup: notebook `02_extract_features` Version 1 (Save & Run All, started 18:18 UTC+6), input = dataset
  `bdsl-k400` only, Accelerator None (CPU), Internet On; Python 3.13.15; MediaPipe 0.10.35 via the main
  route into `/usr/bin/python3` (numpy 2.1.3, cv2 5.0.0); model SHA-256 `e2dab611…50c3f8` OK; 4 worker
  processes; time budget 300 min. Log reported by the owner 19:30 UTC+6. (An extra interactive draft run of the
  same notebook was also started by mistake and stopped; it is not used.)
- Result: **400/400 clips with features** (train 320/320, val 40/40, test 40/40); failures or missing **0**;
  privacy OK True; rotation OK True; max |frames − duration × 15| = 1; **feat_ver `fa89892d4908`** (= the
  pilot's VIDEO-mode features: same MediaPipe, model and settings).
- Time: 400 clips in **3,408.1 s (56.8 min)**, 8.5 s per clip with 4 workers on Kaggle CPU; not stopped by the
  time budget. 2,812 MediaPipe/TFLite log lines hidden by the filter.
- Output: 409 files (65.5 MB) under `/kaggle/working/k400` with `OUTPUT_HASHES.csv`.
- Final list: PASS all 400 clips · PASS no failures · PASS privacy · PASS rotation · PASS feat_ver = pilot →
  **NOTEBOOK RESULT: PASS**. Hand-coverage table not yet copied into this log.
- Observed: the extraction progress lines (every 20 clips) only appeared in the Kaggle log at the end
  (3468.7 s), because the child process's output was buffered → G18 item (4).

## 2026-10-23 — kaggle400 Step D, notebook 01 (upload + split check) on Kaggle — PASS (measured)
- Setup: notebook `01_data_split_check`, input = PRIVATE dataset `bdsl-k400` Version 1, Accelerator None,
  Save & Run All; reported by the owner 17:51–17:57 UTC+6.
- Upload check (`k400_run.py verify-upload`): **UPLOAD CHECK: PASS (every file identical to the desktop
  package)** — 532 files listed in `UPLOAD_MANIFEST.csv` (400 videos, 122 code files, 10 data metadata
  files), missing 0, different 0 (SHA-256 + size). The 3 files not listed are `UPLOAD_MANIFEST.csv` itself,
  `PACKAGE_INFO.json` and `README_UPLOAD.md` (written after the manifest; `kaggle/src/k400/package.py`);
  Kaggle shows 535 files.
- Split checks on the uploaded files (`k400_run.py verify --require-videos`, exit code 0): **RESULT: PASS
  (10 passed, 0 failed, 0 skipped)** — 400 rows; train 320 / val 40 / test 40; 398 groups, none crossing;
  no SHA-256 or normalised sentence crossing or duplicated; 3456/3457/3458 all in train; S1 partition kept
  (`split == s1_split` for all rows — `S1_v0.csv` is not uploaded); 400 files, names and SHA-256 equal;
  no file in two folders; SPLIT_LOCK.json: 4 manifests match their locked hashes.
- Final list: PASS every uploaded file identical · PASS all 10 split checks · PASS counts 320/40/40 →
  **NOTEBOOK RESULT: PASS**.
- Reading problem found by the owner: notebook 01 also displays `SPLIT_REPORT.md`, whose section 7 is the
  selection-time snapshot (7 passed, 3 skipped — written before the videos were copied). The owner first
  took that block for the live result; the live Step 2 output (above) settles it. Improvement proposed in G18.

## 2026-10-23 — kaggle400 Step D, notebook 00 (environment check) on Kaggle — PASS (measured)
- Setup: owner's Kaggle account, notebook `00_env_check_kaggle` imported from `kaggle/notebooks/`, input
  = PRIVATE dataset `bdsl-k400` Version 1, Accelerator GPU T4 x2, Internet On, run with
  Save Version → Save & Run All (version "run 1"), 2026-10-23 (reported 17:36 UTC+6). Values as reported by the owner.
- Machine (measured): 2 × Tesla T4 (`gpu_count` 2; training uses `cuda:0`); Python **3.13.15**; PyTorch
  2.11.0+cu128, CUDA 12.8, cuDNN 91900; 4 CPU cores, 33.7 GB RAM; Linux 6.18.48+ x86_64; free disk
  **20.9 GB of 21.0 GB** in `/kaggle/working`.
- Code provenance: commit `933e9032ac3a3664e447c4e658a335f0ed621ffa`, source "package"
  (CODE_VERSION.json), dirty: false.
- Dataset location: found automatically at `/kaggle/input/datasets/<owner>/bdsl-k400/` (unzipped
  folders; the guide assumed `/kaggle/input/bdsl-k400/` — the depth-independent search handled it).
- MediaPipe: **OK via the main route** (`pip install mediapipe==0.10.35 opencv-contrib-python==5.0.0.93`
  into `/usr/bin/python3`; no fallback); probe: numpy 2.1.3, cv2 5.0.0, mediapipe 0.10.35; one real
  dataset frame 1920 × 1080, orientation_meta 0.0, 33 pose points. Model `holistic_landmarker.task`
  13,683,609 bytes, SHA-256 = `configs/base.yaml` (`e2dab611…50c3f8`).
- Result: PASS GPU visible · PASS MediaPipe 0.10.35 on a real frame · PASS model SHA-256 →
  **NOTEBOOK RESULT: PASS**. 3 output files (0.0 MB) + `OUTPUT_HASHES.csv`; "carried over: 0 files" (expected).
- Note: Kaggle runs Python 3.13 (desktop 3.12, workspace tests 3.12); the remaining notebooks are the
  first runs of this code on 3.13.

## 2026-10-23 — kaggle400 Step B, desktop run 3 of `run_local_steps.ps1` — ALL 7 STEPS PASS (measured)
- Run by the owner 12:34 (UTC+6); log `kaggle/work/run_local_steps_20261023_123448.log`; 1.8 min.
- Steps 1–4 PASS (selection identical; 400/400 copies re-hashed identical; 10/10 split checks).
- Step 5: **209 passed** (42.4 s) on the desktop (Windows, project `.venv`).
- Step 6: local commit **`933e903`** (`933e9032ac3a…`), 93 files, no video/feature/checkpoint/zip/credential;
  code paths clean afterwards; **not pushed**.
- Step 7: `kaggle/work/upload/bdsl-k400-933e9032.zip`, **5,938,005,200 bytes** (5.94 GB; PowerShell and
  Windows show 5.53 GB because they count 1 GB = 1024³ bytes), 535 files: code 122 files (1.0 MB),
  metadata 13 (0.8 MB), videos train 320 (4,742.2 MB), val 40 (591.3 MB), test 40 (603.8 MB).
  `verify-package` re-hashed every entry: PASS.
- Found in the log: the desktop's git converts text files to CRLF (`core.autocrlf`), and `git archive`
  applies that, so `code/` in the zip has CRLF text files; `data/` comes from disk and is LF.
  Workspace check: the same setting (`core.autocrlf=true`) gives CRLF from `git archive` (110 CRLF text
  files in a smoke package); smoke chain A (00, 01, 03–09) and chain B (00, 02 with real MediaPipe
  extraction) on that package gave **identical PASS/FAIL lines** to the earlier LF smoke run, no errors.
  (Smoke FAILs are the expected ones: 50/6 clips instead of 320/40/40 / 400, no GPU in the workspace.)
  Conclusion: the CRLF code in this package is harmless. Proposal for a later package (not needed now):
  `git -c core.autocrlf=false archive` so `code/` is byte-identical to the repository.

## 2026-10-23 — kaggle400 Step B, desktop run 2 of `run_local_steps.ps1` (owner's desktop, measured)
- Run by the owner 12:26 (UTC+6); log `kaggle/work/run_local_steps_20261023_122606.log`; 1.3 min; 77.9 GB free.
- Steps 1–4 PASS again: re-selection identical; copy step re-hashed all copies (copied now 0, already
  present 400, 400/400 byte-identical, sources unchanged 400/400); `verify_split --require-videos` 10/10 PASS.
- Step 5: **208 passed, 1 failed** (41.2 s). Last run's Windows-path failure is gone. New failure:
  `tests/test_text2gloss.py::test_stop_and_resume_gives_identical_weights` (a pre-Session-8 test).
  Weights and epochs were identical; the metrics differed only in `train_seconds` (0.2 vs 0.1).
  Cause: Session 8 added wall-clock `train_seconds` inside the per-seed quality metrics (`agru`,
  `model_b`), and the older resume tests compare those dicts exactly, so they passed only when the
  rounded times happened to match (also true of `test_gloss2motion.py:163`). Steps 6–7 did not run.
- Fix (workspace): both trainers keep time in `metrics["train_seconds"][seed]`, outside the quality
  metrics; readers updated (report table T3, notebooks 04/05 one line each; cell ids unchanged). The old
  tests were left unchanged. New assertions in `test_k400_training.py`: resumed and straight Model B
  metrics identical; no timing key in any per-seed quality dict; T3 training time filled. Check: both old
  resume tests passed 3 times with a fake clock jumping up to 50 s per reading. Workspace suite:
  **209 passed**.

## 2026-10-23 — kaggle400 Step B, desktop run 1 of `run_local_steps.ps1` (owner's desktop, measured)
- Setup: DESKTOP-4NDR99B, `D:\sign_avatar_cse498r`, git 2.52.0.windows.1, uv 0.10.8, branch main at
  `acb711c`; 83.4 GB free on D:. Run by the owner 2026-10-23 12:07 (UTC+6); log
  `kaggle/work/run_local_steps_20261023_120715.log` (gitignored); total 1.7 min.
- Results:
  - Step 1 pre-checks PASS. Step 2 re-selection on the desktop **identical** (same 400 clips, 3 split
    manifests, subset_manifest without `sha256_copy`, G0 corpus); OOV numbers identical to the workspace.
  - Step 3 copy: **400/400 copies byte-identical** (SHA-256 source = copy = manifest_v1), 400 copied now,
    sources unchanged (size + mtime) 400/400, **5.94 GB**, 21 s; SPLIT_LOCK.json written (videos digest
    `ec1f61a2…`). Checked in the workspace afterwards: lock paths use `/`, files are LF, and the lock
    written on Windows also passes check 10 on Linux.
  - Step 4 `verify_split.py --require-videos`: **10/10 PASS**.
  - Step 5 tests: **208 passed, 1 failed** (52.7 s). Failure:
    `test_setup_restores_earlier_outputs_without_overwriting` — `restore()` reported conflicts with the
    Windows separator (`outputs\x.json`); a real portability bug (report text differed per OS), not a test
    flake. Steps 6–7 (commit, package) did not run; nothing committed, nothing pushed.
- Fix (workspace, same day): `restore()` reports `rel.as_posix()`; a re-run of the copy step now replaces its
  own SPLIT_REPORT section (no duplicate) and adds a dated "Re-check" line to the DATASET_WORK_LOG entry
  (first run kept). Test extended. Workspace suite: **209 passed**. Desktop re-run pending.

## 2026-10-23 — kaggle400 Step A — workspace checks (AI cloud workspace, NOT the desktop)
- Setup: the AI's Linux workspace (Python 3.12.3; numpy 2.4.6, pandas 3.0.3, PyYAML 6.0.3, mediapipe
  0.10.35, opencv-contrib 5.0.0.93, torch 2.14.1+cu130 on CPU — no GPU, sacrebleu 2.6.0, pytest 9.1.1).
  Read-only copies of the code, configs, tests, `manifest_v1.csv`, `S1_v0.csv`, the pilot selection and the
  50 pilot feature files (derived data) were staged from the desktop. **No video was copied.** The desktop
  had no shell this session, so nothing here ran on the desktop or on Kaggle.
- Metric(s) / checks and results:
  - Existing suite before any change: 140 passed (workspace).
  - After Session 8: **209 passed** (26 s; incl. 69 new kaggle400 tests). Also 209 passed with
    pandas 2.2.3 + numpy 2.1.3 (older versions a Kaggle image may have); pins restored afterwards.
  - Input hashes: manifest_v1 `2ff133cf…`, S1_v0 `40481a5f…` = their meta files.
  - Selection (seed 20261023): train/val/test **320/40/40** clips, 318/40/40 leakage groups (398 total);
    10 + 10 minimal-pair held-out clips, 20 train siblings, 14 vocabulary-support clips; 4 clips also in
    pilot50; total source size 5.94 GB; longest clip 22.1 s. Shares per split within ≈1.5 percentage points
    of the pool for every stratum (SPLIT_REPORT.md §5).
  - OOV vs the train vocabulary (416 word types): val 35/169 tokens = **20.7%** (22/40 sentences with an
    OOV word), test 21/173 = **12.1%** (16/40).
  - verify_split checks 1–7 PASS (8–10 need the copies + lock: desktop step).
  - G0 corpus file (1,398 words from all 5,010 sheet sentences) reproduces all 50 pilot G0 drafts
    exactly; G0 files: train `aa36b9a4…`, val `a77cf8bd…`, test `9960a5b8…` (canonical SHA-256).
  - mediapipe 0.10.35 (py3-none-manylinux_2_28_x86_64) and opencv-contrib 5.0.0.93 (cp37-abi3) wheels exist
    for Python 3.10–3.14 on Linux (pip download check) — the Python version should not block the main route.
  - Smoke test of the notebooks on a simulated Kaggle filesystem (/kaggle/input, /kaggle/working,
    KAGGLE_KERNEL_RUN_TYPE set; package built from a scratch git commit; tiny epochs via K400_EXTRA_SETS):
    - chain B (6 synthetic videos, one with a 270° rotation flag): 00 and 02 ran; MediaPipe probe OK on a
      real decode; extraction 6/6, feat_ver **fa89892d4908** (= the pilot), privacy OK, rotation OK.
    - chain A (the 50 pilot clips as a stand-in: dummy video files + the real pilot features in place of
      02's output): 00, 01, 03–09 all executed without errors; 01: upload check + 10/10 split checks PASS;
      03: G0 IDENTICAL; 04: resume test PASS; 07: freeze → val → final test → lock; 08: 18 tables + 8
      figures + RESULTS_SUMMARY.md; 09: 5 skeleton videos. Expected FAILs only: no GPU in the workspace,
      50 instead of 400 clips.
    - Consistency: on the 5 pilot test clips the new evaluation code gives the same baseline numbers as the
      Day 4 pilot report (B0 body MPJPE 0.221, hands 58.2/59.7 mm; B1 0.270, 63.2/75.2 mm, velocity ratio 0.99).
  - MediaPipe fallback route (uv-made Python 3.12 + desktop pins): probe OK and extraction 3/3 with
    feat_ver fa89892d4908 after the plot-backend fix below.
- Notes: bugs found by these tests and fixed before delivery — (1) the training lock check opened the test
  manifest (now train/val only; final evaluation checks all); (2) two runs started in the same second shared
  a folder and the second would have resumed the first; (3) `--not-for-paper` did not mark clean-code runs
  (the resume-test runs could have been frozen); (4) prediction required targets; (5) MediaPipe/TFLite log
  noise in notebooks; (6) the model download and fallback environment would have been saved as Kaggle
  output (now /tmp); (7) child Pythons inherited Jupyter's MPLBACKEND and the fallback crashed (now Agg).
  All smoke-test numbers are pipeline tests, never results. Pending: the desktop run (copy, verify, tests,
  commit, package) and every Kaggle run.

## 2026-10-22 — Git publish (Session 7)
- Setup: Owner explicitly requested commit and push on `main`.
- Metric(s) / checks: `git diff --check`; confirmed the mock pilot annotation CSV marks rows with
  `is_mock=true` and notes that they are not video-verified; pushed `main` to `origin`.
- Result: Commit `62e719e` created; push advanced `origin/main` from `edadec9` to `62e719e`.
  No test suite was run for this documentation-only commit; the preceding audit recorded 140 passing
  tests.
- Notes: The push included six earlier unpublished commits, including the clearly marked TEST run and
  mock review data. The broader push policy remains open for owner review.

## 2026-10-22 — Audit + report generation (Session 6)
- Setup: read-only audit of the repository, `work/`, git, hardware and PDF tools; then (owner-approved)
  the two reports. `.venv` unchanged (no installs). PDFs built with system Python 3.14.4 +
  markdown-it-py 4.2.0 and headless Google Chrome (`research/reports/build_reports.py`); checked with
  pdf.js 4.10.38 (jsDelivr) in the browser pane.
- Metric(s) / checks and results:
  - **Hashes:** manifest_v1 `2ff133cf…`, S1_v0 `40481a5f…`, pilot selection `8affc876…` equal their
    meta files; holistic model `e2dab611…`; VRM `1995f174…`.
  - **Pilot copies:** 50/50 SHA-256 match `pilot50_manifest.csv` (40/5/5).
  - **Leakage re-check on S1 v0:** 0 SHA-256 / 0 sentences / 0 groups across splits.
  - **Representative clips:** 3,456; 25,286.8 s ≈ 379,301 frames at 15 fps.
  - **Runs:** 12 current + 6 superseded folders; all 60 checkpoint files load; every run has its
    run/metrics files; every `run.json` records `dirty=True`.
  - **pytest:** 140 passed. **gloss-validate:** exit 1 (normal), exit 0 (`--allow-test-data`).
  - **Hardware:** Ryzen 5 3500X 6C/6T, 23.9 GB RAM, RX 570; D: 83.4 GB free, C: 121.7 GB free.
  - **Line endings:** `core.autocrlf=true`, no `.gitattributes`; annotation CSV working copy
    `9cd37d3d…` vs committed blob `a0be4e91…` (identical after removing CR).
  - **Training code:** no `.to(device)` in `src/bdsl/models/` → CPU only.
  - **Notebooks:** all 7 saved without outputs; only 00 was ever executed.
  - **PDFs:** `PILOT_TEST_VERSION_COMPLETE_REPORT.pdf` 19 pages (813,922 B);
    `FULL_DATASET_EXECUTION_PLAN.pdf` 31 pages (1,168,225 B). Text extractable on every page; all
    Markdown headings present (29 / 120); all 7 figures present (checked by text inside each
    diagram); "Page n of N" on every page except the title page; Bangla text intact; spot pages
    checked visually (tables, code blocks and figures fit).
- Notes:
  - My own build-script bugs, fixed: image paths not rewritten (first PDFs had only alt text, and my
    first figure check wrongly passed on that alt text); Chrome reused cached SVGs; the chart font
    was missing on Windows.
  - The pilot PDF could not be replaced while Adobe Acrobat Reader held it open; after the owner
    quit Acrobat, the final build was written at 21:14:43 and verified.
  - The table of contents links to sections but has no page numbers.

---

## 2026-10-22 — Day 5 — retargeting, skeleton video, avatar viewer, end-to-end demo ("pipeline test")
- Setup:
  - Command: `bdsl.cli demo --sentence <3246>` → `work/demo/demo_20261022T141520Z/`.
  - Text → gloss by G0. Model B = run `gloss2motion_gloss_pilot50_20261022T133822Z`, seed 42, best
    checkpoint (SHA-256 b7639820…). B1 = training clip 3225.
  - Post-processing: One-Euro filter (min cutoff 1.0, β 0.3) on body + hands; hands blend to rest
    over 3 frames where missing.
  - Retargeter rt-v1; avatar = CC0 VRoid `Base_Female.vrm` (VRM 0.x, SHA-256 1995f174…).
  - Viewer: three 0.186.1 + @pixiv/three-vrm 3.5.5 from jsDelivr, served by `http.server` on
    127.0.0.1, checked in the built-in browser.
- Measured before building:
  - MediaPipe "left shoulder" x > "right shoulder" x in 50/50 clips; y points down.
  - The hand world wrist equals the pose wrist (distance 0.000 m), so hands and pose share one frame.
  - The VRM declares CC0 in its own metadata. It has 54 humanoid bones, including 30 finger bones and
    upperChest (G5 answered).
  - Expression presets: a/i/u/e/o, blink (both, left, right), joy, angry, sorrow, fun (no "surprised").
- Checks and results:
  - Demo: G0 gloss "আমি স্কুল? যাই?", no unknown tokens. Model B predicts 91 frames; B1 = 3225
    "আমি সোমবার স্কুল এ যাই", 79 frames, hand coverage L 0.81 / R 0.51.
  - Hash checks (inputs, vocab, standardiser vs the run) all pass.
  - Round-trip, Python canonical T-pose, all 50 pilot recordings (4,806 frames): body / hands /
    fingers / head max ≤ 2.5e-6° (exact by construction; checks the quaternion maths).
  - Round-trip on the real avatar (three-vrm, raw bones after normalised → raw transfer), mean (max):
    - Model B: body 0.50° (3.42°), hand frames ~0° (n=182), fingers ~0° (n=2730);
    - B1: body 0.35° (2.79°), hand frames ~0° (n=104), fingers ~0° (n=1560).
    The body error is not broken down per bone. A likely source: the torso check measures from the
    hips, while the spine rotates around its own joint.
  - Avatar sides: after `rotateVRM0`, leftUpperArm x = +0.108 and rightUpperArm x = −0.109, so the
    avatar's left is on screen right, the same as the skeleton video.
  - Skeleton video: 91 frames, 15 fps, 960×570, two labelled panels; the B1 panel holds its last
    frame marked "(ended)".
  - Viewer: plays at 15 fps (30 frames in 2 s), no console errors. Mirror mode runs. "Record one
    pass" produced a 1.1 MB `.webm`, offered as a save link; it was not downloaded.
  - `uv run pytest`: 140 passed (15 new in `tests/test_avatar.py`).
- Notes:
  - A pipeline test only; nothing here is checked by a BdSL-competent person (`LIMITATIONS.md` in
    the demo folder).
  - Bugs found and fixed during the run:
    - a zero-length hand vector crashed the frame solver;
    - a negative first time-step crashed the viewer;
    - fingertip bones were measured with the previous bone's direction in the first viewer
      round-trip (mean 19°), fixed by measuring each fingertip bone's own rotation;
    - the VRM path under `avatar:` changed the config hash when the work folder moved (moved to
      `paths:`).

---

## 2026-10-22 — Day 4 — Model B pilot (gloss → motion), ablation T, B0/B1 ("pipeline test")
- Setup:
  - Environment: desktop CPU, torch 2.14.1+cpu, 2 threads per run (OMP/MKL_NUM_THREADS=2).
  - Data: pilot50_v1 (40/5/5), features `fa89892d4908`. Inputs: G0 `gloss_auto` (markers removed)
    plus G0 tag tokens, or the normalised Bangla words (ablation T). Reviewed glosses are not used.
  - Frames: 208 values (9 body points in shoulder widths; wrist-relative hands; 52 blendshapes;
    head rotation), standardised on the train clips.
  - Model B: NAR Transformer d 192, 4 heads, 3+3 layers, ff 512, dropout 0.1; 2,663,441 parameters
    (gloss vocab 100). AdamW 5e-4, batch 8, patience 60 on val masked L1. Loss weights: hands ×2,
    λ_v 0.5, λ_len 0.1 (ADR-0026).
- Measured before the runs:
  - Hand world points are NOT hand-centred: |wrist| p50 0.551 m (p5 0.399, max 0.854), while wrist
    → middle fingertip p50 0.128 m. Features were changed to wrist-relative hands, and the runs
    made before that change were superseded.
  - Feature NaNs match the masks exactly. Shoulder width 0.309–0.339 m.
- Checks and results:
  - Unit tests: 14 new, 125 total pass. They cover the masked loss (zero gradient and no effect
    from missing or padded values), gap interpolation, the layout, metrics, B0/B1, model shapes,
    resume and the input guard.
  - Overfit 1 clip (`…overfit1…T133821Z`): train masked L1 0.808 → 0.041 (5.1%) in 400 epochs.
  - Overfit 40 clips (`…overfit40…T134024Z`): 0.707 → 0.136 (19.2%). Train MPJPE body 0.107 vs B0
    0.216; hands 23.8/24.8 mm vs B0 51.8/59.6 mm.
  - Full runs (`gloss…T133822Z`, `text…T133822Z`), 3 seeds each. Gloss best epochs 37/26/38; text
    best epochs 48/45/36. Model B values are the mean over 3 seeds (sd ≤ 0.01 body, ≤ 6 mm hands).
    Body and DTW are in shoulder widths, hands (L/R) in mm, duration error in seconds:

    | split | method | body | hands L / R | DTW body | duration err | velocity ratio | hand-energy ratio | diversity ratio |
    |---|---|---|---|---|---|---|---|---|
    | val | B (gloss) | 0.220 | 63.7 / 57.2 | 0.199 | 3.18 | 0.25 | 0.07 | 0.32 |
    | val | B (text) | 0.217 | 60.0 / 61.1 | 0.199 | 2.99 | 0.30 | 0.09 | 0.39 |
    | val | B0 | 0.235 | 63.2 / 57.1 | 0.215 | 3.20 | 0.23 | 0.05 | 0.00 |
    | val | B1 | 0.244 | 73.4 / 69.0 | 0.210 | 3.76 | 1.06 | 1.30 | 0.89 |
    | test | B (gloss) | 0.224 | 55.9 / 65.3 | 0.209 | 1.91 | 0.20 | 0.05 | 0.27 |
    | test | B (text) | 0.224 | 58.4 / 65.1 | 0.207 | 2.28 | 0.24 | 0.07 | 0.39 |
    | test | B0 | 0.221 | 58.2 / 59.7 | 0.208 | 2.08 | 0.17 | 0.04 | 0.00 |
    | test | B1 | 0.270 | 63.2 / 75.2 | 0.233 | 2.03 | 0.99 | 1.64 | 1.01 |

  - Kill-and-resume: a seed-42 gloss process was force-killed at epoch 50, then `--resume`
    (`…T134800Z`). Last and best checkpoints are weight-identical to the full run, and the metrics
    are identical.
- Notes:
  - Pilot "pipeline test" only (5 items per split, signer-dependent).
  - Model B and ablation T are about as good as mean motion (B0) on held-out clips and move far
    less than real signing (velocity ratio 0.2–0.3). B1 moves realistically but replays another
    sentence. Gloss vs text input shows no clear difference at this size.
  - DTW-MJE is computed for val/test only (cost).
  - The first seed's predictions for all 50 clips are in `seed42/predictions/` for Day 5.
  - Bugs found and fixed in my own code during the run: a too-coarse time code; hand coordinates not
    wrist-relative.

---

## 2026-10-22 — Day 3 Step 1 — Model A pilot, TEST mode (fake review data; ADR-0025)
> **TEST RUN.** The references are fake: they were derived from the sentence text, and no video was
> watched. None of these numbers is a Model A result. G0 is favoured because the references were
> made by editing its drafts.
- Setup:
  - Environment: desktop CPU, torch 2.14.1+cpu, sacreBLEU 2.6.0, branch `test-run-fake-review`
    (code commit `de6db35`), later merged into `main`.
  - Data: pilot50_v1 (40/5/5), `annotations/pilot50_v1_gloss_v01.csv` with 50 rows `team_reviewed`,
    `is_mock=true`. Command: `train-text2gloss --allow-test-data`.
  - A-GRU: emb 128, BiGRU 256, Bahdanau 256, GRU decoder 256, dropout 0.2, Adam 1e-3, batch 8,
    label smoothing 0.1, patience 30 on val greedy WER, beam 4 at the end.
  - Vocab (train only): src 98, tgt 88 (incl. 4 specials and the tag tokens). 1,713,752 parameters.
- Checks and results:
  - Guard: `gloss-validate` without the option → exit 1 (100 problems: 50 mock, 50 "not
    video-verified"). With the option → exit 0, `usable_for_training` 50. `train-text2gloss` without
    the option → exit 2 "Refusing to train". A split that differs from the manifest is refused
    (unit test).
  - Overfit: 1 sentence → 100% exact (beam) at epoch 4; 40 train sentences → 100% exact at epoch 12
    (`…overfit1…T125750Z`, `…overfit40…T125800Z`).
  - Full run `TEST_text2gloss_pilot50_20261022T125820Z`, 46 s. Seeds 42/43/44 stopped at epochs
    39/50/41 (best 9/20/11). G0 vs A-GRU (mean ± sd over 3 seeds):

    | split | G0 WER | G0 exact | A-GRU WER | A-GRU exact | A-GRU tags | A-GRU BLEU-4 | A-GRU chrF |
    |---|---|---|---|---|---|---|---|
    | train (40) | 34.5 | 15% | 1.4 ± 1.5 | 94% | 99% | 97.2 | 98.8 |
    | val (5) | 33.3 | 20% | 68.3 ± 7.3 | 0% | 87% | 8.4 | 33.8 |
    | test (5) | 33.3 | 0% | 69.8 ± 13.7 | 0% | 87% | 9.7 | 38.6 |

  - Kill-and-resume: a seed-42 process was force-killed after epoch 20, then `--resume`. The last and
    best checkpoints are weight-identical to the uninterrupted run, with identical metrics
    (`…T130107Z`). Resuming with other seeds is refused (exit 2).
  - Labels: 0 files under `work/runs/` lack the `TEST_` prefix. Every JSON file and checkpoint has
    `TEST_RUN: true`, and every log line starts with `[TEST]`.
  - `uv run pytest`: 111 passed.
- Notes:
  - The A-GRU memorises its 40 sentences. On held-out sentences it outputs near-copies of training
    sentences (e.g. 3323 → "তোমার প্রিয় রং কি" for all seeds). With 5 items per split, one item
    moves a score by 20 points.
  - BLEU-4 is 0 for any gloss under 4 tokens, so gloss WER is the main score.
  - Two bugs found and fixed: the overfit stop is now judged with beam search; resume now keeps
    the run's seeds. The superseded folders are `…overfit1…T125651Z`, `…overfit40…T125701Z` and
    `…T125920Z`.

---

## 2026-10-22 — Notebooks — structural check at the end of Session 3 (not executed)
- Setup: new thin notebooks `notebooks/01_manifest.ipynb`, `02_extract.ipynb`, `03_gloss.ipynb`
  (call `bdsl.cli.main` and package functions; paths from config only), plus the existing
  `00_env_check.ipynb`. Checked with nbformat 5.11.1 and Python `ast` in `.venv`; no cell was run, so
  no data was read.
- Metric(s) / checks: valid nbformat; no outputs and no execution counts; every code cell parses;
  imports come from `bdsl`; no absolute machine paths; the CLI commands they call exist; the config keys
  and functions they use exist.
- Result: all 4 notebooks pass.
  - `00_env_check`: 5 cells (3 code).
  - `01_manifest`: 8 cells (6 code): manifest, split, pilot-select; `pilot-copy --confirm` is
    commented out behind the approval note.
  - `02_extract`: 4 cells (3 code): extract (pilot50, VIDEO mode).
  - `03_gloss`: 5 cells (4 code): gloss-draft, gloss-validate.
  pytest: 93 passed (unchanged).
- Notes: running 01–03 would re-read data. The manifest resumes from its hash cache, extraction skips
  finished clips, and gloss-draft rewrites the identical file or refuses if rows are reviewed. Not done
  this session.

## 2026-10-22 — Annotations — Day 2 Step 2: gloss convention v0.1 + G0 drafts (Session 3)
- Setup:
  - `.venv` as before (no new packages).
  - Code: `src/bdsl/text/{gloss_rules,annotations}.py`; `bdsl.cli gloss-draft --data pilot50` and
    `gloss-validate`.
  - Inputs: FinalSheet2.xlsx (sentence text only, for the R5 word list) and
    dataset/pilot50_v1/pilot50_manifest.csv. No video opened.
  - Config hash 1563eb579556.
- Metric(s) / checks: rows and statuses; determinism (re-run SHA-256); validation of the real file;
  validator and overwrite-guard unit tests; input SHA-256 before/after; pytest.
- Result:
  - **Drafts:** `annotations/pilot50_v1_gloss_v01.csv` has 50 rows, all `auto_draft` (annotator
    `auto:G0-v0.1`, is_mock=false, reviewer fields empty). A re-run is byte-identical (SHA-256
    bdacd8355c4a…).
  - **G0 v0.1 over the 219 pilot tokens:**
    - R0 pronoun 46; R1 negation 4; R2 wh-word 1; R2b কি/কী 4;
    - R3 number 1; R4 Latin 1;
    - R5 genitive stem (`~`) 5;
    - R6 no rule (`?`) 157.
  - **gloss-validate:** 0 problems; 0 rows usable for training (no reviewed rows; REVIEWERS.csv is
    header only).
  - **Unit tests:** invalid rows are rejected:
    - a reviewed row with an unregistered reviewer;
    - an expert status from a team-role reviewer;
    - a missing gloss_reviewed; a future review date;
    - a mock row; a wrong sentence_norm; a bad status;
    - reviewer fields on a draft; an unknown index;
    - a rejected row without a note; the reviewer code "MOCK".
    The `gloss-draft` command refuses to overwrite a file with a reviewed row (the file stays
    byte-identical).
  - **Inputs unchanged:** FinalSheet2.xlsx and pilot50_manifest.csv SHA-256 identical before and after.
  - **pytest:** 93 passed (26 new).
- Notes:
  - One bug in my own tests (expected outputs were passed through norm_v1, which strips `?`); fixed
    before the real run.
  - G0 output is a pseudo-gloss. 157 of 219 tokens are left to the reviewer.

## 2026-10-22 — Features — Day 2 Step 1: MediaPipe extraction + QC on pilot50_v1 (Session 3)
- Setup:
  - `.venv` as before (no new packages).
  - Code: `src/bdsl/features/{layout,extract,qc}.py`; `bdsl.cli extract --data pilot50 --mode both`.
  - Inputs: the 50 pilot copies (`dataset/pilot50_v1/videos/`). Originals not opened.
  - Process: OpenCV decode with rotation; nearest-timestamp resampling to 15 fps; a fresh
    HolisticLandmarker per clip; blendshapes on; documented default thresholds; 5 worker processes.
  - Config hash f382a31af899.
- Metric(s) / checks: per-clip QC; VIDEO vs IMAGE comparison; privacy check of every .npz;
  kill-and-resume; pilot-copy SHA-256 and original size + mtime; pytest.
- Result:
  - **Extraction:** VIDEO feat_ver `fa89892d4908` and IMAGE feat_ver `395e878f9861`: 50/50 clips
    each, 0 failures. 4,806 grid frames per mode (from 9,613 source frames).
  - **Run time:** VIDEO 138.8 s, IMAGE 129.2 s; 4 min 33 s in total. Median 84 ms per detection with
    5 processes in parallel (25 ms single-process in the smoke test). About 7.4 MB per mode.
  - **QC, VIDEO mode, mean over clips:**
    - Coverage: pose 99.95%, face 99.4%, left hand 69.7%, right hand 35.7%, both hands 25.9%,
      any hand 79.5%.
    - Longest hand gap: left median 0.67 s (max 4.9 s); right median 1.7 s (max 11.9 s, clip 792).
    - Forearm-length coefficient of variation ≈ 0.15.
    - Wrist jitter: left 15.8 m/s², right 19.0 m/s².
    - ts_cv: max 0.064 (median 0).
    - Hand-side agreement with body wrists: median 0.90, minimum 0.49.
    - Median head |yaw|: 2.4°.
  - **By recording type** (VIDEO, mean coverage left / right / both; median agreement):
    - portrait (38): 0.760 / 0.251 / 0.229; 0.771
    - landscape (9): 0.586 / 0.725 / 0.404; 1.000
    - low-res (3): 0.230 / 0.602 / 0.208; 0.985
    - Left > right in 40 of 50 clips.
  - **VIDEO vs IMAGE** (`compare_pilot50.json`):
    - any hand +0.24 points for VIDEO (18 clips higher, 17 lower, 15 equal); both hands −0.18 points;
    - wrist jitter VIDEO 15.8 / 19.0 vs IMAGE 19.6 / 24.8 m/s² (left / right).
    - Owner chose VIDEO mode (ADR-0023).
  - **Privacy:** 150 .npz files checked (both modes and the resume test). No unexpected keys, no
    478-point face mesh, no image arrays.
  - **Kill-and-resume (VIDEO):** killed with 10 clips done and 0 temp files. The resume extracted 40;
    all 50 clips are array-identical to the uninterrupted run, so the extraction is deterministic.
    No leftover processes.
  - **Data unchanged:** the 50 pilot copies still match `pilot50_manifest.csv` (SHA-256); the 50
    originals' size + mtime are unchanged.
  - **pytest:** 67 passed (13 new: resampling, ts_cv, head rotation, QC maths, privacy check,
    feat_ver, read_meta).
- Notes:
  - QC values are reported without thresholds (open_questions G9).
  - Which real hand MediaPipe calls "left" is unknown (mirroring; open_questions G8).
  - Head rotation is an approximation from 4 face points; signs follow the code's convention.
  - Full-set estimate from the pilot rate (≈ 35 grid frames/s with 5 processes; ≈ 533k grid
    frames): about 4–4.5 h per mode. An estimate, not measured.

## 2026-10-22 — Dataset — Day 1 Step 2: manifest v1, split S1 v0, pilot50_v1 (Session 3)
- Setup:
  - `.venv` as in Day 1 Step 1, plus pandas 3.0.3 and openpyxl 3.1.5 (owner-approved; `uv.lock` now
    91 packages).
  - Code: `src/bdsl/{text,data}/`, `src/bdsl/cli.py`.
  - Commands: `uv run python -m bdsl.cli manifest --data full | split | pilot-select |
    pilot-copy --confirm`.
  - 6 worker processes. All 5,010 videos and the sheet were read-only.
- Metric(s) / checks:
  - ID set vs sheet; decodability; source size + mtime of all 5,010 videos and the sheet SHA-256,
    before and after;
  - exact duplicates; leakage groups; leakage checks on the real split; balance;
  - determinism (re-run hashes); pilot quotas; SHA-256 of the 50 copies; pytest.
- Result:
  - **Manifest v1** (2026-10-22T07:05Z; CSV SHA-256 2ff133cf6bb2…; config hash f7aa5765c6a6):
    - Time: 2 min 23 s wall (probe 138 s).
    - Files: 5,010 rows; ID set equals the sheet; 0 missing, 0 extra, 0 decode failures.
    - Duplicates: 3,456 unique SHA-256 (= representatives).
    - Sentences: 3,378 unique `norm_v1` sentences (NFC + `। . ? ! ,` → space + collapsed whitespace;
      990 rows change under NFC).
    - Leakage groups: 3,376 (size histogram 1:1915, 2:1380, 3:35, 4:30, 5:3, 6:7, 7:2, 8:1, 9:1,
      11:2). 0 label conflicts.
    - Video properties: portrait 4,302 / landscape 708; rotation 0°:3,142, 270°:1,838, 90°:18,
      180°:12; codec h264 2,819, hevc 2,181, VP90 10; 71,206,505,652 B; 1,059,409 declared frames;
      Σ(n_frames/fps) = 35,527 s (9.87 h).
    - Spot checks: 0.mp4 and 2.mp4 stored/display sizes agree with Day 1 Step 1.
  - **Sources unchanged:** size + mtime identical for all 5,010 videos, and the sheet SHA-256
    identical — before the run, after it, and after copying the pilot.
  - **Split S1 v0** (salt S1-v0, 80/10/10 by sha256(salt|group_id); CSV SHA-256 40481a5faedc…):
    - Groups 2,700 / 357 / 319 (80.0 / 10.6 / 9.4%).
    - Representative clips 2,759 / 368 / 329.
    - Leakage problems: none. No group, SHA-256, sentence or known link crosses splits.
    - The colour cluster (group g3456, 6 clips) is entirely in train.
  - **Balance, train / val / test (representatives):**
    - tokens 1–2: 112/13/5; 3–4: 1,619/221/191; 5–6: 953/126/123; 7+: 75/8/10
    - question (indicative): 171/20/15; negation (indicative): 165/25/18
    - landscape: 288/35/31
    - resolution 1080: 2,127/298/268; 720: 484/59/45; low (<500 px): 148/11/16
  - **pilot50_v1** (selection SHA-256 8affc876aace…; config hash 08230f0a1b63):
    - Counts and quotas: 40/5/5 from a pool of 3,378; quotas met (landscape 9, low-res 3, all
      duration quartiles: q1 15, q2 21, q3 6, q4 8); hard share 0.24.
    - Composition: 6 minimal-pair families × 4 train clips, plus 16 diversity train clips.
    - Held-out: chosen after the train clips. Option B (owner, ADR-0022): 6 of 10 held-out clips
      use only pilot-train words; 4 keep unseen words, listed per clip.
    - Copies: 50/50 SHA-256 identical to the manifest and the sources (723 MB).
  - **Determinism:** split and selection re-runs gave byte-identical CSVs.
  - **pytest:** 54 passed.
- Notes:
  - The 2026-10-22 count of 3,379 unique sentences (Phase 1 checks) used no NFC; with NFC it is
    3,378, matching 2026-10-21.
  - Indicative tags are word lists, not annotation: e.g. "সব সময়" ("always") counts as a time
    word. The sheet contains no `?`.
  - Before the first real run, my own code had three bugs, found by the tests or a manual review:
    - a pandas `index` column clashed with the row-tuple method;
    - synthetic test data used Latin digits;
    - stale wording in the generated protocol.
    All are fixed.
  - The first pilot list (option A, family siblings only) gave 1/10 held-out clips with seen words
    only. It was never copied.
  - The manifest meta records an earlier config hash than the pilot: only the `pilot` section
    changed afterwards, and that section is not used by the manifest or the split.
  - Timestamp irregularity (ts_cv) is measured during Day-2 extraction.

## 2026-10-22 — Environment + config — Day 1 Step 1 (Session 3)
- Setup:
  - Machine: desktop DESKTOP-4NDR99B, Windows 11 Pro.
  - Project `.venv` created with uv 0.10.8: CPython 3.12.13. Packages from `uv.lock` (88 resolved):
    mediapipe 0.10.35, opencv-contrib-python 5.0.0.93 (opencv-python absent), numpy 2.4.6,
    PyYAML 6.0.3, torch 2.14.1+cpu, matplotlib 3.11.2, pytest 9.1.1, ipykernel 7.4.0,
    nbclient 0.11.0, nbformat 5.11.1.
  - Model `work/models/holistic_landmarker.task`, downloaded from the official float16/latest URL:
    13,683,609 B, SHA-256 e2dab61191e2dcd0a15f943d8e3ed1dce13c82dfa597b9dd39f562975a50c3f8 —
    identical to both copies in the earlier project. The hash is pinned in `configs/base.yaml`.
  - `notebooks/00_env_check.ipynb` executed headless (nbclient) → `work/reports/env_report.json`
    (gitignored).
  - Git at 1809048 plus uncommitted changes.
- Metric(s) / checks: pytest; the 8 env-check checks; an alternate BDSL_WORK_DIR; SHA-256 of the 2
  rotation clips before and after; git diff under dataset/.
- Result:
  - **pytest:** 30 passed.
  - **Env report:** overall pass, 8/8 checks (final run 06:50:41Z, config hash 0f64a5248617):
    - python: 3.12.13 inside `.venv`.
    - packages: all pins match; no OpenCV clash.
    - opencv_rotation:
      - 0.mp4: flag 270°; raw frame 1080×1920 (h×w) → auto-rotated 1920×1080 (portrait), one quarter
        turn, pixel-exact.
      - 2.mp4: flag 0°; frame unchanged at 1080×1920 (landscape).
    - mediapipe_holistic:
      - HolisticLandmarker present; created in 0.15 s.
      - Result fields: face_landmarks, pose_landmarks, pose_world_landmarks, left_hand_landmarks,
        left_hand_world_landmarks, right_hand_landmarks, right_hand_world_landmarks,
        face_blendshapes, segmentation_mask.
      - On 0.mp4 frame 96: 33 pose, 21 + 21 hand (image and world), 478 face, 52 blendshapes.
      - VIDEO mode works.
    - torch_devices: 2.14.1+cpu, 6 threads; CUDA no; MPS no; DirectML not installed.
    - write_permission: pass; no temp files left over.
    - cpu_benchmark:
      - 6 logical CPUs.
      - numpy 512×512 matmul ×20: 0.0187 s ≈ 287.7 GFLOPS (second run: 328.6).
      - MediaPipe IMAGE mode on 1920×1080: 33.4 ms/frame over 5 frames (first 38.3 ms, rest 32.1);
        second run: 36.6 ms/frame. Single-process smoke test only, not a full-dataset estimate.
  - **BDSL_WORK_DIR** pointed outside the project: every derived path moved, the config hash was
    unchanged, and the write test passed.
  - **Clip SHA-256** identical before and after: 0.mp4 ed3713970f46…1bb6, 2.mp4 111ece319ea3…1569.
    No git diff under dataset/.
- Notes:
  - The first notebook run failed `torch_devices` because of a bug in the check, not in torch: the
    expected sum of x @ x.T was hard-coded as 70 (correct: 83). The check now compares with numpy;
    the two later runs passed.
  - Windows-only warnings (zmq Proactor event loop; kernel over TCP) do not affect results.
  - Kaggle and Colab environments are not checked yet; the same notebook will report them.

## 2026-10-22 — Repository + dataset + environment — Phase 1 read-only checks (Session 3)
- Setup: Desktop DESKTOP-4NDR99B, system Python 3.14.4, OpenCV 5.0.0.93, pandas 3.0.3. Scripts in
  the session scratchpad only; nothing written to the project or dataset. Web: PyPI, npm registry,
  MediaPipe docs, GitHub API (unauthenticated).
- Metric(s) / checks: repo visibility; contents of SIGN_LANGUAGE_DATA/; sheet copy identity; Python
  installs; colour-cluster hashes and frame differences; token statistics; sample-clip headers.
- Result:
  - **Repo:** public (`visibility: public`); 50 sample videos in `origin/main`; no LICENSE file.
  - **SIGN_LANGUAGE_DATA/:** 5,012 entries = 5,010 MP4 + SESSION_LOG.md + FinalSheet2.xlsx; the
    copy's SHA-256 equals `initial_dataset/FinalSheet2.xlsx` (prefix 15348b36e11ea8f0); 71.2 GB in
    total.
  - **Python:** 3.14.4 (system) and 3.14.3 (uv); no 3.12; uv present; both opencv-python and
    opencv-contrib-python installed in system Python.
  - **Colour cluster:** 3456=5096, 3457=5100, 3458=5102 by SHA-256; all 1298×720, 30 fps, 181–183
    frames. Mean grey difference at 20 normalised positions:
    - 3456 vs 3458: 0.0 over the first 15 positions, 10.6–13.0 over the last 5;
    - 3456 vs 3457: 0.0–1.9, then 11.1–15.1;
    - 3457 vs 3458: 0.0–1.9, then 9.1–10.7;
    - within-clip reference ≈ 7.1–7.4.
  - **Sheet** (normaliser: `। . ? ! ,` → space, whitespace collapsed): 3,379 unique sentences;
    1,417 tokens; 646 in one sentence only; 2,872 sentences with all tokens seen elsewhere;
    2,588 in 1,086 one-word-difference families (largest 31).
  - **Sample headers:** 0.mp4 rotation 270°, 1.mp4 180°, 2.mp4 0°; fps 23.1–30.2.
- Notes:
  - The 3,379 vs 3,378 difference (2026-10-21) comes from different normalisers; the project
    normaliser will be versioned.
  - The cluster interpretation ("one recording edited onto three endings") is a proposal, not a
    verified fact.


## 2026-10-21 — Dataset + repository + environment — Read-only re-audit (Session 2)
- Setup:
  - Desktop `DESKTOP-4NDR99B`, Windows 11 Pro, system Python 3.14.4, pandas 3.0.3, openpyxl 3.1.5,
    OpenCV 5.0.0.93, PyAV 17.1.0, mediapipe 0.10.35.
  - Scripts lived in the session's temporary scratchpad only. They were not added to the repo and
    wrote nothing to the project or dataset.
  - Data: `dataset/initial_dataset/{FinalSheet2.xlsx, SIGN_LANGUAGE_DATA/, videos/}` and the old CSVs
    `D:\CSE498R\Sign_Language\CSE498R_v2\Sign_Language\outputs\{duplicate_groups,near_duplicate_groups}.csv`.
  - No frames decoded, except 3 single-frame rotation checks.
- Metric(s) / checks: sheet structure and counts; ID ↔ file mapping; sample ↔ full-set identity;
  duplicate-CSV consistency; header metadata of all files; rotation; packet-timestamp regularity;
  hardware/software; MediaPipe API.
- Result:
  - **Sheet:** `Sheet1` has 2 data columns (`Names`, `Index`); 5,010 rows, 5,010 unique Index (0–5460),
    0 blank sentences. Unique sentences: raw 3,414 · stripped 3,395 · punctuation-normalised
    (`। . ? ! ,` removed) 3,378. Vocabulary 1,398 whitespace tokens (20,974 tokens). Words per
    sentence 1–13, mean 4.19. Heuristic counts: 17 rows with Latin letters, 116 with digits, ~538
    question-like, ~264 negation-like (regex; indicative only).
  - **Files:** 5,010 MP4, 71,206,505,652 B; ID set == sheet Index set. All 50 `videos/` clips are
    SHA-256 identical to their `SIGN_LANGUAGE_DATA/` copies.
  - **Exact duplicates:** the old CSV has 1,516 groups / 3,070 files (1,486 pairs, 22 triples,
    8 quads). All groups are same-size, and 25/25 random groups are SHA-256 identical. All 14 same-size
    sets that differ from CSV groups were hashed and split exactly into CSV groups, so the CSV is
    complete for exact duplicates.
  - **After exact dedup:** 3,456 videos; 3,378 unique normalised sentences; 3,324 (98.4%) have one
    video, 41 have 2, 13 have 3–6.
  - **Index structure:** 1,424 of 1,516 second copies are at Index ≥ 4000.
  - **Label mismatches in exact groups:** 3 (3850/3851/5019/5020; 3882/3883/5017/5018; 1515/1569),
    all removed by punctuation normalisation. The colour near-duplicate cluster (old pHash CSV) was not
    re-checked.
  - **Codecs:** h264 2,819 · hevc 2,181 · vp9 10.
  - **Rotation (OpenCV `CAP_PROP_ORIENTATION_META`):** 0° 3,142 · 270° 1,838 · 90° 18 · 180° 12.
    OpenCV auto-applies it (decoded frames of 0.mp4 and 10.mp4 are 1920×1080 h×w). **Displayed:
    portrait 4,302 (85.9%), landscape 708.** 1080×1920: 3,425; 350 low-res clips (short side
    < 500 px), all in Index 3675–5415. PyAV reported rotation 0 for every file, so it is not usable
    for rotation.
  - **Duration:** min 1.30 · median 6.37 · mean 7.10 · p90 11.1 · max 47.73 s; total 9.89 h; declared
    frames 1,059,409.
  - **Frame rate:** average fps ≈30 for 4,686 files, ≈29 for 262, ≈24/23 for 32, ≈60/59 for 16.
    Every file has 1 audio stream.
  - **Packet-timestamp regularity** (80 clips = 50 sample + 30 random, seed 42): 55 constant
    (CV < 1%), 20 near-constant (1–10%), **5 irregular (≥ 10%)**: 3941 (max gap 333 ms), 3947, 3946,
    5451, 3939. This contradicts both the old "all VFR" and the old "0 badly VFR" claims.
  - **Hardware:** Ryzen 5 3500X 6C/6T, 23.9 GB RAM, Radeon RX 570 8 GB (driver 31.0.12027.9001), NVMe
    SSDs; D: 86 GB free.
  - **Software:** mediapipe 0.10.35 imports on Python 3.14; `vision.HolisticLandmarker` and
    `FaceLandmarker` present, `mp.solutions` absent. Not installed: torch, ffmpeg/ffprobe, conda.
  - **Web-checked:** mediapipe latest 1.1.1 (2026-10-14). torch-directml latest 0.2.5.dev240914
    (pre-release), Python 3.8–3.12 wheels only.
  - **Old outputs:** found at `D:\CSE498R\Sign_Language\CSE498R_v2\`. `D:\CSE498R\derived` (old
    features) does not exist; `Sign_Language/data/{keypoints,deduplicated}` are empty.
- Notes:
  - PyAV segfaulted (exit 139) during a long in-process packet-demux loop; it ran fine one file per
    subprocess.
  - Not re-run: pHash near-duplicates, audio content, MediaPipe coverage, signer estimate. Treat those
    old numbers as **reported**.
  - Full SHA-256 of all 5,010 files is deferred to the scale-up stage.

## 2026-09-27 — Repository — Real-folder verification + worktree removal (Session 1)
- Setup: `git rev-parse`, `git worktree list`, `git status`, `git diff --cached -M --name-status`,
  `find`, `grep` in `C:/Workspace/NSU/sign_avatar_cse498r` on branch `main`.
- Metric(s) / checks: session location; dataset files unchanged; analyses cleaned (D3); references to
  the old worktree; worktree removal.
- Result: Session ran in the real folder (`.git` is the main git dir). Dataset: 53 files are 100%
  renames (3 sheets + 50 videos), `videos.txt` deleted, `dataset/README.md` added. Analyses 01–07 were
  edited to remove the medical/dialect context (similarity 87–99%); 08 is a 100% rename. Remaining
  medical/dialect mentions are paper findings, except two "Medical" table rows in 07 (flagged, E3).
  No symlinks, and no project file depends on the worktree. Worktree folder was already empty; its
  branch had no commits beyond `main`. `git worktree prune -v` removed the stale metadata;
  `git worktree list` now shows only the real folder. `rmdir` of the empty folder failed ("Device or
  resource busy").
- Notes: The empty folder can be deleted once the process holding it (likely the old Claude session)
  is closed.

## 2026-09-27 — Repository — Bootstrap reorganization check
- Setup: `git status` / `find` on branch `claude/bangla-sign-avatar-setup-699b03` after the `git mv`
  moves; spreadsheets read with Python's standard library (zipfile + XML).
- Metric(s) / checks: every moved file shows as a rename; file counts per folder; no leftover files in
  the old folders; sheet row counts and video ↔ Index alignment.
- Result: 70 files were moved (6 PDFs + notice README, 8 analyses, reading form, 3 sheets, 50 videos +
  `videos.txt`). 69 are byte-identical renames; the only content edit was the reading form (3 lines
  removed, ADR-0003). The 17 `templates/` files were deleted (git shows one of them as "renamed" to
  `session_protocol.md` only because the content is similar).
  `FinalSheet.xlsx` 3,491 rows; `FinalSheet2.xlsx` 5,010 rows (superset); all 50 videos match an Index
  in `FinalSheet2.xlsx`.
- Notes: The first `git mv` failed with "Permission denied" because the shell's working directory was
  inside the folder being moved. Retrying from the repo root worked.
