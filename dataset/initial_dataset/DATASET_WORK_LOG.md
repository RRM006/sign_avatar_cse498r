# Dataset Work Log

## 2026-09-28

- Computer: Desktop
- Task: Inspect and document the verified `dataset/initial_dataset/` layout and safe dataset-handling protocol.
- Files/folders inspected: `dataset/initial_dataset/`; `videos/`; `superseded/FinalSheet.xlsx`; `SIGN_LANGUAGE_DATA/` including `SESSION_LOG.md`; `FinalSheet2.xlsx`; `FinalSheet_DuplicateGroups.xlsx`; `dataset/README.md`; `.gitignore`; Git status and index.
- Action performed: Read-only inventory and workbook inspection; compared video filename IDs with `FinalSheet2.xlsx`; created `README.md` and this work-log entry. Video payloads were not opened or changed.
- Files changed: `dataset/initial_dataset/README.md`; `dataset/initial_dataset/DATASET_WORK_LOG.md`.
- Dataset files changed: None.
- Result: Verified 50 sample MP4s and 5,010 full-set MP4s. All sample IDs occur in the current sheet, and the full-set ID set exactly matches its 5,010 unique `Index` values. The full set is ignored by the existing Git rule.
- Errors/warnings: Neither target documentation file existed before this entry. The spreadsheet's unnamed third column has no values; its purpose is unknown. No errors encountered.
- Next step: Read this README before future dataset work and log each meaningful dataset operation.

## 2026-10-21

- Computer: Desktop (`DESKTOP-4NDR99B`)
- Task: Read-only re-audit of dataset claims for the Session 2 design plan.
- Files/folders inspected:
  - `FinalSheet2.xlsx`;
  - `SIGN_LANGUAGE_DATA/` (file sizes; container headers of all 5,010 MP4s; SHA-256 of about 80 files;
    packet timestamps of 80 files; 3 single decoded frames);
  - `videos/` (SHA-256 of all 50).
  - Also the old CSVs in `D:\CSE498R\Sign_Language\CSE498R_v2\Sign_Language\outputs\`.
- Action performed: Read-only measurements with temporary scripts outside the repo (session scratchpad).
  No dataset file was opened for writing.
- Files changed: This log entry only (written at end of session).
- Dataset files changed: None.
- Result: See `agent_docs/test_log.md` (2026-10-21). In short:
  - ID set == sheet; 50 samples identical to the full-set copies; old exact-duplicate CSV consistent
    (25/25 groups re-hashed identical); 3,456 unique videos.
  - Rotation flags on 1,868 files; 85.9% portrait when displayed.
  - 5/80 clips have irregular timestamps.
- Errors/warnings: PyAV 17.1 segfaulted in a long in-process demux loop (no data affected); PyAV does
  not report the rotation flag, OpenCV does.
- Next step: Pilot selection/copying only after the owner's go (`agent_docs/open_questions.md` F3).

## 2026-10-22

- Computer: Desktop (`DESKTOP-4NDR99B`)
- Task: Read-only checks for the Phase 1 design review (Session 3).
- Files/folders inspected:
  - `FinalSheet2.xlsx` (sentence/token statistics);
  - `SIGN_LANGUAGE_DATA/` (listing, byte total, SHA-256 of its `FinalSheet2.xlsx` copy);
  - `SIGN_LANGUAGE_DATA/{3456,3457,3458,5096,5100,5102}.mp4` (SHA-256; every frame decoded read-only
    for a difference profile; one 3×8 contact sheet written to the session scratchpad, outside the
    repo);
  - `videos/*.mp4` (header metadata only).
- Action performed: Read-only, with temporary scripts in the session scratchpad. No dataset file was
  opened for writing.
- Files changed: This log entry only.
- Dataset files changed: None.
- Result: see `agent_docs/test_log.md` (2026-10-22). In short:
  - the sheet copy inside `SIGN_LANGUAGE_DATA/` is identical;
  - the colour-cluster clips are 3 exact pairs, and the 3 unique clips share their first ~70% of
    frames;
  - 3,379 unique sentences with the session normaliser.
- Errors/warnings: None.
- Next step: Day 1 Step 1 (environment + config) on the owner's go; no dataset files are touched in
  that step except reading 2 sample clips for the rotation test.

## 2026-10-22 (Day 1 Step 1)

- Computer: Desktop (`DESKTOP-4NDR99B`)
- Task: Environment check — OpenCV rotation test and MediaPipe smoke test.
- Files/folders inspected: `videos/0.mp4` and `videos/2.mp4` (frames decoded read-only; `0.mp4`
  also used for the MediaPipe check and benchmark).
- Action performed: Read-only, via `notebooks/00_env_check.ipynb` (`src/bdsl/env.py`).
- Files changed: This log entry only.
- Dataset files changed: None. SHA-256 before = after (0.mp4 ed3713970f46…1bb6; 2.mp4
  111ece319ea3…1569).
- Result: rotation handled correctly (0.mp4 270° → portrait; 2.mp4 unchanged). See
  `agent_docs/test_log.md` (Day 1 Step 1).
- Errors/warnings: None.
- Next step: Day 1 Step 2 (manifest, split S1 v0, pilot50_v1) on the owner's go.

## 2026-10-22 (Day 1 Step 2)

- Computer: Desktop (`DESKTOP-4NDR99B`)
- Task: Manifest v1, leakage groups, split S1 v0, pilot50_v1 selection and copy (owner-approved plan;
  pilot list option B approved by the owner).
- Files/folders inspected: `FinalSheet2.xlsx`; all 5,010 `SIGN_LANGUAGE_DATA/*.mp4` (full SHA-256,
  OpenCV header + first frame, read-only).
- Action performed: `uv run python -m bdsl.cli manifest | split | pilot-select | pilot-copy --confirm`.
  50 clips **copied** (temp file + rename) to `dataset/pilot50_v1/videos/` (gitignored, ADR-0017).
- Files changed: new `dataset/pilot50_v1/{videos/ (50 copies), pilot50_manifest.csv,
  SELECTION_PROTOCOL.md, README.md}`; this log entry. Outputs in `work/` (gitignored).
- Dataset files changed: None. Size + mtime of all 5,010 videos and the sheet SHA-256 identical
  before, after the manifest run, and after copying.
- Result: 5,010 rows, 0 decode failures, 3,456 unique SHA-256, 3,378 unique `norm_v1` sentences,
  3,376 leakage groups, 0 label conflicts; S1 v0 2,700/357/319 groups, no leakage found; pilot 40/5/5,
  50/50 copies SHA-256 identical to the sources. Details: `agent_docs/test_log.md` (2026-10-22, Day 1 Step 2) and
  `dataset/pilot50_v1/SELECTION_PROTOCOL.md`.
- Errors/warnings: None.
- Next step: Owner reviews Step 2; doc updates for the results; then Day 2 on the owner's go.

## 2026-10-22 (Day 2 Step 1)

- Computer: Desktop (`DESKTOP-4NDR99B`)
- Task: MediaPipe Holistic feature extraction + QC on pilot50_v1 (owner-approved plan).
- Files/folders inspected: the 50 pilot **copies** in `dataset/pilot50_v1/videos/` (decoded read-only,
  three times: VIDEO run, IMAGE run, kill-and-resume test). The originals in `SIGN_LANGUAGE_DATA/` were
  not opened. One copy (3671) was also decoded for a smoke test before the run.
- Action performed: `uv run python -m bdsl.cli extract --data pilot50 --mode both`; kill-and-resume test
  (VIDEO mode) into `work/features_resume_test/`. Features written to `work/features/` (gitignored); no
  raw face mesh and no image data stored (checked on all 150 .npz files).
- Files changed: This log entry only.
- Dataset files changed: None. The 50 copies still match `pilot50_manifest.csv` (SHA-256); the 50
  originals' size + mtime are unchanged.
- Result: 50/50 clips per mode, 0 failures; feat_ver VIDEO `fa89892d4908`, IMAGE `395e878f9861`.
  Details in `work/features/*/qc.csv` and `work/features/compare_pilot50.json`.
- Errors/warnings: None.
- Next step: Owner chose VIDEO mode (ADR-0023). How hand sides map to the signer (mirroring) is
  open (agent_docs/open_questions.md G8). Then Day 2 Step 2 on the owner's go.

## 2026-10-22 (Day 2 Step 2)

- Computer: Desktop (`DESKTOP-4NDR99B`)
- Task: Gloss convention v0.1 + G0 auto-drafts for pilot50_v1 (owner-approved plan, with rule R5).
- Files/folders inspected: `FinalSheet2.xlsx` (sentence text only, for the R5 word list) and
  `dataset/pilot50_v1/pilot50_manifest.csv`. No video was opened.
- Action performed: `uv run python -m bdsl.cli gloss-draft --data pilot50` (twice, byte-identical) and
  `gloss-validate`.
- Files changed: new `annotations/{GLOSS_CONVENTION_v0.1.md, REVIEW_GUIDE.md, REVIEWERS.csv,
  pilot50_v1_gloss_v01.csv}`; this log entry.
- Dataset files changed: None (sheet and pilot manifest SHA-256 identical before and after).
- Result: 50/50 rows `auto_draft`, 0 validation problems, 0 rows usable for training until a
  registered team member reviews them.
- Errors/warnings: None.
- Next step: Owner registers reviewer code(s) in `annotations/REVIEWERS.csv` and arranges the team
  review (`annotations/REVIEW_GUIDE.md`) before Day 3.

## 2026-10-22 (Session 6 audit)

- Computer: Desktop (`DESKTOP-4NDR99B`)
- Task: Read-only audit for the pilot report and the full-dataset plan.
- Files/folders inspected:
  - `dataset/pilot50_v1/videos/` (SHA-256 of all 50 copies, compared with `pilot50_manifest.csv`);
  - `SIGN_LANGUAGE_DATA/` (listing and size only: 5,012 entries, 67 GB on disk);
  - `videos/` (file count only: 50).
- Action performed: Read-only hashing and listing. No video was opened or decoded.
- Files changed: This log entry only.
- Dataset files changed: None.
- Result: 50/50 pilot copies match their manifest. Details in `agent_docs/test_log.md` (2026-10-22,
  Audit + report generation).
- Errors/warnings: None.
- Next step: Owner reviews `research/reports/` and proposal 05; any dataset processing follows its
  approval gates.

## 2026-10-23 (kaggle400 selection, Session 8)

- Computer: Desktop files read by the AI through the desktop app link; work done in the AI's cloud workspace.
- Task: choose 400 clips for the kaggle400 experiment (owner request, chat 2026-10-23).
- Files/folders inspected: copies of `work/manifests/manifest_v1.csv` (SHA-256 `2ff133cf…`, = meta),
  `work/splits/S1_v0.csv` (`40481a5f…`, = meta), `work/pilot/pilot50_v1_selection.csv` and the 50 pilot
  feature files (`work/features/fa89892d4908/*.npz`, derived data) were copied read-only into the AI
  workspace. **No video file was opened, copied or uploaded in this step.**
- Action performed: `kaggle/src/k400_run.py select` → `kaggle/data/` manifests, SPLIT_REPORT.md,
  SPLIT_SUMMARY.png, SELECTION_META.json; `gloss` → `kaggle/processed/glosses/`.
- Files changed: the files above (new); this log entry.
- Dataset files changed: None.
- Result: 320 / 40 / 40 clips (5.94 GB of source videos per manifest_v1); leakage checks 1–7 PASS.
- Errors/warnings: None.
- Next step: the owner runs `kaggle/tools/run_local_steps.ps1`; its copy step adds its own entry below.

## 2026-10-23 (kaggle400: 400-video copy for the Kaggle experiment) <!-- k400-copy-log -->

- Computer: DESKTOP-4NDR99B
- Task: copy the 400 clips chosen for kaggle400 (owner permission in chat, 2026-10-23) into
  `kaggle/data/{train,val,test}/videos/`.
- Files/folders inspected: `SIGN_LANGUAGE_DATA/<Index>.mp4` for the 400 Index values in
  `kaggle/data/subset_manifest.csv` (read-only: SHA-256, size, modification time).
- Action performed: `kaggle/src/k400_run.py copy-videos --confirm` (temp file + rename; SHA-256 of
  source, copy and manifest_v1 compared; size and modification time of every source compared before/after).
- Files changed: `kaggle/data/` (gitignored copies, COPY_VERIFICATION.csv, subset_manifest.csv
  `sha256_copy`, SPLIT_LOCK.json, SPLIT_REPORT.md section 9); this log entry.
- Dataset files changed: None (sources unchanged: 400/400).
- Result: 400/400 copies byte-identical; 5.94 GB; videos digest
  `ec1f61a231048286…`; leakage tests PASS.
- Errors/warnings: None.
- Next step: upload the package (private Kaggle dataset) on the owner's own action.
- Re-check 2026-10-23T06:26:35+00:00 (DESKTOP-4NDR99B): copied in this run 0, already present 400; 400/400 byte-identical; sources unchanged 400/400; leakage tests PASS.
- Re-check 2026-10-23T06:35:16+00:00 (DESKTOP-4NDR99B): copied in this run 0, already present 400; 400/400 byte-identical; sources unchanged 400/400; leakage tests PASS.
