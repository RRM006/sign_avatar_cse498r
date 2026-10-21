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