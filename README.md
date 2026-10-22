# Bangla Text → Bangla Sign Language (BdSL) Translation Using a 3D Avatar

CSE498R research project (NSU). A Bangla text sentence goes in; the BdSL translation is performed by a 3D avatar.

**Status (2026-10-22):** The literature review is closed. The research design was approved in principle on 2026-10-22 (`agent_docs/decisions.md`, ADR-0014–0024). The 5-day prototype is in progress: Day 1 (environment, configuration, dataset manifest, split S1 v0, 50-video pilot) and Day 2 (pilot feature extraction; provisional gloss convention and automatic gloss drafts awaiting team review) are done. There are no trained models or experimental results yet.

## Scope (confirmed)

- Input: Bangla text. Output: BdSL performed by a 3D avatar.
- Translation is sentence-level and must handle BdSL grammar/word order rather than word-by-word lookup.
- Out of scope: speech input, and sign-to-text.
- Deliverables: report, literature review, trained model and results. Goal: a publishable research paper with proper academic rigour.

## Folder layout

| Path | Contents |
|---|---|
| `dataset/` | Team dataset: current and superseded spreadsheets, 50-clip video sample (the full video set is local and gitignored). See `dataset/README.md`. |
| `dataset/pilot50_v1/` | The 50-video pilot set: selection protocol and manifest (videos are local copies, gitignored). |
| `configs/`, `src/bdsl/`, `tests/`, `notebooks/` | Pipeline code (Python package `bdsl`), layered configs, tests and notebooks. Setup and commands: `CLAUDE.md`. |
| `annotations/` | Provisional gloss convention, review guide, reviewer register (codes only) and pilot gloss annotations (`auto_draft` until reviewed). |
| `research/papers/` | The six source PDFs (see the notice in its README: use the analyses instead of reading the PDFs). |
| `research/paper_analyses/` | `01`–`06`: one analysis per paper. `07`–`08`: cross-paper comparisons. |
| `research/design_proposals/` | Research/design documents. `01`–`03` are proposals; `04` is the design review approved in principle on 2026-10-22. |
| `research/paper_reading_template.md` | The form used to write the paper analyses. |
| `agent_docs/` | Project memory: current task, decisions (ADRs), open questions, logs. |

## Design (approved in principle, 2026-10-22)

- **Pipeline:** Bangla sentence → gloss sequence (Model A) → generated motion on MediaPipe-derived features (Model B) → retargeted 3D VRM avatar. A direct text → motion model is a comparison; learned models are compared with simple baselines.
- **Annotations:** gloss statuses `auto_draft`, `team_reviewed`, `expert_validated`, `rejected`. Automatic pseudo-glosses are never presented as BdSL annotations.
- **Evaluation:** text → gloss, gloss → motion and the avatar are evaluated separately, plus human/expert evaluation when available. Results are signer-dependent (signer identities are unknown).
- **Compute:** local CPU (desktop) for data work and feature extraction; Kaggle for training; Colab as fallback.

Details and approval status of each item: `agent_docs/decisions.md`.

## Dataset

Team-owned, with permissions secured; the owner has permission to make it publicly available. Terms for reuse by others: not yet stated (`agent_docs/open_questions.md` G1). `FinalSheet2.xlsx` is current. There is one signer per clip. The spelling in the dataset is intentional.

## Open

See `agent_docs/open_questions.md` §G (reuse licence, deadline, and measurements still to be made).
