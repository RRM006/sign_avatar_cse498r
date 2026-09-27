# decisions.md — Decision Record (ADR style)

> A dated record of real design choices: what we chose, why, and what we rejected, so decisions
> aren't silently re-opened later. **Only the owner confirms a decision.** Undecided items live in
> `open_questions.md`.
>
> Template:
> ```
> ## ADR-NNNN — YYYY-MM-DD — <title>
> - Decision: <what we will do>
> - Why: <the reason>
> - Rejected: <the main alternative(s) and why not>
> - Status: Accepted | Superseded by ADR-XXXX
> ```

---

## ADR-0001 — 2026-09-27 — Use a markdown project-memory system (CLAUDE.md + agent_docs/)
- Decision: Keep a short `CLAUDE.md` at the root and living docs in `agent_docs/`, updated every
  session (see `session_protocol.md`).
- Why: The owner asked for the project to be set up following `BOOTSTRAP_PROJECT_PROMPT.md`. Its
  stated purpose is to let any AI assistant resume the project session after session without
  re-explaining it.
- Rejected: None recorded.
- Status: Accepted

## ADR-0002 — 2026-09-27 — The design stays open during the research phase
- Decision: No translation pipeline, ML/NLP architecture, dataset strategy, sign representation, 3D
  avatar technology, model, training method or evaluation method is chosen yet. Options are collected
  in `open_questions.md` and decided later with the owner.
- Why: Owner statement. The project is in idea generation and research, and the owner will provide
  ideas and requirements in future sessions.
- Rejected: Adopting a pipeline suggested in the paper analyses now. The owner explicitly deferred these
  decisions.
- Status: Accepted (individual items will be settled by later ADRs)

## ADR-0003 — 2026-09-27 — Not a medical project; no dialect focus
- Decision: The project has no medical-domain focus, no medical audio recordings, no medical entity
  extraction (symptoms, diseases, medications, duration, allergies) and no dialect focus (Dhaka,
  Sylhet, Chittagong, Barishal). Those lines were removed from `research/paper_reading_template.md`.
- Why: Owner correction: "this not medical project this is new project". The lines had been in the
  paper-reading form's context block by mistake, and several analyses already flagged them as a possible
  leftover.
- Rejected: Keeping them as possible scope.
- Status: Accepted

## ADR-0004 — 2026-09-27 — Zero budget; Colab + one local machine
- Decision: Work within zero budget, using Google Colab (T4 GPU, ~15 GB VRAM, ~12 h session limit)
  and a local machine with 24 GB RAM and an AMD Radeon RX 570.
- Why: Owner-confirmed as true for this project. The underlying reason is not stated (TBD).
- Rejected: None recorded.
- Status: Accepted

## ADR-0005 — 2026-09-27 — Folder layout: research/ + dataset/ + inbox
- Decision: Papers → `research/papers/`, paper analyses → `research/paper_analyses/`, reading form →
  `research/paper_reading_template.md`, data → `dataset/initial_dataset/`. `new_project_intake/` stays
  as the inbox for new owner material. The generic `templates/` folder was deleted after use. Analysis
  08 was renamed so it no longer shares its name with 07.
- Why: The owner chose the reorganization for clarity. Files were moved with `git mv` (history kept);
  no file contents changed except the reading-form edit in ADR-0003.
- Rejected: Keeping files in their original `misc/` + `new_project_intake/` locations (the other option
  offered). No reason recorded beyond the owner's choice.
- Status: Accepted

## ADR-0006 — 2026-09-27 — AI does not read the paper PDFs
- Decision: The notice in `research/papers/README.md` (formerly `misc/README.md`) stays. AI assistants
  use `research/paper_analyses/` instead of reading the PDFs.
- Why: Owner confirmed the notice is intentional. The reason is not stated (TBD).
- Rejected: Removing the notice.
- Status: Accepted

## ADR-0007 — 2026-09-27 — Scope and deliverable (answers A1–A3)
- Decision: The deliverable is a report, a literature review, a trained model and results, aimed at a
  publishable research paper (A1). The direction is Bangla text sentence → BdSL on a 3D avatar only
  (A2). Translation is sentence-level and must handle BdSL grammar/word order (A3).
- Why: Owner answers to `open_questions.md` A1–A3.
- Rejected: Speech input and sign → text (out of scope, A2). Word-by-word lookup as the translation
  approach (A3).
- Status: Accepted. Target end users: not stated (TBD — decide with owner).

## ADR-0008 — 2026-09-27 — The initial dataset (answers B1, B2, B3, B5, B6)
- Decision:
  - B1: The dataset was collected by the team and is fully team-owned. Permissions are in place.
  - B2: `FinalSheet2.xlsx` is the current sheet. `FinalSheet.xlsx` is obsolete/superseded (kept in
    `dataset/initial_dataset/superseded/`).
  - B3: One signer per clip. The total number of distinct signers is still unverified.
  - B5: The videos are primarily training data. Pose/landmarks extracted from them feed the
    sign-generation model. A held-out evaluation split must be reserved.
  - B6: The non-standard spelling is intentional and stays unchanged. `videos/videos.txt` was
    unnecessary (no longer in the folder).
- Why: Owner answers to `open_questions.md` B1–B3, B5, B6.
- Rejected: Correcting the spelling in the sheets (B6).
- Status: Accepted. Still open: number of distinct signers; how the split is defined.

## ADR-0009 — 2026-09-27 — Data storage and what runs where (answers B4, C6)
- Decision: The full dataset stays on the desktop or goes Google Drive → Colab. Only the 50-clip
  sample is in this repo. Colab is for training, the desktop for full-dataset work, the laptop for code
  and small samples only.
- Why: Owner answers to `open_questions.md` B4 and C6.
- Rejected: None recorded.
- Status: Accepted. Refines ADR-0004, which names "one local machine (24 GB RAM, RX 570)". Which of
  the two machines that is: (TBD — confirm with owner).

## ADR-0010 — 2026-09-27 — Sign representation, mapping and lexicon stay open (answers C1–C4)
- Decision:
  - C1: The final sign representation and avatar technology are **not decided**. MediaPipe Holistic
    is only the interim landmark-extraction step.
  - C2: The text → sign mapping is **not decided**.
  - C3: The sign lexicon / data source is **not decided**.
  - C4: Fingerspelling is the recommended fallback for words without a sign, but this still has to
    be validated as a research/design decision.
- Why: Owner answers to `open_questions.md` C1–C4. ADR-0002 stays in force for these items.
- Rejected: None recorded.
- Status: Accepted (C1–C4 remain open in `open_questions.md`).

## ADR-0011 — 2026-09-27 — Evaluation combines human and automatic evaluation (answer C5)
- Decision: Evaluation combines human evaluation (BdSL experts, deaf signers, interpreters) with an
  automatic metric. Which metric, who the evaluators are and the exact protocol are (TBD — decide with
  owner).
- Why: Owner answer to `open_questions.md` C5.
- Rejected: None recorded.
- Status: Accepted (direction only).

## ADR-0012 — 2026-09-27 — Literature review closed; IsharaKotha citation; analyses cleaned (answers D1–D3)
- Decision:
  - D1: Cite IsharaKotha as **arXiv:2511.16896 (2025)**. The "Rahman et al. 2023, Heliyon" reference
    in analysis 05 is not the project citation.
  - D2: The literature review is complete. The next phase is pipeline/system design.
  - D3: Remove the unrelated medical/dialect context blocks from analyses 01–08 and keep the genuine
    research-paper findings. Done by the owner; verified on 2026-09-27 (see `test_log.md`).
- Why: Owner answers to `open_questions.md` D1–D3.
- Rejected: Keeping the wrong context blocks with a warning (the earlier interim approach).
- Status: Accepted. ADR-0003 (not medical, no dialect focus) still applies.

## ADR-0013 — 2026-09-27 — Conservative defaults and working style kept (answer D4)
- Decision: These stay unchanged: never commit secrets; don't share dataset videos outside the
  repo/team; no implementation code unless the owner asks; explain things simply.
- Why: Owner answer to `open_questions.md` D4.
- Rejected: None recorded.
- Status: Accepted
