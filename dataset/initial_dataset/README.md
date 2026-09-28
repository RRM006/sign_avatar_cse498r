# Initial Dataset Directory

## Purpose

This directory holds the project's local working/sample dataset for Vibe Coding. It contains a small video sample, the current sentence-text/index spreadsheet, related duplicate-group information, and the separate full video set. The full set is kept locally and ignored by Git; do not add it to Git.

## Verified Contents

```text
initial_dataset/
|-- FinalSheet2.xlsx
|-- FinalSheet_DuplicateGroups.xlsx
|-- README.md
|-- DATASET_WORK_LOG.md
|-- SIGN_LANGUAGE_DATA/
|   `-- SESSION_LOG.md plus 5,010 MP4 files
|-- superseded/
|   `-- FinalSheet.xlsx
`-- videos/
    `-- 50 sample MP4 files
```

- `videos/` contains 50 sample videos. Their filenames are numeric IDs with the `.mp4` extension.
- `FinalSheet2.xlsx` is the current text/annotation file. Its `Sheet1` has `Names` and `Index` columns, 5,010 data rows, and 5,010 unique nonblank `Index` values. `Names` contains the Bangla sentence text. The observed `Index` range is 0 through 5460; IDs are not contiguous.
- `FinalSheet_DuplicateGroups.xlsx` contains `Duplicate Groups` (`Group No`, `Sentence`, `Original Index`) and `Summary` (`Metric`, `Value`) worksheets.
- `superseded/FinalSheet.xlsx` is the superseded spreadsheet. Its `Sheet1` has `Names` and `Index` columns and 3,491 data rows.
- `SIGN_LANGUAGE_DATA/` is the full/raw video set. It contains 5,010 numeric-ID MP4 files and `SESSION_LOG.md`. No subdirectories were present when inspected. The exact filename-ID set matches the 5,010 unique `Index` values in `FinalSheet2.xlsx`.
- The full set is protected by the repository ignore rule `dataset/initial_dataset/SIGN_LANGUAGE_DATA/`.

## Video-to-Text IDs

The video filename stem is the numeric `Index` value in `FinalSheet2.xlsx` (for example, `videos/0.mp4` maps to the row whose `Index` is `0`). All 50 sample video IDs were found in the current spreadsheet. The full set has exactly the same ID set as the current spreadsheet. This verifies the ID mapping, not the correctness or meaning of each annotation.

## Limitations and Unknowns

- Both inspected annotation workbooks have an unnamed third column with no values; its intended purpose is unknown.
- No separate train/validation/test split files or split-specific subdirectories were found here.
- No separate data dictionary was found in this directory.
- Video contents were not inspected as part of the directory and ID verification; no claims are made here about duration, codec, framing, signer, or sign quality.
- The duplicate-group workbook's detailed methodology is not established by this directory inventory.

## AI/Vibe Coding Instructions

- Whenever you need to work with this dataset, read this `README.md` first.
- Inspect the relevant files before making claims. Do not assume the dataset structure, filenames, formats, or metadata.
- Do not rename, move, delete, overwrite, or modify dataset files unless the owner explicitly requests it.
- If sample videos are needed, use the samples already in `videos/`.
- If text/annotation data is needed, use `FinalSheet2.xlsx` as the current file and inspect the actual workbook.
- Do not copy or upload dataset files outside the project/team without explicit permission.
- Do not add `SIGN_LANGUAGE_DATA/` or any of its files to Git. Do not force-add it.
- Do not commit dataset files unless they are explicitly intended to be tracked.
- If actual contents contradict this README, report the difference. Update this README only after verifying the actual information.
- Record every meaningful inspection or operation involving files under `dataset/initial_dataset/` in `DATASET_WORK_LOG.md`, including read-only inspections. Use the actual date and state explicitly when no dataset files changed.