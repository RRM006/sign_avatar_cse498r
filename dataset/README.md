# Dataset

Team-owned Bangla sentence → BdSL video dataset. Full permissions are secured, and the owner has permission to make the dataset publicly available (2026-10-22, ADR-0017); this repository is public by the owner's choice. Terms for reuse by others are not yet stated (`agent_docs/open_questions.md` G1). Each new distribution channel needs the owner's OK. Videos are primarily training data; a held-out evaluation split must be reserved (policy: ADR-0018; split S1 v0 created 2026-10-22, provisional until the shared-segment scan, in `work/splits/` — gitignored).

**Do not modify the dataset files.** The spelling in the sentence text is intentional and stays unchanged unless a later research decision changes this.

## `initial_dataset/`

| File | Status | Contents (verified) |
|---|---|---|
| `FinalSheet2.xlsx` | **Current** | Sheet `Sheet1`, columns `Names` (Bangla sentence) and `Index`. 5,010 rows; `Index` 0–5460, all unique; values 333–783 are absent. |
| `superseded/FinalSheet.xlsx` | Superseded | Same columns. 3,491 rows (`Index` 0–3941), identical to the first 3,491 rows of `FinalSheet2.xlsx`. `FinalSheet2.xlsx` adds 1,519 rows (`Index` 3942–5460). |
| `FinalSheet_DuplicateGroups.xlsx` | Derived | Sheets `Duplicate Groups` (178 rows: `Group No`, `Sentence`, `Original Index`) and `Summary` (82 groups; 3,395 unique sentences after trimming whitespace). Computed over the 3,491 rows of `FinalSheet.xlsx` only, so it does not cover `Index` 3942–5460. |
| `videos/` | Sample (`sample50`) | 50 clips named `<Index>.mp4` (~767 MB): `Index` 0–3, 328–332, 784–794, 3931–3950, 5451–5460. Every clip has a matching row in `FinalSheet2.xlsx`. Not the same set as `pilot50_v1`. |

## Full dataset

- The full video set (5,010 MP4, 66.3 GiB) is stored on the desktop in
  `initial_dataset/SIGN_LANGUAGE_DATA/`, which is **gitignored** (verified 2026-10-21). That folder also
  holds `SESSION_LOG.md` and a byte-identical copy of `FinalSheet2.xlsx` (verified 2026-10-22). Only the
  50-clip sample above is committed to git. See `initial_dataset/README.md`.
- Data work and MediaPipe extraction run on the desktop (CPU). Training uses derived features on Kaggle
  (private dataset, no videos), with Colab as fallback (ADR-0016, ADR-0017). The laptop is for code and
  small-sample work.
- Measured 2026-10-22 (manifest v1, `agent_docs/test_log.md`): 3,456 unique videos after exact-duplicate removal;
  3,378 unique sentences after `norm_v1` (NFC + punctuation + whitespace); 3,376 leakage groups; 0 label conflicts.
- `pilot50_v1/` (2026-10-22): 50 pilot clips (40/5/5 from split S1 v0) as gitignored copies in `pilot50_v1/videos/`,
  with `pilot50_manifest.csv` and `SELECTION_PROTOCOL.md` (ADR-0017, ADR-0018, ADR-0022).

## Known / unknown

- One signer per clip. Total number of distinct signers: **unverified** (owner estimate ~4–6); signer
  per clip is unknown and is not inferred (ADR-0018).
- Colour cluster (Index 3456/3457/3458 + exact copies 5096/5100/5102): retained as one group with
  provisional labels (ADR-0018).
- Train/validation/held-out evaluation split: **S1 v0 created 2026-10-22** (2,700/357/319 groups; provisional until the shared-segment scan, open_questions G2; policy ADR-0018).
