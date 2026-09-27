# CLAUDE.md — Bangla Text-to-BdSL Translation Using a 3D Avatar

> Claude Code (and any AI assistant) reads this file at the start of every session.
> Keep it SHORT. The detailed, living docs are in `agent_docs/` (listed at the bottom).

## What this project is

An initial research project, **"Bangla Text-to-Bangla Sign Language (BdSL) Translation Using a 3D
Avatar"**, by a beginner ML/NLP team (CSE498R, inferred from folder and file names). The goal is to
investigate research, methods, datasets, models and technologies for converting Bangla text into BdSL
and showing the result through a 3D avatar.

**Confirmed scope (ADR-0007):** Bangla text sentence → BdSL on a 3D avatar only (no speech input, no
sign → text). Sentence-level translation with BdSL grammar/word order, not word-by-word lookup.
Deliverable: report + literature review + trained model + results, aimed at a publishable paper.

**Current phase: pipeline/system design.** The literature review is complete (ADR-0012). No pipeline,
model, sign representation, text → sign mapping, sign lexicon, avatar technology or training method has
been chosen (ADR-0002, ADR-0010). MediaPipe Holistic is only the interim landmark-extraction step.

**Not a medical project** (owner, 2026-09-27). No medical audio, no medical entity extraction, no
dialect focus (ADR-0003). The wrong context blocks were removed from analyses 01–08 (ADR-0012).
Remaining medical/dialect mentions there are genuine paper findings.

## NON-NEGOTIABLE RULES (never break these)

1. **Don't invent project facts.** If it isn't in the repo or said by the owner, write "(TBD — decide
   with owner)" or ask. Say "I don't know" rather than guess.
2. **Don't finalize design decisions yourself.** Pipeline, model, dataset strategy, sign
   representation, avatar tech, training and evaluation are chosen by the owner. Record a decision in
   `agent_docs/decisions.md` only after the owner confirms it.
3. **Keep evidence, owner requirements, proposals and future work separate.** Recommendations inside
   `research/paper_analyses/` ("our v0.1 baseline", "we should…") are AI-written **proposals**, not
   decisions.
4. **Don't read the PDFs in `research/papers/`.** The owner keeps that notice on purpose (ADR-0006).
   Use the analyses in `research/paper_analyses/` instead.
5. **Don't move, rename or delete files when the reason is uncertain.** Ask first.
6. **Never commit secrets or credentials.** *(Conservative default — kept by owner, ADR-0013.)*
7. **Don't share or upload `dataset/` videos outside this repo/team** until their origin, licence and
   consent are known. *(Conservative default — kept unchanged by owner, ADR-0013; see
   `open_questions.md` E4.)*

## HOW I WANT YOU (THE AI) TO WORK WITH ME

- Inspect the actual files before making claims or changes. Never claim something was read, created,
  moved or verified unless you actually did it.
- If an important detail is unclear and it changes the result, ask. Don't ask questions that don't
  change anything.
- Label clearly: existing evidence · owner requirement · proposed idea · future work.
- Research/design phase: don't write implementation code unless the owner asks for it.
  *(Owner-confirmed, ADR-0013.)*
- Explain things simply; the team is new to ML/NLP. *(Owner-confirmed, ADR-0013.)*

## TECH CONSTRAINTS

- **Zero budget.** Free tools and resources only (owner-confirmed 2026-09-27, ADR-0004).
- **Compute (ADR-0004, ADR-0009):** Google Colab (T4 GPU, ~15 GB VRAM, ~12 h session limit) for
  training; desktop for full-dataset work; laptop for code and small samples only. The 24 GB RAM /
  AMD Radeon RX 570 machine is one of these two — which one is (TBD — confirm with owner).
- **Data location:** full dataset on the desktop or Drive → Colab. Only a 50-clip sample is in this
  repo.
- **Language:** Bangla (primary).

## CURRENT STACK

None yet. There is no code. Only MediaPipe Holistic is named, as the interim landmark-extraction
step (ADR-0010). Every other tool, model and framework is **(TBD — see
`agent_docs/open_questions.md`)**. Candidate technologies in the paper analyses and
`research/design_proposals/` are options, not choices.

## COMMANDS

None yet. There is no code to set up, run or test.

## CONVENTIONS

- Dates are absolute, `YYYY-MM-DD`.
- New paper analyses: fill `research/paper_reading_template.md` and save as
  `research/paper_analyses/NN-<short_title>.md` (next number: 09). Add the PDF to `research/papers/`.
- Dataset: `FinalSheet2.xlsx` is the current sheet (ADR-0008). Each sentence's `Index` equals the
  video filename `videos/<Index>.mp4`. The non-standard spelling is intentional; don't correct it.
- New raw ideas, notes or requirements from the owner go in `new_project_intake/` (the inbox).

## PROJECT MEMORY FILES — our shared brain (in `agent_docs/`)

**At the START of every session, read these in order:**
1. `agent_docs/session_protocol.md` — how we start and end a session
2. `agent_docs/current_task.md` — what we are doing RIGHT NOW + the next step
3. `agent_docs/changelog.md` — recent session history (newest first)
4. `agent_docs/milestone_log.md` — status of all milestones and phases

**Read these when relevant:**
5. `agent_docs/constitution.md` — stable purpose, rules, constraints, what's hard
6. `agent_docs/decisions.md` — decisions made so far (ADR style)
7. `agent_docs/open_questions.md` — undecided questions + candidate options from the literature
8. `agent_docs/codebase_map.md` — where everything lives in the repo
9. `agent_docs/test_log.md` — what was checked/tested + results
10. `README.md` and `dataset/README.md` — confirmed scope and dataset facts
11. `research/papers/README.md` — which analysis covers which paper
12. `research/design_proposals/` — AI-written design proposals (not decisions)

**At the END of every session**, update `changelog.md` and `current_task.md` (and
`milestone_log.md` / `decisions.md` / `open_questions.md` / `test_log.md` / `codebase_map.md` if they
changed). The exact steps are in `session_protocol.md`.
