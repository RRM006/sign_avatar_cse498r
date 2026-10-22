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

**Current phase: 5-day prototype (Phase 3), in progress (Days 1–2 done 2026-10-22; pilot gloss review pending).** The literature review is complete
(ADR-0012). The research design was approved in principle on 2026-10-22 (ADR-0014–0021; rationale in
`research/design_proposals/04_…`): Bangla → gloss (Model A) → motion (Model B, MediaPipe-derived
features) → retargeted VRM avatar. Technical specifics marked "Accepted in principle" may change from
evidence, only with the owner's OK. Implementation runs one owner-approved step at a time
(`agent_docs/current_task.md`).

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
7. **Dataset sharing follows ADR-0017.** The repo is public by the owner's choice, and the owner has
   permission to make the dataset public. Any *new* channel or use (e.g. a public Kaggle dataset, a
   paper supplement, another platform) needs the owner's explicit OK; keep consent, privacy, licence
   and attribution requirements. Only derived features (no videos, no raw face mesh) go to the
   private Kaggle dataset.

## HOW I WANT YOU (THE AI) TO WORK WITH ME

- Inspect the actual files before making claims or changes. Never claim something was read, created,
  moved or verified unless you actually did it.
- If an important detail is unclear and it changes the result, ask. Don't ask questions that don't
  change anything.
- Label clearly: existing evidence · owner requirement · proposed idea · future work.
- Write implementation code only for the step the owner has approved, and stop at its end.
  *(Owner-confirmed, ADR-0013.)*
- Never install packages, download models, upload data, copy videos, commit or push without the
  owner's explicit OK for that action.
- Explain things simply; the team is new to ML/NLP. *(Owner-confirmed, ADR-0013.)*

## TECH CONSTRAINTS

- **Zero budget.** Free tools and resources only (owner-confirmed 2026-09-27, ADR-0004).
- **Compute (ADR-0016):** the desktop (Ryzen 5 3500X, ~24 GB RAM, RX 570 8 GB) holds the full
  dataset and runs inspection and MediaPipe extraction on CPU; Kaggle is the primary training
  platform (derived features only); Google Colab is the fallback; the laptop is for code and small
  samples. Python 3.12 + mediapipe 0.10.35 (Day-1 check passed 2026-10-22).
- **Data location (verified 2026-10-21):** the full 5,010-video set is in
  `dataset/initial_dataset/SIGN_LANGUAGE_DATA/` on the desktop and is **gitignored** — never add it to
  git. Only the 50-clip sample (`videos/`) is committed. Drive → Colab remains allowed (ADR-0009);
  derived features may go to a private Kaggle dataset (ADR-0017).
- **Public repo (ADR-0017):** everything committed is published. Never commit derived features,
  checkpoints, `work/`, credentials or reviewers' personal data.
- **Language:** Bangla (primary).

## CURRENT STACK

Installed in `.venv` (2026-10-22, pins in `pyproject.toml` / `uv.lock`): Python 3.12.13, mediapipe
0.10.35, opencv-contrib-python 5.0.0.93, numpy 2.4.6, PyYAML 6.0.3, pandas 3.0.3, openpyxl 3.1.5, torch 2.14.1 (CPU); dev: pytest,
ipykernel, nbclient, nbformat. Planned (ADR-0019): three.js + three-vrm.

## COMMANDS

Run from the project root. The environment is the uv-managed `.venv` (Python 3.12; ADR-0016).
- Set up or update the environment: `uv sync --extra extract --extra train`
- Run the tests: `uv run pytest`
- Environment check: open `notebooks/00_env_check.ipynb` with the `.venv` kernel and run all cells
  → `work/reports/env_report.json`
- Dataset (Day 1 Step 2): `uv run python -m bdsl.cli manifest --data full`, then `… split`, then
  `… pilot-select`; `… pilot-copy --confirm` only after the owner approves the pilot list.
- Features (Day 2 Step 1): `uv run python -m bdsl.cli extract --data pilot50 --mode video` (VIDEO
  mode, ADR-0023; full-set extraction only on the owner's go).
- Annotations (Day 2 Step 2): `uv run python -m bdsl.cli gloss-draft --data pilot50` (never overwrites
  reviewed rows) and `… gloss-validate` (run after every review session).
- Choose the platform layer with `BDSL_ENV` (local / kaggle / colab); move outputs with `BDSL_WORK_DIR`.
- Never `git add` work/, .venv/ or videos (CLAUDE.md rules 6–7, ADR-0017).

## CONVENTIONS

- Dates are absolute, `YYYY-MM-DD`.
- New paper analyses: fill `research/paper_reading_template.md` and save as
  `research/paper_analyses/NN-<short_title>.md` (next number: 09). Add the PDF to `research/papers/`.
- Dataset: `FinalSheet2.xlsx` is the current sheet (ADR-0008). Each sentence's `Index` equals the
  video filename `videos/<Index>.mp4`. The non-standard spelling is intentional; don't correct it.
- New ideas, notes or requirements from the owner: given in chat; the AI records them in
  `agent_docs/` (ADR-0021).

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
