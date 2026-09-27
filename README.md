# Bangla Text → Bangla Sign Language (BdSL) Translation Using a 3D Avatar

CSE498R research project (NSU). A Bangla text sentence goes in; the BdSL translation is performed by a 3D avatar.

**Status (2026-09-27):** The literature review is closed. The next phase is end-to-end pipeline/system design. This repository does not yet contain any code, trained models or experimental results.

## Scope (confirmed)

- Input: Bangla text. Output: BdSL performed by a 3D avatar.
- Translation is sentence-level and must handle BdSL grammar/word order rather than word-by-word lookup.
- Out of scope: speech input, and sign-to-text.
- Deliverables: report, literature review, trained model and results. Goal: a publishable research paper with proper academic rigour.

## Folder layout

| Path | Contents |
|---|---|
| `dataset/` | Team dataset: current and superseded spreadsheets, 50-clip video sample. See `dataset/README.md`. |
| `research/papers/` | The six source PDFs (see the notice in its README: use the analyses instead of reading the PDFs). |
| `research/paper_analyses/` | `01`–`06`: one analysis per paper. `07`–`08`: cross-paper comparisons. |
| `research/design_proposals/` | Research/design **proposals**, not decisions. `02` is newer and corrects parts of `01`. |
| `research/paper_reading_template.md` | The form used to write the paper analyses. |
| `new_project_intake/` | Inbox for new material that has not been sorted yet. |

## Confirmed decisions

- **Dataset:** team-owned, with full permissions secured. `FinalSheet2.xlsx` is current and `FinalSheet.xlsx` is superseded. There is one signer per clip. The spelling in the dataset is intentional. A held-out evaluation split must be reserved.
- **Landmark extraction (interim):** MediaPipe Holistic is the current, interim approach. It does not fix the rest of the architecture.
- **Evaluation:** should eventually include both automatic metrics and human/expert evaluation. The protocol is not fixed yet.
- **Compute:** Colab for major training; the desktop for full-dataset storage and preprocessing; the laptop for code editing and small-sample experiments.

## Open (TBD)

- ML / NLP architecture and the final translation pipeline
- Sign representation
- Sign-source strategy
- Avatar / rendering technology
- Training architecture
- Final evaluation protocol and metrics
- Total number of distinct signers (unverified)
- Definition of the train / validation / held-out evaluation split

The documents in `research/design_proposals/` discuss options for these open items. They are proposals only.
