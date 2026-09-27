# Dataset

Team-owned Bangla sentence → BdSL video dataset. Full permissions are secured. Videos are primarily training data; a held-out evaluation split must be reserved (not yet created).

**Do not modify the dataset files.** The spelling in the sentence text is intentional and stays unchanged unless a later research decision changes this.

## `initial_dataset/`

| File | Status | Contents (verified) |
|---|---|---|
| `FinalSheet2.xlsx` | **Current** | Sheet `Sheet1`, columns `Names` (Bangla sentence) and `Index`. 5,010 rows; `Index` 0–5460, all unique; values 333–783 are absent. |
| `superseded/FinalSheet.xlsx` | Superseded | Same columns. 3,491 rows (`Index` 0–3941), identical to the first 3,491 rows of `FinalSheet2.xlsx`. `FinalSheet2.xlsx` adds 1,519 rows (`Index` 3942–5460). |
| `FinalSheet_DuplicateGroups.xlsx` | Derived | Sheets `Duplicate Groups` (178 rows: `Group No`, `Sentence`, `Original Index`) and `Summary` (82 groups; 3,395 unique sentences after trimming whitespace). Computed over the 3,491 rows of `FinalSheet.xlsx` only, so it does not cover `Index` 3942–5460. |
| `videos/` | Sample | 50 clips named `<Index>.mp4` (~767 MB): `Index` 0–3, 328–332, 784–794, 3931–3950, 5451–5460. Every clip has a matching row in `FinalSheet2.xlsx`. |

## Full dataset

- The full video set is stored on the desktop. Only the 50-clip sample above is in this folder.
- Full-dataset work runs on the desktop or via Drive → Colab. The laptop is for code and small-sample work.
- Profiling reported in `research/design_proposals/02_BdSL_Text-to-Sign_Research_and_Build_Guide.md` (not re-verified here): 5,010 MP4 files, 66.3 GB; about 3,456 unique sentence/video pairs after duplicate removal.

## Known / unknown

- One signer per clip. Total number of distinct signers: **unverified**.
- Train/validation/held-out evaluation split: **not yet created**.
